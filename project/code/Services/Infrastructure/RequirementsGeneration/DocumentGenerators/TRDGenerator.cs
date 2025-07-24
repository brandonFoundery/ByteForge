using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.RegularExpressions;

using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.DocumentGenerators;

public class TRDGenerator : IDocumentGenerator<TRDGenerationRequest, TRDGenerationResponse>
{
    private readonly ILLMService _llmService;
    private readonly IDocumentTemplateService _templateService;
    private readonly IDocumentValidationService _validationService;
    private readonly ILogger<TRDGenerator> _logger;

    private static readonly string[] RequiredSections = 
    {
        "Technical Architecture",
        "Technical Requirements",
        "Technology Stack",
        "Integration Points",
        "Non-Functional Requirements"
    };

    public string DocumentType => "TRD";

    public TRDGenerator(
        ILLMService llmService,
        IDocumentTemplateService templateService,
        IDocumentValidationService validationService,
        ILogger<TRDGenerator> logger)
    {
        _llmService = llmService;
        _templateService = templateService;
        _validationService = validationService;
        _logger = logger;
    }

    public async Task<TRDGenerationResponse> GenerateAsync(TRDGenerationRequest request, CancellationToken cancellationToken = default)
    {
        var response = new TRDGenerationResponse
        {
            GeneratedAt = DateTime.UtcNow
        };

        try
        {
            var prompt = BuildPrompt(request);

            var llmRequest = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a technical architect expert creating comprehensive Technical Requirements Documents. " +
                              "Generate well-structured, clear, and implementable technical requirements with proper requirement IDs.",
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
            response.TechnicalRequirements = ExtractTechnicalRequirements(processedContent);
            response.ArchitectureComponents = ExtractArchitectureComponents(processedContent);
            response.TechnologyChoices = ExtractTechnologyChoices(processedContent);

            var template = await _templateService.LoadTemplateAsync(DocumentType);
            var finalContent = await _templateService.ProcessTemplateAsync(template, new Dictionary<string, object>
            {
                ["content"] = processedContent,
                ["projectName"] = request.ProjectName,
                ["generatedDate"] = DateTime.UtcNow.ToString("yyyy-MM-dd"),
                ["documentType"] = "Technical Requirements Document"
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
            
            response.Metadata["technologyCount"] = request.TechnologyStack.Count;
            response.Metadata["integrationPointCount"] = request.IntegrationPoints.Count;
            response.Metadata["requirementCount"] = response.RequirementIds.Count;
            response.Metadata["llmProvider"] = llmResponse.Provider;

            _logger.LogInformation("Successfully generated TRD for project {ProjectName} with {RequirementCount} requirements",
                request.ProjectName, response.RequirementIds.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating TRD for project {ProjectName}", request.ProjectName);
            response.Success = false;
            response.Error = $"Unexpected error: {ex.Message}";
            return response;
        }
    }

    private string BuildPrompt(TRDGenerationRequest request)
    {
        var promptBuilder = new StringBuilder();
        
        promptBuilder.AppendLine($"Create a comprehensive Technical Requirements Document (TRD) for: {request.ProjectName}");
        promptBuilder.AppendLine();
        
        if (!string.IsNullOrWhiteSpace(request.ProjectDescription))
        {
            promptBuilder.AppendLine($"Project Description: {request.ProjectDescription}");
            promptBuilder.AppendLine();
        }

        if (request.TechnologyStack.Any())
        {
            promptBuilder.AppendLine("Required Technology Stack:");
            foreach (var tech in request.TechnologyStack)
            {
                promptBuilder.AppendLine($"- {tech}");
            }
            promptBuilder.AppendLine();
        }

        if (request.IntegrationPoints.Any())
        {
            promptBuilder.AppendLine("Integration Points:");
            foreach (var integration in request.IntegrationPoints)
            {
                promptBuilder.AppendLine($"- {integration}");
            }
            promptBuilder.AppendLine();
        }

        if (!string.IsNullOrWhiteSpace(request.DeploymentEnvironment))
        {
            promptBuilder.AppendLine($"Deployment Environment: {request.DeploymentEnvironment}");
            promptBuilder.AppendLine();
        }

        promptBuilder.AppendLine("Please include the following sections:");
        promptBuilder.AppendLine("1. Technical Architecture Overview");
        promptBuilder.AppendLine("2. Technical Requirements (with unique IDs starting with TR-)");
        promptBuilder.AppendLine("3. Technology Stack and Choices");
        promptBuilder.AppendLine("4. Integration Points and APIs");
        promptBuilder.AppendLine("5. Non-Functional Requirements (performance, security, scalability)");
        
        if (request.IncludeArchitectureDiagram)
        {
            promptBuilder.AppendLine("6. Architecture Diagram (textual description)");
        }
        
        promptBuilder.AppendLine("7. Security Requirements");
        promptBuilder.AppendLine("8. Deployment and Infrastructure Requirements");
        promptBuilder.AppendLine();
        promptBuilder.AppendLine("Format requirements with IDs like: TR001, TR002, etc.");
        promptBuilder.AppendLine("Make requirements specific, measurable, and implementable.");

        return promptBuilder.ToString();
    }

    private string ProcessContent(string content, TRDGenerationRequest request)
    {
        content = AddRequirementIds(content);
        content = EnsureProperFormatting(content);

        foreach (var section in RequiredSections)
        {
            if (!content.Contains(section, StringComparison.OrdinalIgnoreCase))
            {
                _logger.LogWarning("Missing section {Section} in generated TRD, adding placeholder", section);
                content += $"\n\n## {section}\n[To be determined]\n";
            }
        }

        return content;
    }

    private string AddRequirementIds(string content)
    {
        var requirementCounter = 1;
        var requirementPattern = @"(?:^|\n)\s*[-•]\s*(?!TR\d{3}:)([A-Z][^.!?\n]+(?:[.!?]|$))";
        
        content = Regex.Replace(content, requirementPattern, match =>
        {
            var requirementText = match.Groups[1].Value.Trim();
            if (IsLikelyRequirement(requirementText))
            {
                var id = $"TR{requirementCounter:D3}";
                requirementCounter++;
                return $"\n- {id}: {requirementText}";
            }
            return match.Value;
        }, RegexOptions.Multiline);

        return content;
    }

    private bool IsLikelyRequirement(string text)
    {
        var requirementKeywords = new[] { "shall", "must", "will", "should", "system", "application", "service", "database", "api" };
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
        var pattern = @"TR\d{3}";
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

    private List<string> ExtractTechnicalRequirements(string content)
    {
        var requirements = new List<string>();
        var pattern = @"TR\d{3}:\s*(.+?)(?=\n|$)";
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

    private List<string> ExtractArchitectureComponents(string content)
    {
        var components = new List<string>();
        var architectureSection = ExtractSection(content, "Technical Architecture");
        
        if (!string.IsNullOrEmpty(architectureSection))
        {
            var pattern = @"[-•]\s*([A-Z][^:\n]+)(?::|$)";
            var matches = Regex.Matches(architectureSection, pattern);
            
            foreach (Match match in matches)
            {
                if (match.Groups.Count >= 2)
                {
                    var component = match.Groups[1].Value.Trim();
                    if (!string.IsNullOrWhiteSpace(component) && component.Length > 5)
                    {
                        components.Add(component);
                    }
                }
            }
        }
        
        return components;
    }

    private Dictionary<string, object> ExtractTechnologyChoices(string content)
    {
        var choices = new Dictionary<string, object>();
        var techSection = ExtractSection(content, "Technology Stack");
        
        if (!string.IsNullOrEmpty(techSection))
        {
            var pattern = @"[-•]\s*([^:]+):\s*(.+)";
            var matches = Regex.Matches(techSection, pattern);
            
            foreach (Match match in matches)
            {
                if (match.Groups.Count >= 3)
                {
                    var category = match.Groups[1].Value.Trim();
                    var technology = match.Groups[2].Value.Trim();
                    choices[category] = technology;
                }
            }
        }
        
        return choices;
    }

    private string ExtractSection(string content, string sectionName)
    {
        var pattern = $@"##\s*{Regex.Escape(sectionName)}.*?\n(.*?)(?=\n##|\z)";
        var match = Regex.Match(content, pattern, RegexOptions.Singleline | RegexOptions.IgnoreCase);
        
        return match.Success ? match.Groups[1].Value.Trim() : string.Empty;
    }
}