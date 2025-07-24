using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Logging;
using Scriban;
using Scriban.Runtime;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

public class DocumentTemplateService : IDocumentTemplateService
{
    private readonly IFileProvider _fileProvider;
    private readonly ILogger<DocumentTemplateService> _logger;
    private readonly Dictionary<string, Template> _templateCache = new();

    public DocumentTemplateService(IFileProvider fileProvider, ILogger<DocumentTemplateService> logger)
    {
        _fileProvider = fileProvider ?? throw new ArgumentNullException(nameof(fileProvider));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<string?> LoadTemplateAsync(string templateName)
    {
        try
        {
            var templatePath = $"Templates/{templateName}.md";
            var fileInfo = _fileProvider.GetFileInfo(templatePath);

            if (!fileInfo.Exists)
            {
                _logger.LogError("Template not found: {TemplateName} at path {Path}", templateName, templatePath);
                throw new FileNotFoundException($"Template '{templateName}' not found");
            }

            using var stream = fileInfo.CreateReadStream();
            using var reader = new StreamReader(stream);
            var content = await reader.ReadToEndAsync();
            
            _logger.LogInformation("Loaded template: {TemplateName}", templateName);
            return content;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading template: {TemplateName}", templateName);
            throw;
        }
    }

    public IEnumerable<string> GetAvailableTemplates()
    {
        try
        {
            var templates = new List<string>();
            var templateDir = _fileProvider.GetDirectoryContents("Templates");

            foreach (var file in templateDir)
            {
                if (!file.IsDirectory && file.Name.EndsWith(".md", StringComparison.OrdinalIgnoreCase))
                {
                    var templateName = Path.GetFileNameWithoutExtension(file.Name);
                    templates.Add(templateName);
                }
            }

            _logger.LogInformation("Found {Count} templates", templates.Count);
            return templates;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting available templates");
            return Enumerable.Empty<string>();
        }
    }

    public async Task<string> ProcessTemplateAsync(string templateContent, Dictionary<string, object> data)
    {
        try
        {
            // Parse the template using Scriban
            var template = Template.Parse(templateContent);
            
            if (template.HasErrors)
            {
                var errors = string.Join("; ", template.Messages.Select(m => m.ToString()));
                _logger.LogError("Template parsing errors: {Errors}", errors);
                throw new InvalidOperationException($"Template parsing failed: {errors}");
            }

            // Create a script object with the data
            var scriptObject = new ScriptObject();
            foreach (var kvp in data)
            {
                scriptObject[kvp.Key] = kvp.Value;
            }

            // Add custom functions
            scriptObject.Import(typeof(DocumentTemplateFunctions));

            var context = new TemplateContext();
            context.PushGlobal(scriptObject);

            // Render the template
            var result = await template.RenderAsync(context);
            
            _logger.LogInformation("Successfully processed template");
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing template");
            throw;
        }
    }
    
    public async Task<string> GenerateDocumentAsync(string templateName, Dictionary<string, object> data)
    {
        var template = await LoadTemplateAsync(templateName);
        if (template == null)
        {
            throw new InvalidOperationException($"Template '{templateName}' not found");
        }
        
        return await ProcessTemplateAsync(template, data);
    }
}

// Custom template functions
public static class DocumentTemplateFunctions
{
    public static string FormatDate(DateTime date, string format = "yyyy-MM-dd")
    {
        return date.ToString(format);
    }

    public static string ToUpper(string text)
    {
        return text?.ToUpperInvariant() ?? string.Empty;
    }

    public static string ToLower(string text)
    {
        return text?.ToLowerInvariant() ?? string.Empty;
    }

    public static string ToCamelCase(string text)
    {
        if (string.IsNullOrEmpty(text))
            return text;

        return char.ToLowerInvariant(text[0]) + text.Substring(1);
    }

    public static string ToPascalCase(string text)
    {
        if (string.IsNullOrEmpty(text))
            return text;

        return char.ToUpperInvariant(text[0]) + text.Substring(1);
    }
}