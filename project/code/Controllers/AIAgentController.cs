using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.AIAgents;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class AIAgentController : ControllerBase
    {
        private readonly IAgentRegistry _agentRegistry;
        private readonly IServiceProvider _serviceProvider;
        private readonly IClaudeCodeOrchestrator _claudeOrchestrator;
        private readonly ILogger<AIAgentController> _logger;

        public AIAgentController(
            IAgentRegistry agentRegistry,
            IServiceProvider serviceProvider,
            IClaudeCodeOrchestrator claudeOrchestrator,
            ILogger<AIAgentController> logger)
        {
            _agentRegistry = agentRegistry;
            _serviceProvider = serviceProvider;
            _claudeOrchestrator = claudeOrchestrator;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> GetAllAgents()
        {
            var agents = await _agentRegistry.GetAllAgentsAsync();
            var agentDtos = agents.Select(a => new AgentDto
            {
                Id = a.Id,
                Name = a.Name,
                Status = a.Status.ToString(),
                StartTime = a.StartTime,
                ExecutionTime = a.ExecutionTime,
                Metrics = a.Metrics
            });

            return Ok(agentDtos);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetAgent(Guid id)
        {
            var agent = await _agentRegistry.GetAgentAsync(id);
            if (agent == null)
            {
                return NotFound();
            }

            return Ok(new AgentDto
            {
                Id = agent.Id,
                Name = agent.Name,
                Status = agent.Status.ToString(),
                StartTime = agent.StartTime,
                ExecutionTime = agent.ExecutionTime,
                Metrics = agent.Metrics
            });
        }

        [HttpPost("start/{type}")]
        public async Task<IActionResult> StartAgent(string type, [FromBody] AgentStartRequest request)
        {
            try
            {
                IAgent agent = type.ToLower() switch
                {
                    "backend" => _serviceProvider.GetRequiredService<BackendAgent>(),
                    "frontend" => _serviceProvider.GetRequiredService<FrontendAgent>(),
                    "security" => _serviceProvider.GetRequiredService<SecurityAgent>(),
                    "infrastructure" => _serviceProvider.GetRequiredService<InfrastructureAgent>(),
                    _ => throw new ArgumentException($"Unknown agent type: {type}")
                };

                await _agentRegistry.RegisterAsync(agent);
                await agent.StartAsync();

                return Ok(new { agentId = agent.Id, status = "Started" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to start {AgentType} agent", type);
                return BadRequest(new { error = ex.Message });
            }
        }

        [HttpPost("{id}/stop")]
        public async Task<IActionResult> StopAgent(Guid id)
        {
            var agent = await _agentRegistry.GetAgentAsync(id);
            if (agent == null)
            {
                return NotFound();
            }

            await agent.StopAsync();
            await _agentRegistry.UnregisterAsync(id);

            return Ok(new { status = "Stopped" });
        }

        [HttpPost("generate")]
        public async Task<IActionResult> GenerateCode([FromBody] CodeGenerationRequest request)
        {
            try
            {
                var context = new AgentProjectContext
                {
                    ProjectId = request.ProjectId,
                    WorkingDirectory = request.WorkingDirectory,
                    Requirements = request.Requirements
                };

                var results = new Dictionary<string, AgentCodeGenerationResult>();

                // Create and execute agents based on request
                foreach (var agentType in request.AgentTypes)
                {
                    ICodeGeneratingAgent agent = agentType.ToLower() switch
                    {
                        "backend" => _serviceProvider.GetRequiredService<BackendAgent>(),
                        "frontend" => _serviceProvider.GetRequiredService<FrontendAgent>(),
                        "security" => _serviceProvider.GetRequiredService<SecurityAgent>(),
                        "infrastructure" => _serviceProvider.GetRequiredService<InfrastructureAgent>(),
                        _ => null
                    };

                    if (agent != null)
                    {
                        await _agentRegistry.RegisterAsync(agent);
                        await agent.StartAsync();
                        
                        var result = await agent.GenerateCodeAsync(context);
                        results[agentType] = result;
                        
                        await agent.StopAsync();
                        await _agentRegistry.UnregisterAsync(agent.Id);
                    }
                }

                return Ok(results);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Code generation failed");
                return BadRequest(new { error = ex.Message });
            }
        }

        [HttpPost("orchestrate")]
        public async Task<IActionResult> OrchestrateAgents([FromBody] OrchestrationRequest request)
        {
            try
            {
                var agentConfigs = request.Agents.Select(a => new ClaudeAgentConfig
                {
                    AgentName = a.Name,
                    WorktreeBranch = $"agent/{a.Name}",
                    BackendPort = a.BackendPort,
                    FrontendPort = a.FrontendPort
                }).ToList();

                var results = await _claudeOrchestrator.RunAgentsInParallelAsync(agentConfigs);
                var aggregated = await _claudeOrchestrator.AggregateResultsAsync(results);

                return Ok(aggregated);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Agent orchestration failed");
                return BadRequest(new { error = ex.Message });
            }
        }

        [HttpGet("health")]
        public async Task<IActionResult> GetAgentHealth()
        {
            var agents = await _agentRegistry.GetAllAgentsAsync();
            var healthStatuses = new List<object>();

            foreach (var agent in agents)
            {
                var health = await _agentRegistry.GetAgentHealthAsync(agent.Id);
                healthStatuses.Add(new
                {
                    agentId = agent.Id,
                    name = agent.Name,
                    status = health.Status.ToString(),
                    isHealthy = health.IsHealthy,
                    message = health.HealthMessage
                });
            }

            return Ok(healthStatuses);
        }
    }

    public class AgentDto
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public string Status { get; set; }
        public DateTime? StartTime { get; set; }
        public TimeSpan ExecutionTime { get; set; }
        public AgentMetrics Metrics { get; set; }
    }

    public class AgentStartRequest
    {
        public string Name { get; set; }
        public Dictionary<string, string> Configuration { get; set; }
    }

    public class CodeGenerationRequest
    {
        public Guid ProjectId { get; set; }
        public string WorkingDirectory { get; set; }
        public List<string> AgentTypes { get; set; }
        public RequirementsContext Requirements { get; set; }
    }

    public class OrchestrationRequest
    {
        public List<AgentConfig> Agents { get; set; }
    }

    public class AgentConfig
    {
        public string Name { get; set; }
        public int BackendPort { get; set; }
        public int FrontendPort { get; set; }
    }
}