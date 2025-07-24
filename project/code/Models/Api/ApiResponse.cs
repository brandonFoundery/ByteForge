using System.ComponentModel.DataAnnotations;

using System;
using System.Collections.Generic;
namespace ByteForgeFrontend.Models.Api;

public class ApiResponse<T>
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public T? Data { get; set; }
    public string? Error { get; set; }
    public IEnumerable<string>? Errors { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class ApiResponse
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public string? Error { get; set; }
    public IEnumerable<string>? Errors { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class PagedResult<T>
{
    public IEnumerable<T> Items { get; set; } = new List<T>();
    public int TotalCount { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
    public int TotalPages { get; set; }
    public bool HasNextPage => Page < TotalPages;
    public bool HasPreviousPage => Page > 1;
}

public class LeadDto
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string? Phone { get; set; }
    public string? Company { get; set; }
    public string Source { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public int? Score { get; set; }
    public bool IsEnriched { get; set; }
    public bool IsVetted { get; set; }
    public bool IsUpsertedToZoho { get; set; }
    public string? WorkflowInstanceId { get; set; }
    public DateTime CreatedDate { get; set; }
    public DateTime? ModifiedDate { get; set; }
}

public class CreateLeadRequest
{
    [Required]
    [StringLength(100, MinimumLength = 1)]
    public string Name { get; set; } = string.Empty;

    [Required]
    [EmailAddress]
    [StringLength(255)]
    public string Email { get; set; } = string.Empty;

    [RegularExpression(@"^\d{3}-\d{3}-\d{4}$|^$", ErrorMessage = "Phone format should be XXX-XXX-XXXX")]
    [StringLength(20)]
    public string? Phone { get; set; }

    [StringLength(100)]
    public string? Company { get; set; }

    [StringLength(50)]
    public string? Source { get; set; }
}

public class UpdateLeadRequest
{
    [StringLength(100, MinimumLength = 1)]
    public string? Name { get; set; }

    [EmailAddress]
    [StringLength(255)]
    public string? Email { get; set; }

    [RegularExpression(@"^\d{3}-\d{3}-\d{4}$|^$", ErrorMessage = "Phone format should be XXX-XXX-XXXX")]
    [StringLength(20)]
    public string? Phone { get; set; }

    [StringLength(100)]
    public string? Company { get; set; }

    [StringLength(50)]
    public string? Status { get; set; }
}

public class WorkflowResult
{
    public string WorkflowInstanceId { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}

public class DashboardMetrics
{
    public int TotalLeads { get; set; }
    public int TodayLeads { get; set; }
    public int WeekLeads { get; set; }
    public Dictionary<string, int> StatusCounts { get; set; } = new();
    public Dictionary<string, int> SourceCounts { get; set; } = new();
    public int EnrichedLeads { get; set; }
    public int VettedLeads { get; set; }
    public int ZohoLeads { get; set; }
    public int AverageScore { get; set; }
    public DateTime LastUpdated { get; set; }
}

public class FilterOptions
{
    public List<string> Sources { get; set; } = new();
    public List<string> Statuses { get; set; } = new();
}