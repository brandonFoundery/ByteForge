using System.ComponentModel.DataAnnotations;
using ByteForgeFrontend.Services;

namespace ByteForgeFrontend.Models;

public class SettingsViewModel
{
    public WorkflowSettings WorkflowSettings { get; set; } = new();
    public ExternalServicesConfiguration ApiConfiguration { get; set; } = new();
}

public class WorkflowSettingsUpdateModel
{
    [Range(1, 100, ErrorMessage = "Enrichment process count must be between 1 and 100")]
    public int EnrichmentProcessCount { get; set; } = 10;

    [Range(1, 100, ErrorMessage = "Vetting process count must be between 1 and 100")]
    public int VettingProcessCount { get; set; } = 10;

    [Range(1, 100, ErrorMessage = "Scoring process count must be between 1 and 100")]
    public int ScoringProcessCount { get; set; } = 10;

    [Range(1, 100, ErrorMessage = "CRM update process count must be between 1 and 100")]
    public int CrmUpdateProcessCount { get; set; } = 10;
}

public class ApiConfigurationUpdateModel
{
    public bool UseFakeData { get; set; } = true;

    // Google Settings
    public string? GoogleApiKey { get; set; }
    public string? GoogleCustomSearchEngineId { get; set; }

    // Facebook Settings
    public string? FacebookAccessToken { get; set; }
    public string? FacebookAppId { get; set; }
    public string? FacebookAppSecret { get; set; }

    // LinkedIn Settings
    public string? LinkedInAccessToken { get; set; }
    public string? LinkedInClientId { get; set; }
    public string? LinkedInClientSecret { get; set; }

    // YellowPages Settings
    public string? YellowPagesApiKey { get; set; }
    public string? YellowPagesPublisherId { get; set; }

    // Zoho Settings
    public string? ZohoAccessToken { get; set; }
    public string? ZohoRefreshToken { get; set; }
    public string? ZohoClientId { get; set; }
    public string? ZohoClientSecret { get; set; }
}