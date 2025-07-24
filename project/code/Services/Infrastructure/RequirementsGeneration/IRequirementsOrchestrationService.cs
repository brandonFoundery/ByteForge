using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;

public interface IRequirementsOrchestrationService
{
    Task<GenerateRequirementsResponse> GenerateRequirementsAsync(GenerateRequirementsRequest request, CancellationToken cancellationToken = default);
    Task<RequirementsGenerationProgress> GetGenerationProgressAsync(Guid projectId, CancellationToken cancellationToken = default);
}

public class GenerateRequirementsRequest
{
    public Guid ProjectId { get; set; }
    public string ProjectName { get; set; } = string.Empty;
    public string? ProjectDescription { get; set; }
    public string? ClientRequirements { get; set; }
    public Dictionary<string, object>? AdditionalContext { get; set; }
}

public class GenerateRequirementsResponse
{
    public bool Success { get; set; }
    public Dictionary<string, string> GeneratedDocuments { get; set; } = new();
    public List<string> Errors { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
    public DateTime StartedAt { get; set; }
    public DateTime CompletedAt { get; set; }
    public TimeSpan TotalDuration { get; set; }
}

public class RequirementsGenerationProgress
{
    public Guid ProjectId { get; set; }
    public RequirementsGenerationStatus Status { get; set; }
    public int OverallProgress { get; set; } // 0-100
    public Dictionary<string, DocumentGenerationProgress> DocumentProgress { get; set; } = new();
    public DateTime? StartedAt { get; set; }
    public DateTime? LastUpdatedAt { get; set; }
    public string? CurrentActivity { get; set; }
}

public class DocumentGenerationProgress
{
    public string DocumentType { get; set; } = string.Empty;
    public DocumentGenerationStatus Status { get; set; }
    public int Progress { get; set; } // 0-100
    public string? Error { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
}

public enum RequirementsGenerationStatus
{
    NotStarted,
    InProgress,
    Completed,
    Failed,
    PartiallyCompleted
}

public enum DocumentGenerationStatus
{
    Pending,
    InProgress,
    Completed,
    Failed,
    Skipped
}