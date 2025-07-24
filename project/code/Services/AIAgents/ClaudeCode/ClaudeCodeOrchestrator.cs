using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.AIAgents
{
    public class ClaudeCodeOrchestrator : IClaudeCodeOrchestrator
    {
        private readonly IWorktreeManager _worktreeManager;
        private readonly IClaudeCodeExecutor _claudeExecutor;
        private readonly IAgentMonitor _agentMonitor;
        private readonly ILogger<ClaudeCodeOrchestrator> _logger;

        public ClaudeCodeOrchestrator(
            IWorktreeManager worktreeManager,
            IClaudeCodeExecutor claudeExecutor,
            IAgentMonitor agentMonitor,
            ILogger<ClaudeCodeOrchestrator> logger)
        {
            _worktreeManager = worktreeManager ?? throw new ArgumentNullException(nameof(worktreeManager));
            _claudeExecutor = claudeExecutor ?? throw new ArgumentNullException(nameof(claudeExecutor));
            _agentMonitor = agentMonitor ?? throw new ArgumentNullException(nameof(agentMonitor));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<WorktreeInfo> CreateAgentWorktreeAsync(ClaudeAgentConfig config)
        {
            _logger.LogInformation("Creating worktree for agent {AgentName}", config.AgentName);
            
            var worktreePath = $"/worktrees/{config.AgentName}";
            var worktree = await _worktreeManager.CreateWorktreeAsync(
                config.WorktreeBranch, 
                worktreePath, 
                CancellationToken.None);

            _logger.LogInformation("Created worktree at {Path} on branch {Branch}", 
                worktree.Path, worktree.Branch);

            return worktree;
        }

        public async Task<bool> ConfigureAgentEnvironmentAsync(string worktreePath, ClaudeAgentConfig config)
        {
            _logger.LogInformation("Configuring environment for {AgentName}", config.AgentName);

            var environment = new Dictionary<string, string>
            {
                { "BACKEND_PORT", config.BackendPort.ToString() },
                { "FRONTEND_PORT", config.FrontendPort.ToString() },
                { "AGENT_NAME", config.AgentName }
            };

            foreach (var kvp in config.EnvironmentVariables)
            {
                environment[kvp.Key] = kvp.Value;
            }

            return await _worktreeManager.ConfigureEnvironmentAsync(
                worktreePath, 
                environment, 
                CancellationToken.None);
        }

        public async Task<ClaudeExecutionResult> ExecuteClaudeAgentAsync(
            string worktreePath, 
            ClaudeInstructions instructions)
        {
            _logger.LogInformation("Executing Claude agent in {WorktreePath}", worktreePath);
            
            var stopwatch = Stopwatch.StartNew();
            
            try
            {
                var result = await _claudeExecutor.ExecuteAsync(
                    instructions, 
                    worktreePath, 
                    CancellationToken.None);

                stopwatch.Stop();
                result.Duration = stopwatch.Elapsed;

                if (result.Success)
                {
                    _logger.LogInformation("Claude execution completed successfully. Generated {FileCount} files", 
                        result.GeneratedFiles?.Length ?? 0);
                }
                else
                {
                    _logger.LogError("Claude execution failed: {Error}", result.Error);
                }

                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error executing Claude agent");
                return new ClaudeExecutionResult
                {
                    Success = false,
                    Error = ex.Message,
                    Duration = stopwatch.Elapsed
                };
            }
        }

        public async Task MonitorAgentAsync(
            Guid agentId, 
            string worktreePath, 
            Action<AgentProgress> progressCallback)
        {
            _logger.LogInformation("Starting monitoring for agent {AgentId}", agentId);
            
            await _agentMonitor.StartMonitoringAsync(
                agentId, 
                worktreePath, 
                progressCallback, 
                CancellationToken.None);
        }

        public async Task<Dictionary<string, ClaudeExecutionResult>> RunAgentsInParallelAsync(
            IEnumerable<ClaudeAgentConfig> agents)
        {
            _logger.LogInformation("Running {AgentCount} agents in parallel", agents.Count());
            
            var tasks = new List<Task<(string name, ClaudeExecutionResult result)>>();

            foreach (var agentConfig in agents)
            {
                tasks.Add(RunSingleAgentAsync(agentConfig));
            }

            var results = await Task.WhenAll(tasks);
            
            return results.ToDictionary(r => r.name, r => r.result);
        }

        public async Task<AggregatedResult> AggregateResultsAsync(
            Dictionary<string, ClaudeExecutionResult> results)
        {
            var aggregated = new AggregatedResult
            {
                Success = results.All(r => r.Value.Success),
                AgentResults = results
            };

            foreach (var result in results.Values)
            {
                aggregated.TotalFilesGenerated += result.GeneratedFiles?.Length ?? 0;
                aggregated.TotalDuration += result.Duration;

                if (!result.Success && !string.IsNullOrEmpty(result.Error))
                {
                    aggregated.Errors.Add(result.Error);
                }
            }

            _logger.LogInformation("Aggregated results: Success={Success}, TotalFiles={TotalFiles}", 
                aggregated.Success, aggregated.TotalFilesGenerated);

            return aggregated;
        }

        public async Task CleanupWorktreesAsync(IEnumerable<string> worktreePaths)
        {
            _logger.LogInformation("Cleaning up {Count} worktrees", worktreePaths.Count());
            
            var tasks = worktreePaths.Select(path => 
                _worktreeManager.RemoveWorktreeAsync(path, CancellationToken.None));
            
            await Task.WhenAll(tasks);
        }

        public async Task<bool> SetupSharedContextAsync(AgentSharedContext context)
        {
            _logger.LogInformation("Setting up shared context at {Directory}", context.SharedDirectory);
            
            return await _worktreeManager.CreateSharedContextAsync(context, CancellationToken.None);
        }

        private async Task<(string name, ClaudeExecutionResult result)> RunSingleAgentAsync(
            ClaudeAgentConfig config)
        {
            try
            {
                // Create worktree
                var worktree = await CreateAgentWorktreeAsync(config);
                
                // Configure environment
                await ConfigureAgentEnvironmentAsync(worktree.Path, config);
                
                // Create instructions based on agent type
                var instructions = CreateAgentInstructions(config.AgentName);
                
                // Execute Claude
                var result = await ExecuteClaudeAgentAsync(worktree.Path, instructions);
                
                return (config.AgentName, result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error running agent {AgentName}", config.AgentName);
                return (config.AgentName, new ClaudeExecutionResult
                {
                    Success = false,
                    Error = ex.Message
                });
            }
        }

        private ClaudeInstructions CreateAgentInstructions(string agentName)
        {
            var baseInstructions = new ClaudeInstructions
            {
                MaxIterations = 10,
                Context = new Dictionary<string, object>
                {
                    { "agentName", agentName },
                    { "projectType", "ByteForgeFrontend" }
                }
            };

            switch (agentName.ToLower())
            {
                case "backend-agent":
                    baseInstructions.SystemPrompt = "You are a backend development agent specializing in ASP.NET Core";
                    baseInstructions.Task = "Generate backend API code following Clean Architecture patterns";
                    break;
                    
                case "frontend-agent":
                    baseInstructions.SystemPrompt = "You are a frontend development agent specializing in React and TypeScript";
                    baseInstructions.Task = "Generate React components and pages with Material-UI";
                    break;
                    
                case "security-agent":
                    baseInstructions.SystemPrompt = "You are a security specialist agent";
                    baseInstructions.Task = "Implement authentication, authorization, and security features";
                    break;
                    
                case "infrastructure-agent":
                    baseInstructions.SystemPrompt = "You are an infrastructure and DevOps agent";
                    baseInstructions.Task = "Generate Docker, CI/CD, and infrastructure configurations";
                    break;
                    
                default:
                    baseInstructions.SystemPrompt = "You are a specialized development agent";
                    baseInstructions.Task = "Generate code based on project requirements";
                    break;
            }

            return baseInstructions;
        }
    }
}