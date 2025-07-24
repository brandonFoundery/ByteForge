using Microsoft.AspNetCore.Mvc;
using ByteForgeFrontend.Services;

using Microsoft.Extensions.Logging;
using System;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[Route("api/[controller]")]
[ApiController]
public class WorkflowMonitoringApiController : ControllerBase
{
    private readonly IWorkflowMonitoringService _monitoringService;
    private readonly ILogger<WorkflowMonitoringApiController> _logger;

    public WorkflowMonitoringApiController(
        IWorkflowMonitoringService monitoringService,
        ILogger<WorkflowMonitoringApiController> logger)
    {
        _monitoringService = monitoringService;
        _logger = logger;
    }

    /// <summary>
    /// Get workflow health status
    /// </summary>
    [HttpGet("health")]
    public async Task<IActionResult> GetWorkflowHealth()
    {
        try
        {
            var health = await _monitoringService.GetWorkflowHealthAsync();
            _logger.LogDebug("WorkflowMonitoringApi: Retrieved workflow health - IsHealthy: {IsHealthy}, Active: {Active}, Success Rate: {SuccessRate:P2}",
                health.IsHealthy, health.ActiveWorkflows, health.SuccessRateLast24Hours);
            
            return Ok(health);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringApi: Error retrieving workflow health");
            return StatusCode(500, new { error = "Failed to retrieve workflow health" });
        }
    }

    /// <summary>
    /// Get recent workflow executions
    /// </summary>
    [HttpGet("executions")]
    public async Task<IActionResult> GetRecentExecutions([FromQuery] int count = 50)
    {
        try
        {
            if (count <= 0 || count > 1000)
            {
                return BadRequest(new { error = "Count must be between 1 and 1000" });
            }

            var executions = await _monitoringService.GetRecentWorkflowExecutionsAsync(count);
            _logger.LogDebug("WorkflowMonitoringApi: Retrieved {Count} recent workflow executions", executions.Count);
            
            return Ok(executions);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringApi: Error retrieving recent workflow executions");
            return StatusCode(500, new { error = "Failed to retrieve workflow executions" });
        }
    }

    /// <summary>
    /// Get workflow statistics summary
    /// </summary>
    [HttpGet("stats")]
    public async Task<IActionResult> GetWorkflowStats()
    {
        try
        {
            var health = await _monitoringService.GetWorkflowHealthAsync();
            var executions = await _monitoringService.GetRecentWorkflowExecutionsAsync(100);

            // Calculate additional stats
            var completedExecutions = executions.Where(e => e.EndTime.HasValue).ToList();
            var avgDuration = completedExecutions.Any() ? completedExecutions.Average(e => e.Duration?.TotalSeconds ?? 0) : 0;
            var minDuration = completedExecutions.Any() ? completedExecutions.Min(e => e.Duration?.TotalSeconds ?? 0) : 0;
            var maxDuration = completedExecutions.Any() ? completedExecutions.Max(e => e.Duration?.TotalSeconds ?? 0) : 0;

            var stats = new
            {
                Health = health,
                RecentExecutions = executions.Count,
                CompletedExecutions = completedExecutions.Count,
                AverageDurationSeconds = avgDuration,
                MinDurationSeconds = minDuration,
                MaxDurationSeconds = maxDuration,
                MostCommonActivities = executions
                    .SelectMany(e => e.Activities)
                    .GroupBy(a => a.ActivityName)
                    .OrderByDescending(g => g.Count())
                    .Take(5)
                    .Select(g => new { ActivityName = g.Key, Count = g.Count() })
                    .ToList()
            };

            _logger.LogDebug("WorkflowMonitoringApi: Calculated workflow statistics - Recent: {Recent}, Completed: {Completed}, Avg Duration: {AvgDuration}s",
                stats.RecentExecutions, stats.CompletedExecutions, stats.AverageDurationSeconds);

            return Ok(stats);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringApi: Error retrieving workflow statistics");
            return StatusCode(500, new { error = "Failed to retrieve workflow statistics" });
        }
    }
}