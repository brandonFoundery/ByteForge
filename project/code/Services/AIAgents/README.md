# AI Agent System Documentation

## Overview

The AI Agent System is a sophisticated framework for orchestrating specialized AI agents that generate code based on requirements documents. It integrates with Claude Code and other LLM services to produce high-quality, production-ready code across different layers of the application.

## Architecture

### Core Components

1. **Base Agent Framework**
   - `IAgent` - Core agent interface
   - `BaseAgent` - Abstract base class with lifecycle management
   - `AgentStatus` - Agent state enumeration
   - `AgentMetrics` - Performance tracking

2. **Agent Communication**
   - `IAgentMessageBus` - Inter-agent messaging
   - `AgentMessage` - Message structure
   - Supports request/response and broadcast patterns

3. **Agent Registry**
   - `IAgentRegistry` - Agent registration and discovery
   - Health monitoring capabilities
   - Type-based agent queries

4. **Specialized Agents**
   - `BackendAgent` - ASP.NET Core API generation
   - `FrontendAgent` - React/TypeScript component generation
   - `SecurityAgent` - Authentication/authorization implementation
   - `InfrastructureAgent` - Docker/CI/CD configuration

5. **Claude Code Integration**
   - `IClaudeCodeOrchestrator` - Claude Code execution orchestration
   - `IWorktreeManager` - Git worktree management
   - `IClaudeCodeExecutor` - Claude command execution
   - `IAgentMonitor` - Progress monitoring

## Usage

### Starting an Agent

```csharp
// Via dependency injection
var backendAgent = serviceProvider.GetRequiredService<BackendAgent>();
await agentRegistry.RegisterAsync(backendAgent);
await backendAgent.StartAsync();
```

### Generating Code

```csharp
var context = new AgentProjectContext
{
    ProjectId = Guid.NewGuid(),
    WorkingDirectory = "/project/backend",
    Requirements = new RequirementsContext
    {
        FunctionalRequirements = "User management API",
        TechnicalRequirements = "ASP.NET Core 8.0, Clean Architecture"
    }
};

var result = await backendAgent.GenerateCodeAsync(context);
```

### Agent Communication

```csharp
// Subscribe to messages
await messageBus.SubscribeAsync(agentId, async (message) =>
{
    Console.WriteLine($"Received: {message.Content}");
});

// Send a message
await messageBus.PublishAsync(new AgentMessage
{
    SenderId = senderAgent.Id,
    ReceiverId = receiverAgent.Id,
    Type = MessageType.Request,
    Content = "Generate matching frontend for UserController"
});
```

### Orchestrating Multiple Agents

```csharp
var agents = new[]
{
    new ClaudeAgentConfig { AgentName = "backend-agent", BackendPort = 5010 },
    new ClaudeAgentConfig { AgentName = "frontend-agent", BackendPort = 5011 }
};

var results = await orchestrator.RunAgentsInParallelAsync(agents);
var aggregated = await orchestrator.AggregateResultsAsync(results);
```

## API Endpoints

### Agent Management

- `GET /api/AIAgent` - List all registered agents
- `GET /api/AIAgent/{id}` - Get specific agent details
- `POST /api/AIAgent/start/{type}` - Start a new agent
- `POST /api/AIAgent/{id}/stop` - Stop an agent
- `GET /api/AIAgent/health` - Get health status of all agents

### Code Generation

- `POST /api/AIAgent/generate` - Generate code using specified agents
- `POST /api/AIAgent/orchestrate` - Orchestrate multiple agents in parallel

## Agent Types

### Backend Agent
Generates:
- API Controllers with CQRS pattern
- Business services and interfaces
- Data models and DTOs
- Repository implementations
- Validation logic

### Frontend Agent
Generates:
- React functional components
- TypeScript interfaces
- API service modules
- Material-UI styled components
- Routing configuration

### Security Agent
Generates:
- JWT authentication services
- Authorization handlers and policies
- Security middleware
- Audit logging services
- Identity management code

### Infrastructure Agent
Generates:
- Dockerfiles and docker-compose
- CI/CD pipeline configurations
- Terraform/IaC scripts
- Kubernetes manifests
- Monitoring configurations

## Configuration

Agents can be configured through environment variables:

```bash
BACKEND_PORT=5004
FRONTEND_PORT=3004
AGENT_NAME=backend-agent
```

## Testing

The AI Agent system includes comprehensive test coverage:

- `AgentLifecycleTests` - Agent startup, shutdown, and state management
- `AgentCommunicationTests` - Message bus and inter-agent communication
- `AgentRegistryTests` - Registration, discovery, and health monitoring
- `SpecializedAgentTests` - Code generation for each agent type
- `ClaudeCodeIntegrationTests` - Worktree management and orchestration

## Best Practices

1. **Isolation**: Each agent runs in its own worktree to prevent conflicts
2. **Error Handling**: Agents gracefully handle failures and report errors
3. **Monitoring**: Use the agent monitor to track progress
4. **Resource Management**: Properly stop agents and cleanup worktrees
5. **Communication**: Use the message bus for agent coordination

## Extension Points

To create a custom agent:

1. Inherit from `BaseAgent`
2. Implement `ICodeGeneratingAgent` if it generates code
3. Override `PerformWorkAsync` for the main logic
4. Register in the DI container
5. Add to the agent controller switch statement

```csharp
public class CustomAgent : BaseAgent, ICodeGeneratingAgent
{
    public CustomAgent(IServiceProvider serviceProvider, string name) 
        : base(serviceProvider, name) { }

    public async Task<AgentCodeGenerationResult> GenerateCodeAsync(
        AgentProjectContext context)
    {
        // Implementation
    }

    protected override async Task<AgentResult> PerformWorkAsync(
        CancellationToken cancellationToken)
    {
        // Background work
    }
}
```

## Troubleshooting

Common issues:

1. **Agent fails to start**: Check service registration and dependencies
2. **No code generated**: Verify LLM service configuration
3. **Communication failures**: Ensure agents are registered with message bus
4. **Worktree conflicts**: Clean up old worktrees before running

## Future Enhancements

- Real-time streaming of generation progress
- Agent templates and presets
- Code validation and linting integration
- Automated testing of generated code
- Agent performance optimization
- Multi-project support