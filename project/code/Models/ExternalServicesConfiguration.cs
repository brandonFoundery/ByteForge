using System;

namespace ByteForgeFrontend.Models;

public class ExternalServicesConfiguration
{
    public int Id { get; set; }
    
    public bool UseFakeData { get; set; } = true;
    
    public GoogleConfiguration Google { get; set; } = new();
    public FacebookConfiguration Facebook { get; set; } = new();
    public LinkedInConfiguration LinkedIn { get; set; } = new();
    public YellowPagesConfiguration YellowPages { get; set; } = new();
    public ZohoConfiguration Zoho { get; set; } = new();
    
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;
    public DateTime? ModifiedDate { get; set; }
    public string? ModifiedBy { get; set; }
}

public class GoogleConfiguration
{
    public string? ApiKey { get; set; }
    public string? CustomSearchEngineId { get; set; }
    public bool IsConfigured => !string.IsNullOrEmpty(ApiKey) && !string.IsNullOrEmpty(CustomSearchEngineId);
}

public class FacebookConfiguration
{
    public string? AccessToken { get; set; }
    public string? AppId { get; set; }
    public string? AppSecret { get; set; }
    public bool IsConfigured => !string.IsNullOrEmpty(AccessToken) && !string.IsNullOrEmpty(AppId);
}

public class LinkedInConfiguration
{
    public string? AccessToken { get; set; }
    public string? ClientId { get; set; }
    public string? ClientSecret { get; set; }
    public bool IsConfigured => !string.IsNullOrEmpty(AccessToken) && !string.IsNullOrEmpty(ClientId);
}

public class YellowPagesConfiguration
{
    public string? ApiKey { get; set; }
    public string? PublisherId { get; set; }
    public bool IsConfigured => !string.IsNullOrEmpty(ApiKey) && !string.IsNullOrEmpty(PublisherId);
}

public class ZohoConfiguration
{
    public string? AccessToken { get; set; }
    public string? RefreshToken { get; set; }
    public string? ClientId { get; set; }
    public string? ClientSecret { get; set; }
    public bool IsConfigured => !string.IsNullOrEmpty(AccessToken) && !string.IsNullOrEmpty(ClientId);
}