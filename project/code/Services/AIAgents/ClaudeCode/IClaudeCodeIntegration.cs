using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.AIAgents
{
    public interface IWorktreeManager
    {
        Task<WorktreeInfo> CreateWorktreeAsync(string branch, string path, CancellationToken cancellationToken);
        Task<bool> RemoveWorktreeAsync(string path, CancellationToken cancellationToken);
        Task<bool> ConfigureEnvironmentAsync(string worktreePath, Dictionary<string, string> environment, CancellationToken cancellationToken);
        Task<bool> CreateSharedContextAsync(AgentSharedContext context, CancellationToken cancellationToken);
    }

    public interface IClaudeCodeExecutor
    {
        Task<ClaudeExecutionResult> ExecuteAsync(ClaudeInstructions instructions, string workingDirectory, CancellationToken cancellationToken);
    }

    public interface IAgentMonitor
    {
        Task<bool> StartMonitoringAsync(Guid agentId, string worktreePath, Action<AgentProgress> progressCallback, CancellationToken cancellationToken);
        Task StopMonitoringAsync(Guid agentId);
    }

    public interface IClaudeCodeOrchestrator
    {
        Task<WorktreeInfo> CreateAgentWorktreeAsync(ClaudeAgentConfig config);
        Task<bool> ConfigureAgentEnvironmentAsync(string worktreePath, ClaudeAgentConfig config);
        Task<ClaudeExecutionResult> ExecuteClaudeAgentAsync(string worktreePath, ClaudeInstructions instructions);
        Task MonitorAgentAsync(Guid agentId, string worktreePath, Action<AgentProgress> progressCallback);
        Task<Dictionary<string, ClaudeExecutionResult>> RunAgentsInParallelAsync(IEnumerable<ClaudeAgentConfig> agents);
        Task<AggregatedResult> AggregateResultsAsync(Dictionary<string, ClaudeExecutionResult> results);
        Task CleanupWorktreesAsync(IEnumerable<string> worktreePaths);
        Task<bool> SetupSharedContextAsync(AgentSharedContext context);
    }

    public class WorktreeInfo
    {
        public string Path { get; set; }
        public string Branch { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

    public class ClaudeAgentConfig
    {
        public string AgentName { get; set; }
        public string WorktreeBranch { get; set; }
        public int BackendPort { get; set; }
        public int FrontendPort { get; set; }
        public Dictionary<string, string> EnvironmentVariables { get; set; } = new();
    }

    public class ClaudeInstructions
    {
        public string SystemPrompt { get; set; }
        public string Task { get; set; }
        public Dictionary<string, object> Context { get; set; } = new();
        public List<string> Files { get; set; } = new();
        public int MaxIterations { get; set; } = 10;
    }

    public class ClaudeExecutionResult
    {
        public bool Success { get; set; }
        public string Output { get; set; }
        public string Error { get; set; }
        public string[] GeneratedFiles { get; set; } = Array.Empty<string>();
        public Dictionary<string, string> FileContents { get; set; } = new();
        public TimeSpan Duration { get; set; }
    }

    public class AgentProgress
    {
        public int Percentage { get; set; }
        public string Status { get; set; }
        public string CurrentTask { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }

    public class AggregatedResult
    {
        public bool Success { get; set; }
        public int TotalFilesGenerated { get; set; }
        public Dictionary<string, ClaudeExecutionResult> AgentResults { get; set; } = new();
        public List<string> Errors { get; set; } = new();
        public TimeSpan TotalDuration { get; set; }
    }

    public class AgentSharedContext
    {
        public string SharedDirectory { get; set; }
        public Dictionary<string, string> Files { get; set; } = new();
        public Dictionary<string, object> SharedData { get; set; } = new();
    }
}