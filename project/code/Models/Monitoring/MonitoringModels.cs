using System;
using System.Collections.Generic;

namespace ByteForgeFrontend.Models.Monitoring;

// Document Generation Models
public class DocumentGenerationStatus
{
    public string ProjectId { get; set; } = string.Empty;
    public Dictionary<string, DocumentProgress> Documents { get; set; } = new();
    public int OverallProgress { get; set; }
    public DateTime StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public bool IsComplete { get; set; }
    public bool HasErrors { get; set; }
}

public class DocumentProgress
{
    public string DocumentType { get; set; } = string.Empty;
    public int Progress { get; set; }
    public string Status { get; set; } = string.Empty;
    public DateTime StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public string? Error { get; set; }
    public List<string> Milestones { get; set; } = new();
}

public class DocumentGenerationProgress
{
    public string ProjectId { get; set; } = string.Empty;
    public string DocumentType { get; set; } = string.Empty;
    public int Progress { get; set; }
    public string Status { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

// AI Agent Models
public class AgentStatus
{
    public string AgentId { get; set; } = string.Empty;
    public string AgentType { get; set; } = string.Empty;
    public string ProjectId { get; set; } = string.Empty;
    public AgentState State { get; set; }
    public string? CurrentTask { get; set; }
    public DateTime StartedAt { get; set; }
    public DateTime LastHeartbeat { get; set; }
    public int TasksCompleted { get; set; }
    public int TasksFailed { get; set; }
}

public enum AgentState
{
    Idle,
    Starting,
    Running,
    Paused,
    Stopping,
    Stopped,
    Failed,
    Completed
}

public class AgentHealthReport
{
    public string AgentId { get; set; } = string.Empty;
    public string AgentType { get; set; } = string.Empty;
    public bool IsHealthy { get; set; }
    public double CpuUsage { get; set; }
    public double MemoryUsage { get; set; }
    public int RequestsPerMinute { get; set; }
    public double AverageResponseTime { get; set; }
    public int ErrorCount { get; set; }
    public DateTime LastError { get; set; }
    public string? LastErrorMessage { get; set; }
    public Dictionary<string, object> CustomMetrics { get; set; } = new();
}

public class AgentMetrics
{
    public double CpuUsage { get; set; }
    public double MemoryUsage { get; set; }
    public int RequestCount { get; set; }
    public double ResponseTime { get; set; }
    public Dictionary<string, object> CustomMetrics { get; set; } = new();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

// Project Models
public class ProjectOverview
{
    public string ProjectId { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
    public string ProjectType { get; set; } = string.Empty;
    public int OverallProgress { get; set; }
    public ProjectPhase CurrentPhase { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? EstimatedCompletion { get; set; }
    public List<PhaseProgress> Phases { get; set; } = new();
    public Dictionary<string, int> DocumentProgress { get; set; } = new();
    public List<string> ActiveAgents { get; set; } = new();
    public bool HasErrors { get; set; }
}

public enum ProjectPhase
{
    Initialization,
    RequirementsGathering,
    DocumentGeneration,
    CodeGeneration,
    Testing,
    Deployment,
    Completed
}

public class PhaseProgress
{
    public ProjectPhase Phase { get; set; }
    public int Progress { get; set; }
    public string Status { get; set; } = string.Empty;
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
}

public class ProjectStatus
{
    public string ProjectId { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public int Progress { get; set; }
    public DateTime LastUpdated { get; set; }
}

public class ProjectUpdate
{
    public string ProjectId { get; set; } = string.Empty;
    public string UpdateType { get; set; } = string.Empty;
    public string Component { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public int? Progress { get; set; }
    public Dictionary<string, object> Data { get; set; } = new();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

// System Models
public class SystemMetrics
{
    public double CpuUsage { get; set; }
    public double MemoryUsage { get; set; }
    public long DiskSpaceUsed { get; set; }
    public long DiskSpaceAvailable { get; set; }
    public int ActiveProjects { get; set; }
    public int ActiveAgents { get; set; }
    public int QueuedTasks { get; set; }
    public double SystemLoad { get; set; }
    public Dictionary<string, ServiceHealth> ServiceHealth { get; set; } = new();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class ServiceHealth
{
    public string ServiceName { get; set; } = string.Empty;
    public bool IsHealthy { get; set; }
    public DateTime LastCheck { get; set; }
    public string? ErrorMessage { get; set; }
}

public class ResourceUsage
{
    public List<ResourceSnapshot> CpuHistory { get; set; } = new();
    public List<ResourceSnapshot> MemoryHistory { get; set; } = new();
    public List<ResourceSnapshot> DiskHistory { get; set; } = new();
    public List<ResourceSnapshot> NetworkHistory { get; set; } = new();
}

public class ResourceSnapshot
{
    public double Value { get; set; }
    public DateTime Timestamp { get; set; }
}

public class SystemEvent
{
    public string EventType { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public EventSeverity Severity { get; set; }
    public Dictionary<string, object> Data { get; set; } = new();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public enum EventSeverity
{
    Debug,
    Info,
    Warning,
    Error,
    Critical
}

// Analytics Models
public class DocumentGenerationAnalytics
{
    public int TotalDocumentsGenerated { get; set; }
    public int SuccessfulGenerations { get; set; }
    public int FailedGenerations { get; set; }
    public double SuccessRate { get; set; }
    public double AverageGenerationTime { get; set; }
    public Dictionary<string, int> DocumentTypeCounts { get; set; } = new();
    public Dictionary<string, double> DocumentTypeAverageTimes { get; set; } = new();
    public List<GenerationTrend> DailyTrends { get; set; } = new();
}

public class GenerationTrend
{
    public DateTime Date { get; set; }
    public int Count { get; set; }
    public double AverageTime { get; set; }
    public double SuccessRate { get; set; }
}

public class AgentPerformanceAnalytics
{
    public Dictionary<string, AgentPerformance> AgentPerformance { get; set; } = new();
    public double OverallSuccessRate { get; set; }
    public double AverageTaskDuration { get; set; }
    public int TotalTasksCompleted { get; set; }
    public int TotalTasksFailed { get; set; }
    public List<AgentEfficiencyTrend> EfficiencyTrends { get; set; } = new();
}

public class AgentPerformance
{
    public string AgentType { get; set; } = string.Empty;
    public int TasksCompleted { get; set; }
    public int TasksFailed { get; set; }
    public double SuccessRate { get; set; }
    public double AverageTaskDuration { get; set; }
    public double AverageCpuUsage { get; set; }
    public double AverageMemoryUsage { get; set; }
}

public class AgentEfficiencyTrend
{
    public DateTime Date { get; set; }
    public Dictionary<string, double> AgentEfficiency { get; set; } = new();
}

public class SystemHealthReport
{
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    public string OverallHealth { get; set; } = string.Empty;
    public SystemMetrics CurrentMetrics { get; set; } = new();
    public List<SystemIssue> Issues { get; set; } = new();
    public List<SystemRecommendation> Recommendations { get; set; } = new();
    public Dictionary<string, ServiceHealthHistory> ServiceHealthHistory { get; set; } = new();
}

public class SystemIssue
{
    public string IssueType { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public EventSeverity Severity { get; set; }
    public DateTime DetectedAt { get; set; }
    public bool IsResolved { get; set; }
}

public class SystemRecommendation
{
    public string Category { get; set; } = string.Empty;
    public string Recommendation { get; set; } = string.Empty;
    public string Impact { get; set; } = string.Empty;
    public int Priority { get; set; }
}

public class ServiceHealthHistory
{
    public string ServiceName { get; set; } = string.Empty;
    public double Uptime { get; set; }
    public int ErrorCount { get; set; }
    public List<ServiceIncident> Incidents { get; set; } = new();
}

public class ServiceIncident
{
    public DateTime StartTime { get; set; }
    public DateTime? EndTime { get; set; }
    public string Description { get; set; } = string.Empty;
    public string Resolution { get; set; } = string.Empty;
}

// File System Monitoring
public class FileSystemChangeEventArgs : EventArgs
{
    public string Path { get; set; } = string.Empty;
    public FileSystemChangeType ChangeType { get; set; }
    public string? OldPath { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public enum FileSystemChangeType
{
    Created,
    Modified,
    Deleted,
    Renamed
}

public class AnalyticsData
{
    public string Period { get; set; } = string.Empty;
    public int TotalDocumentsGenerated { get; set; }
    public int SuccessfulGenerations { get; set; }
    public int FailedGenerations { get; set; }
    public double AverageGenerationTime { get; set; }
    public Dictionary<string, int> DocumentTypeBreakdown { get; set; } = new();
    public Dictionary<string, double> AgentPerformance { get; set; } = new();
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
}

public class SystemStatus
{
    public int ActiveMonitors { get; set; }
    public int TotalEvents { get; set; }
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    public bool IsHealthy { get; set; } = true;
}