using System.ComponentModel.DataAnnotations;

using System;
using System.Collections.Generic;
namespace ByteForgeFrontend.Models.ProjectManagement;

public class Project
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = string.Empty;
    
    [MaxLength(1000)]
    public string? Description { get; set; }
    
    [MaxLength(50)]
    public string? TemplateId { get; set; }
    
    public string? ClientRequirements { get; set; }
    
    public ProjectStatus Status { get; set; } = ProjectStatus.Created;
    
    public DateTime CreatedAt { get; set; }
    
    public DateTime? UpdatedAt { get; set; }
    
    [MaxLength(200)]
    public string? CreatedBy { get; set; }
    
    // Multi-tenant support
    [Required]
    public string TenantId { get; set; } = string.Empty;
    
    public string? UserId { get; set; }
    
    public Dictionary<string, object> Metadata { get; set; } = new();
    
    // Navigation properties
    public virtual ICollection<ProjectDocument> Documents { get; set; } = new List<ProjectDocument>();
}

public enum ProjectStatus
{
    Created,
    InProgress,
    RequirementsComplete,
    DevelopmentInProgress,
    Testing,
    Completed,
    OnHold,
    Cancelled
}