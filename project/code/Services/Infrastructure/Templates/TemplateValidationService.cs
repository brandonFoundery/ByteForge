using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Models.ProjectManagement;
using System.Text.RegularExpressions;

using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.Templates;

public class TemplateValidationService : ITemplateValidationService
{
    private readonly ILogger<TemplateValidationService> _logger;
    private readonly HashSet<string> _validDocumentTypes = new()
    {
        "BRD", "PRD", "FRD", "TRD", "DRD", "UX_SPEC", "TEST_PLAN", "API_SPEC", "RTM"
    };
    
    private readonly HashSet<string> _validCategories = new()
    {
        "Business", "E-commerce", "Healthcare", "Education", "Finance", "Social", "Entertainment", "Productivity", "General"
    };
    
    private readonly HashSet<string> _validAuthProviders = new()
    {
        "JWT", "OAuth", "Azure AD", "Auth0", "IdentityServer", "Custom"
    };
    
    private readonly HashSet<string> _validDatabases = new()
    {
        "SQL Server", "PostgreSQL", "MySQL", "MongoDB", "CosmosDB", "SQLite"
    };

    public TemplateValidationService(ILogger<TemplateValidationService> logger)
    {
        _logger = logger;
    }

    public async Task<TemplateValidationResult> ValidateTemplateAsync(ProjectTemplate template)
    {
        var result = new TemplateValidationResult { IsValid = true };

        // Validate basic properties
        if (string.IsNullOrWhiteSpace(template.Id))
        {
            result.Errors.Add("Template ID is required");
            result.IsValid = false;
        }
        else if (!await IsValidTemplateIdAsync(template.Id))
        {
            result.Errors.Add("Template ID must contain only letters, numbers, hyphens, and underscores");
            result.IsValid = false;
        }

        if (string.IsNullOrWhiteSpace(template.Name))
        {
            result.Errors.Add("Template name is required");
            result.IsValid = false;
        }

        // Validate version
        if (!string.IsNullOrWhiteSpace(template.Version) && !IsValidSemanticVersion(template.Version))
        {
            result.Errors.Add($"Invalid version format: {template.Version}. Use semantic versioning (e.g., 1.0.0)");
            result.IsValid = false;
        }

        // Validate category
        if (!string.IsNullOrWhiteSpace(template.Category) && !_validCategories.Contains(template.Category))
        {
            result.Errors.Add($"Invalid category: {template.Category}. Valid categories are: {string.Join(", ", _validCategories)}");
            result.IsValid = false;
        }

        // Validate documents
        foreach (var doc in template.RequiredDocuments)
        {
            if (!await IsValidDocumentTypeAsync(doc))
            {
                result.Errors.Add($"Invalid document type: {doc}");
                result.IsValid = false;
            }
        }

        foreach (var doc in template.OptionalDocuments)
        {
            if (!await IsValidDocumentTypeAsync(doc))
            {
                result.Errors.Add($"Invalid document type: {doc}");
                result.IsValid = false;
            }
        }

        // Validate file structure
        if (template.FileStructure != null)
        {
            foreach (var (path, type) in template.FileStructure)
            {
                if (!IsValidPath(path))
                {
                    result.Errors.Add($"Invalid path: {path}");
                    result.IsValid = false;
                }

                if (type != "file" && type != "directory")
                {
                    result.Errors.Add($"Invalid file structure type: {type}. Must be 'file' or 'directory'");
                    result.IsValid = false;
                }
            }

            // Check for recommended directories
            var hasSourceDir = template.FileStructure.Any(fs => fs.Key.Contains("/src") || fs.Key.Contains("/source"));
            var hasTestDir = template.FileStructure.Any(fs => fs.Key.Contains("/test") || fs.Key.Contains("/tests"));
            var hasDocsDir = template.FileStructure.Any(fs => fs.Key.Contains("/docs") || fs.Key.Contains("/documentation"));

            if (!hasSourceDir)
            {
                result.Warnings.Add("Missing recommended directory: source code directory (e.g., /src)");
            }

            if (!hasTestDir)
            {
                result.Warnings.Add("Missing recommended directory: tests directory (e.g., /tests)");
            }

            if (!hasDocsDir)
            {
                result.Warnings.Add("Missing recommended directory: documentation directory (e.g., /docs)");
            }
        }

        // Validate default settings
        if (template.DefaultSettings != null)
        {
            var settingsResult = await ValidateDefaultSettingsAsync(template.DefaultSettings);
            result.Errors.AddRange(settingsResult.Errors);
            result.Warnings.AddRange(settingsResult.Warnings);
            if (!settingsResult.IsValid)
            {
                result.IsValid = false;
            }
        }

        return result;
    }

    public async Task<TemplateValidationResult> ValidateTemplateStructureAsync(TemplateStructure structure)
    {
        var result = new TemplateValidationResult { IsValid = true };

        // Check for duplicate files
        var duplicateFiles = structure.Files
            .GroupBy(f => f.ToLowerInvariant())
            .Where(g => g.Count() > 1)
            .Select(g => g.Key);

        foreach (var dup in duplicateFiles)
        {
            result.Errors.Add($"Duplicate file: {dup}");
            result.IsValid = false;
        }

        // Check for duplicate directories
        var duplicateDirs = structure.Directories
            .GroupBy(d => d.ToLowerInvariant())
            .Where(g => g.Count() > 1)
            .Select(g => g.Key);

        foreach (var dup in duplicateDirs)
        {
            result.Errors.Add($"Duplicate directory: {dup}");
            result.IsValid = false;
        }

        // Validate paths
        foreach (var file in structure.Files)
        {
            if (!IsValidPath(file))
            {
                result.Errors.Add($"Invalid file path: {file}");
                result.IsValid = false;
            }
        }

        foreach (var dir in structure.Directories)
        {
            if (!IsValidPath(dir))
            {
                result.Errors.Add($"Invalid directory path: {dir}");
                result.IsValid = false;
            }
        }

        await Task.CompletedTask;
        return result;
    }

    public async Task<TemplateValidationResult> ValidateDefaultSettingsAsync(Dictionary<string, object> settings)
    {
        var result = new TemplateValidationResult { IsValid = true };

        // Validate auth provider
        if (settings.TryGetValue("authProvider", out var authProvider))
        {
            var authProviderStr = authProvider?.ToString();
            if (!string.IsNullOrWhiteSpace(authProviderStr) && !_validAuthProviders.Contains(authProviderStr))
            {
                result.Errors.Add($"Invalid auth provider: {authProviderStr}. Valid providers are: {string.Join(", ", _validAuthProviders)}");
                result.IsValid = false;
            }
        }

        // Validate database
        if (settings.TryGetValue("database", out var database))
        {
            var databaseStr = database?.ToString();
            if (!string.IsNullOrWhiteSpace(databaseStr) && !_validDatabases.Contains(databaseStr))
            {
                result.Errors.Add($"Invalid database: {databaseStr}. Valid databases are: {string.Join(", ", _validDatabases)}");
                result.IsValid = false;
            }
        }

        // Validate boolean settings
        var booleanSettings = new[] { "multiTenant", "enableAudit", "enableCache", "enableNotifications" };
        foreach (var setting in booleanSettings)
        {
            if (settings.TryGetValue(setting, out var value) && value != null)
            {
                if (!(value is bool) && !bool.TryParse(value.ToString(), out _))
                {
                    result.Errors.Add($"Setting '{setting}' must be a boolean value");
                    result.IsValid = false;
                }
            }
        }

        await Task.CompletedTask;
        return result;
    }

    public async Task<TemplateValidationResult> ValidateTemplateMetadataAsync(ProjectTemplate template)
    {
        var result = new TemplateValidationResult { IsValid = true };

        // Validate category
        if (!string.IsNullOrWhiteSpace(template.Category) && !_validCategories.Contains(template.Category))
        {
            result.Errors.Add($"Invalid category: {template.Category}");
            result.IsValid = false;
        }

        // Validate description length
        if (!string.IsNullOrWhiteSpace(template.Description) && template.Description.Length > 1000)
        {
            result.Warnings.Add($"Description exceeds recommended length of 1000 characters (current: {template.Description.Length})");
        }

        // Validate version format
        if (!string.IsNullOrWhiteSpace(template.Version) && !IsValidSemanticVersion(template.Version))
        {
            result.Errors.Add("Version must follow semantic versioning format (e.g., 1.0.0)");
            result.IsValid = false;
        }

        await Task.CompletedTask;
        return result;
    }

    public async Task<bool> IsValidTemplateIdAsync(string templateId)
    {
        if (string.IsNullOrWhiteSpace(templateId))
            return false;

        // Template ID must contain only letters, numbers, hyphens, and underscores
        var regex = new Regex(@"^[a-zA-Z0-9\-_]+$");
        return await Task.FromResult(regex.IsMatch(templateId));
    }

    public async Task<bool> IsValidDocumentTypeAsync(string documentType)
    {
        return await Task.FromResult(_validDocumentTypes.Contains(documentType));
    }

    public async Task<IEnumerable<string>> GetValidCategoriesAsync()
    {
        return await Task.FromResult(_validCategories.ToList());
    }

    public async Task<IEnumerable<string>> GetValidDocumentTypesAsync()
    {
        return await Task.FromResult(_validDocumentTypes.ToList());
    }

    private bool IsValidSemanticVersion(string version)
    {
        // Basic semantic versioning pattern (e.g., 1.0.0, 2.1.0-beta, 3.0.0-rc.1)
        var regex = new Regex(@"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$");
        return regex.IsMatch(version);
    }

    private bool IsValidPath(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            return false;

        // Check for invalid characters
        var invalidChars = Path.GetInvalidPathChars();
        if (path.Any(c => invalidChars.Contains(c)))
            return false;

        // Additional validation for common invalid patterns
        var invalidPatterns = new[] { "..", "~", "*", "?" };
        return !invalidPatterns.Any(pattern => path.Contains(pattern));
    }
}