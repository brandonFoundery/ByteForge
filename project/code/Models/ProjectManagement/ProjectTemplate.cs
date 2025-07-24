using System.ComponentModel.DataAnnotations;

using System;
using System.Collections.Generic;
namespace ByteForgeFrontend.Models.ProjectManagement;

public class ProjectTemplate
{
    [Required]
    [MaxLength(50)]
    public string Id { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = string.Empty;
    
    [MaxLength(1000)]
    public string? Description { get; set; }
    
    [MaxLength(50)]
    public string Category { get; set; } = "General";
    
    [MaxLength(20)]
    public string Version { get; set; } = "1.0.0";
    
    public string[] RequiredDocuments { get; set; } = Array.Empty<string>();
    
    public string[] OptionalDocuments { get; set; } = Array.Empty<string>();
    
    public Dictionary<string, object> DefaultSettings { get; set; } = new();
    
    public Dictionary<string, string> FileStructure { get; set; } = new();
    
    public bool IsActive { get; set; } = true;
    
    public DateTime CreatedAt { get; set; }
    
    public DateTime? UpdatedAt { get; set; }
}

public class TemplateStructure
{
    public List<string> Files { get; set; } = new();
    public List<string> Directories { get; set; } = new();
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public class TemplateValidationResult
{
    public bool IsValid { get; set; }
    public List<string> Errors { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
}