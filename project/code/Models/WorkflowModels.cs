using System;
using System.Collections.Generic;

namespace ByteForgeFrontend.Models;

public class WorkflowHealthStatus
{
    public DateTime Timestamp { get; set; }
    public int ActiveWorkflows { get; set; }
    public int StalledWorkflows { get; set; }
    public int TotalExecutionsLast24Hours { get; set; }
    public int SuccessfulExecutionsLast24Hours { get; set; }
    public double SuccessRateLast24Hours { get; set; }
    public int TotalExecutionsLastHour { get; set; }
    public int SuccessfulExecutionsLastHour { get; set; }
    public double SuccessRateLastHour { get; set; }
    public double AverageProcessingTimeSeconds { get; set; }
    public bool IsHealthy { get; set; }
}

public class WorkflowExecution
{
    public int LeadId { get; set; }
    public string WorkflowType { get; set; } = default!;
    public DateTime StartTime { get; set; }
    public DateTime? EndTime { get; set; }
    public TimeSpan? Duration { get; set; }
    public bool IsSuccessful { get; set; }
    public List<ActivityExecution> Activities { get; set; } = new();
}

public class ActivityExecution
{
    public string ActivityName { get; set; } = default!;
    public DateTime StartTime { get; set; }
    public DateTime? EndTime { get; set; }
    public TimeSpan? Duration { get; set; }
    public bool IsSuccessful { get; set; }
    public string? ErrorMessage { get; set; }
}