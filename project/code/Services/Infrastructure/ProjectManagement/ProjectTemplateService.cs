using System.Text.Json;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Models.ProjectManagement;

using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.ProjectManagement;

public class ProjectTemplateService : IProjectTemplateService
{
    private readonly IFileProvider _fileProvider;
    private readonly ILogger<ProjectTemplateService> _logger;
    private readonly Dictionary<string, ProjectTemplate> _templateCache = new();

    public ProjectTemplateService(IFileProvider fileProvider, ILogger<ProjectTemplateService> logger)
    {
        _fileProvider = fileProvider ?? throw new ArgumentNullException(nameof(fileProvider));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<ProjectTemplate?> GetTemplateAsync(string templateId)
    {
        try
        {
            // Check cache first
            if (_templateCache.TryGetValue(templateId, out var cachedTemplate))
            {
                return cachedTemplate;
            }

            var metadataPath = $"Templates/{templateId}/metadata.json";
            var fileInfo = _fileProvider.GetFileInfo(metadataPath);

            if (!fileInfo.Exists)
            {
                _logger.LogWarning("Template metadata not found: {TemplateId}", templateId);
                return null;
            }

            using var stream = fileInfo.CreateReadStream();
            var template = await JsonSerializer.DeserializeAsync<ProjectTemplate>(stream, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            if (template != null)
            {
                template.CreatedAt = fileInfo.LastModified.DateTime;
                _templateCache[templateId] = template;
            }

            return template;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading template {TemplateId}", templateId);
            return null;
        }
    }

    public async Task<IEnumerable<ProjectTemplate>> GetAllTemplatesAsync()
    {
        try
        {
            var templates = new List<ProjectTemplate>();
            var templateDir = _fileProvider.GetDirectoryContents("Templates");

            foreach (var item in templateDir)
            {
                if (item.IsDirectory)
                {
                    var template = await GetTemplateAsync(item.Name);
                    if (template != null && template.IsActive)
                    {
                        templates.Add(template);
                    }
                }
            }

            return templates.OrderBy(t => t.Category).ThenBy(t => t.Name);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting all templates");
            return Enumerable.Empty<ProjectTemplate>();
        }
    }

    public async Task<IEnumerable<ProjectTemplate>> GetTemplatesByCategoryAsync(string category)
    {
        var allTemplates = await GetAllTemplatesAsync();
        return allTemplates.Where(t => t.Category.Equals(category, StringComparison.OrdinalIgnoreCase));
    }

    public async Task<TemplateStructure?> GetTemplateStructureAsync(string templateId)
    {
        try
        {
            var templatePath = $"Templates/{templateId}";
            var templateDir = _fileProvider.GetDirectoryContents(templatePath);

            if (!templateDir.Exists)
            {
                return null;
            }

            var structure = new TemplateStructure();
            
            foreach (var item in templateDir)
            {
                if (item.IsDirectory)
                {
                    structure.Directories.Add(item.Name);
                }
                else
                {
                    structure.Files.Add(item.Name);
                }
            }

            structure.Metadata["totalFiles"] = structure.Files.Count;
            structure.Metadata["totalDirectories"] = structure.Directories.Count;

            return structure;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting template structure for {TemplateId}", templateId);
            return null;
        }
    }

    public async Task<TemplateValidationResult> ValidateTemplateAsync(string templateId)
    {
        var result = new TemplateValidationResult { IsValid = true };

        try
        {
            // Check if template exists
            var template = await GetTemplateAsync(templateId);
            if (template == null)
            {
                result.IsValid = false;
                result.Errors.Add($"Template '{templateId}' not found");
                return result;
            }

            // Check required files
            var requiredFiles = new[] { "metadata.json", "template.yaml" };
            foreach (var file in requiredFiles)
            {
                var filePath = $"Templates/{templateId}/{file}";
                var fileInfo = _fileProvider.GetFileInfo(filePath);
                if (!fileInfo.Exists)
                {
                    result.IsValid = false;
                    result.Errors.Add($"Required file '{file}' not found");
                }
            }

            // Check required document templates
            foreach (var docType in template.RequiredDocuments)
            {
                var docPath = $"Templates/{templateId}/Documents/{docType}.md";
                var docInfo = _fileProvider.GetFileInfo(docPath);
                if (!docInfo.Exists)
                {
                    result.IsValid = false;
                    result.Errors.Add($"Required document template '{docType}.md' not found");
                }
            }

            // Validate template metadata
            if (string.IsNullOrEmpty(template.Name))
            {
                result.IsValid = false;
                result.Errors.Add("Template name is required");
            }

            if (string.IsNullOrEmpty(template.Id))
            {
                result.IsValid = false;
                result.Errors.Add("Template ID is required");
            }

            _logger.LogInformation("Template validation completed for {TemplateId}: IsValid={IsValid}", 
                templateId, result.IsValid);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating template {TemplateId}", templateId);
            result.IsValid = false;
            result.Errors.Add($"Validation error: {ex.Message}");
        }

        return result;
    }

    public async Task<ProjectTemplate?> CloneTemplateAsync(string sourceTemplateId, string newTemplateId, string newName)
    {
        try
        {
            var sourceTemplate = await GetTemplateAsync(sourceTemplateId);
            if (sourceTemplate == null)
            {
                throw new InvalidOperationException($"Source template '{sourceTemplateId}' not found");
            }

            // Create a clone of the template
            var clonedTemplate = new ProjectTemplate
            {
                Id = newTemplateId,
                Name = newName,
                Description = $"Cloned from {sourceTemplate.Name}. {sourceTemplate.Description}",
                Category = sourceTemplate.Category,
                Version = "1.0.0",
                RequiredDocuments = sourceTemplate.RequiredDocuments.ToArray(),
                OptionalDocuments = sourceTemplate.OptionalDocuments.ToArray(),
                DefaultSettings = new Dictionary<string, object>(sourceTemplate.DefaultSettings),
                FileStructure = new Dictionary<string, string>(sourceTemplate.FileStructure),
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            };

            // In a real implementation, you would also copy the template files
            // For now, we'll just return the cloned metadata
            _logger.LogInformation("Cloned template {SourceId} to {NewId}", sourceTemplateId, newTemplateId);
            
            return clonedTemplate;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error cloning template from {SourceId} to {NewId}", sourceTemplateId, newTemplateId);
            return null;
        }
    }
}