using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.DocumentGenerators;

public interface IDocumentGenerator<TRequest, TResponse> 
    where TRequest : DocumentGenerationRequestBase
    where TResponse : DocumentGenerationResponseBase
{
    Task<TResponse> GenerateAsync(TRequest request, CancellationToken cancellationToken = default);
    string DocumentType { get; }
}

public abstract class DocumentGenerationRequestBase
{
    public string ProjectName { get; set; } = string.Empty;
    public string? ProjectDescription { get; set; }
    public Dictionary<string, object> Dependencies { get; set; } = new();
    public Dictionary<string, object> AdditionalContext { get; set; } = new();
}

public abstract class DocumentGenerationResponseBase
{
    public bool Success { get; set; }
    public string Content { get; set; } = string.Empty;
    public string? Error { get; set; }
    public List<string> ValidationErrors { get; set; } = new();
    public List<string> ValidationWarnings { get; set; } = new();
    public List<string> RequirementIds { get; set; } = new();
    public Dictionary<string, object> Metadata { get; set; } = new();
    public DateTime GeneratedAt { get; set; }
}

// BRD specific types
public class BRDGenerationRequest : DocumentGenerationRequestBase
{
    public string? ClientRequirements { get; set; }
    public List<string> Stakeholders { get; set; } = new();
    public List<string> BusinessConstraints { get; set; } = new();
    public string? BusinessContext { get; set; }
}

public class BRDGenerationResponse : DocumentGenerationResponseBase
{
    public List<string> BusinessObjectives { get; set; } = new();
    public Dictionary<string, object> StakeholderRoles { get; set; } = new();
}

// PRD specific types
public class PRDGenerationRequest : DocumentGenerationRequestBase
{
    public string? MarketAnalysis { get; set; }
    public List<string> TargetUsers { get; set; } = new();
    public List<string> CompetitorProducts { get; set; } = new();
    public string? ProductVision { get; set; }
}

public class PRDGenerationResponse : DocumentGenerationResponseBase
{
    public List<string> ProductFeatures { get; set; } = new();
    public List<string> UserStories { get; set; } = new();
}

// FRD specific types
public class FRDGenerationRequest : DocumentGenerationRequestBase
{
    public List<string> FunctionalAreas { get; set; } = new();
    public bool IncludeUseCases { get; set; } = true;
    public bool IncludeDataFlow { get; set; } = true;
}

public class FRDGenerationResponse : DocumentGenerationResponseBase
{
    public List<string> FunctionalRequirements { get; set; } = new();
    public List<string> UseCases { get; set; } = new();
}

// TRD specific types
public class TRDGenerationRequest : DocumentGenerationRequestBase
{
    public List<string> TechnologyStack { get; set; } = new();
    public List<string> IntegrationPoints { get; set; } = new();
    public bool IncludeArchitectureDiagram { get; set; } = true;
    public string? DeploymentEnvironment { get; set; }
}

public class TRDGenerationResponse : DocumentGenerationResponseBase
{
    public List<string> TechnicalRequirements { get; set; } = new();
    public List<string> ArchitectureComponents { get; set; } = new();
    public Dictionary<string, object> TechnologyChoices { get; set; } = new();
}