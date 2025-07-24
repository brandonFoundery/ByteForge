using System;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.AIAgents
{
    public abstract class BaseAgent : IAgent
    {
        protected readonly IServiceProvider _serviceProvider;
        protected readonly ILogger<BaseAgent> _logger;
        private readonly Stopwatch _stopwatch = new();
        private CancellationTokenSource _cancellationTokenSource;

        public Guid Id { get; }
        public string Name { get; }
        public AgentStatus Status { get; private set; } = AgentStatus.Idle;
        public DateTime? StartTime { get; private set; }
        public DateTime? StopTime { get; private set; }
        public TimeSpan ExecutionTime => _stopwatch.Elapsed;
        public AgentMetrics Metrics { get; private set; } = new();
        public string LastError { get; private set; }

        protected BaseAgent(IServiceProvider serviceProvider, string name)
        {
            _serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
            _logger = serviceProvider.GetService<ILogger<BaseAgent>>() ?? 
                     throw new InvalidOperationException("Logger not found in service provider");
            
            Id = Guid.NewGuid();
            Name = name ?? throw new ArgumentNullException(nameof(name));
        }

        public virtual async Task StartAsync()
        {
            if (Status == AgentStatus.Running)
            {
                _logger.LogWarning("Agent {Name} is already running", Name);
                return;
            }

            try
            {
                Status = AgentStatus.Starting;
                StartTime = DateTime.UtcNow;
                _stopwatch.Start();
                _cancellationTokenSource = new CancellationTokenSource();
                
                await OnStartingAsync();
                
                Status = AgentStatus.Running;
                _logger.LogInformation("Agent {Name} started successfully", Name);
            }
            catch (Exception ex)
            {
                Status = AgentStatus.Failed;
                LastError = ex.Message;
                _logger.LogError(ex, "Failed to start agent {Name}", Name);
                throw;
            }
        }

        public virtual async Task StopAsync()
        {
            if (Status != AgentStatus.Running)
            {
                _logger.LogWarning("Agent {Name} is not running", Name);
                return;
            }

            try
            {
                Status = AgentStatus.Stopping;
                _cancellationTokenSource?.Cancel();
                
                await OnStoppingAsync();
                
                Status = AgentStatus.Stopped;
                StopTime = DateTime.UtcNow;
                _stopwatch.Stop();
                
                UpdateMetrics();
                _logger.LogInformation("Agent {Name} stopped successfully", Name);
            }
            catch (Exception ex)
            {
                Status = AgentStatus.Failed;
                LastError = ex.Message;
                _logger.LogError(ex, "Failed to stop agent {Name}", Name);
                throw;
            }
            finally
            {
                _cancellationTokenSource?.Dispose();
            }
        }

        public async Task<AgentResult> ExecuteAsync(CancellationToken cancellationToken)
        {
            if (Status != AgentStatus.Running)
            {
                throw new InvalidOperationException($"Agent {Name} must be running to execute");
            }

            var taskStopwatch = Stopwatch.StartNew();
            
            try
            {
                using (var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(
                    cancellationToken, _cancellationTokenSource.Token))
                {
                    var result = await PerformWorkAsync(linkedCts.Token);
                    
                    if (linkedCts.Token.IsCancellationRequested)
                    {
                        Status = AgentStatus.Stopped;
                    }
                    
                    if (result.Success)
                    {
                        Metrics.TasksCompleted++;
                    }
                    else
                    {
                        Metrics.TasksFailed++;
                    }
                    
                    taskStopwatch.Stop();
                    UpdateTaskMetrics(taskStopwatch.Elapsed);
                    
                    return result;
                }
            }
            catch (OperationCanceledException)
            {
                Status = AgentStatus.Stopped;
                throw;
            }
            catch (Exception ex)
            {
                Status = AgentStatus.Failed;
                LastError = ex.Message;
                Metrics.TasksFailed++;
                _logger.LogError(ex, "Agent {Name} execution failed", Name);
                throw;
            }
        }

        protected abstract Task<AgentResult> PerformWorkAsync(CancellationToken cancellationToken);

        protected virtual Task OnStartingAsync() => Task.CompletedTask;
        protected virtual Task OnStoppingAsync() => Task.CompletedTask;

        private void UpdateMetrics()
        {
            Metrics.TotalExecutionTime = ExecutionTime;
            
            // Update memory usage
            using (var process = Process.GetCurrentProcess())
            {
                Metrics.MemoryUsage = process.WorkingSet64;
            }
        }

        private void UpdateTaskMetrics(TimeSpan taskDuration)
        {
            var totalTasks = Metrics.TasksCompleted + Metrics.TasksFailed;
            if (totalTasks > 0)
            {
                Metrics.AverageTaskDuration = 
                    ((Metrics.AverageTaskDuration * (totalTasks - 1)) + taskDuration.TotalMilliseconds) / totalTasks;
            }
        }
    }
}