using System;
using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.AIAgents
{
    public class AgentMonitor : IAgentMonitor
    {
        private readonly ILogger<AgentMonitor> _logger;
        private readonly ConcurrentDictionary<Guid, CancellationTokenSource> _monitoringTasks = new();

        public AgentMonitor(ILogger<AgentMonitor> logger)
        {
            _logger = logger;
        }

        public async Task<bool> StartMonitoringAsync(Guid agentId, string worktreePath, Action<AgentProgress> progressCallback, CancellationToken cancellationToken)
        {
            _logger.LogInformation("Starting monitoring for agent {AgentId} at path {Path}", agentId, worktreePath);
            
            try
            {
                var monitoringCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                _monitoringTasks[agentId] = monitoringCts;
                
                // Start monitoring task
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await MonitorAgentProgress(agentId, worktreePath, progressCallback, monitoringCts.Token);
                    }
                    catch (OperationCanceledException)
                    {
                        _logger.LogInformation("Monitoring cancelled for agent {AgentId}", agentId);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, "Error monitoring agent {AgentId}", agentId);
                    }
                    finally
                    {
                        _monitoringTasks.TryRemove(agentId, out _);
                    }
                }, monitoringCts.Token);
                
                await Task.Delay(100, cancellationToken); // Allow task to start
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to start monitoring for agent {AgentId}", agentId);
                return false;
            }
        }

        public async Task StopMonitoringAsync(Guid agentId)
        {
            _logger.LogInformation("Stopping monitoring for agent {AgentId}", agentId);
            
            if (_monitoringTasks.TryRemove(agentId, out var cts))
            {
                cts.Cancel();
                cts.Dispose();
            }
            
            await Task.CompletedTask;
        }

        private async Task MonitorAgentProgress(Guid agentId, string worktreePath, Action<AgentProgress> progressCallback, CancellationToken cancellationToken)
        {
            var progress = 0;
            var tasks = new[] { "Initializing", "Processing", "Generating files", "Finalizing" };
            
            while (progress < 100 && !cancellationToken.IsCancellationRequested)
            {
                var taskIndex = progress / 25;
                var currentTask = taskIndex < tasks.Length ? tasks[taskIndex] : "Completing";
                
                progressCallback(new AgentProgress
                {
                    Percentage = progress,
                    Status = "Running",
                    CurrentTask = currentTask,
                    Timestamp = DateTime.UtcNow
                });
                
                // Simulate progress
                await Task.Delay(500, cancellationToken);
                progress += 5;
            }
            
            // Final progress update
            if (!cancellationToken.IsCancellationRequested)
            {
                progressCallback(new AgentProgress
                {
                    Percentage = 100,
                    Status = "Completed",
                    CurrentTask = "Finished",
                    Timestamp = DateTime.UtcNow
                });
            }
        }
    }
}