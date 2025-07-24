using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using Microsoft.Extensions.Logging;
using System.Collections.Concurrent;
using System.Diagnostics;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;

public class RequirementsOrchestrationService : IRequirementsOrchestrationService
{
    private readonly IDocumentGenerationService _documentGenerationService;
    private readonly IProjectService _projectService;
    private readonly IWorkflowMonitoringService _workflowMonitoringService;
    private readonly ILogger<RequirementsOrchestrationService> _logger;
    
    // Document generation order and dependencies
    private static readonly List<DocumentTypeDefinition> DocumentTypes = new()
    {
        new DocumentTypeDefinition { Type = "BRD", Name = "Business Requirements Document", Dependencies = Array.Empty<string>() },
        new DocumentTypeDefinition { Type = "PRD", Name = "Product Requirements Document", Dependencies = new[] { "BRD" } },
        new DocumentTypeDefinition { Type = "FRD", Name = "Functional Requirements Document", Dependencies = new[] { "BRD", "PRD" } },
        new DocumentTypeDefinition { Type = "TRD", Name = "Technical Requirements Document", Dependencies = new[] { "BRD", "PRD", "FRD" } }
    };

    // Progress tracking
    private readonly ConcurrentDictionary<Guid, RequirementsGenerationProgress> _progressTracking = new();

    public RequirementsOrchestrationService(
        IDocumentGenerationService documentGenerationService,
        IProjectService projectService,
        IWorkflowMonitoringService workflowMonitoringService,
        ILogger<RequirementsOrchestrationService> logger)
    {
        _documentGenerationService = documentGenerationService;
        _projectService = projectService;
        _workflowMonitoringService = workflowMonitoringService;
        _logger = logger;
    }

    public async Task<GenerateRequirementsResponse> GenerateRequirementsAsync(GenerateRequirementsRequest request, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();
        var response = new GenerateRequirementsResponse
        {
            StartedAt = DateTime.UtcNow
        };

        // Initialize progress tracking
        var progress = new RequirementsGenerationProgress
        {
            ProjectId = request.ProjectId,
            Status = RequirementsGenerationStatus.InProgress,
            StartedAt = DateTime.UtcNow,
            LastUpdatedAt = DateTime.UtcNow
        };

        foreach (var docType in DocumentTypes)
        {
            progress.DocumentProgress[docType.Type] = new DocumentGenerationProgress
            {
                DocumentType = docType.Type,
                Status = DocumentGenerationStatus.Pending
            };
        }

        _progressTracking[request.ProjectId] = progress;

        // Use project ID hash as workflow ID for monitoring
        var workflowId = Math.Abs(request.ProjectId.GetHashCode());

        try
        {
            // Get project details
            var project = await _projectService.GetProjectAsync(request.ProjectId.ToString());
            if (project == null)
            {
                response.Success = false;
                response.Errors.Add($"Project with ID {request.ProjectId} not found");
                UpdateProgressStatus(request.ProjectId, RequirementsGenerationStatus.Failed);
                return response;
            }

            // Start workflow monitoring
            await _workflowMonitoringService.RecordWorkflowStartAsync(workflowId, "RequirementsGeneration");

            // Generate documents in order
            var generatedDocuments = new Dictionary<string, string>();

            foreach (var docType in DocumentTypes)
            {
                UpdateDocumentProgress(request.ProjectId, docType.Type, DocumentGenerationStatus.InProgress);
                UpdateCurrentActivity(request.ProjectId, $"Generating {docType.Name}");

                await _workflowMonitoringService.RecordActivityStartAsync(workflowId, $"{docType.Type} Generation");
                var activityStopwatch = Stopwatch.StartNew();

                try
                {
                    // Prepare dependencies
                    var dependencies = new Dictionary<string, string>();
                    foreach (var dep in docType.Dependencies)
                    {
                        if (generatedDocuments.ContainsKey(dep))
                        {
                            dependencies[dep] = generatedDocuments[dep];
                        }
                    }

                    // Generate document
                    var generationRequest = new DocumentGenerationRequest
                    {
                        DocumentType = docType.Type,
                        ProjectName = request.ProjectName ?? project.Name,
                        ProjectDescription = request.ProjectDescription ?? project.Description,
                        Dependencies = dependencies,
                        AdditionalContext = new Dictionary<string, object>
                        {
                            ["ClientRequirements"] = request.ClientRequirements ?? project.ClientRequirements ?? string.Empty
                        }
                    };

                    if (request.AdditionalContext != null)
                    {
                        foreach (var kvp in request.AdditionalContext)
                        {
                            generationRequest.AdditionalContext[kvp.Key] = kvp.Value;
                        }
                    }

                    var result = await _documentGenerationService.GenerateDocumentAsync(generationRequest, cancellationToken);

                    if (result.Success)
                    {
                        generatedDocuments[docType.Type] = result.Content;
                        response.GeneratedDocuments[docType.Type] = result.Content;

                        // Store document in project
                        await _projectService.AddDocumentToProjectAsync(new AddDocumentRequest
                        {
                            ProjectId = request.ProjectId.ToString(),
                            DocumentType = docType.Type,
                            Content = result.Content,
                            Version = "1.0.0",
                            Metadata = result.Metadata
                        });

                        UpdateDocumentProgress(request.ProjectId, docType.Type, DocumentGenerationStatus.Completed);
                        await _workflowMonitoringService.RecordActivityCompletionAsync(
                            workflowId, 
                            $"{docType.Type} Generation", 
                            true, 
                            activityStopwatch.Elapsed);

                        _logger.LogInformation("Successfully generated {DocumentType} for project {ProjectId}", 
                            docType.Type, request.ProjectId);
                    }
                    else
                    {
                        var error = $"Failed to generate {docType.Type}: {result.Error}";
                        response.Errors.Add(error);
                        UpdateDocumentProgress(request.ProjectId, docType.Type, DocumentGenerationStatus.Failed, result.Error);
                        
                        await _workflowMonitoringService.RecordActivityCompletionAsync(
                            workflowId, 
                            $"{docType.Type} Generation", 
                            false, 
                            activityStopwatch.Elapsed,
                            result.Error);

                        _logger.LogError("Failed to generate {DocumentType} for project {ProjectId}: {Error}", 
                            docType.Type, request.ProjectId, result.Error);

                        // Stop further generation on failure
                        break;
                    }

                    // Add any warnings
                    response.Warnings.AddRange(result.ValidationWarnings);
                }
                catch (Exception ex)
                {
                    var error = $"Exception while generating {docType.Type}: {ex.Message}";
                    response.Errors.Add(error);
                    UpdateDocumentProgress(request.ProjectId, docType.Type, DocumentGenerationStatus.Failed, ex.Message);
                    
                    await _workflowMonitoringService.RecordActivityCompletionAsync(
                        workflowId, 
                        $"{docType.Type} Generation", 
                        false, 
                        activityStopwatch.Elapsed,
                        ex.Message);

                    _logger.LogError(ex, "Exception while generating {DocumentType} for project {ProjectId}", 
                        docType.Type, request.ProjectId);
                    break;
                }

                // Update overall progress
                UpdateOverallProgress(request.ProjectId);
            }

            // Determine final status
            response.Success = response.Errors.Count == 0;
            var finalStatus = response.Success 
                ? RequirementsGenerationStatus.Completed 
                : (response.GeneratedDocuments.Count > 0 
                    ? RequirementsGenerationStatus.PartiallyCompleted 
                    : RequirementsGenerationStatus.Failed);

            UpdateProgressStatus(request.ProjectId, finalStatus);

            // Record workflow completion
            await _workflowMonitoringService.RecordWorkflowCompletionAsync(
                workflowId, 
                "RequirementsGeneration", 
                response.Success, 
                stopwatch.Elapsed);
        }
        catch (Exception ex)
        {
            response.Success = false;
            response.Errors.Add($"Unexpected error: {ex.Message}");
            UpdateProgressStatus(request.ProjectId, RequirementsGenerationStatus.Failed);
            
            await _workflowMonitoringService.RecordWorkflowCompletionAsync(
                workflowId, 
                "RequirementsGeneration", 
                false, 
                stopwatch.Elapsed);

            _logger.LogError(ex, "Unexpected error during requirements generation for project {ProjectId}", request.ProjectId);
        }
        finally
        {
            response.CompletedAt = DateTime.UtcNow;
            response.TotalDuration = stopwatch.Elapsed;
        }

        return response;
    }

    public Task<RequirementsGenerationProgress> GetGenerationProgressAsync(Guid projectId, CancellationToken cancellationToken = default)
    {
        if (_progressTracking.TryGetValue(projectId, out var progress))
        {
            return Task.FromResult(progress);
        }

        // Return empty progress if not found
        return Task.FromResult(new RequirementsGenerationProgress
        {
            ProjectId = projectId,
            Status = RequirementsGenerationStatus.NotStarted,
            OverallProgress = 0,
            DocumentProgress = DocumentTypes.ToDictionary(
                dt => dt.Type,
                dt => new DocumentGenerationProgress
                {
                    DocumentType = dt.Type,
                    Status = DocumentGenerationStatus.Pending,
                    Progress = 0
                })
        });
    }

    private void UpdateDocumentProgress(Guid projectId, string documentType, DocumentGenerationStatus status, string? error = null)
    {
        if (_progressTracking.TryGetValue(projectId, out var progress))
        {
            if (progress.DocumentProgress.TryGetValue(documentType, out var docProgress))
            {
                docProgress.Status = status;
                docProgress.Error = error;
                
                switch (status)
                {
                    case DocumentGenerationStatus.InProgress:
                        docProgress.StartedAt = DateTime.UtcNow;
                        docProgress.Progress = 50;
                        break;
                    case DocumentGenerationStatus.Completed:
                        docProgress.CompletedAt = DateTime.UtcNow;
                        docProgress.Progress = 100;
                        break;
                    case DocumentGenerationStatus.Failed:
                        docProgress.CompletedAt = DateTime.UtcNow;
                        docProgress.Progress = 0;
                        break;
                }
            }

            progress.LastUpdatedAt = DateTime.UtcNow;
        }
    }

    private void UpdateProgressStatus(Guid projectId, RequirementsGenerationStatus status)
    {
        if (_progressTracking.TryGetValue(projectId, out var progress))
        {
            progress.Status = status;
            progress.LastUpdatedAt = DateTime.UtcNow;
        }
    }

    private void UpdateCurrentActivity(Guid projectId, string activity)
    {
        if (_progressTracking.TryGetValue(projectId, out var progress))
        {
            progress.CurrentActivity = activity;
            progress.LastUpdatedAt = DateTime.UtcNow;
        }
    }

    private void UpdateOverallProgress(Guid projectId)
    {
        if (_progressTracking.TryGetValue(projectId, out var progress))
        {
            var totalDocs = progress.DocumentProgress.Count;
            var completedDocs = progress.DocumentProgress.Values.Count(d => d.Status == DocumentGenerationStatus.Completed);
            progress.OverallProgress = totalDocs > 0 ? (completedDocs * 100) / totalDocs : 0;
            progress.LastUpdatedAt = DateTime.UtcNow;
        }
    }

    private class DocumentTypeDefinition
    {
        public string Type { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string[] Dependencies { get; set; } = Array.Empty<string>();
    }
}