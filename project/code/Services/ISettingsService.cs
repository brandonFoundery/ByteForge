using ByteForgeFrontend.Models;

using System.Threading.Tasks;
namespace ByteForgeFrontend.Services;

public interface ISettingsService
{
    Task<WorkflowSettings> GetWorkflowSettingsAsync();
    Task<WorkflowSettings> UpdateWorkflowSettingsAsync(WorkflowSettings settings);
    Task<ExternalServicesConfiguration> GetApiConfigurationAsync();
    Task UpdateApiConfigurationAsync(ExternalServicesConfiguration configuration);
}