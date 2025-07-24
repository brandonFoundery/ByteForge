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

public class PRDGenerator : IDocumentGenerator<PRDGenerationRequest, PRDGenerationResponse>
{
    private readonly ILLMService _llmService;
    private readonly IDocumentTemplateService _templateService;
    private readonly IDocumentValidationService _validationService;
    private readonly ILogger<PRDGenerator> _logger;

    private static readonly string[] RequiredSections = 
    {
        "Product Overview",
        "Target Audience",
        "Product Features",
        "User Stories",
        "Success Metrics"
    };

    public string DocumentType => "PRD";

    public PRDGenerator(
        ILLMService llmService,
        IDocumentTemplateService templateService,
        IDocumentValidationService validationService,
        ILogger<PRDGenerator> logger)
    {
        _llmService = llmService;
        _templateService = templateService;
        _validationService = validationService;
        _logger = logger;
    }

    public async Task<PRDGenerationResponse> GenerateAsync(PRDGenerationRequest request, CancellationToken cancellationToken = default)
    {
        var response = new PRDGenerationResponse
        {
            GeneratedAt = DateTime.UtcNow
        };

        try
        {
            // Build the prompt including BRD dependency if available
            var prompt = BuildPrompt(request);

            // Generate content using LLM
            var llmRequest = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a product manager expert creating comprehensive Product Requirements Documents. " +
                              "Generate detailed product features, user stories, and success metrics. " +
                              "Ensure alignment with business requirements and use proper requirement IDs (PR###).",
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
            
            // Extract structured data
            response.RequirementIds = ExtractRequirementIds(processedContent);
            response.ProductFeatures = ExtractProductFeatures(processedContent);
            response.UserStories = ExtractUserStories(processedContent);

            // Apply template
            var template = await _templateService.LoadTemplateAsync(DocumentType);
            var finalContent = await _templateService.ProcessTemplateAsync(template, new Dictionary<string, object>
            {
                ["content"] = processedContent,
                ["projectName"] = request.ProjectName,
                ["generatedDate"] = DateTime.UtcNow.ToString("yyyy-MM-dd"),
                ["documentType"] = "Product Requirements Document"
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
            response.Metadata["featureCount"] = response.ProductFeatures.Count;
            response.Metadata["userStoryCount"] = response.UserStories.Count;
            response.Metadata["requirementCount"] = response.RequirementIds.Count;
            response.Metadata["llmProvider"] = llmResponse.Provider;

            _logger.LogInformation("Successfully generated PRD for project {ProjectName} with {FeatureCount} features and {StoryCount} user stories",
                request.ProjectName, response.ProductFeatures.Count, response.UserStories.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating PRD for project {ProjectName}", request.ProjectName);
            response.Success = false;
            response.Error = $"Unexpected error: {ex.Message}";
            return response;
        }
    }

    private string BuildPrompt(PRDGenerationRequest request)
    {
        var promptBuilder = new StringBuilder();
        
        promptBuilder.AppendLine($"Create a comprehensive Product Requirements Document (PRD) for: {request.ProjectName}");
        promptBuilder.AppendLine();
        
        if (!string.IsNullOrWhiteSpace(request.ProjectDescription))
        {
            promptBuilder.AppendLine($"Project Description: {request.ProjectDescription}");
            promptBuilder.AppendLine();
        }

        // Include BRD content if available
        if (request.Dependencies.TryGetValue("BRD", out var brdContentObj) && !string.IsNullOrWhiteSpace(brdContentObj?.ToString()))
        {
            promptBuilder.AppendLine("Business Requirements from BRD:");
            promptBuilder.AppendLine(brdContentObj.ToString());
            promptBuilder.AppendLine();
            promptBuilder.AppendLine("Ensure the product requirements align with and fulfill these business requirements.");
            promptBuilder.AppendLine();
        }

        if (!string.IsNullOrWhiteSpace(request.ProductVision))
        {
            promptBuilder.AppendLine($"Product Vision: {request.ProductVision}");
            promptBuilder.AppendLine();
        }

        if (request.TargetUsers.Any())
        {
            promptBuilder.AppendLine("Target Users:");
            foreach (var user in request.TargetUsers)
            {
                promptBuilder.AppendLine($"- {user}");
            }
            promptBuilder.AppendLine();
        }

        if (!string.IsNullOrWhiteSpace(request.MarketAnalysis))
        {
            promptBuilder.AppendLine("Market Analysis:");
            promptBuilder.AppendLine(request.MarketAnalysis);
            promptBuilder.AppendLine();
        }

        if (request.CompetitorProducts.Any())
        {
            promptBuilder.AppendLine("Competitor Products:");
            foreach (var competitor in request.CompetitorProducts)
            {
                promptBuilder.AppendLine($"- {competitor}");
            }
            promptBuilder.AppendLine();
        }

        promptBuilder.AppendLine("Please include the following sections:");
        promptBuilder.AppendLine("1. Product Overview (vision and goals)");
        promptBuilder.AppendLine("2. Target Audience (user personas and demographics)");
        promptBuilder.AppendLine("3. Product Features (grouped by category, with unique IDs starting with PR-)");
        promptBuilder.AppendLine("4. User Stories (in 'As a... I want... So that...' format)");
        promptBuilder.AppendLine("5. Success Metrics (KPIs and measurable outcomes)");
        promptBuilder.AppendLine("6. Market Positioning (if market analysis provided)");
        promptBuilder.AppendLine("7. Technical Considerations");
        promptBuilder.AppendLine("8. Release Planning");
        promptBuilder.AppendLine();
        promptBuilder.AppendLine("Format requirements with IDs like: PR001, PR002, etc.");
        promptBuilder.AppendLine("Ensure features are detailed, user-centric, and measurable.");

        return promptBuilder.ToString();
    }

    private string ProcessContent(string content, PRDGenerationRequest request)
    {
        // Add requirement IDs if missing
        content = AddRequirementIds(content);

        // Ensure proper formatting
        content = EnsureProperFormatting(content);

        // Cross-reference with BRD if available
        if (request.Dependencies.TryGetValue("BRD", out var brdContentObj) && brdContentObj != null)
        {
            content = AddBRDReferences(content, brdContentObj.ToString());
        }

        // Add any missing required sections
        foreach (var section in RequiredSections)
        {
            if (!content.Contains(section, StringComparison.OrdinalIgnoreCase))
            {
                _logger.LogWarning("Missing section {Section} in generated PRD, adding placeholder", section);
                content += $"\n\n## {section}\n[To be determined]\n";
            }
        }

        return content;
    }

    private string AddRequirementIds(string content)
    {
        var requirementCounter = 1;
        var requirementPattern = @"(?:^|\n)\s*[-•]\s*(?!PR\d{3}:)([A-Z][^.!?\n]+(?:[.!?]|$))";
        
        content = Regex.Replace(content, requirementPattern, match =>
        {
            var requirementText = match.Groups[1].Value.Trim();
            // Only add IDs to lines that look like product requirements
            if (IsLikelyProductRequirement(requirementText))
            {
                var id = $"PR{requirementCounter:D3}";
                requirementCounter++;
                return $"\n- {id}: {requirementText}";
            }
            return match.Value;
        }, RegexOptions.Multiline);

        return content;
    }

    private bool IsLikelyProductRequirement(string text)
    {
        var requirementKeywords = new[] { "feature", "functionality", "capability", "support", "allow", "enable", "provide" };
        return requirementKeywords.Any(keyword => text.Contains(keyword, StringComparison.OrdinalIgnoreCase)) &&
               text.Length > 20;
    }

    private string AddBRDReferences(string content, string brdContent)
    {
        // Extract BR IDs from BRD content
        var brIdPattern = @"BR\d{3}";
        var brIds = Regex.Matches(brdContent, brIdPattern).Cast<Match>().Select(m => m.Value).Distinct().ToList();

        // Add references section if BR IDs found
        if (brIds.Any())
        {
            var referencesSection = "\n\n## Business Requirements Traceability\n";
            referencesSection += "This PRD addresses the following business requirements:\n";
            foreach (var brId in brIds)
            {
                referencesSection += $"- {brId}\n";
            }
            
            content += referencesSection;
        }

        return content;
    }

    private string EnsureProperFormatting(string content)
    {
        // Ensure headers use ## format
        content = Regex.Replace(content, @"^([A-Z][^:\n]+):?\s*$", "## $1", RegexOptions.Multiline);
        
        // Ensure consistent bullet points
        content = Regex.Replace(content, @"^\s*[•·*]\s*", "- ", RegexOptions.Multiline);
        
        // Format user stories consistently
        content = Regex.Replace(content, @"As an?\s+", "As a ", RegexOptions.IgnoreCase);
        
        return content;
    }

    private List<string> ExtractRequirementIds(string content)
    {
        var ids = new List<string>();
        var pattern = @"PR\d{3}";
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

    private List<string> ExtractProductFeatures(string content)
    {
        var features = new List<string>();
        var featuresSection = ExtractSection(content, "Product Features");
        
        if (!string.IsNullOrEmpty(featuresSection))
        {
            // Look for feature categories (numbered items followed by feature details)
            var categoryPattern = @"^\d+\.\s*(.+?)(?=\n\s*(?:[-•]|PR\d{3}|\d+\.|\z))";
            var matches = Regex.Matches(featuresSection, categoryPattern, RegexOptions.Multiline | RegexOptions.Singleline);
            
            foreach (Match match in matches)
            {
                var featureName = match.Groups[1].Value.Trim();
                if (!string.IsNullOrWhiteSpace(featureName) && featureName.Length > 5)
                {
                    features.Add(featureName);
                }
            }
        }
        
        return features;
    }

    private List<string> ExtractUserStories(string content)
    {
        var stories = new List<string>();
        var storiesSection = ExtractSection(content, "User Stories");
        
        if (!string.IsNullOrEmpty(storiesSection))
        {
            // Match user story pattern
            var storyPattern = @"[-•]\s*(As a[^,\n]+,\s*I want[^,\n]+(?:,\s*so that[^.\n]+)?\.?)";
            var matches = Regex.Matches(storiesSection, storyPattern, RegexOptions.IgnoreCase);
            
            foreach (Match match in matches)
            {
                stories.Add(match.Groups[1].Value.Trim());
            }
        }
        
        return stories;
    }

    private string ExtractSection(string content, string sectionName)
    {
        var pattern = $@"##\s*{Regex.Escape(sectionName)}.*?\n(.*?)(?=\n##|\z)";
        var match = Regex.Match(content, pattern, RegexOptions.Singleline | RegexOptions.IgnoreCase);
        
        return match.Success ? match.Groups[1].Value.Trim() : string.Empty;
    }
}