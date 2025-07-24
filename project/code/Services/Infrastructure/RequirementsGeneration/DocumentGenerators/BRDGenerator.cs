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

public class BRDGenerator : IDocumentGenerator<BRDGenerationRequest, BRDGenerationResponse>
{
    private readonly ILLMService _llmService;
    private readonly IDocumentTemplateService _templateService;
    private readonly IDocumentValidationService _validationService;
    private readonly ILogger<BRDGenerator> _logger;

    private static readonly string[] RequiredSections = 
    {
        "Executive Summary",
        "Business Objectives",
        "Stakeholder Analysis",
        "Business Requirements",
        "Success Criteria"
    };

    public string DocumentType => "BRD";

    public BRDGenerator(
        ILLMService llmService,
        IDocumentTemplateService templateService,
        IDocumentValidationService validationService,
        ILogger<BRDGenerator> logger)
    {
        _llmService = llmService;
        _templateService = templateService;
        _validationService = validationService;
        _logger = logger;
    }

    public async Task<BRDGenerationResponse> GenerateAsync(BRDGenerationRequest request, CancellationToken cancellationToken = default)
    {
        var response = new BRDGenerationResponse
        {
            GeneratedAt = DateTime.UtcNow
        };

        try
        {
            // Build the prompt
            var prompt = BuildPrompt(request);

            // Generate content using LLM
            var llmRequest = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a business analyst expert creating comprehensive Business Requirements Documents. " +
                              "Generate well-structured, clear, and actionable business requirements with proper requirement IDs.",
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

            // Process and enhance content
            var processedContent = ProcessContent(llmResponse.Content, request);
            
            // Extract requirement IDs
            response.RequirementIds = ExtractRequirementIds(processedContent);

            // Extract business objectives
            response.BusinessObjectives = ExtractBusinessObjectives(processedContent);

            // Extract stakeholder roles
            response.StakeholderRoles = ExtractStakeholderRoles(processedContent);

            // Apply template
            var template = await _templateService.LoadTemplateAsync(DocumentType);
            var finalContent = await _templateService.ProcessTemplateAsync(template, new Dictionary<string, object>
            {
                ["content"] = processedContent,
                ["projectName"] = request.ProjectName,
                ["generatedDate"] = DateTime.UtcNow.ToString("yyyy-MM-dd"),
                ["documentType"] = "Business Requirements Document"
            });

            // Validate document
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
            
            // Add metadata
            response.Metadata["stakeholderCount"] = request.Stakeholders.Count;
            response.Metadata["requirementCount"] = response.RequirementIds.Count;
            response.Metadata["llmProvider"] = llmResponse.Provider;

            _logger.LogInformation("Successfully generated BRD for project {ProjectName} with {RequirementCount} requirements",
                request.ProjectName, response.RequirementIds.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating BRD for project {ProjectName}", request.ProjectName);
            response.Success = false;
            response.Error = $"Unexpected error: {ex.Message}";
            return response;
        }
    }

    private string BuildPrompt(BRDGenerationRequest request)
    {
        var promptBuilder = new StringBuilder();
        
        promptBuilder.AppendLine($"Create a comprehensive Business Requirements Document (BRD) for: {request.ProjectName}");
        promptBuilder.AppendLine();
        
        if (!string.IsNullOrWhiteSpace(request.ProjectDescription))
        {
            promptBuilder.AppendLine($"Project Description: {request.ProjectDescription}");
            promptBuilder.AppendLine();
        }

        if (!string.IsNullOrWhiteSpace(request.ClientRequirements))
        {
            promptBuilder.AppendLine("Client Requirements:");
            promptBuilder.AppendLine(request.ClientRequirements);
            promptBuilder.AppendLine();
        }

        if (request.Stakeholders.Any())
        {
            promptBuilder.AppendLine("Key Stakeholders:");
            foreach (var stakeholder in request.Stakeholders)
            {
                promptBuilder.AppendLine($"- {stakeholder}");
            }
            promptBuilder.AppendLine();
        }

        if (request.BusinessConstraints.Any())
        {
            promptBuilder.AppendLine("Business Constraints:");
            foreach (var constraint in request.BusinessConstraints)
            {
                promptBuilder.AppendLine($"- {constraint}");
            }
            promptBuilder.AppendLine();
        }

        if (!string.IsNullOrWhiteSpace(request.BusinessContext))
        {
            promptBuilder.AppendLine($"Business Context: {request.BusinessContext}");
            promptBuilder.AppendLine();
        }

        promptBuilder.AppendLine("Please include the following sections:");
        promptBuilder.AppendLine("1. Executive Summary");
        promptBuilder.AppendLine("2. Business Objectives (numbered list)");
        promptBuilder.AppendLine("3. Stakeholder Analysis (with roles and needs)");
        promptBuilder.AppendLine("4. Business Requirements (grouped by category, with unique IDs starting with BR-)");
        promptBuilder.AppendLine("5. Success Criteria (measurable outcomes)");
        promptBuilder.AppendLine("6. Business Constraints (if applicable)");
        promptBuilder.AppendLine("7. Assumptions and Dependencies");
        promptBuilder.AppendLine();
        promptBuilder.AppendLine("Format requirements with IDs like: BR001, BR002, etc.");
        promptBuilder.AppendLine("Make the document professional, comprehensive, and actionable.");

        return promptBuilder.ToString();
    }

    private string ProcessContent(string content, BRDGenerationRequest request)
    {
        // Add requirement IDs if missing
        content = AddRequirementIds(content);

        // Ensure proper formatting
        content = EnsureProperFormatting(content);

        // Add any missing required sections
        foreach (var section in RequiredSections)
        {
            if (!content.Contains(section, StringComparison.OrdinalIgnoreCase))
            {
                _logger.LogWarning("Missing section {Section} in generated BRD, adding placeholder", section);
                content += $"\n\n## {section}\n[To be determined]\n";
            }
        }

        return content;
    }

    private string AddRequirementIds(string content)
    {
        var requirementCounter = 1;
        var requirementPattern = @"(?:^|\n)\s*[-•]\s*(?!BR\d{3}:)([A-Z][^.!?\n]+(?:[.!?]|$))";
        
        content = Regex.Replace(content, requirementPattern, match =>
        {
            var requirementText = match.Groups[1].Value.Trim();
            // Only add IDs to lines that look like requirements
            if (IsLikelyRequirement(requirementText))
            {
                var id = $"BR{requirementCounter:D3}";
                requirementCounter++;
                return $"\n- {id}: {requirementText}";
            }
            return match.Value;
        }, RegexOptions.Multiline);

        return content;
    }

    private bool IsLikelyRequirement(string text)
    {
        var requirementKeywords = new[] { "shall", "must", "will", "should", "system", "user", "ability" };
        return requirementKeywords.Any(keyword => text.Contains(keyword, StringComparison.OrdinalIgnoreCase)) &&
               text.Length > 20;
    }

    private string EnsureProperFormatting(string content)
    {
        // Ensure headers use ## format
        content = Regex.Replace(content, @"^([A-Z][^:\n]+):?\s*$", "## $1", RegexOptions.Multiline);
        
        // Ensure consistent bullet points
        content = Regex.Replace(content, @"^\s*[•·*]\s*", "- ", RegexOptions.Multiline);
        
        return content;
    }

    private List<string> ExtractRequirementIds(string content)
    {
        var ids = new List<string>();
        var pattern = @"BR\d{3}";
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

    private List<string> ExtractBusinessObjectives(string content)
    {
        var objectives = new List<string>();
        var objectivesSection = ExtractSection(content, "Business Objectives");
        
        if (!string.IsNullOrEmpty(objectivesSection))
        {
            var lines = objectivesSection.Split('\n', StringSplitOptions.RemoveEmptyEntries);
            foreach (var line in lines)
            {
                var cleaned = Regex.Replace(line, @"^\s*\d+\.\s*|-\s*", "").Trim();
                if (!string.IsNullOrWhiteSpace(cleaned) && cleaned.Length > 10)
                {
                    objectives.Add(cleaned);
                }
            }
        }
        
        return objectives;
    }

    private Dictionary<string, object> ExtractStakeholderRoles(string content)
    {
        var roles = new Dictionary<string, object>();
        var stakeholderSection = ExtractSection(content, "Stakeholder Analysis");
        
        if (!string.IsNullOrEmpty(stakeholderSection))
        {
            var pattern = @"[-•]\s*([^:]+):\s*(.+)";
            var matches = Regex.Matches(stakeholderSection, pattern);
            
            foreach (Match match in matches)
            {
                if (match.Groups.Count >= 3)
                {
                    var stakeholder = match.Groups[1].Value.Trim();
                    var role = match.Groups[2].Value.Trim();
                    roles[stakeholder] = role;
                }
            }
        }
        
        return roles;
    }

    private string ExtractSection(string content, string sectionName)
    {
        var pattern = $@"##\s*{Regex.Escape(sectionName)}.*?\n(.*?)(?=\n##|\z)";
        var match = Regex.Match(content, pattern, RegexOptions.Singleline | RegexOptions.IgnoreCase);
        
        return match.Success ? match.Groups[1].Value.Trim() : string.Empty;
    }
}