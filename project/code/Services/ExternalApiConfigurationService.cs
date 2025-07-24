using Microsoft.Extensions.Configuration;
using ByteForgeFrontend.Models;

namespace ByteForgeFrontend.Services;

public class ExternalApiConfigurationService : IExternalApiConfigurationService
{
    private readonly IConfiguration _configuration;

    public ExternalApiConfigurationService(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public ExternalServicesConfiguration GetConfiguration()
    {
        var config = new ExternalServicesConfiguration
        {
            UseFakeData = _configuration.GetValue<bool>("ExternalServices:UseFakeData", true),
            Google = new GoogleConfiguration
            {
                ApiKey = _configuration["ExternalServices:Google:ApiKey"],
                CustomSearchEngineId = _configuration["ExternalServices:Google:CustomSearchEngineId"]
            },
            Facebook = new FacebookConfiguration
            {
                AccessToken = _configuration["ExternalServices:Facebook:AccessToken"],
                AppId = _configuration["ExternalServices:Facebook:AppId"],
                AppSecret = _configuration["ExternalServices:Facebook:AppSecret"]
            },
            LinkedIn = new LinkedInConfiguration
            {
                AccessToken = _configuration["ExternalServices:LinkedIn:AccessToken"],
                ClientId = _configuration["ExternalServices:LinkedIn:ClientId"],
                ClientSecret = _configuration["ExternalServices:LinkedIn:ClientSecret"]
            },
            YellowPages = new YellowPagesConfiguration
            {
                ApiKey = _configuration["ExternalServices:YellowPages:ApiKey"],
                PublisherId = _configuration["ExternalServices:YellowPages:PublisherId"]
            },
            Zoho = new ZohoConfiguration
            {
                AccessToken = _configuration["ExternalServices:Zoho:AccessToken"],
                RefreshToken = _configuration["ExternalServices:Zoho:RefreshToken"],
                ClientId = _configuration["ExternalServices:Zoho:ClientId"],
                ClientSecret = _configuration["ExternalServices:Zoho:ClientSecret"]
            }
        };

        return config;
    }
}