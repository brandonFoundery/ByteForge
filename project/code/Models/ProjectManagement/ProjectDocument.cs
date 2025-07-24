using System.ComponentModel.DataAnnotations;

using System;
using System.Collections.Generic;
namespace ByteForgeFrontend.Models.ProjectManagement;

public class ProjectDocument
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    public string ProjectId { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(50)]
    public string DocumentType { get; set; } = string.Empty;
    
    [Required]
    public string Content { get; set; } = string.Empty;
    
    [MaxLength(20)]
    public string Version { get; set; } = "1.0.0";
    
    public DocumentStatus Status { get; set; } = DocumentStatus.Draft;
    
    public DateTime CreatedAt { get; set; }
    
    public DateTime? UpdatedAt { get; set; }
    
    [MaxLength(200)]
    public string? CreatedBy { get; set; }
    
    public Dictionary<string, object> Metadata { get; set; } = new();
    
    // Navigation property
    public virtual Project? Project { get; set; }
}

public enum DocumentStatus
{
    Draft,
    InReview,
    Approved,
    Published,
    Obsolete
}