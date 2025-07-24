using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

public interface IDocumentTemplateService
{
    Task<string?> LoadTemplateAsync(string templateName);
    IEnumerable<string> GetAvailableTemplates();
    Task<string> ProcessTemplateAsync(string template, Dictionary<string, object> data);
    Task<string> GenerateDocumentAsync(string templateName, Dictionary<string, object> data);
}