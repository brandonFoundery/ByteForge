using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.AIAgents
{
    public interface IAgentRegistry
    {
        Task RegisterAsync(IAgent agent);
        Task UnregisterAsync(Guid agentId);
        Task<IAgent> GetAgentAsync(Guid agentId);
        Task<IAgent> GetAgentByNameAsync(string name);
        Task<IEnumerable<IAgent>> GetAllAgentsAsync();
        Task<IEnumerable<T>> GetAgentsByTypeAsync<T>() where T : IAgent;
        Task<IEnumerable<IAgent>> GetRunningAgentsAsync();
        Task<AgentHealth> GetAgentHealthAsync(Guid agentId);
        
        // Synchronous methods for compatibility
        IEnumerable<IAgent> GetAllAgents();
        AgentStatus GetAgentStatus(Guid agentId);
    }

    public class AgentHealth
    {
        public Guid AgentId { get; set; }
        public AgentStatus Status { get; set; }
        public bool IsHealthy { get; set; }
        public DateTime LastHeartbeat { get; set; }
        public AgentMetrics Metrics { get; set; }
        public string HealthMessage { get; set; }
    }
}