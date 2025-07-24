using ByteForgeFrontend.Models;

namespace ByteForgeFrontend.Services;

public interface IExternalApiConfigurationService
{
    ExternalServicesConfiguration GetConfiguration();
}