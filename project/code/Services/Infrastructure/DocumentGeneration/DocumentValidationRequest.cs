using System.Collections.Generic;

namespace ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

public class DocumentValidationRequest
{
    public string DocumentType { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public Dictionary<string, string> Dependencies { get; set; } = new Dictionary<string, string>();
    public bool CheckDependencies { get; set; } = true;
    public bool CheckStructure { get; set; } = true;
    public bool CheckCompleteness { get; set; } = true;
}