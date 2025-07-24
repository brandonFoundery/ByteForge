using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services.Infrastructure.LLM;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

public class DocumentGenerationService : IDocumentGenerationService
{
    private readonly IDocumentTemplateService _templateService;
    private readonly IDocumentValidationService _validationService;
    private readonly ILLMService _llmService;
    private readonly ILogger<DocumentGenerationService> _logger;

    private readonly Dictionary<string, string> _documentPrompts = new()
    {
        ["BRD"] = "Generate a comprehensive Business Requirements Document that includes executive summary, business objectives, stakeholder analysis, business requirements, and success criteria.",
        ["PRD"] = "Generate a detailed Product Requirements Document that includes product overview, features, user stories, technical requirements, and acceptance criteria.",
        ["FRD"] = "Generate a thorough Functional Requirements Document that includes system overview, functional requirements, use cases, data requirements, and interface requirements.",
        ["TRD"] = "Generate a complete Technical Requirements Document that includes architecture overview, technology stack, database design, API design, security requirements, and performance requirements."
    };

    public DocumentGenerationService(
        IDocumentTemplateService templateService,
        IDocumentValidationService validationService,
        ILLMService llmService,
        ILogger<DocumentGenerationService> logger)
    {
        _templateService = templateService ?? throw new ArgumentNullException(nameof(templateService));
        _validationService = validationService ?? throw new ArgumentNullException(nameof(validationService));
        _llmService = llmService ?? throw new ArgumentNullException(nameof(llmService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<DocumentGenerationResponse> GenerateDocumentAsync(
        DocumentGenerationRequest request,
        CancellationToken cancellationToken = default)
    {
        var response = new DocumentGenerationResponse
        {
            DocumentType = request.DocumentType,
            GeneratedAt = DateTime.UtcNow
        };

        try
        {
            _logger.LogInformation("Starting document generation for {DocumentType}", request.DocumentType);

            // Load template
            var template = await _templateService.LoadTemplateAsync(request.DocumentType);
            if (string.IsNullOrEmpty(template))
            {
                throw new InvalidOperationException($"Template not found for document type: {request.DocumentType}");
            }

            // Build LLM prompt
            var systemPrompt = BuildSystemPrompt(request);
            var userPrompt = BuildUserPrompt(request);

            // Generate content with retry logic
            var llmRequest = new LLMGenerationRequest
            {
                SystemPrompt = systemPrompt,
                Prompt = userPrompt,
                Temperature = 0.7,
                MaxTokens = 4000
            };

            LLMGenerationResponse? llmResponse = null;
            var retryCount = 0;

            while (retryCount < request.MaxRetries)
            {
                llmResponse = await _llmService.GenerateAsync(llmRequest, cancellationToken);
                
                if (llmResponse.Success)
                {
                    break;
                }

                retryCount++;
                _logger.LogWarning("LLM generation failed, retry {Count}/{Max}: {Error}", 
                    retryCount, request.MaxRetries, llmResponse.Error);
                
                if (retryCount < request.MaxRetries)
                {
                    await Task.Delay(TimeSpan.FromSeconds(Math.Pow(2, retryCount)), cancellationToken);
                }
            }

            if (llmResponse == null || !llmResponse.Success)
            {
                response.Success = false;
                response.Error = llmResponse?.Error ?? "Failed to generate content after retries";
                return response;
            }

            // Process template with generated content
            var templateData = new Dictionary<string, object>
            {
                ["DocumentType"] = GetFriendlyDocumentName(request.DocumentType),
                ["ProjectName"] = request.ProjectName,
                ["ProjectDescription"] = request.ProjectDescription ?? string.Empty,
                ["Content"] = llmResponse.Content,
                ["GeneratedDate"] = DateTime.UtcNow.ToString("yyyy-MM-dd"),
                ["GeneratedBy"] = "ByteForge AI"
            };

            // Add additional context
            foreach (var kvp in request.AdditionalContext)
            {
                templateData[kvp.Key] = kvp.Value;
            }

            var processedContent = await _templateService.ProcessTemplateAsync(template, templateData);

            // Validate the generated document
            var validationResult = await _validationService.ValidateDocumentAsync(request.DocumentType, processedContent);
            
            response.Content = processedContent;
            response.ValidationErrors = validationResult.Errors;
            response.ValidationWarnings = validationResult.Warnings;
            response.Success = validationResult.IsValid;

            if (!validationResult.IsValid)
            {
                response.Error = "Document validation failed";
            }

            // Add metadata
            response.Metadata["llmProvider"] = llmResponse.Provider;
            response.Metadata["llmModel"] = llmResponse.Model;
            response.Metadata["tokensUsed"] = llmResponse.TokensUsed;
            response.Metadata["wordCount"] = validationResult.Metadata.GetValueOrDefault("wordCount", 0);

            _logger.LogInformation("Document generation completed for {DocumentType}: Success={Success}", 
                request.DocumentType, response.Success);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating document for {DocumentType}", request.DocumentType);
            response.Success = false;
            response.Error = $"Document generation failed: {ex.Message}";
            return response;
        }
    }

    public async Task<IEnumerable<DocumentGenerationResponse>> GenerateBatchAsync(
        IEnumerable<DocumentGenerationRequest> requests,
        CancellationToken cancellationToken = default)
    {
        var tasks = requests.Select(request => GenerateDocumentAsync(request, cancellationToken));
        return await Task.WhenAll(tasks);
    }

    private string BuildSystemPrompt(DocumentGenerationRequest request)
    {
        var prompt = "You are an expert technical writer and requirements analyst. ";
        prompt += $"Generate a professional {GetFriendlyDocumentName(request.DocumentType)} following industry best practices. ";
        prompt += "Use clear, concise language and ensure all required sections are included. ";
        prompt += "Format the output in Markdown with proper headings and structure.";

        // Include dependencies context
        if (request.Dependencies.Any())
        {
            prompt += "\n\nConsider the following dependent documents:\n";
            foreach (var dep in request.Dependencies)
            {
                prompt += $"\n{dep.Key}:\n{dep.Value}\n";
            }
        }

        return prompt;
    }

    private string BuildUserPrompt(DocumentGenerationRequest request)
    {
        var basePrompt = _documentPrompts.GetValueOrDefault(request.DocumentType.ToUpper(), 
            "Generate a comprehensive document");

        var prompt = $"{basePrompt}\n\n";
        prompt += $"Project Name: {request.ProjectName}\n";
        
        if (!string.IsNullOrEmpty(request.ProjectDescription))
        {
            prompt += $"Project Description: {request.ProjectDescription}\n";
        }

        // Add any additional context
        if (request.AdditionalContext.Any())
        {
            prompt += "\nAdditional Context:\n";
            foreach (var kvp in request.AdditionalContext)
            {
                prompt += $"- {kvp.Key}: {kvp.Value}\n";
            }
        }

        return prompt;
    }

    private string GetFriendlyDocumentName(string documentType)
    {
        return documentType.ToUpper() switch
        {
            "BRD" => "Business Requirements Document",
            "PRD" => "Product Requirements Document",
            "FRD" => "Functional Requirements Document",
            "TRD" => "Technical Requirements Document",
            _ => documentType
        };
    }
    
    public async Task<string?> GetTemplateAsync(string templateName)
    {
        return await _templateService.LoadTemplateAsync(templateName);
    }
    
    public async Task<string> RenderTemplateAsync(string template, Dictionary<string, object> data)
    {
        return await _templateService.ProcessTemplateAsync(template, data);
    }
}