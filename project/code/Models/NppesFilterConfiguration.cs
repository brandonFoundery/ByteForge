using System.ComponentModel.DataAnnotations;

using System;
namespace ByteForgeFrontend.Models;

public class NppesFilterConfiguration
{
    public int Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string Description { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string FilterType { get; set; } = "Specialty";
    
    [StringLength(1000)]
    public string FilterCriteria { get; set; } = string.Empty;
    
    public bool IsActive { get; set; } = true;
    
    public bool RequirePhoneNumber { get; set; } = false;
    
    [StringLength(100)]
    public string ConfigurationName { get; set; } = string.Empty;
    
    public bool IsDefault { get; set; } = false;
    
    public bool FilterByState { get; set; } = false;
    
    [StringLength(500)]
    public string? AllowedStates { get; set; }
    
    public bool FilterBySpecialty { get; set; } = false;
    
    [StringLength(1000)]
    public string? AllowedSpecialties { get; set; }
    
    public bool FilterByEntityType { get; set; } = false;
    
    [StringLength(500)]
    public string? AllowedEntityTypes { get; set; }
    
    public int MaxRecordsToProcess { get; set; } = 1000;
    
    [StringLength(200)]
    public string? CreatedBy { get; set; }
    
    [StringLength(500)]
    public string? Notes { get; set; }
    
    public int Priority { get; set; } = 0;
    
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;
    
    public DateTime? ModifiedDate { get; set; }
    
    [StringLength(200)]
    public string? ModifiedBy { get; set; }
}