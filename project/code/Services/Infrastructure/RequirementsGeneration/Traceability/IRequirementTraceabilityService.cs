using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.Traceability;

public interface IRequirementTraceabilityService
{
    Task<TraceabilityMatrixResponse> GenerateTraceabilityMatrixAsync(Guid projectId, CancellationToken cancellationToken = default);
    Task<ChangeImpactResponse> AnalyzeChangeImpactAsync(ChangeImpactRequest request, CancellationToken cancellationToken = default);
    Task<TraceabilityValidationResponse> ValidateTraceabilityAsync(Guid projectId, CancellationToken cancellationToken = default);
    Task<RequirementDetailsResponse> GetRequirementDetailsAsync(Guid projectId, string requirementId, CancellationToken cancellationToken = default);
    Task<TraceabilityExportResponse> ExportTraceabilityMatrixAsync(Guid projectId, ExportFormat format, CancellationToken cancellationToken = default);
    Task<TraceabilityGapAnalysisResponse> AnalyzeTraceabilityGapsAsync(Guid projectId, CancellationToken cancellationToken = default);
}

// Request/Response models
public class TraceabilityMatrixResponse
{
    public bool Success { get; set; }
    public string? Error { get; set; }
    public RequirementTraceabilityMatrix Matrix { get; set; } = new();
    public Dictionary<string, int> Statistics { get; set; } = new();
}

public class RequirementTraceabilityMatrix
{
    private readonly Dictionary<string, HashSet<string>> _forwardLinks = new();
    private readonly Dictionary<string, HashSet<string>> _backwardLinks = new();
    private readonly Dictionary<string, RequirementInfo> _requirements = new();

    public void AddRequirement(string id, string type, string description)
    {
        _requirements[id] = new RequirementInfo { Id = id, Type = type, Description = description };
    }

    public void AddLink(string sourceId, string targetId, string linkType = "Implements")
    {
        if (!_forwardLinks.ContainsKey(sourceId))
            _forwardLinks[sourceId] = new HashSet<string>();
        
        if (!_backwardLinks.ContainsKey(targetId))
            _backwardLinks[targetId] = new HashSet<string>();

        _forwardLinks[sourceId].Add(targetId);
        _backwardLinks[targetId].Add(sourceId);
    }

    public IEnumerable<string> GetLinksForRequirement(string requirementId)
    {
        return _forwardLinks.TryGetValue(requirementId, out var links) 
            ? links 
            : Enumerable.Empty<string>();
    }

    public IEnumerable<string> GetSourceRequirements(string requirementId)
    {
        return _backwardLinks.TryGetValue(requirementId, out var sources) 
            ? sources 
            : Enumerable.Empty<string>();
    }

    public IEnumerable<RequirementInfo> GetAllRequirements()
    {
        return _requirements.Values;
    }

    public RequirementInfo? GetRequirement(string id)
    {
        return _requirements.TryGetValue(id, out var req) ? req : null;
    }
}

public class RequirementInfo
{
    public string Id { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
}

public class ChangeImpactRequest
{
    public Guid ProjectId { get; set; }
    public string ChangedRequirementId { get; set; } = string.Empty;
    public string ChangeDescription { get; set; } = string.Empty;
    public ChangeType ChangeType { get; set; } = ChangeType.Modification;
}

public enum ChangeType
{
    Addition,
    Modification,
    Deletion
}

public class ChangeImpactResponse
{
    public bool Success { get; set; }
    public string? Error { get; set; }
    public string SourceRequirement { get; set; } = string.Empty;
    public List<string> DirectlyAffectedRequirements { get; set; } = new();
    public List<string> IndirectlyAffectedRequirements { get; set; } = new();
    public ImpactSeverity Severity { get; set; }
    public List<string> AffectedDocuments { get; set; } = new();
    public Dictionary<string, string> ImpactDetails { get; set; } = new();
}

public enum ImpactSeverity
{
    Low,
    Medium,
    High,
    Critical
}

public class TraceabilityValidationResponse
{
    public bool Success { get; set; }
    public bool IsValid { get; set; }
    public string? Error { get; set; }
    public List<string> OrphanedRequirements { get; set; } = new();
    public List<string> UnimplementedRequirements { get; set; } = new();
    public List<BrokenLink> BrokenLinks { get; set; } = new();
    public List<string> ValidationMessages { get; set; } = new();
}

public class BrokenLink
{
    public string From { get; set; } = string.Empty;
    public string To { get; set; } = string.Empty;
    public string Reason { get; set; } = string.Empty;
}

public class RequirementDetailsResponse
{
    public bool Success { get; set; }
    public string? Error { get; set; }
    public string RequirementId { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string DocumentType { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public List<string> ImplementedBy { get; set; } = new();
    public List<string> Implements { get; set; } = new();
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public class TraceabilityExportResponse
{
    public bool Success { get; set; }
    public string? Error { get; set; }
    public string Content { get; set; } = string.Empty;
    public ExportFormat Format { get; set; }
    public string FileName { get; set; } = string.Empty;
}

public enum ExportFormat
{
    CSV,
    JSON,
    HTML,
    Markdown
}

public class TraceabilityGapAnalysisResponse
{
    public bool Success { get; set; }
    public string? Error { get; set; }
    public List<string> RequirementsWithoutUpstreamLinks { get; set; } = new();
    public List<string> RequirementsWithoutDownstreamLinks { get; set; } = new();
    public double UpstreamCoveragePercentage { get; set; }
    public double DownstreamCoveragePercentage { get; set; }
    public Dictionary<string, List<string>> GapsByDocumentType { get; set; } = new();
}