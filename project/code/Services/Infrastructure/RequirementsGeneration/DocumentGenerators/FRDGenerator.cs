using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.RegularExpressions;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.DocumentGenerators;

public class FRDGenerator : IDocumentGenerator<FRDGenerationRequest, FRDGenerationResponse>
{
    private readonly ILLMService _llmService;
    private readonly IDocumentTemplateService _templateService;
    private readonly IDocumentValidationService _validationService;
    private readonly ILogger<FRDGenerator> _logger;

    private static readonly string[] RequiredSections = 
    {
        "Introduction",
        "Functional Requirements",
        "Use Cases",
        "Data Flow",
        "Acceptance Criteria"
    };

    public string DocumentType => "FRD";

    public FRDGenerator(
        ILLMService llmService,
        IDocumentTemplateService templateService,
        IDocumentValidationService validationService,
        ILogger<FRDGenerator> logger)
    {
        _llmService = llmService;
        _templateService = templateService;
        _validationService = validationService;
        _logger = logger;
    }

    public async Task<FRDGenerationResponse> GenerateAsync(FRDGenerationRequest request, CancellationToken cancellationToken = default)
    {
        var response = new FRDGenerationResponse
        {
            GeneratedAt = DateTime.UtcNow
        };

        try
        {
            var prompt = BuildPrompt(request);

            var llmRequest = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a systems analyst expert creating comprehensive Functional Requirements Documents. " +
                              "Generate well-structured, clear, and testable functional requirements with proper requirement IDs.",
                Temperature = 0.7,
                MaxTokens = 4000
            };

            var llmResponse = await _llmService.GenerateAsync(llmRequest, cancellationToken);

            if (!llmResponse.Success)
            {
                response.Success = false;
                response.Error = $"LLM generation failed: {llmResponse.Error}";
                return response;
            }

            var processedContent = ProcessContent(llmResponse.Content, request);
            
            response.RequirementIds = ExtractRequirementIds(processedContent);
            response.FunctionalRequirements = ExtractFunctionalRequirements(processedContent);
            response.UseCases = ExtractUseCases(processedContent);

            var template = await _templateService.LoadTemplateAsync(DocumentType);
            var finalContent = await _templateService.ProcessTemplateAsync(template, new Dictionary<string, object>
            {
                ["content"] = processedContent,
                ["projectName"] = request.ProjectName,
                ["generatedDate"] = DateTime.UtcNow.ToString("yyyy-MM-dd"),
                ["documentType"] = "Functional Requirements Document"
            });

            var validationResponse = await _validationService.ValidateDocumentAsync(DocumentType, finalContent);

            if (!validationResponse.IsValid)
            {
                response.Success = false;
                response.Error = "Document validation failed";
                response.ValidationErrors = validationResponse.Errors;
                response.ValidationWarnings = validationResponse.Warnings;
                return response;
            }

            response.Success = true;
            response.Content = finalContent;
            response.ValidationWarnings = validationResponse.Warnings;
            
            response.Metadata["functionalAreaCount"] = request.FunctionalAreas.Count;
            response.Metadata["requirementCount"] = response.RequirementIds.Count;
            response.Metadata["llmProvider"] = llmResponse.Provider;

            _logger.LogInformation("Successfully generated FRD for project {ProjectName} with {RequirementCount} requirements",
                request.ProjectName, response.RequirementIds.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating FRD for project {ProjectName}", request.ProjectName);
            response.Success = false;
            response.Error = $"Unexpected error: {ex.Message}";
            return response;
        }
    }

    private string BuildPrompt(FRDGenerationRequest request)
    {
        var promptBuilder = new StringBuilder();
        
        promptBuilder.AppendLine($"Create a comprehensive Functional Requirements Document (FRD) for: {request.ProjectName}");
        promptBuilder.AppendLine();
        
        if (!string.IsNullOrWhiteSpace(request.ProjectDescription))
        {
            promptBuilder.AppendLine($"Project Description: {request.ProjectDescription}");
            promptBuilder.AppendLine();
        }

        if (request.FunctionalAreas.Any())
        {
            promptBuilder.AppendLine("Functional Areas to Cover:");
            foreach (var area in request.FunctionalAreas)
            {
                promptBuilder.AppendLine($"- {area}");
            }
            promptBuilder.AppendLine();
        }

        promptBuilder.AppendLine("Please include the following sections:");
        promptBuilder.AppendLine("1. Introduction and Overview");
        promptBuilder.AppendLine("2. Functional Requirements (grouped by functional area, with unique IDs starting with FR-)");
        
        if (request.IncludeUseCases)
        {
            promptBuilder.AppendLine("3. Use Cases (detailed scenarios with actors and flows)");
        }
        
        if (request.IncludeDataFlow)
        {
            promptBuilder.AppendLine("4. Data Flow Diagrams (textual descriptions)");
        }
        
        promptBuilder.AppendLine("5. Acceptance Criteria (testable conditions)");
        promptBuilder.AppendLine("6. Dependencies and Assumptions");
        promptBuilder.AppendLine();
        promptBuilder.AppendLine("Format requirements with IDs like: FR001, FR002, etc.");
        promptBuilder.AppendLine("Make requirements specific, measurable, and testable.");

        return promptBuilder.ToString();
    }

    private string ProcessContent(string content, FRDGenerationRequest request)
    {
        content = AddRequirementIds(content);
        content = EnsureProperFormatting(content);

        foreach (var section in RequiredSections)
        {
            if (!content.Contains(section, StringComparison.OrdinalIgnoreCase))
            {
                _logger.LogWarning("Missing section {Section} in generated FRD, adding placeholder", section);
                content += $"\n\n## {section}\n[To be determined]\n";
            }
        }

        return content;
    }

    private string AddRequirementIds(string content)
    {
        var requirementCounter = 1;
        var requirementPattern = @"(?:^|\n)\s*[-•]\s*(?!FR\d{3}:)([A-Z][^.!?\n]+(?:[.!?]|$))";
        
        content = Regex.Replace(content, requirementPattern, match =>
        {
            var requirementText = match.Groups[1].Value.Trim();
            if (IsLikelyRequirement(requirementText))
            {
                var id = $"FR{requirementCounter:D3}";
                requirementCounter++;
                return $"\n- {id}: {requirementText}";
            }
            return match.Value;
        }, RegexOptions.Multiline);

        return content;
    }

    private bool IsLikelyRequirement(string text)
    {
        var requirementKeywords = new[] { "shall", "must", "will", "should", "system", "user", "function", "feature" };
        return requirementKeywords.Any(keyword => text.Contains(keyword, StringComparison.OrdinalIgnoreCase)) &&
               text.Length > 20;
    }

    private string EnsureProperFormatting(string content)
    {
        content = Regex.Replace(content, @"^([A-Z][^:\n]+):?\s*$", "## $1", RegexOptions.Multiline);
        content = Regex.Replace(content, @"^\s*[•·*]\s*", "- ", RegexOptions.Multiline);
        return content;
    }

    private List<string> ExtractRequirementIds(string content)
    {
        var ids = new List<string>();
        var pattern = @"FR\d{3}";
        var matches = Regex.Matches(content, pattern);
        
        foreach (Match match in matches)
        {
            if (!ids.Contains(match.Value))
            {
                ids.Add(match.Value);
            }
        }
        
        return ids.OrderBy(id => id).ToList();
    }

    private List<string> ExtractFunctionalRequirements(string content)
    {
        var requirements = new List<string>();
        var pattern = @"FR\d{3}:\s*(.+?)(?=\n|$)";
        var matches = Regex.Matches(content, pattern);
        
        foreach (Match match in matches)
        {
            if (match.Groups.Count >= 2)
            {
                var requirement = match.Groups[1].Value.Trim();
                if (!string.IsNullOrWhiteSpace(requirement))
                {
                    requirements.Add(requirement);
                }
            }
        }
        
        return requirements;
    }

    private List<string> ExtractUseCases(string content)
    {
        var useCases = new List<string>();
        var useCaseSection = ExtractSection(content, "Use Cases");
        
        if (!string.IsNullOrEmpty(useCaseSection))
        {
            var pattern = @"(?:Use Case|UC)\s*\d*:\s*([^\n]+)";
            var matches = Regex.Matches(useCaseSection, pattern, RegexOptions.IgnoreCase);
            
            foreach (Match match in matches)
            {
                if (match.Groups.Count >= 2)
                {
                    var useCase = match.Groups[1].Value.Trim();
                    if (!string.IsNullOrWhiteSpace(useCase))
                    {
                        useCases.Add(useCase);
                    }
                }
            }
        }
        
        return useCases;
    }

    private string ExtractSection(string content, string sectionName)
    {
        var pattern = $@"##\s*{Regex.Escape(sectionName)}.*?\n(.*?)(?=\n##|\z)";
        var match = Regex.Match(content, pattern, RegexOptions.Singleline | RegexOptions.IgnoreCase);
        
        return match.Success ? match.Groups[1].Value.Trim() : string.Empty;
    }
}