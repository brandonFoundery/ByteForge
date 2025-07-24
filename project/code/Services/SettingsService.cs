using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Models;

using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services;

public class SettingsService : ISettingsService
{
    private readonly ApplicationDbContext _context;
    private readonly IExternalApiConfigurationService _apiConfigService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<SettingsService> _logger;
    private WorkflowSettings? _cachedSettings;
    private DateTime _lastCacheUpdate = DateTime.MinValue;
    private readonly TimeSpan _cacheExpiry = TimeSpan.FromMinutes(5);

    public SettingsService(
        ApplicationDbContext context,
        IExternalApiConfigurationService apiConfigService,
        IConfiguration configuration,
        ILogger<SettingsService> logger)
    {
        _context = context;
        _apiConfigService = apiConfigService;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<WorkflowSettings> GetWorkflowSettingsAsync()
    {
        // Check cache first
        if (_cachedSettings != null && DateTime.UtcNow - _lastCacheUpdate < _cacheExpiry)
        {
            return _cachedSettings;
        }

        try
        {
            var settings = await _context.WorkflowSettings
                .OrderByDescending(s => s.Id)
                .FirstOrDefaultAsync();

            if (settings == null)
            {
                // Create default settings if none exist
                settings = new WorkflowSettings
                {
                    EnrichmentProcessCount = 10,
                    VettingProcessCount = 10,
                    ScoringProcessCount = 10,
                    CrmUpdateProcessCount = 10,
                    CreatedDate = DateTime.UtcNow,
                    ModifiedDate = DateTime.UtcNow
                };

                _context.WorkflowSettings.Add(settings);
                await _context.SaveChangesAsync();
                
                _logger.LogInformation("Created default workflow settings with all process counts set to 10");
            }

            // Update cache
            _cachedSettings = settings;
            _lastCacheUpdate = DateTime.UtcNow;

            return settings;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get workflow settings");
            
            // Return default settings if database fails
            return new WorkflowSettings
            {
                EnrichmentProcessCount = 10,
                VettingProcessCount = 10,
                ScoringProcessCount = 10,
                CrmUpdateProcessCount = 10
            };
        }
    }

    public async Task<WorkflowSettings> UpdateWorkflowSettingsAsync(WorkflowSettings settings)
    {
        try
        {
            var existingSettings = await _context.WorkflowSettings
                .OrderByDescending(s => s.Id)
                .FirstOrDefaultAsync();

            if (existingSettings == null)
            {
                // Create new settings
                settings.CreatedDate = DateTime.UtcNow;
                settings.ModifiedDate = DateTime.UtcNow;
                _context.WorkflowSettings.Add(settings);
                _logger.LogInformation("Created new workflow settings");
            }
            else
            {
                // Update existing settings
                existingSettings.EnrichmentProcessCount = settings.EnrichmentProcessCount;
                existingSettings.VettingProcessCount = settings.VettingProcessCount;
                existingSettings.ScoringProcessCount = settings.ScoringProcessCount;
                existingSettings.CrmUpdateProcessCount = settings.CrmUpdateProcessCount;
                existingSettings.ModifiedDate = DateTime.UtcNow;
                existingSettings.ModifiedBy = settings.ModifiedBy;
                existingSettings.Notes = settings.Notes;
                
                settings = existingSettings;
                _logger.LogInformation("Updated existing workflow settings");
            }

            await _context.SaveChangesAsync();

            // Update cache
            _cachedSettings = settings;
            _lastCacheUpdate = DateTime.UtcNow;

            _logger.LogInformation("Workflow settings saved successfully: " +
                "Enrichment={EnrichmentCount}, Vetting={VettingCount}, " +
                "Scoring={ScoringCount}, CrmUpdate={CrmCount}",
                settings.EnrichmentProcessCount,
                settings.VettingProcessCount,
                settings.ScoringProcessCount,
                settings.CrmUpdateProcessCount);

            return settings;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update workflow settings");
            throw;
        }
    }

    public async Task<ExternalServicesConfiguration> GetApiConfigurationAsync()
    {
        return await Task.FromResult(_apiConfigService.GetConfiguration());
    }

    public async Task UpdateApiConfigurationAsync(ExternalServicesConfiguration configuration)
    {
        try
        {
            // Update configuration values in memory
            var configSection = _configuration.GetSection("ExternalServices");
            
            // Update the configuration through IConfiguration
            // Note: This is for in-memory updates. For persistent updates,
            // you would need to update the actual configuration file or database
            configSection["UseFakeData"] = configuration.UseFakeData.ToString();
            configSection["Google:ApiKey"] = configuration.Google.ApiKey;
            configSection["Google:CustomSearchEngineId"] = configuration.Google.CustomSearchEngineId;
            configSection["Facebook:AccessToken"] = configuration.Facebook.AccessToken;
            configSection["Facebook:AppId"] = configuration.Facebook.AppId;
            configSection["Facebook:AppSecret"] = configuration.Facebook.AppSecret;
            configSection["LinkedIn:AccessToken"] = configuration.LinkedIn.AccessToken;
            configSection["LinkedIn:ClientId"] = configuration.LinkedIn.ClientId;
            configSection["LinkedIn:ClientSecret"] = configuration.LinkedIn.ClientSecret;
            configSection["YellowPages:ApiKey"] = configuration.YellowPages.ApiKey;
            configSection["YellowPages:PublisherId"] = configuration.YellowPages.PublisherId;
            configSection["Zoho:AccessToken"] = configuration.Zoho.AccessToken;
            configSection["Zoho:RefreshToken"] = configuration.Zoho.RefreshToken;
            configSection["Zoho:ClientId"] = configuration.Zoho.ClientId;
            configSection["Zoho:ClientSecret"] = configuration.Zoho.ClientSecret;

            _logger.LogInformation("API configuration updated successfully. UseFakeData={UseFakeData}", 
                configuration.UseFakeData);
            
            await Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update API configuration");
            throw;
        }
    }
}