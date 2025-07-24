using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.AIAgents
{
    public class AgentRegistry : IAgentRegistry
    {
        private readonly ConcurrentDictionary<Guid, IAgent> _agents = new();
        private readonly ILogger<AgentRegistry> _logger;

        public AgentRegistry(ILogger<AgentRegistry> logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public Task RegisterAsync(IAgent agent)
        {
            if (agent == null)
            {
                throw new ArgumentNullException(nameof(agent));
            }

            if (!_agents.TryAdd(agent.Id, agent))
            {
                throw new InvalidOperationException($"Agent {agent.Name} ({agent.Id}) is already registered");
            }

            _logger.LogInformation("Registered agent {AgentName} ({AgentId})", agent.Name, agent.Id);
            return Task.CompletedTask;
        }

        public Task UnregisterAsync(Guid agentId)
        {
            if (_agents.TryRemove(agentId, out var agent))
            {
                _logger.LogInformation("Unregistered agent {AgentName} ({AgentId})", agent.Name, agentId);
            }
            else
            {
                _logger.LogWarning("Attempted to unregister non-existent agent {AgentId}", agentId);
            }

            return Task.CompletedTask;
        }

        public Task<IAgent> GetAgentAsync(Guid agentId)
        {
            _agents.TryGetValue(agentId, out var agent);
            return Task.FromResult(agent);
        }

        public Task<IAgent> GetAgentByNameAsync(string name)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                throw new ArgumentException("Agent name cannot be empty", nameof(name));
            }

            var agent = _agents.Values.FirstOrDefault(a => a.Name.Equals(name, StringComparison.OrdinalIgnoreCase));
            return Task.FromResult(agent);
        }

        public Task<IEnumerable<IAgent>> GetAllAgentsAsync()
        {
            return Task.FromResult<IEnumerable<IAgent>>(_agents.Values.ToList());
        }

        public Task<IEnumerable<T>> GetAgentsByTypeAsync<T>() where T : IAgent
        {
            var agentsOfType = _agents.Values
                .OfType<T>()
                .ToList();

            return Task.FromResult<IEnumerable<T>>(agentsOfType);
        }

        public Task<IEnumerable<IAgent>> GetRunningAgentsAsync()
        {
            var runningAgents = _agents.Values
                .Where(a => a.Status == AgentStatus.Running)
                .ToList();

            return Task.FromResult<IEnumerable<IAgent>>(runningAgents);
        }

        public Task<AgentHealth> GetAgentHealthAsync(Guid agentId)
        {
            if (!_agents.TryGetValue(agentId, out var agent))
            {
                return Task.FromResult<AgentHealth>(null);
            }

            var health = new AgentHealth
            {
                AgentId = agentId,
                Status = agent.Status,
                IsHealthy = agent.Status == AgentStatus.Running || agent.Status == AgentStatus.Idle,
                LastHeartbeat = DateTime.UtcNow,
                Metrics = agent.Metrics,
                HealthMessage = GetHealthMessage(agent)
            };

            return Task.FromResult(health);
        }

        private string GetHealthMessage(IAgent agent)
        {
            return agent.Status switch
            {
                AgentStatus.Running => "Agent is running normally",
                AgentStatus.Failed => $"Agent failed: {agent.LastError}",
                AgentStatus.Stopped => "Agent is stopped",
                AgentStatus.Idle => "Agent is idle",
                _ => $"Agent status: {agent.Status}"
            };
        }
        
        // Synchronous methods for compatibility
        public IEnumerable<IAgent> GetAllAgents()
        {
            return _agents.Values;
        }
        
        public AgentStatus GetAgentStatus(Guid agentId)
        {
            if (_agents.TryGetValue(agentId, out var agent))
            {
                return agent.Status;
            }
            return AgentStatus.Failed;
        }
    }
}