using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

public interface IDocumentValidationService
{
    Task<DocumentValidationResult> ValidateMarkdownStructureAsync(string markdown);
    Task<DocumentValidationResult> ValidateYamlAsync(string yaml);
    Task<DocumentValidationResult> ValidateDocumentAsync(string documentType, string content);
}

public class DocumentValidationResult
{
    public bool IsValid { get; set; }
    public List<string> Errors { get; set; } = new List<string>();
    public List<string> Warnings { get; set; } = new List<string>();
    public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
}