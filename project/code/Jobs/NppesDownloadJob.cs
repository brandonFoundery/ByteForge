using Hangfire;
using Microsoft.Extensions.Logging;

using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Jobs;

public class NppesDownloadJob
{
    private readonly ILogger<NppesDownloadJob> _logger;
    
    public NppesDownloadJob(ILogger<NppesDownloadJob> logger)
    {
        _logger = logger;
    }
    
    [DisableConcurrentExecution(timeoutInSeconds: 3600)]
    public async Task Execute()
    {
        await DownloadFullFileAsync();
    }
    
    public async Task DownloadFullFileAsync()
    {
        _logger.LogInformation("Downloading full NPPES file at {Time}", DateTime.UtcNow);
        
        try
        {
            // Simulate NPPES full file download
            await Task.Delay(2000);
            
            _logger.LogInformation("NPPES full file download completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error downloading full NPPES file");
            throw;
        }
    }
    
    public async Task DownloadWeeklyFileAsync()
    {
        _logger.LogInformation("Downloading weekly NPPES file at {Time}", DateTime.UtcNow);
        
        try
        {
            // Simulate NPPES weekly file download
            await Task.Delay(1000);
            
            _logger.LogInformation("NPPES weekly file download completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error downloading weekly NPPES file");
            throw;
        }
    }
}