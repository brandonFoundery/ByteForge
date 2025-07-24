using Hangfire;
using Microsoft.Extensions.Logging;

using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Jobs;

public class GoogleLeadJob
{
    private readonly ILogger<GoogleLeadJob> _logger;
    
    public GoogleLeadJob(ILogger<GoogleLeadJob> logger)
    {
        _logger = logger;
    }
    
    [DisableConcurrentExecution(timeoutInSeconds: 300)]
    public async Task Execute()
    {
        _logger.LogInformation("Executing Google Lead Job at {Time}", DateTime.UtcNow);
        
        try
        {
            // Simulate lead generation from Google
            await Task.Delay(1000);
            
            _logger.LogInformation("Google Lead Job completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing Google Lead Job");
            throw;
        }
    }
}