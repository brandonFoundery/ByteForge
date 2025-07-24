using System.ComponentModel.DataAnnotations;

using System;
using System.Collections.Generic;
namespace ByteForgeFrontend.Models;

public class JobScheduleSettings
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string JobName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string DisplayName { get; set; } = string.Empty;
    
    [Required]
    public string CronExpression { get; set; } = string.Empty;
    
    [Required]
    [StringLength(200)]
    public string Description { get; set; } = string.Empty;
    
    public bool IsEnabled { get; set; } = true;
    
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;
    public DateTime ModifiedDate { get; set; } = DateTime.UtcNow;
    
    public string? ModifiedBy { get; set; }
    public string? Notes { get; set; }
}

public class JobScheduleUpdateModel
{
    [Required]
    public string JobName { get; set; } = string.Empty;
    
    [Required]
    public string CronExpression { get; set; } = string.Empty;
    
    public bool IsEnabled { get; set; } = true;
    
    public string? Notes { get; set; }
}

public class JobScheduleViewModel
{
    public string JobName { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string CronExpression { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public bool IsEnabled { get; set; }
    public string FriendlySchedule { get; set; } = string.Empty;
    public DateTime LastModified { get; set; }
    public string? ModifiedBy { get; set; }
}

public class JobSchedulingSettingsViewModel
{
    public List<JobScheduleViewModel> Jobs { get; set; } = new();
    public bool AllowScheduleChanges { get; set; } = true;
}