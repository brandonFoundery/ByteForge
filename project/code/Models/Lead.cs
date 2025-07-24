using System.ComponentModel.DataAnnotations;

using System;
namespace ByteForgeFrontend.Models;

public class Lead
{
    public int Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;
    
    [Required]
    [EmailAddress]
    [StringLength(255)]
    public string Email { get; set; } = string.Empty;
    
    [StringLength(20)]
    public string? Phone { get; set; }
    
    [StringLength(100)]
    public string? Company { get; set; }
    
    [Required]
    [StringLength(50)]
    public string Source { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string Status { get; set; } = "New";
    
    public int? Score { get; set; }
    
    public bool IsEnriched { get; set; }
    
    public bool IsVetted { get; set; }
    
    public bool IsUpsertedToZoho { get; set; }
    
    [StringLength(100)]
    public string? WorkflowInstanceId { get; set; }
    
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;
    
    public DateTime? ModifiedDate { get; set; }
    
    [StringLength(500)]
    public string? Notes { get; set; }
}