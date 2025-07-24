using Hangfire;
using Microsoft.Extensions.Logging;

using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Jobs;

public class LinkedInLeadJob
{
    private readonly ILogger<LinkedInLeadJob> _logger;
    
    public LinkedInLeadJob(ILogger<LinkedInLeadJob> logger)
    {
        _logger = logger;
    }
    
    [DisableConcurrentExecution(timeoutInSeconds: 300)]
    public async Task Execute()
    {
        _logger.LogInformation("Executing LinkedIn Lead Job at {Time}", DateTime.UtcNow);
        
        try
        {
            // Simulate lead generation from LinkedIn
            await Task.Delay(1000);
            
            _logger.LogInformation("LinkedIn Lead Job completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing LinkedIn Lead Job");
            throw;
        }
    }
}