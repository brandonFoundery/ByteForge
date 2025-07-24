using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using ByteForgeFrontend.Models;
using ByteForgeFrontend.Services;
using System.ComponentModel.DataAnnotations;

using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers;

[Authorize]
public class SettingsController : Controller
{
    private readonly ISettingsService _settingsService;
    private readonly ILogger<SettingsController> _logger;

    public SettingsController(
        ISettingsService settingsService,
        ILogger<SettingsController> logger)
    {
        _settingsService = settingsService;
        _logger = logger;
    }

    [HttpGet]
    public async Task<IActionResult> Index()
    {
        try
        {
            var workflowSettings = await _settingsService.GetWorkflowSettingsAsync();
            var apiConfiguration = await _settingsService.GetApiConfigurationAsync();

            var viewModel = new SettingsViewModel
            {
                WorkflowSettings = workflowSettings,
                ApiConfiguration = apiConfiguration
            };

            return View(viewModel);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load settings page");
            TempData["Error"] = "Failed to load settings. Please try again.";
            return RedirectToAction("Index", "Home");
        }
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> UpdateWorkflowSettings(WorkflowSettingsUpdateModel model)
    {
        if (!ModelState.IsValid)
        {
            return Json(new { success = false, message = "Invalid input. Please check your values and try again." });
        }

        try
        {
            var settings = new WorkflowSettings
            {
                EnrichmentProcessCount = model.EnrichmentProcessCount,
                VettingProcessCount = model.VettingProcessCount,
                ScoringProcessCount = model.ScoringProcessCount,
                CrmUpdateProcessCount = model.CrmUpdateProcessCount,
                ModifiedBy = User.Identity?.Name ?? "System"
            };

            await _settingsService.UpdateWorkflowSettingsAsync(settings);

            _logger.LogInformation("Workflow settings updated by {User}: " +
                "Enrichment={EnrichmentCount}, Vetting={VettingCount}, " +
                "Scoring={ScoringCount}, CrmUpdate={CrmCount}",
                User.Identity?.Name,
                settings.EnrichmentProcessCount,
                settings.VettingProcessCount,
                settings.ScoringProcessCount,
                settings.CrmUpdateProcessCount);

            return Json(new { success = true, message = "Workflow settings updated successfully!" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update workflow settings for user {User}", User.Identity?.Name);
            return Json(new { success = false, message = "Failed to update workflow settings. Please try again." });
        }
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> UpdateApiKeys(ApiConfigurationUpdateModel model)
    {
        if (!ModelState.IsValid)
        {
            return Json(new { success = false, message = "Invalid API configuration. Please check your values and try again." });
        }

        try
        {
            var configuration = new ExternalServicesConfiguration
            {
                UseFakeData = model.UseFakeData,
                Google = new GoogleConfiguration
                {
                    ApiKey = model.GoogleApiKey,
                    CustomSearchEngineId = model.GoogleCustomSearchEngineId
                },
                Facebook = new FacebookConfiguration
                {
                    AccessToken = model.FacebookAccessToken,
                    AppId = model.FacebookAppId,
                    AppSecret = model.FacebookAppSecret
                },
                LinkedIn = new LinkedInConfiguration
                {
                    AccessToken = model.LinkedInAccessToken,
                    ClientId = model.LinkedInClientId,
                    ClientSecret = model.LinkedInClientSecret
                },
                YellowPages = new YellowPagesConfiguration
                {
                    ApiKey = model.YellowPagesApiKey,
                    PublisherId = model.YellowPagesPublisherId
                },
                Zoho = new ZohoConfiguration
                {
                    AccessToken = model.ZohoAccessToken,
                    RefreshToken = model.ZohoRefreshToken,
                    ClientId = model.ZohoClientId,
                    ClientSecret = model.ZohoClientSecret
                }
            };

            await _settingsService.UpdateApiConfigurationAsync(configuration);

            _logger.LogInformation("API configuration updated by {User}. UseFakeData={UseFakeData}",
                User.Identity?.Name, configuration.UseFakeData);

            return Json(new { success = true, message = "API configuration updated successfully!" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update API configuration for user {User}", User.Identity?.Name);
            return Json(new { success = false, message = "Failed to update API configuration. Please try again." });
        }
    }

    [HttpGet]
    public async Task<IActionResult> GetCurrentSettings()
    {
        try
        {
            var workflowSettings = await _settingsService.GetWorkflowSettingsAsync();
            var apiConfiguration = await _settingsService.GetApiConfigurationAsync();

            return Json(new
            {
                success = true,
                workflowSettings = new
                {
                    enrichmentProcessCount = workflowSettings.EnrichmentProcessCount,
                    vettingProcessCount = workflowSettings.VettingProcessCount,
                    scoringProcessCount = workflowSettings.ScoringProcessCount,
                    crmUpdateProcessCount = workflowSettings.CrmUpdateProcessCount,
                    lastModified = workflowSettings.ModifiedDate
                },
                apiConfiguration = new
                {
                    useFakeData = apiConfiguration.UseFakeData,
                    google = new
                    {
                        isConfigured = apiConfiguration.Google.IsConfigured,
                        hasApiKey = !string.IsNullOrWhiteSpace(apiConfiguration.Google.ApiKey)
                    },
                    facebook = new
                    {
                        isConfigured = apiConfiguration.Facebook.IsConfigured,
                        hasAccessToken = !string.IsNullOrWhiteSpace(apiConfiguration.Facebook.AccessToken)
                    },
                    linkedIn = new
                    {
                        isConfigured = apiConfiguration.LinkedIn.IsConfigured,
                        hasAccessToken = !string.IsNullOrWhiteSpace(apiConfiguration.LinkedIn.AccessToken)
                    },
                    yellowPages = new
                    {
                        isConfigured = apiConfiguration.YellowPages.IsConfigured,
                        hasApiKey = !string.IsNullOrWhiteSpace(apiConfiguration.YellowPages.ApiKey)
                    },
                    zoho = new
                    {
                        isConfigured = apiConfiguration.Zoho.IsConfigured,
                        hasAccessToken = !string.IsNullOrWhiteSpace(apiConfiguration.Zoho.AccessToken)
                    }
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get current settings");
            return Json(new { success = false, message = "Failed to load current settings" });
        }
    }
}