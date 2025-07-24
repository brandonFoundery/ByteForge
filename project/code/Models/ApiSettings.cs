namespace ByteForgeFrontend.Models;

public class GoogleApiSettings
{
    public string? ApiKey { get; set; }
    public string? CustomSearchEngineId { get; set; }
    public string PlacesApiUrl { get; set; } = "https://maps.googleapis.com/maps/api/place";
    public string CustomSearchUrl { get; set; } = "https://www.googleapis.com/customsearch/v1";
    public bool IsConfigured => !string.IsNullOrEmpty(ApiKey) && !string.IsNullOrEmpty(CustomSearchEngineId);
}

public class FacebookApiSettings
{
    public string? AccessToken { get; set; }
    public string? AppId { get; set; }
    public string? AppSecret { get; set; }
    public string GraphApiUrl { get; set; } = "https://graph.facebook.com";
    public bool IsConfigured => !string.IsNullOrEmpty(AccessToken) && !string.IsNullOrEmpty(AppId);
}

public class LinkedInApiSettings
{
    public string? AccessToken { get; set; }
    public string? ClientId { get; set; }
    public string? ClientSecret { get; set; }
    public string ApiUrl { get; set; } = "https://api.linkedin.com/v2";
    public bool IsConfigured => !string.IsNullOrEmpty(AccessToken) && !string.IsNullOrEmpty(ClientId);
}

public class YellowPagesApiSettings
{
    public string? ApiKey { get; set; }
    public string? PublisherId { get; set; }
    public string ApiUrl { get; set; } = "https://api.yellowapi.com";
    public bool IsConfigured => !string.IsNullOrEmpty(ApiKey) && !string.IsNullOrEmpty(PublisherId);
}

public class ZohoApiSettings
{
    public string? AccessToken { get; set; }
    public string? RefreshToken { get; set; }
    public string? ClientId { get; set; }
    public string? ClientSecret { get; set; }
    public string ApiUrl { get; set; } = "https://www.zohoapis.com/crm/v2";
    public bool IsConfigured => !string.IsNullOrEmpty(AccessToken) && !string.IsNullOrEmpty(ClientId);
}