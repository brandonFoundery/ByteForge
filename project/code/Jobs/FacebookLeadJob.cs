using Hangfire;
using Microsoft.Extensions.Logging;

using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Jobs;

public class FacebookLeadJob
{
    private readonly ILogger<FacebookLeadJob> _logger;
    
    public FacebookLeadJob(ILogger<FacebookLeadJob> logger)
    {
        _logger = logger;
    }
    
    [DisableConcurrentExecution(timeoutInSeconds: 300)]
    public async Task Execute()
    {
        _logger.LogInformation("Executing Facebook Lead Job at {Time}", DateTime.UtcNow);
        
        try
        {
            // Simulate lead generation from Facebook
            await Task.Delay(1000);
            
            _logger.LogInformation("Facebook Lead Job completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing Facebook Lead Job");
            throw;
        }
    }
}