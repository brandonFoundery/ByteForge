using System;
using System.Linq;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.AIAgents;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;
using Moq;

namespace ByteForgeFrontend.Tests.AIAgents
{
    public class AgentRegistryTests
    {
        private readonly IAgentRegistry _registry;
        private readonly IServiceProvider _serviceProvider;

        public AgentRegistryTests()
        {
            var services = new ServiceCollection();
            services.AddSingleton<IAgentRegistry, AgentRegistry>();
            services.AddSingleton(Mock.Of<ILogger<AgentRegistry>>());
            services.AddSingleton(Mock.Of<ILogger<BaseAgent>>());
            
            _serviceProvider = services.BuildServiceProvider();
            _registry = _serviceProvider.GetRequiredService<IAgentRegistry>();
        }

        [Fact]
        public async Task Should_Register_Agent_Successfully()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");

            // Act
            await _registry.RegisterAsync(agent);

            // Assert
            var registeredAgent = await _registry.GetAgentAsync(agent.Id);
            Assert.NotNull(registeredAgent);
            Assert.Equal(agent.Id, registeredAgent.Id);
        }

        [Fact]
        public async Task Should_Not_Register_Duplicate_Agent()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");
            await _registry.RegisterAsync(agent);

            // Act & Assert
            await Assert.ThrowsAsync<InvalidOperationException>(
                async () => await _registry.RegisterAsync(agent)
            );
        }

        [Fact]
        public async Task Should_Unregister_Agent_Successfully()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");
            await _registry.RegisterAsync(agent);

            // Act
            await _registry.UnregisterAsync(agent.Id);

            // Assert
            var result = await _registry.GetAgentAsync(agent.Id);
            Assert.Null(result);
        }

        [Fact]
        public async Task Should_Get_All_Registered_Agents()
        {
            // Arrange
            var agent1 = new TestAgent(_serviceProvider, "agent1");
            var agent2 = new TestAgent(_serviceProvider, "agent2");
            var agent3 = new TestAgent(_serviceProvider, "agent3");

            await _registry.RegisterAsync(agent1);
            await _registry.RegisterAsync(agent2);
            await _registry.RegisterAsync(agent3);

            // Act
            var agents = await _registry.GetAllAgentsAsync();

            // Assert
            Assert.Equal(3, agents.Count());
            Assert.Contains(agents, a => a.Name == "agent1");
            Assert.Contains(agents, a => a.Name == "agent2");
            Assert.Contains(agents, a => a.Name == "agent3");
        }

        [Fact]
        public async Task Should_Get_Agents_By_Type()
        {
            // Arrange
            var backendAgent = new BackendTestAgent(_serviceProvider, "backend1");
            var frontendAgent = new FrontendTestAgent(_serviceProvider, "frontend1");
            var backendAgent2 = new BackendTestAgent(_serviceProvider, "backend2");

            await _registry.RegisterAsync(backendAgent);
            await _registry.RegisterAsync(frontendAgent);
            await _registry.RegisterAsync(backendAgent2);

            // Act
            var backendAgents = await _registry.GetAgentsByTypeAsync<BackendTestAgent>();
            var frontendAgents = await _registry.GetAgentsByTypeAsync<FrontendTestAgent>();

            // Assert
            Assert.Equal(2, backendAgents.Count());
            Assert.Single(frontendAgents);
        }

        [Fact]
        public async Task Should_Get_Agent_By_Name()
        {
            // Arrange
            var agent1 = new TestAgent(_serviceProvider, "unique-name");
            var agent2 = new TestAgent(_serviceProvider, "another-name");

            await _registry.RegisterAsync(agent1);
            await _registry.RegisterAsync(agent2);

            // Act
            var found = await _registry.GetAgentByNameAsync("unique-name");

            // Assert
            Assert.NotNull(found);
            Assert.Equal("unique-name", found.Name);
        }

        [Fact]
        public async Task Should_Get_Running_Agents_Only()
        {
            // Arrange
            var agent1 = new TestAgent(_serviceProvider, "agent1");
            var agent2 = new TestAgent(_serviceProvider, "agent2");
            var agent3 = new TestAgent(_serviceProvider, "agent3");

            await _registry.RegisterAsync(agent1);
            await _registry.RegisterAsync(agent2);
            await _registry.RegisterAsync(agent3);

            await agent1.StartAsync();
            await agent2.StartAsync();
            // agent3 remains stopped

            // Act
            var runningAgents = await _registry.GetRunningAgentsAsync();

            // Assert
            Assert.Equal(2, runningAgents.Count());
            Assert.All(runningAgents, a => Assert.Equal(AgentStatus.Running, a.Status));
        }

        [Fact]
        public async Task Should_Monitor_Agent_Health()
        {
            // Arrange
            var agent = new TestAgent(_serviceProvider, "test-agent");
            await _registry.RegisterAsync(agent);
            await agent.StartAsync();

            // Act
            var health = await _registry.GetAgentHealthAsync(agent.Id);

            // Assert
            Assert.NotNull(health);
            Assert.Equal(agent.Id, health.AgentId);
            Assert.Equal(AgentStatus.Running, health.Status);
            Assert.True(health.IsHealthy);
        }

        // Test implementations
        private class TestAgent : BaseAgent
        {
            public TestAgent(IServiceProvider serviceProvider, string name) 
                : base(serviceProvider, name)
            {
            }

            protected override Task<AgentResult> PerformWorkAsync(CancellationToken cancellationToken)
            {
                return Task.FromResult(new AgentResult { Success = true });
            }
        }

        private class BackendTestAgent : TestAgent
        {
            public BackendTestAgent(IServiceProvider serviceProvider, string name) 
                : base(serviceProvider, name)
            {
            }
        }

        private class FrontendTestAgent : TestAgent
        {
            public FrontendTestAgent(IServiceProvider serviceProvider, string name) 
                : base(serviceProvider, name)
            {
            }
        }
    }
}