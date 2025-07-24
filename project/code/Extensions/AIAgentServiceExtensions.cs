using ByteForgeFrontend.Services.AIAgents;
using Microsoft.Extensions.DependencyInjection;

namespace ByteForgeFrontend.Extensions
{
    public static class AIAgentServiceExtensions
    {
        public static IServiceCollection AddAIAgentServices(this IServiceCollection services)
        {
            // Core agent services
            services.AddSingleton<IAgentRegistry, AgentRegistry>();
            services.AddSingleton<IAgentMessageBus, AgentMessageBus>();
            
            // Specialized agents - register as transient so each instance is unique
            services.AddTransient<BackendAgent>();
            services.AddTransient<FrontendAgent>();
            services.AddTransient<SecurityAgent>();
            services.AddTransient<InfrastructureAgent>();
            
            // Claude Code integration services
            services.AddSingleton<IClaudeCodeOrchestrator, ClaudeCodeOrchestrator>();
            services.AddSingleton<IWorktreeManager, WorktreeManager>();
            services.AddSingleton<IClaudeCodeExecutor, ClaudeCodeExecutor>();
            services.AddSingleton<IAgentMonitor, AgentMonitor>();
            
            return services;
        }
    }
}