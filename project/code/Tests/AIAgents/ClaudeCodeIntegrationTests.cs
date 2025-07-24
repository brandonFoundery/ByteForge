using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.AIAgents;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;
using Moq;

using Microsoft.AspNetCore.Mvc;
namespace ByteForgeFrontend.Tests.AIAgents
{
    public class ClaudeCodeIntegrationTests
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly Mock<IWorktreeManager> _mockWorktreeManager;
        private readonly Mock<IClaudeCodeExecutor> _mockClaudeExecutor;
        private readonly Mock<IAgentMonitor> _mockAgentMonitor;

        public ClaudeCodeIntegrationTests()
        {
            var services = new ServiceCollection();
            
            _mockWorktreeManager = new Mock<IWorktreeManager>();
            _mockClaudeExecutor = new Mock<IClaudeCodeExecutor>();
            _mockAgentMonitor = new Mock<IAgentMonitor>();
            
            services.AddSingleton(_mockWorktreeManager.Object);
            services.AddSingleton(_mockClaudeExecutor.Object);
            services.AddSingleton(_mockAgentMonitor.Object);
            services.AddSingleton(Mock.Of<ILogger<ClaudeCodeOrchestrator>>());
            services.AddSingleton<IClaudeCodeOrchestrator, ClaudeCodeOrchestrator>();
            
            _serviceProvider = services.BuildServiceProvider();
        }

        [Fact]
        public async Task Should_Create_Isolated_Worktree_For_Agent()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var agentConfig = new ClaudeAgentConfig
            {
                AgentName = "test-agent",
                WorktreeBranch = "agent/test-agent",
                BackendPort = 5010,
                FrontendPort = 3010
            };

            _mockWorktreeManager.Setup(x => x.CreateWorktreeAsync(
                It.IsAny<string>(), 
                It.IsAny<string>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(new WorktreeInfo
                {
                    Path = "/worktrees/test-agent",
                    Branch = "agent/test-agent"
                });

            // Act
            var worktree = await orchestrator.CreateAgentWorktreeAsync(agentConfig);

            // Assert
            Assert.NotNull(worktree);
            Assert.Equal("/worktrees/test-agent", worktree.Path);
            _mockWorktreeManager.Verify(x => x.CreateWorktreeAsync(
                "agent/test-agent", 
                It.Is<string>(p => p.Contains("test-agent")), 
                It.IsAny<CancellationToken>()), 
                Times.Once);
        }

        [Fact]
        public async Task Should_Configure_Agent_Environment()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var agentConfig = new ClaudeAgentConfig
            {
                AgentName = "backend-agent",
                BackendPort = 5011,
                FrontendPort = 3011,
                EnvironmentVariables = new Dictionary<string, string>
                {
                    { "ASPNETCORE_ENVIRONMENT", "Development" }
                }
            };

            _mockWorktreeManager.Setup(x => x.ConfigureEnvironmentAsync(
                It.IsAny<string>(), 
                It.IsAny<Dictionary<string, string>>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(true);

            // Act
            var configured = await orchestrator.ConfigureAgentEnvironmentAsync(
                "/worktrees/backend-agent", 
                agentConfig);

            // Assert
            Assert.True(configured);
            _mockWorktreeManager.Verify(x => x.ConfigureEnvironmentAsync(
                "/worktrees/backend-agent",
                It.Is<Dictionary<string, string>>(env => 
                    env["BACKEND_PORT"] == "5011" &&
                    env["FRONTEND_PORT"] == "3011" &&
                    env["ASPNETCORE_ENVIRONMENT"] == "Development"),
                It.IsAny<CancellationToken>()), 
                Times.Once);
        }

        [Fact]
        public async Task Should_Execute_Claude_Code_With_Instructions()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var instructions = new ClaudeInstructions
            {
                SystemPrompt = "You are a backend development agent",
                Task = "Generate ASP.NET Core API controllers",
                Context = new Dictionary<string, object>
                {
                    { "requirements", "User management API" }
                }
            };

            _mockClaudeExecutor.Setup(x => x.ExecuteAsync(
                It.IsAny<ClaudeInstructions>(), 
                It.IsAny<string>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(new ClaudeExecutionResult
                {
                    Success = true,
                    Output = "Generated controllers successfully",
                    GeneratedFiles = new[] { "UserController.cs", "AuthController.cs" }
                });

            // Act
            var result = await orchestrator.ExecuteClaudeAgentAsync(
                "/worktrees/backend-agent", 
                instructions);

            // Assert
            Assert.True(result.Success);
            Assert.Contains("UserController.cs", result.GeneratedFiles);
            _mockClaudeExecutor.Verify(x => x.ExecuteAsync(
                It.Is<ClaudeInstructions>(i => i.SystemPrompt.Contains("backend")),
                "/worktrees/backend-agent",
                It.IsAny<CancellationToken>()), 
                Times.Once);
        }

        [Fact]
        public async Task Should_Monitor_Agent_Progress()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var agentId = Guid.NewGuid();
            var progressUpdates = new List<AgentProgress>();

            _mockAgentMonitor.Setup(x => x.StartMonitoringAsync(
                It.IsAny<Guid>(), 
                It.IsAny<string>(), 
                It.IsAny<Action<AgentProgress>>(), 
                It.IsAny<CancellationToken>()))
                .Callback<Guid, string, Action<AgentProgress>, CancellationToken>((id, path, callback, ct) =>
                {
                    // Simulate progress updates
                    callback(new AgentProgress { Percentage = 25, Status = "Analyzing requirements" });
                    callback(new AgentProgress { Percentage = 50, Status = "Generating code" });
                    callback(new AgentProgress { Percentage = 100, Status = "Complete" });
                })
                .ReturnsAsync(true);

            // Act
            await orchestrator.MonitorAgentAsync(
                agentId, 
                "/worktrees/test-agent",
                progress => progressUpdates.Add(progress));

            // Assert
            Assert.Equal(3, progressUpdates.Count);
            Assert.Equal(100, progressUpdates[^1].Percentage);
            _mockAgentMonitor.Verify(x => x.StartMonitoringAsync(
                agentId,
                "/worktrees/test-agent",
                It.IsAny<Action<AgentProgress>>(),
                It.IsAny<CancellationToken>()), 
                Times.Once);
        }

        [Fact]
        public async Task Should_Handle_Multiple_Agents_In_Parallel()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var agents = new[]
            {
                new ClaudeAgentConfig { AgentName = "backend-agent", BackendPort = 5020 },
                new ClaudeAgentConfig { AgentName = "frontend-agent", BackendPort = 5021 },
                new ClaudeAgentConfig { AgentName = "security-agent", BackendPort = 5022 }
            };

            _mockWorktreeManager.Setup(x => x.CreateWorktreeAsync(
                It.IsAny<string>(), 
                It.IsAny<string>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync((string branch, string path, CancellationToken ct) => new WorktreeInfo
                {
                    Path = path,
                    Branch = branch
                });

            _mockClaudeExecutor.Setup(x => x.ExecuteAsync(
                It.IsAny<ClaudeInstructions>(), 
                It.IsAny<string>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(new ClaudeExecutionResult { Success = true });

            // Act
            var results = await orchestrator.RunAgentsInParallelAsync(agents);

            // Assert
            Assert.Equal(3, results.Count);
            Assert.All(results.Values, r => Assert.True(r.Success));
            _mockClaudeExecutor.Verify(x => x.ExecuteAsync(
                It.IsAny<ClaudeInstructions>(),
                It.IsAny<string>(),
                It.IsAny<CancellationToken>()), 
                Times.Exactly(3));
        }

        [Fact]
        public async Task Should_Aggregate_Results_From_Multiple_Agents()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var results = new Dictionary<string, ClaudeExecutionResult>
            {
                ["backend-agent"] = new ClaudeExecutionResult
                {
                    Success = true,
                    GeneratedFiles = new[] { "UserController.cs", "ProductController.cs" }
                },
                ["frontend-agent"] = new ClaudeExecutionResult
                {
                    Success = true,
                    GeneratedFiles = new[] { "UserList.tsx", "ProductGrid.tsx" }
                }
            };

            // Act
            var aggregated = await orchestrator.AggregateResultsAsync(results);

            // Assert
            Assert.True(aggregated.Success);
            Assert.Equal(4, aggregated.TotalFilesGenerated);
            Assert.Contains("backend-agent", aggregated.AgentResults.Keys);
            Assert.Contains("frontend-agent", aggregated.AgentResults.Keys);
        }

        [Fact]
        public async Task Should_Cleanup_Worktrees_After_Completion()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var worktreePaths = new[] 
            { 
                "/worktrees/agent1", 
                "/worktrees/agent2" 
            };

            _mockWorktreeManager.Setup(x => x.RemoveWorktreeAsync(
                It.IsAny<string>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(true);

            // Act
            await orchestrator.CleanupWorktreesAsync(worktreePaths);

            // Assert
            _mockWorktreeManager.Verify(x => x.RemoveWorktreeAsync(
                It.IsAny<string>(),
                It.IsAny<CancellationToken>()), 
                Times.Exactly(2));
        }

        [Fact]
        public async Task Should_Handle_Agent_Failures_Gracefully()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var instructions = new ClaudeInstructions { Task = "Generate code" };

            _mockClaudeExecutor.Setup(x => x.ExecuteAsync(
                It.IsAny<ClaudeInstructions>(), 
                It.IsAny<string>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(new ClaudeExecutionResult
                {
                    Success = false,
                    Error = "Claude Code execution failed"
                });

            // Act
            var result = await orchestrator.ExecuteClaudeAgentAsync(
                "/worktrees/failed-agent", 
                instructions);

            // Assert
            Assert.False(result.Success);
            Assert.Contains("Claude Code execution failed", result.Error);
        }

        [Fact]
        public async Task Should_Support_Agent_Communication_Through_Files()
        {
            // Arrange
            var orchestrator = _serviceProvider.GetRequiredService<IClaudeCodeOrchestrator>();
            var sharedContext = new AgentSharedContext
            {
                SharedDirectory = "/shared/context",
                Files = new Dictionary<string, string>
                {
                    { "api-spec.yaml", "OpenAPI specification content" },
                    { "models.json", "Shared data models" }
                }
            };

            _mockWorktreeManager.Setup(x => x.CreateSharedContextAsync(
                It.IsAny<AgentSharedContext>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync(true);

            // Act
            var created = await orchestrator.SetupSharedContextAsync(sharedContext);

            // Assert
            Assert.True(created);
            _mockWorktreeManager.Verify(x => x.CreateSharedContextAsync(
                It.Is<AgentSharedContext>(ctx => 
                    ctx.Files.ContainsKey("api-spec.yaml") &&
                    ctx.Files.ContainsKey("models.json")),
                It.IsAny<CancellationToken>()), 
                Times.Once);
        }
    }
}