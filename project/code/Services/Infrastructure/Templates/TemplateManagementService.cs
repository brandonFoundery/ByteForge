using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Data;
using System.Text.Json;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.Templates;

public class TemplateManagementService : ITemplateManagementService
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<TemplateManagementService> _logger;

    public TemplateManagementService(ApplicationDbContext context, ILogger<TemplateManagementService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<ProjectTemplate> CreateTemplateAsync(ProjectTemplate template)
    {
        if (string.IsNullOrWhiteSpace(template.Id))
        {
            throw new ArgumentException("Template ID is required", nameof(template));
        }

        var existing = await _context.ProjectTemplates.FindAsync(template.Id);
        if (existing != null)
        {
            throw new InvalidOperationException($"Template with ID '{template.Id}' already exists");
        }

        template.CreatedAt = DateTime.UtcNow;
        template.IsActive = true;

        _context.ProjectTemplates.Add(template);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Created template {TemplateId} - {TemplateName}", template.Id, template.Name);
        return template;
    }

    public async Task<ProjectTemplate?> GetTemplateAsync(string templateId)
    {
        return await _context.ProjectTemplates
            .FirstOrDefaultAsync(t => t.Id == templateId);
    }

    public async Task<IEnumerable<ProjectTemplate>> GetAllTemplatesAsync()
    {
        return await _context.ProjectTemplates
            .Where(t => t.IsActive)
            .OrderBy(t => t.Category)
            .ThenBy(t => t.Name)
            .ToListAsync();
    }

    public async Task<IEnumerable<ProjectTemplate>> GetTemplatesByCategoryAsync(string category)
    {
        return await _context.ProjectTemplates
            .Where(t => t.Category == category && t.IsActive)
            .OrderBy(t => t.Name)
            .ToListAsync();
    }

    public async Task<ProjectTemplate> UpdateTemplateAsync(ProjectTemplate template)
    {
        var existing = await _context.ProjectTemplates.FindAsync(template.Id);
        if (existing == null)
        {
            throw new KeyNotFoundException($"Template with ID '{template.Id}' not found");
        }

        existing.Name = template.Name;
        existing.Description = template.Description;
        existing.Category = template.Category;
        existing.Version = template.Version;
        existing.RequiredDocuments = template.RequiredDocuments;
        existing.OptionalDocuments = template.OptionalDocuments;
        existing.DefaultSettings = template.DefaultSettings;
        existing.FileStructure = template.FileStructure;
        existing.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        _logger.LogInformation("Updated template {TemplateId} - {TemplateName}", existing.Id, existing.Name);
        return existing;
    }

    public async Task<bool> DeleteTemplateAsync(string templateId)
    {
        var template = await _context.ProjectTemplates.FindAsync(templateId);
        if (template == null)
        {
            return false;
        }

        // Check if template is in use
        var inUse = await IsTemplateInUseAsync(templateId);
        if (inUse)
        {
            throw new InvalidOperationException($"Cannot delete template '{templateId}' because it is in use by one or more projects");
        }

        _context.ProjectTemplates.Remove(template);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Deleted template {TemplateId} - {TemplateName}", template.Id, template.Name);
        return true;
    }

    public async Task<ProjectTemplate> CloneTemplateAsync(string sourceTemplateId, string newTemplateId, string newName)
    {
        var sourceTemplate = await GetTemplateAsync(sourceTemplateId);
        if (sourceTemplate == null)
        {
            throw new KeyNotFoundException($"Source template '{sourceTemplateId}' not found");
        }

        var clonedTemplate = new ProjectTemplate
        {
            Id = newTemplateId,
            Name = newName,
            Description = $"{sourceTemplate.Description} (Cloned from {sourceTemplate.Name})",
            Category = sourceTemplate.Category,
            Version = "1.0.0",
            RequiredDocuments = sourceTemplate.RequiredDocuments.ToArray(),
            OptionalDocuments = sourceTemplate.OptionalDocuments.ToArray(),
            DefaultSettings = new Dictionary<string, object>(sourceTemplate.DefaultSettings),
            FileStructure = new Dictionary<string, string>(sourceTemplate.FileStructure),
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };

        return await CreateTemplateAsync(clonedTemplate);
    }

    public async Task<bool> IsTemplateInUseAsync(string templateId)
    {
        return await _context.Projects.AnyAsync(p => p.TemplateId == templateId);
    }

    public async Task<int> GetTemplateUsageCountAsync(string templateId)
    {
        return await _context.Projects.CountAsync(p => p.TemplateId == templateId);
    }

    public async Task<ProjectTemplate> CreateTemplateVersionAsync(string templateId, string newVersion, string changeNotes)
    {
        var template = await GetTemplateAsync(templateId);
        if (template == null)
        {
            throw new KeyNotFoundException($"Template '{templateId}' not found");
        }

        // Store version history in metadata (in a real implementation, this would be a separate table)
        if (!template.DefaultSettings.ContainsKey("_versionHistory"))
        {
            template.DefaultSettings["_versionHistory"] = new List<object>();
        }

        var versionHistory = template.DefaultSettings["_versionHistory"] as List<object> ?? new List<object>();
        versionHistory.Add(new
        {
            Version = template.Version,
            CreatedAt = template.UpdatedAt ?? template.CreatedAt,
            ChangeNotes = "Previous version"
        });

        template.Version = newVersion;
        template.UpdatedAt = DateTime.UtcNow;
        template.DefaultSettings["_versionHistory"] = versionHistory;
        template.DefaultSettings["_latestChangeNotes"] = changeNotes;

        await _context.SaveChangesAsync();

        _logger.LogInformation("Created new version {Version} for template {TemplateId}", newVersion, templateId);
        return template;
    }

    public async Task<IEnumerable<TemplateVersion>> GetTemplateVersionsAsync(string templateId)
    {
        var template = await GetTemplateAsync(templateId);
        if (template == null)
        {
            return Enumerable.Empty<TemplateVersion>();
        }

        var versions = new List<TemplateVersion>();

        // Add current version
        versions.Add(new TemplateVersion
        {
            Version = template.Version,
            CreatedAt = template.UpdatedAt ?? template.CreatedAt,
            ChangeNotes = template.DefaultSettings.ContainsKey("_latestChangeNotes") 
                ? template.DefaultSettings["_latestChangeNotes"].ToString() ?? "Current version"
                : "Current version",
            CreatedBy = "System"
        });

        // Add version history
        if (template.DefaultSettings.ContainsKey("_versionHistory"))
        {
            var historyJson = JsonSerializer.Serialize(template.DefaultSettings["_versionHistory"]);
            var history = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(historyJson);
            
            if (history != null)
            {
                foreach (var item in history)
                {
                    versions.Add(new TemplateVersion
                    {
                        Version = item.ContainsKey("Version") ? item["Version"].ToString() ?? "" : "",
                        CreatedAt = item.ContainsKey("CreatedAt") ? DateTime.Parse(item["CreatedAt"].ToString() ?? DateTime.UtcNow.ToString()) : DateTime.UtcNow,
                        ChangeNotes = item.ContainsKey("ChangeNotes") ? item["ChangeNotes"].ToString() ?? "" : "",
                        CreatedBy = "System"
                    });
                }
            }
        }

        return versions.OrderByDescending(v => v.CreatedAt);
    }

    public async Task<TemplateVersionComparison> CompareTemplateVersionsAsync(string templateId, string version1, string version2)
    {
        var versions = await GetTemplateVersionsAsync(templateId);
        var v1 = versions.FirstOrDefault(v => v.Version == version1);
        var v2 = versions.FirstOrDefault(v => v.Version == version2);

        if (v1 == null || v2 == null)
        {
            throw new KeyNotFoundException("One or both versions not found");
        }

        // In a real implementation, this would compare actual template content
        return new TemplateVersionComparison
        {
            FromVersion = version1,
            ToVersion = version2,
            Changes = new List<TemplateChange>
            {
                new TemplateChange
                {
                    Type = ChangeType.Modified,
                    Path = "Version",
                    OldValue = version1,
                    NewValue = version2,
                    Description = $"Version changed from {version1} to {version2}"
                }
            }
        };
    }

    public async Task<ProjectTemplate> ImportTemplateAsync(Stream templateStream, string format = "json")
    {
        if (format.ToLower() != "json")
        {
            throw new NotSupportedException($"Format '{format}' is not supported. Only JSON is currently supported.");
        }

        using var reader = new StreamReader(templateStream);
        var json = await reader.ReadToEndAsync();
        var template = JsonSerializer.Deserialize<ProjectTemplate>(json);

        if (template == null)
        {
            throw new InvalidOperationException("Failed to deserialize template");
        }

        return await CreateTemplateAsync(template);
    }

    public async Task<Stream> ExportTemplateAsync(string templateId, string format = "json")
    {
        if (format.ToLower() != "json")
        {
            throw new NotSupportedException($"Format '{format}' is not supported. Only JSON is currently supported.");
        }

        var template = await GetTemplateAsync(templateId);
        if (template == null)
        {
            throw new KeyNotFoundException($"Template '{templateId}' not found");
        }

        var json = JsonSerializer.Serialize(template, new JsonSerializerOptions 
        { 
            WriteIndented = true 
        });

        var stream = new MemoryStream();
        var writer = new StreamWriter(stream);
        await writer.WriteAsync(json);
        await writer.FlushAsync();
        stream.Position = 0;

        return stream;
    }

    public async Task<IEnumerable<ProjectTemplate>> SearchTemplatesAsync(string searchTerm, TemplateSearchOptions? options = null)
    {
        var query = _context.ProjectTemplates.AsQueryable();

        if (!string.IsNullOrWhiteSpace(searchTerm))
        {
            query = query.Where(t => 
                t.Name.Contains(searchTerm) || 
                (t.Description != null && t.Description.Contains(searchTerm)));
        }

        if (options != null)
        {
            if (!string.IsNullOrWhiteSpace(options.Category))
            {
                query = query.Where(t => t.Category == options.Category);
            }

            if (!options.IncludeInactive)
            {
                query = query.Where(t => t.IsActive);
            }

            // Apply sorting
            query = options.SortBy switch
            {
                TemplateSortBy.Name => query.OrderBy(t => t.Name),
                TemplateSortBy.CreatedDate => query.OrderByDescending(t => t.CreatedAt),
                TemplateSortBy.UpdatedDate => query.OrderByDescending(t => t.UpdatedAt ?? t.CreatedAt),
                _ => query.OrderBy(t => t.Name)
            };
        }

        return await query.ToListAsync();
    }

    public async Task<TemplateRating?> GetTemplateRatingAsync(string templateId)
    {
        var template = await GetTemplateAsync(templateId);
        if (template == null)
        {
            return null;
        }

        // In a real implementation, ratings would be stored in a separate table
        // For now, return mock data
        return new TemplateRating
        {
            TemplateId = templateId,
            AverageRating = 4.5,
            TotalRatings = 10,
            Reviews = new List<TemplateReview>()
        };
    }

    public async Task RateTemplateAsync(string templateId, int rating, string? review = null, string userId = "anonymous")
    {
        var template = await GetTemplateAsync(templateId);
        if (template == null)
        {
            throw new KeyNotFoundException($"Template '{templateId}' not found");
        }

        if (rating < 1 || rating > 5)
        {
            throw new ArgumentException("Rating must be between 1 and 5", nameof(rating));
        }

        // In a real implementation, this would store the rating in a separate table
        _logger.LogInformation("User {UserId} rated template {TemplateId} with {Rating} stars", 
            userId, templateId, rating);

        await Task.CompletedTask;
    }
}