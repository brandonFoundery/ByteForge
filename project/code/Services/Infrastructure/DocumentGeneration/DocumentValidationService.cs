using System.Text.RegularExpressions;
using Microsoft.Extensions.Logging;
using YamlDotNet.Core;
using YamlDotNet.RepresentationModel;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

public class DocumentValidationService : IDocumentValidationService
{
    private readonly ILogger<DocumentValidationService> _logger;
    
    // Define required sections for each document type
    private readonly Dictionary<string, string[]> _requiredSections = new()
    {
        ["BRD"] = new[] { "Executive Summary", "Business Objectives", "Stakeholders", "Business Requirements", "Success Criteria" },
        ["PRD"] = new[] { "Product Overview", "Features", "User Stories", "Technical Requirements", "Acceptance Criteria" },
        ["FRD"] = new[] { "System Overview", "Functional Requirements", "Use Cases", "Data Requirements", "Interface Requirements" },
        ["TRD"] = new[] { "Architecture Overview", "Technology Stack", "Database Design", "API Design", "Security Requirements", "Performance Requirements" }
    };

    public DocumentValidationService(ILogger<DocumentValidationService> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<DocumentValidationResult> ValidateMarkdownStructureAsync(string markdown)
    {
        var result = new DocumentValidationResult { IsValid = true };

        try
        {
            if (string.IsNullOrWhiteSpace(markdown))
            {
                result.IsValid = false;
                result.Errors.Add("Document is empty");
                return result;
            }

            // Check for main title (# Title)
            var titlePattern = @"^#\s+.+";
            if (!Regex.IsMatch(markdown, titlePattern, RegexOptions.Multiline))
            {
                result.IsValid = false;
                result.Errors.Add("Document must have a main title (# Title)");
            }

            // Check for proper heading hierarchy
            var lines = markdown.Split('\n');
            var headingLevels = new List<int>();
            
            foreach (var line in lines)
            {
                var headingMatch = Regex.Match(line, @"^(#+)\s+.+");
                if (headingMatch.Success)
                {
                    headingLevels.Add(headingMatch.Groups[1].Value.Length);
                }
            }

            // Validate heading hierarchy
            for (int i = 1; i < headingLevels.Count; i++)
            {
                if (headingLevels[i] - headingLevels[i - 1] > 1)
                {
                    result.Warnings.Add($"Heading hierarchy skips levels at position {i + 1}");
                }
            }

            // Check for common markdown elements
            var hasLists = Regex.IsMatch(markdown, @"^\s*[-*+]\s+.+", RegexOptions.Multiline);
            var hasTables = Regex.IsMatch(markdown, @"\|.+\|");
            var hasCodeBlocks = Regex.IsMatch(markdown, @"```[\s\S]*?```");

            result.Metadata["hasLists"] = hasLists;
            result.Metadata["hasTables"] = hasTables;
            result.Metadata["hasCodeBlocks"] = hasCodeBlocks;
            result.Metadata["headingCount"] = headingLevels.Count;

            _logger.LogInformation("Markdown structure validation completed: IsValid={IsValid}", result.IsValid);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating markdown structure");
            result.IsValid = false;
            result.Errors.Add($"Validation error: {ex.Message}");
        }

        return await Task.FromResult(result);
    }

    public async Task<DocumentValidationResult> ValidateYamlAsync(string yaml)
    {
        var result = new DocumentValidationResult { IsValid = true };

        try
        {
            if (string.IsNullOrWhiteSpace(yaml))
            {
                result.IsValid = false;
                result.Errors.Add("YAML content is empty");
                return result;
            }

            // Try to parse the YAML
            using var input = new StringReader(yaml);
            var yamlStream = new YamlStream();
            
            try
            {
                yamlStream.Load(input);
                result.Metadata["documentCount"] = yamlStream.Documents.Count;
                
                _logger.LogInformation("YAML validation successful");
            }
            catch (YamlException ex)
            {
                result.IsValid = false;
                result.Errors.Add($"YAML parsing error: {ex.Message}");
                _logger.LogError(ex, "YAML parsing failed");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating YAML");
            result.IsValid = false;
            result.Errors.Add($"Validation error: {ex.Message}");
        }

        return await Task.FromResult(result);
    }

    public async Task<DocumentValidationResult> ValidateDocumentAsync(string documentType, string content)
    {
        var result = new DocumentValidationResult { IsValid = true };

        try
        {
            // First, validate basic markdown structure
            var structureResult = await ValidateMarkdownStructureAsync(content);
            result.Errors.AddRange(structureResult.Errors);
            result.Warnings.AddRange(structureResult.Warnings);
            
            if (!structureResult.IsValid)
            {
                result.IsValid = false;
            }

            // Check document-specific requirements
            if (_requiredSections.TryGetValue(documentType.ToUpper(), out var requiredSections))
            {
                foreach (var section in requiredSections)
                {
                    var sectionPattern = $@"#{{1,3}}\s+{Regex.Escape(section)}";
                    if (!Regex.IsMatch(content, sectionPattern, RegexOptions.IgnoreCase | RegexOptions.Multiline))
                    {
                        result.IsValid = false;
                        result.Errors.Add($"Missing required section: {section}");
                    }
                }
            }
            else
            {
                result.Warnings.Add($"Unknown document type: {documentType}. Skipping section validation.");
            }

            // Check minimum content length
            var wordCount = content.Split(new[] { ' ', '\n', '\r', '\t' }, StringSplitOptions.RemoveEmptyEntries).Length;
            if (wordCount < 100)
            {
                result.Warnings.Add($"Document appears to be incomplete (only {wordCount} words)");
            }

            result.Metadata["wordCount"] = wordCount;
            result.Metadata["documentType"] = documentType;

            _logger.LogInformation("Document validation completed for {DocumentType}: IsValid={IsValid}", documentType, result.IsValid);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating document");
            result.IsValid = false;
            result.Errors.Add($"Validation error: {ex.Message}");
        }

        return result;
    }
}