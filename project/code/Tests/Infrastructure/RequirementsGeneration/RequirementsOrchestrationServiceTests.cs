using ByteForgeFrontend.Services;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.RequirementsGeneration;

public class RequirementsOrchestrationServiceTests
{
    private readonly Mock<IDocumentGenerationService> _mockDocumentGenerationService;
    private readonly Mock<IProjectService> _mockProjectService;
    private readonly Mock<IWorkflowMonitoringService> _mockWorkflowMonitoringService;
    private readonly Mock<ILogger<RequirementsOrchestrationService>> _mockLogger;
    private readonly RequirementsOrchestrationService _service;

    public RequirementsOrchestrationServiceTests()
    {
        _mockDocumentGenerationService = new Mock<IDocumentGenerationService>();
        _mockProjectService = new Mock<IProjectService>();
        _mockWorkflowMonitoringService = new Mock<IWorkflowMonitoringService>();
        _mockLogger = new Mock<ILogger<RequirementsOrchestrationService>>();

        _service = new RequirementsOrchestrationService(
            _mockDocumentGenerationService.Object,
            _mockProjectService.Object,
            _mockWorkflowMonitoringService.Object,
            _mockLogger.Object
        );
    }

    [Fact]
    public async Task GenerateRequirementsAsync_ShouldGenerateDocumentsInCorrectOrder()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var request = new GenerateRequirementsRequest
        {
            ProjectId = projectId,
            ProjectName = "Test Project",
            ProjectDescription = "Test project description",
            ClientRequirements = "Build a CRM system"
        };

        var project = new Project
        {
            Id = projectId,
            Name = request.ProjectName,
            Description = request.ProjectDescription,
            ClientRequirements = request.ClientRequirements
        };

        _mockProjectService.Setup(x => x.GetProjectAsync(projectId))
            .ReturnsAsync(project);

        SetupSuccessfulDocumentGeneration("BRD", "Business requirements content");
        SetupSuccessfulDocumentGeneration("PRD", "Product requirements content");
        SetupSuccessfulDocumentGeneration("FRD", "Functional requirements content");
        SetupSuccessfulDocumentGeneration("TRD", "Technical requirements content");

        // Act
        var result = await _service.GenerateRequirementsAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Equal(4, result.GeneratedDocuments.Count);
        Assert.Contains("BRD", result.GeneratedDocuments.Keys);
        Assert.Contains("PRD", result.GeneratedDocuments.Keys);
        Assert.Contains("FRD", result.GeneratedDocuments.Keys);
        Assert.Contains("TRD", result.GeneratedDocuments.Keys);

        // Verify documents were generated in the correct order
        var invocations = _mockDocumentGenerationService.Invocations
            .Where(i => i.Method.Name == nameof(IDocumentGenerationService.GenerateDocumentAsync))
            .ToList();

        Assert.Equal(4, invocations.Count);
        Assert.Equal("BRD", ((DocumentGenerationRequest)invocations[0].Arguments[0]).DocumentType);
        Assert.Equal("PRD", ((DocumentGenerationRequest)invocations[1].Arguments[0]).DocumentType);
        Assert.Equal("FRD", ((DocumentGenerationRequest)invocations[2].Arguments[0]).DocumentType);
        Assert.Equal("TRD", ((DocumentGenerationRequest)invocations[3].Arguments[0]).DocumentType);
    }

    [Fact]
    public async Task GenerateRequirementsAsync_ShouldPassDependenciesCorrectly()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var request = new GenerateRequirementsRequest
        {
            ProjectId = projectId,
            ProjectName = "Test Project",
            ClientRequirements = "Build a CRM system"
        };

        var project = new Project
        {
            Id = projectId,
            Name = request.ProjectName,
            ClientRequirements = request.ClientRequirements
        };

        _mockProjectService.Setup(x => x.GetProjectAsync(projectId))
            .ReturnsAsync(project);

        string? capturedBRDContent = null;
        string? capturedPRDContent = null;
        string? capturedFRDContent = null;

        // Capture generated content for each document
        _mockDocumentGenerationService
            .Setup(x => x.GenerateDocumentAsync(It.Is<DocumentGenerationRequest>(r => r.DocumentType == "BRD"), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DocumentGenerationRequest r, CancellationToken ct) =>
            {
                capturedBRDContent = "BRD content for " + r.ProjectName;
                return new DocumentGenerationResponse
                {
                    Success = true,
                    DocumentType = r.DocumentType,
                    Content = capturedBRDContent
                };
            });

        _mockDocumentGenerationService
            .Setup(x => x.GenerateDocumentAsync(It.Is<DocumentGenerationRequest>(r => r.DocumentType == "PRD"), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DocumentGenerationRequest r, CancellationToken ct) =>
            {
                capturedPRDContent = "PRD content based on BRD";
                Assert.True(r.Dependencies.ContainsKey("BRD"));
                Assert.Equal(capturedBRDContent, r.Dependencies["BRD"]);
                return new DocumentGenerationResponse
                {
                    Success = true,
                    DocumentType = r.DocumentType,
                    Content = capturedPRDContent
                };
            });

        _mockDocumentGenerationService
            .Setup(x => x.GenerateDocumentAsync(It.Is<DocumentGenerationRequest>(r => r.DocumentType == "FRD"), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DocumentGenerationRequest r, CancellationToken ct) =>
            {
                capturedFRDContent = "FRD content based on BRD and PRD";
                Assert.True(r.Dependencies.ContainsKey("BRD"));
                Assert.True(r.Dependencies.ContainsKey("PRD"));
                Assert.Equal(capturedBRDContent, r.Dependencies["BRD"]);
                Assert.Equal(capturedPRDContent, r.Dependencies["PRD"]);
                return new DocumentGenerationResponse
                {
                    Success = true,
                    DocumentType = r.DocumentType,
                    Content = capturedFRDContent
                };
            });

        _mockDocumentGenerationService
            .Setup(x => x.GenerateDocumentAsync(It.Is<DocumentGenerationRequest>(r => r.DocumentType == "TRD"), It.IsAny<CancellationToken>()))
            .ReturnsAsync((DocumentGenerationRequest r, CancellationToken ct) =>
            {
                Assert.True(r.Dependencies.ContainsKey("BRD"));
                Assert.True(r.Dependencies.ContainsKey("PRD"));
                Assert.True(r.Dependencies.ContainsKey("FRD"));
                return new DocumentGenerationResponse
                {
                    Success = true,
                    DocumentType = r.DocumentType,
                    Content = "TRD content"
                };
            });

        // Act
        var result = await _service.GenerateRequirementsAsync(request);

        // Assert
        Assert.True(result.Success);
        _mockDocumentGenerationService.Verify(x => x.GenerateDocumentAsync(It.IsAny<DocumentGenerationRequest>(), It.IsAny<CancellationToken>()), Times.Exactly(4));
    }

    [Fact]
    public async Task GenerateRequirementsAsync_ShouldTrackProgressWithWorkflowMonitoring()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var request = new GenerateRequirementsRequest
        {
            ProjectId = projectId,
            ProjectName = "Test Project"
        };

        var project = new Project { Id = projectId, Name = request.ProjectName };
        _mockProjectService.Setup(x => x.GetProjectAsync(projectId)).ReturnsAsync(project);

        SetupSuccessfulDocumentGeneration("BRD", "BRD content");
        SetupSuccessfulDocumentGeneration("PRD", "PRD content");
        SetupSuccessfulDocumentGeneration("FRD", "FRD content");
        SetupSuccessfulDocumentGeneration("TRD", "TRD content");

        // Act
        await _service.GenerateRequirementsAsync(request);

        // Assert - Verify workflow monitoring calls
        _mockWorkflowMonitoringService.Verify(x => x.RecordWorkflowStartAsync(
            It.IsAny<int>(), 
            "RequirementsGeneration"), 
            Times.Once);

        _mockWorkflowMonitoringService.Verify(x => x.RecordActivityStartAsync(
            It.IsAny<int>(), 
            It.IsIn("BRD Generation", "PRD Generation", "FRD Generation", "TRD Generation")), 
            Times.Exactly(4));

        _mockWorkflowMonitoringService.Verify(x => x.RecordActivityCompletionAsync(
            It.IsAny<int>(), 
            It.IsIn("BRD Generation", "PRD Generation", "FRD Generation", "TRD Generation"),
            true,
            It.IsAny<TimeSpan>(),
            null), 
            Times.Exactly(4));

        _mockWorkflowMonitoringService.Verify(x => x.RecordWorkflowCompletionAsync(
            It.IsAny<int>(), 
            "RequirementsGeneration",
            true,
            It.IsAny<TimeSpan>()), 
            Times.Once);
    }

    [Fact]
    public async Task GenerateRequirementsAsync_ShouldHandleDocumentGenerationFailure()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var request = new GenerateRequirementsRequest
        {
            ProjectId = projectId,
            ProjectName = "Test Project"
        };

        var project = new Project { Id = projectId, Name = request.ProjectName };
        _mockProjectService.Setup(x => x.GetProjectAsync(projectId)).ReturnsAsync(project);

        // BRD succeeds
        SetupSuccessfulDocumentGeneration("BRD", "BRD content");
        
        // PRD fails
        _mockDocumentGenerationService
            .Setup(x => x.GenerateDocumentAsync(It.Is<DocumentGenerationRequest>(r => r.DocumentType == "PRD"), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DocumentGenerationResponse
            {
                Success = false,
                DocumentType = "PRD",
                Error = "Failed to generate PRD"
            });

        // Act
        var result = await _service.GenerateRequirementsAsync(request);

        // Assert
        Assert.False(result.Success);
        Assert.Contains("Failed to generate PRD", result.Errors);
        Assert.Single(result.GeneratedDocuments); // Only BRD should be generated
        Assert.Contains("BRD", result.GeneratedDocuments.Keys);

        // Verify workflow recorded as failed
        _mockWorkflowMonitoringService.Verify(x => x.RecordWorkflowCompletionAsync(
            It.IsAny<int>(), 
            "RequirementsGeneration",
            false,
            It.IsAny<TimeSpan>()), 
            Times.Once);
    }

    [Fact]
    public async Task GenerateRequirementsAsync_ShouldStoreGeneratedDocumentsInProject()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var request = new GenerateRequirementsRequest
        {
            ProjectId = projectId,
            ProjectName = "Test Project"
        };

        var project = new Project { Id = projectId, Name = request.ProjectName };
        _mockProjectService.Setup(x => x.GetProjectAsync(projectId)).ReturnsAsync(project);

        SetupSuccessfulDocumentGeneration("BRD", "BRD content");
        SetupSuccessfulDocumentGeneration("PRD", "PRD content");
        SetupSuccessfulDocumentGeneration("FRD", "FRD content");
        SetupSuccessfulDocumentGeneration("TRD", "TRD content");

        // Act
        await _service.GenerateRequirementsAsync(request);

        // Assert - Verify documents were added to project
        _mockProjectService.Verify(x => x.AddDocumentToProjectAsync(
            It.Is<AddDocumentRequest>(r => 
                r.ProjectId == projectId && 
                r.DocumentType == "BRD" && 
                r.Content == "BRD content")), 
            Times.Once);

        _mockProjectService.Verify(x => x.AddDocumentToProjectAsync(
            It.Is<AddDocumentRequest>(r => 
                r.ProjectId == projectId && 
                r.DocumentType == "PRD" && 
                r.Content == "PRD content")), 
            Times.Once);

        _mockProjectService.Verify(x => x.AddDocumentToProjectAsync(
            It.Is<AddDocumentRequest>(r => 
                r.ProjectId == projectId && 
                r.DocumentType == "FRD" && 
                r.Content == "FRD content")), 
            Times.Once);

        _mockProjectService.Verify(x => x.AddDocumentToProjectAsync(
            It.Is<AddDocumentRequest>(r => 
                r.ProjectId == projectId && 
                r.DocumentType == "TRD" && 
                r.Content == "TRD content")), 
            Times.Once);
    }

    [Fact]
    public async Task GetGenerationProgressAsync_ShouldReturnCurrentProgress()
    {
        // Arrange
        var projectId = Guid.NewGuid();

        // Act
        var progress = await _service.GetGenerationProgressAsync(projectId);

        // Assert
        Assert.NotNull(progress);
        Assert.Equal(projectId, progress.ProjectId);
        Assert.NotNull(progress.DocumentProgress);
    }

    [Fact]
    public async Task GenerateRequirementsAsync_ShouldUpdateProgressDuringGeneration()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var request = new GenerateRequirementsRequest
        {
            ProjectId = projectId,
            ProjectName = "Test Project"
        };

        var project = new Project { Id = projectId, Name = request.ProjectName };
        _mockProjectService.Setup(x => x.GetProjectAsync(projectId)).ReturnsAsync(project);

        var progressUpdates = new List<RequirementsGenerationProgress>();

        // Capture progress updates during generation
        _mockDocumentGenerationService
            .Setup(x => x.GenerateDocumentAsync(It.IsAny<DocumentGenerationRequest>(), It.IsAny<CancellationToken>()))
            .Returns<DocumentGenerationRequest, CancellationToken>(async (r, ct) =>
            {
                // Get current progress
                var progress = await _service.GetGenerationProgressAsync(projectId);
                progressUpdates.Add(progress);

                return new DocumentGenerationResponse
                {
                    Success = true,
                    DocumentType = r.DocumentType,
                    Content = $"{r.DocumentType} content"
                };
            });

        // Act
        await _service.GenerateRequirementsAsync(request);

        // Assert
        Assert.Equal(4, progressUpdates.Count); // One for each document type
        
        // Verify progress tracking
        var finalProgress = await _service.GetGenerationProgressAsync(projectId);
        Assert.Equal(RequirementsGenerationStatus.Completed, finalProgress.Status);
        Assert.Equal(100, finalProgress.OverallProgress);
    }

    private void SetupSuccessfulDocumentGeneration(string documentType, string content)
    {
        _mockDocumentGenerationService
            .Setup(x => x.GenerateDocumentAsync(
                It.Is<DocumentGenerationRequest>(r => r.DocumentType == documentType), 
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(new DocumentGenerationResponse
            {
                Success = true,
                DocumentType = documentType,
                Content = content,
                GeneratedAt = DateTime.UtcNow
            });
    }
}