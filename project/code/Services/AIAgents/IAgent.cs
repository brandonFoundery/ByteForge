using System;
using System.Threading;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.AIAgents
{
    public interface IAgent
    {
        Guid Id { get; }
        string Name { get; }
        AgentStatus Status { get; }
        DateTime? StartTime { get; }
        DateTime? StopTime { get; }
        TimeSpan ExecutionTime { get; }
        AgentMetrics Metrics { get; }
        string LastError { get; }
        
        Task StartAsync();
        Task StopAsync();
        Task<AgentResult> ExecuteAsync(CancellationToken cancellationToken);
    }

    public enum AgentStatus
    {
        Idle,
        Starting,
        Running,
        Stopping,
        Stopped,
        Failed,
        Ready
    }

    public class AgentResult
    {
        public bool Success { get; set; }
        public string Message { get; set; }
        public string Error { get; set; }
        public object Data { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }

    public class AgentMetrics
    {
        public int TasksCompleted { get; set; }
        public int TasksFailed { get; set; }
        public TimeSpan TotalExecutionTime { get; set; }
        public double AverageTaskDuration { get; set; }
        public long MemoryUsage { get; set; }
        public double CpuUsage { get; set; }
    }
}