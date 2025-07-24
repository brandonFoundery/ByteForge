using ByteForgeFrontend.Models.ProjectManagement;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.Templates;

public interface ITemplateGenerator
{
    // Template Generation
    Task<TemplateGenerationResult> GenerateCRMTemplateAsync(string outputPath, TemplateGenerationOptions options);
    Task<TemplateGenerationResult> GenerateEcommerceTemplateAsync(string outputPath, TemplateGenerationOptions options);
    Task<TemplateGenerationResult> GenerateCustomTemplateAsync(string outputPath, string templateId, TemplateGenerationOptions options);
    
    // Template Customization
    Task<TemplateGenerationResult> CustomizeTemplateAsync(string templatePath, string outputPath, TemplateCustomization customization);
    Task<TemplateGenerationResult> MergeTemplatesAsync(string[] templatePaths, string outputPath, TemplateMergeOptions options);
    
    // Template Application
    Task<TemplateGenerationResult> ApplyTemplateToProjectAsync(string projectPath, string templateId, TemplateApplicationOptions options);
    Task<TemplateGenerationResult> UpdateProjectFromTemplateAsync(string projectPath, string templateId, string fromVersion, string toVersion);
}

public class TemplateGenerationOptions
{
    public string ProjectName { get; set; } = string.Empty;
    public bool IncludeSampleData { get; set; }
    public bool MultiTenant { get; set; }
    public string AuthProvider { get; set; } = "JWT";
    public string Database { get; set; } = "SQL Server";
    public string[] PaymentProviders { get; set; } = Array.Empty<string>();
    public string[] ShippingProviders { get; set; } = Array.Empty<string>();
    public bool OverwriteExisting { get; set; }
    public Dictionary<string, object> CustomSettings { get; set; } = new();
}

public class TemplateCustomization
{
    public Dictionary<string, string> Variables { get; set; } = new();
    public string[] ExcludeFiles { get; set; } = Array.Empty<string>();
    public Dictionary<string, string> AdditionalFiles { get; set; } = new();
    public bool MergeMode { get; set; }
    public bool PreserveExisting { get; set; }
}

public class TemplateMergeOptions
{
    public string[] PreferredTemplates { get; set; } = Array.Empty<string>();
    public ConflictResolution ConflictResolution { get; set; } = ConflictResolution.PreferFirst;
    public bool MergeSettings { get; set; } = true;
}

public enum ConflictResolution
{
    PreferFirst,
    PreferLast,
    Merge,
    Prompt
}

public class TemplateApplicationOptions
{
    public bool BackupExisting { get; set; } = true;
    public bool ValidateCompatibility { get; set; } = true;
    public bool UpdateDocumentation { get; set; } = true;
}

public class TemplateGenerationResult
{
    public bool Success { get; set; }
    public List<string> GeneratedFiles { get; set; } = new();
    public List<string> ModifiedFiles { get; set; } = new();
    public List<string> Errors { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public class TemplateVersion
{
    public string Version { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public string ChangeNotes { get; set; } = string.Empty;
    public string CreatedBy { get; set; } = string.Empty;
}

public class TemplateVersionComparison
{
    public string FromVersion { get; set; } = string.Empty;
    public string ToVersion { get; set; } = string.Empty;
    public List<TemplateChange> Changes { get; set; } = new();
}

public class TemplateChange
{
    public ChangeType Type { get; set; }
    public string Path { get; set; } = string.Empty;
    public string? OldValue { get; set; }
    public string? NewValue { get; set; }
    public string Description { get; set; } = string.Empty;
}

public enum ChangeType
{
    Added,
    Modified,
    Removed,
    Renamed
}

public class TemplateSearchOptions
{
    public string? Category { get; set; }
    public string? Author { get; set; }
    public int? MinRating { get; set; }
    public string[] Tags { get; set; } = Array.Empty<string>();
    public TemplateSortBy SortBy { get; set; } = TemplateSortBy.Popularity;
    public bool IncludeInactive { get; set; }
}

public enum TemplateSortBy
{
    Name,
    CreatedDate,
    UpdatedDate,
    Popularity,
    Rating
}

public class TemplateRating
{
    public string TemplateId { get; set; } = string.Empty;
    public double AverageRating { get; set; }
    public int TotalRatings { get; set; }
    public List<TemplateReview> Reviews { get; set; } = new();
}

public class TemplateReview
{
    public string UserId { get; set; } = string.Empty;
    public int Rating { get; set; }
    public string? Review { get; set; }
    public DateTime CreatedAt { get; set; }
}