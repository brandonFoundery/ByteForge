using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

public interface IDocumentGenerationService
{
    Task<DocumentGenerationResponse> GenerateDocumentAsync(DocumentGenerationRequest request, CancellationToken cancellationToken = default);
    Task<IEnumerable<DocumentGenerationResponse>> GenerateBatchAsync(IEnumerable<DocumentGenerationRequest> requests, CancellationToken cancellationToken = default);
    Task<string?> GetTemplateAsync(string templateName);
    Task<string> RenderTemplateAsync(string template, Dictionary<string, object> data);
}

public class DocumentGenerationRequest
{
    public string DocumentType { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
    public string? ProjectDescription { get; set; }
    public Dictionary<string, string> Dependencies { get; set; } = new Dictionary<string, string>();
    public Dictionary<string, object> AdditionalContext { get; set; } = new Dictionary<string, object>();
    public int MaxRetries { get; set; } = 3;
}

public class DocumentGenerationResponse
{
    public bool Success { get; set; }
    public string DocumentType { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string? Error { get; set; }
    public List<string> ValidationErrors { get; set; } = new List<string>();
    public List<string> ValidationWarnings { get; set; } = new List<string>();
    public DateTime GeneratedAt { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
}