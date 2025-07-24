using ByteForgeFrontend.Models;
using ByteForgeFrontend.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using System.Collections.Concurrent;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services;

public class WorkflowMonitoringService : IWorkflowMonitoringService
{
    private readonly ApplicationDbContext _dbContext;
    private readonly ILogger<WorkflowMonitoringService> _logger;
    
    // In-memory tracking for real-time monitoring
    private readonly ConcurrentDictionary<int, WorkflowExecution> _activeWorkflows = new();
    private readonly ConcurrentQueue<WorkflowExecution> _recentExecutions = new();

    public WorkflowMonitoringService(ApplicationDbContext dbContext, ILogger<WorkflowMonitoringService> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    public async Task<WorkflowHealthStatus> GetWorkflowHealthAsync()
    {
        try
        {
            var now = DateTime.UtcNow;
            var last24Hours = now.AddHours(-24);
            var lastHour = now.AddHours(-1);

            // Get workflow execution stats from recent executions
            var recentExecutions = _recentExecutions.ToArray();
            var last24HourExecutions = recentExecutions.Where(e => e.StartTime >= last24Hours).ToList();
            var lastHourExecutions = recentExecutions.Where(e => e.StartTime >= lastHour).ToList();

            // Calculate success rates
            var totalLast24Hours = last24HourExecutions.Count;
            var successfulLast24Hours = last24HourExecutions.Count(e => e.IsSuccessful);
            var totalLastHour = lastHourExecutions.Count;
            var successfulLastHour = lastHourExecutions.Count(e => e.IsSuccessful);

            // Get average processing time
            var completedExecutions = last24HourExecutions.Where(e => e.EndTime.HasValue).ToList();
            var avgProcessingTime = completedExecutions.Any() 
                ? completedExecutions.Average(e => e.Duration?.TotalSeconds ?? 0) 
                : 0;

            // Check for stalled workflows (running for more than 2 hours)
            var stalledWorkflows = _activeWorkflows.Values
                .Where(w => !w.EndTime.HasValue && (now - w.StartTime).TotalHours > 2)
                .Count();

            // Get current active count
            var activeCount = _activeWorkflows.Count;

            var healthStatus = new WorkflowHealthStatus
            {
                Timestamp = now,
                ActiveWorkflows = activeCount,
                StalledWorkflows = stalledWorkflows,
                TotalExecutionsLast24Hours = totalLast24Hours,
                SuccessfulExecutionsLast24Hours = successfulLast24Hours,
                SuccessRateLast24Hours = totalLast24Hours > 0 ? (double)successfulLast24Hours / totalLast24Hours : 1.0,
                TotalExecutionsLastHour = totalLastHour,
                SuccessfulExecutionsLastHour = successfulLastHour,
                SuccessRateLastHour = totalLastHour > 0 ? (double)successfulLastHour / totalLastHour : 1.0,
                AverageProcessingTimeSeconds = avgProcessingTime,
                IsHealthy = stalledWorkflows == 0 && (totalLast24Hours == 0 || (double)successfulLast24Hours / totalLast24Hours >= 0.8)
            };

            _logger.LogDebug("WorkflowMonitoringService: Health check completed - Active: {ActiveCount}, Stalled: {StalledCount}, 24h Success Rate: {SuccessRate:P2}, IsHealthy: {IsHealthy}",
                activeCount, stalledWorkflows, healthStatus.SuccessRateLast24Hours, healthStatus.IsHealthy);

            return healthStatus;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringService: Error getting workflow health status");
            return new WorkflowHealthStatus
            {
                Timestamp = DateTime.UtcNow,
                IsHealthy = false
            };
        }
    }

    public async Task<List<WorkflowExecution>> GetRecentWorkflowExecutionsAsync(int count = 50)
    {
        try
        {
            var executions = _recentExecutions.ToArray()
                .OrderByDescending(e => e.StartTime)
                .Take(count)
                .ToList();

            _logger.LogDebug("WorkflowMonitoringService: Retrieved {Count} recent workflow executions", executions.Count);
            return executions;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringService: Error getting recent workflow executions");
            return new List<WorkflowExecution>();
        }
    }

    public async Task RecordWorkflowStartAsync(int leadId, string workflowType)
    {
        try
        {
            var execution = new WorkflowExecution
            {
                LeadId = leadId,
                WorkflowType = workflowType,
                StartTime = DateTime.UtcNow,
                Activities = new List<ActivityExecution>()
            };

            _activeWorkflows[leadId] = execution;

            _logger.LogInformation("WorkflowMonitoringService: Recorded workflow start for lead {LeadId} - Type: {WorkflowType}", 
                leadId, workflowType);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringService: Error recording workflow start for lead {LeadId}", leadId);
        }
    }

    public async Task RecordWorkflowCompletionAsync(int leadId, string workflowType, bool successful, TimeSpan duration)
    {
        try
        {
            if (_activeWorkflows.TryRemove(leadId, out var execution))
            {
                execution.EndTime = DateTime.UtcNow;
                execution.Duration = duration;
                execution.IsSuccessful = successful;

                // Add to recent executions queue
                _recentExecutions.Enqueue(execution);

                // Keep only last 1000 executions to prevent memory growth
                while (_recentExecutions.Count > 1000)
                {
                    _recentExecutions.TryDequeue(out _);
                }

                _logger.LogInformation("WorkflowMonitoringService: Recorded workflow completion for lead {LeadId} - Type: {WorkflowType}, Successful: {Successful}, Duration: {DurationMs}ms", 
                    leadId, workflowType, successful, duration.TotalMilliseconds);
            }
            else
            {
                _logger.LogWarning("WorkflowMonitoringService: Could not find active workflow for lead {LeadId} to record completion", leadId);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringService: Error recording workflow completion for lead {LeadId}", leadId);
        }
    }

    public async Task RecordActivityStartAsync(int leadId, string activityName)
    {
        try
        {
            if (_activeWorkflows.TryGetValue(leadId, out var execution))
            {
                var activity = new ActivityExecution
                {
                    ActivityName = activityName,
                    StartTime = DateTime.UtcNow
                };

                execution.Activities.Add(activity);

                _logger.LogDebug("WorkflowMonitoringService: Recorded activity start for lead {LeadId} - Activity: {ActivityName}", 
                    leadId, activityName);
            }
            else
            {
                _logger.LogWarning("WorkflowMonitoringService: Could not find active workflow for lead {LeadId} to record activity start: {ActivityName}", 
                    leadId, activityName);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringService: Error recording activity start for lead {LeadId}, activity {ActivityName}", 
                leadId, activityName);
        }
    }

    public async Task RecordActivityCompletionAsync(int leadId, string activityName, bool successful, TimeSpan duration, string? errorMessage = null)
    {
        try
        {
            if (_activeWorkflows.TryGetValue(leadId, out var execution))
            {
                var activity = execution.Activities.LastOrDefault(a => a.ActivityName == activityName);
                if (activity != null)
                {
                    activity.EndTime = DateTime.UtcNow;
                    activity.Duration = duration;
                    activity.IsSuccessful = successful;
                    activity.ErrorMessage = errorMessage;

                    _logger.LogDebug("WorkflowMonitoringService: Recorded activity completion for lead {LeadId} - Activity: {ActivityName}, Successful: {Successful}, Duration: {DurationMs}ms", 
                        leadId, activityName, successful, duration.TotalMilliseconds);
                }
                else
                {
                    _logger.LogWarning("WorkflowMonitoringService: Could not find activity {ActivityName} for lead {LeadId} to record completion", 
                        activityName, leadId);
                }
            }
            else
            {
                _logger.LogWarning("WorkflowMonitoringService: Could not find active workflow for lead {LeadId} to record activity completion: {ActivityName}", 
                    leadId, activityName);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "WorkflowMonitoringService: Error recording activity completion for lead {LeadId}, activity {ActivityName}", 
                leadId, activityName);
        }
    }
}