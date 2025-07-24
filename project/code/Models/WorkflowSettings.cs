using System.ComponentModel.DataAnnotations;

using System;
using System.Collections.Generic;
namespace ByteForgeFrontend.Models;

public class WorkflowSettings
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(100)]
    public string WorkflowName { get; set; } = "Default";
    
    [Required]
    [MaxLength(50)]
    public string WorkflowType { get; set; } = "Generic";
    
    [Range(1, 100, ErrorMessage = "Max concurrent processes must be between 1 and 100")]
    public int MaxConcurrentProcesses { get; set; } = 10;
    
    [Range(1, 100, ErrorMessage = "Enrichment process count must be between 1 and 100")]
    public int EnrichmentProcessCount { get; set; } = 10;
    
    [Range(1, 100, ErrorMessage = "Vetting process count must be between 1 and 100")]
    public int VettingProcessCount { get; set; } = 10;
    
    [Range(1, 100, ErrorMessage = "Scoring process count must be between 1 and 100")]
    public int ScoringProcessCount { get; set; } = 10;
    
    [Range(1, 100, ErrorMessage = "CRM update process count must be between 1 and 100")]
    public int CrmUpdateProcessCount { get; set; } = 10;
    
    [Range(1, 3600, ErrorMessage = "Timeout must be between 1 and 3600 seconds")]
    public int TimeoutSeconds { get; set; } = 300;
    
    [Range(0, 10, ErrorMessage = "Retry count must be between 0 and 10")]
    public int RetryCount { get; set; } = 3;
    
    public bool IsEnabled { get; set; } = true;
    
    public Dictionary<string, object> CustomSettings { get; set; } = new();
    
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;
    public DateTime ModifiedDate { get; set; } = DateTime.UtcNow;
    
    public string? ModifiedBy { get; set; }
    public string? Notes { get; set; }
}