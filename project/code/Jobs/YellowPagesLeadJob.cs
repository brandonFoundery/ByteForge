using Hangfire;
using Microsoft.Extensions.Logging;

using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Jobs;

public class YellowPagesLeadJob
{
    private readonly ILogger<YellowPagesLeadJob> _logger;
    
    public YellowPagesLeadJob(ILogger<YellowPagesLeadJob> logger)
    {
        _logger = logger;
    }
    
    [DisableConcurrentExecution(timeoutInSeconds: 300)]
    public async Task Execute()
    {
        _logger.LogInformation("Executing YellowPages Lead Job at {Time}", DateTime.UtcNow);
        
        try
        {
            // Simulate lead generation from YellowPages
            await Task.Delay(1000);
            
            _logger.LogInformation("YellowPages Lead Job completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing YellowPages Lead Job");
            throw;
        }
    }
}