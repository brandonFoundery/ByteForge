using System;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.AIAgents;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;
using Moq;

namespace ByteForgeFrontend.Tests.AIAgents
{
    public class AgentLifecycleTests
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly Mock<ILogger<BaseAgent>> _mockLogger;

        public AgentLifecycleTests()
        {
            var services = new ServiceCollection();
            _mockLogger = new Mock<ILogger<BaseAgent>>();
            services.AddSingleton(_mockLogger.Object);
            _serviceProvider = services.BuildServiceProvider();
        }

        [Fact]
        public async Task Agent_Should_Start_Successfully()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");

            // Act
            await agent.StartAsync();

            // Assert
            Assert.Equal(AgentStatus.Running, agent.Status);
            Assert.NotNull(agent.StartTime);
        }

        [Fact]
        public async Task Agent_Should_Stop_Successfully()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");
            await agent.StartAsync();

            // Act
            await agent.StopAsync();

            // Assert
            Assert.Equal(AgentStatus.Stopped, agent.Status);
            Assert.NotNull(agent.StopTime);
        }

        [Fact]
        public async Task Agent_Should_Handle_Cancellation()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");
            var cts = new CancellationTokenSource();
            
            // Act
            await agent.StartAsync();
            cts.Cancel();
            await agent.ExecuteAsync(cts.Token);

            // Assert
            Assert.Equal(AgentStatus.Stopped, agent.Status);
        }

        [Fact]
        public void Agent_Should_Have_Unique_Id()
        {
            // Arrange & Act
            var agent1 = new TestAgent(_serviceProvider, "agent1");
            var agent2 = new TestAgent(_serviceProvider, "agent2");

            // Assert
            Assert.NotEqual(agent1.Id, agent2.Id);
            Assert.Equal("agent1", agent1.Name);
            Assert.Equal("agent2", agent2.Name);
        }

        [Fact]
        public async Task Agent_Should_Track_Execution_Metrics()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");

            // Act
            await agent.StartAsync();
            await Task.Delay(100); // Simulate some work
            await agent.StopAsync();

            // Assert
            Assert.True(agent.ExecutionTime.TotalMilliseconds > 0);
            Assert.NotNull(agent.Metrics);
        }

        [Fact]
        public async Task Agent_Should_Handle_Errors_Gracefully()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "error-agent")
            {
                ShouldThrowError = true
            };

            // Act & Assert
            await agent.StartAsync();
            var ex = await Assert.ThrowsAsync<InvalidOperationException>(
                async () => await agent.ExecuteAsync(CancellationToken.None)
            );
            
            Assert.Equal(AgentStatus.Failed, agent.Status);
            Assert.NotNull(agent.LastError);
        }

        // Test implementation of BaseAgent for testing purposes
        private class TestAgent : BaseAgent
        {
            public bool ShouldThrowError { get; set; }

            public TestAgent(IServiceProvider serviceProvider, string name) 
                : base(serviceProvider, name)
            {
            }

            protected override async Task<AgentResult> PerformWorkAsync(CancellationToken cancellationToken)
            {
                if (ShouldThrowError)
                {
                    throw new InvalidOperationException("Test error");
                }

                await Task.Delay(50, cancellationToken);
                
                return new AgentResult
                {
                    Success = true,
                    Message = "Test work completed"
                };
            }
        }
    }
}