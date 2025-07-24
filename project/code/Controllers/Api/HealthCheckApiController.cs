using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Api;
using ByteForgeFrontend.Services.AIAgents;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Services.Monitoring;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using StackExchange.Redis;

namespace ByteForgeFrontend.Controllers.Api
{
    /// <summary>
    /// Health check endpoints for monitoring service health and dependencies
    /// </summary>
    [ApiController]
    [Route("api/health")]
    public class HealthCheckApiController : ControllerBase
    {
        private readonly ILogger<HealthCheckApiController> _logger;
        private readonly IConfiguration _configuration;
        private readonly Data.ApplicationDbContext _dbContext;
        private readonly IAgentRegistry _agentRegistry;
        private readonly IMonitoringService _monitoringService;
        private readonly ILLMProviderFactory _llmProviderFactory;
        private readonly IProjectService _projectService;

        public HealthCheckApiController(
            ILogger<HealthCheckApiController> logger,
            IConfiguration configuration,
            Data.ApplicationDbContext dbContext,
            IAgentRegistry agentRegistry,
            IMonitoringService monitoringService,
            ILLMProviderFactory llmProviderFactory,
            IProjectService projectService)
        {
            _logger = logger;
            _configuration = configuration;
            _dbContext = dbContext;
            _agentRegistry = agentRegistry;
            _monitoringService = monitoringService;
            _llmProviderFactory = llmProviderFactory;
            _projectService = projectService;
        }

        /// <summary>
        /// Basic health check endpoint
        /// </summary>
        [HttpGet]
        [AllowAnonymous]
        public async Task<IActionResult> GetHealth()
        {
            var health = new HealthCheckResponse
            {
                Status = "Healthy",
                Timestamp = DateTime.UtcNow,
                Version = GetType().Assembly.GetName().Version?.ToString() ?? "1.0.0",
                Checks = new Dictionary<string, HealthCheckDetail>()
            };

            try
            {
                // Check database
                var dbHealth = await CheckDatabaseHealth();
                health.Checks["database"] = dbHealth;

                // Check Redis
                var redisHealth = await CheckRedisHealth();
                health.Checks["redis"] = redisHealth;

                // Check AI Agents
                var agentHealth = CheckAgentHealth();
                health.Checks["agents"] = agentHealth;

                // Check LLM Providers
                var llmHealth = await CheckLLMHealth();
                health.Checks["llm_providers"] = llmHealth;

                // Determine overall status
                var allHealthy = health.Checks.Values.All(c => c.Status == "Healthy");
                var anyUnhealthy = health.Checks.Values.Any(c => c.Status == "Unhealthy");

                if (anyUnhealthy)
                {
                    health.Status = "Unhealthy";
                    return StatusCode(503, health);
                }
                else if (!allHealthy)
                {
                    health.Status = "Degraded";
                }

                return Ok(health);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Health check failed");
                health.Status = "Unhealthy";
                health.Error = ex.Message;
                return StatusCode(503, health);
            }
        }

        /// <summary>
        /// Detailed health check with all subsystems
        /// </summary>
        [HttpGet("detailed")]
        [Authorize]
        public async Task<IActionResult> GetDetailedHealth()
        {
            var detailedHealth = new DetailedHealthCheckResponse
            {
                Status = "Healthy",
                Timestamp = DateTime.UtcNow,
                Version = GetType().Assembly.GetName().Version?.ToString() ?? "1.0.0",
                Environment = _configuration["ASPNETCORE_ENVIRONMENT"] ?? "Production",
                Subsystems = new Dictionary<string, SubsystemHealth>()
            };

            // Database subsystem
            detailedHealth.Subsystems["database"] = await GetDatabaseSubsystemHealth();

            // Caching subsystem
            detailedHealth.Subsystems["caching"] = await GetCachingSubsystemHealth();

            // AI Agent subsystem
            detailedHealth.Subsystems["ai_agents"] = GetAIAgentSubsystemHealth();

            // LLM subsystem
            detailedHealth.Subsystems["llm_providers"] = await GetLLMSubsystemHealth();

            // Monitoring subsystem
            detailedHealth.Subsystems["monitoring"] = GetMonitoringSubsystemHealth();

            // File storage subsystem
            detailedHealth.Subsystems["file_storage"] = GetFileStorageSubsystemHealth();

            // Calculate overall health
            var unhealthyCount = detailedHealth.Subsystems.Values.Count(s => s.Status == "Unhealthy");
            var degradedCount = detailedHealth.Subsystems.Values.Count(s => s.Status == "Degraded");

            if (unhealthyCount > 0)
            {
                detailedHealth.Status = "Unhealthy";
                return StatusCode(503, detailedHealth);
            }
            else if (degradedCount > 0)
            {
                detailedHealth.Status = "Degraded";
            }

            return Ok(detailedHealth);
        }

        /// <summary>
        /// Liveness probe for container orchestration
        /// </summary>
        [HttpGet("live")]
        [AllowAnonymous]
        public IActionResult GetLiveness()
        {
            return Ok(new { status = "alive", timestamp = DateTime.UtcNow });
        }

        /// <summary>
        /// Readiness probe for container orchestration
        /// </summary>
        [HttpGet("ready")]
        [AllowAnonymous]
        public async Task<IActionResult> GetReadiness()
        {
            try
            {
                // Quick database check
                await _dbContext.Database.ExecuteSqlRawAsync("SELECT 1");

                // Check critical services
                var agents = _agentRegistry.GetAllAgents();
                if (!agents.Any())
                {
                    return StatusCode(503, new { status = "not_ready", reason = "No agents registered" });
                }

                return Ok(new { status = "ready", timestamp = DateTime.UtcNow });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Readiness check failed");
                return StatusCode(503, new { status = "not_ready", reason = ex.Message });
            }
        }

        /// <summary>
        /// Performance metrics endpoint
        /// </summary>
        [HttpGet("metrics")]
        [Authorize]
        public async Task<IActionResult> GetMetrics()
        {
            var metrics = new PerformanceMetrics
            {
                Timestamp = DateTime.UtcNow,
                Cpu = GetCpuUsage(),
                Memory = GetMemoryUsage(),
                ActiveConnections = GetActiveConnections(),
                RequestsPerSecond = await GetRequestsPerSecond(),
                AverageResponseTime = await GetAverageResponseTime(),
                ErrorRate = await GetErrorRate()
            };

            return Ok(metrics);
        }

        // Private helper methods
        private async Task<HealthCheckDetail> CheckDatabaseHealth()
        {
            var detail = new HealthCheckDetail { Status = "Healthy" };

            try
            {
                var sw = System.Diagnostics.Stopwatch.StartNew();
                await _dbContext.Database.ExecuteSqlRawAsync("SELECT 1");
                sw.Stop();

                detail.ResponseTime = sw.ElapsedMilliseconds;
                detail.Details = new Dictionary<string, object>
                {
                    { "connection_string", _dbContext.Database.GetConnectionString()?.Split(';')[0] ?? "Unknown" },
                    { "pending_migrations", (await _dbContext.Database.GetPendingMigrationsAsync()).Count() }
                };
            }
            catch (Exception ex)
            {
                detail.Status = "Unhealthy";
                detail.Error = ex.Message;
                _logger.LogError(ex, "Database health check failed");
            }

            return detail;
        }

        private async Task<HealthCheckDetail> CheckRedisHealth()
        {
            var detail = new HealthCheckDetail { Status = "Healthy" };

            try
            {
                var redisConnection = _configuration.GetConnectionString("Redis") ?? "localhost:6379";
                using var redis = await ConnectionMultiplexer.ConnectAsync(redisConnection);
                
                var sw = System.Diagnostics.Stopwatch.StartNew();
                var db = redis.GetDatabase();
                await db.PingAsync();
                sw.Stop();

                detail.ResponseTime = sw.ElapsedMilliseconds;
                detail.Details = new Dictionary<string, object>
                {
                    { "endpoint", redis.GetEndPoints().FirstOrDefault()?.ToString() ?? "Unknown" },
                    { "connected", redis.IsConnected }
                };
            }
            catch (Exception ex)
            {
                detail.Status = "Unhealthy";
                detail.Error = ex.Message;
                _logger.LogWarning(ex, "Redis health check failed");
            }

            return detail;
        }

        private HealthCheckDetail CheckAgentHealth()
        {
            var detail = new HealthCheckDetail { Status = "Healthy" };

            try
            {
                var agents = _agentRegistry.GetAllAgents();
                var healthyAgents = agents.Count(a => _agentRegistry.GetAgentStatus(a.Id) == AgentStatus.Running);
                var totalAgents = agents.Count();

                if (totalAgents == 0)
                {
                    detail.Status = "Unhealthy";
                    detail.Error = "No agents registered";
                }
                else if (healthyAgents < totalAgents)
                {
                    detail.Status = "Degraded";
                }

                detail.Details = new Dictionary<string, object>
                {
                    { "total_agents", totalAgents },
                    { "healthy_agents", healthyAgents },
                    { "agent_statuses", agents.ToDictionary(a => a.Name, a => _agentRegistry.GetAgentStatus(a.Id).ToString()) }
                };
            }
            catch (Exception ex)
            {
                detail.Status = "Unhealthy";
                detail.Error = ex.Message;
                _logger.LogError(ex, "Agent health check failed");
            }

            return detail;
        }

        private async Task<HealthCheckDetail> CheckLLMHealth()
        {
            var detail = new HealthCheckDetail { Status = "Healthy" };
            var providerStatuses = new Dictionary<string, object>();

            try
            {
                var providers = new[] { "openai", "anthropic", "gemini", "grok" };
                var healthyProviders = 0;

                foreach (var providerName in providers)
                {
                    try
                    {
                        var provider = _llmProviderFactory.GetProvider(providerName);
                        if (provider != null && await provider.ValidateConnectionAsync())
                        {
                            healthyProviders++;
                            providerStatuses[providerName] = "Available";
                        }
                        else
                        {
                            providerStatuses[providerName] = "Unavailable";
                        }
                    }
                    catch
                    {
                        providerStatuses[providerName] = "Error";
                    }
                }

                if (healthyProviders == 0)
                {
                    detail.Status = "Unhealthy";
                    detail.Error = "No LLM providers available";
                }
                else if (healthyProviders < providers.Length)
                {
                    detail.Status = "Degraded";
                }

                detail.Details = new Dictionary<string, object>
                {
                    { "available_providers", healthyProviders },
                    { "total_providers", providers.Length },
                    { "provider_statuses", providerStatuses }
                };
            }
            catch (Exception ex)
            {
                detail.Status = "Unhealthy";
                detail.Error = ex.Message;
                _logger.LogError(ex, "LLM health check failed");
            }

            return detail;
        }

        // Subsystem health methods
        private async Task<SubsystemHealth> GetDatabaseSubsystemHealth()
        {
            var subsystem = new SubsystemHealth
            {
                Name = "Database",
                Status = "Healthy",
                Components = new List<ComponentHealth>()
            };

            // Check main database
            var mainDb = new ComponentHealth { Name = "SQL Server", Status = "Healthy" };
            try
            {
                var connectionString = _dbContext.Database.GetConnectionString();
                await _dbContext.Database.CanConnectAsync();
                
                // Get database statistics
                var stats = await _dbContext.Database.ExecuteSqlRawAsync(@"
                    SELECT 
                        COUNT(*) as TableCount 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'");

                mainDb.Metrics = new Dictionary<string, object>
                {
                    { "can_connect", true },
                    { "pending_migrations", (await _dbContext.Database.GetPendingMigrationsAsync()).Count() }
                };
            }
            catch (Exception ex)
            {
                mainDb.Status = "Unhealthy";
                mainDb.Error = ex.Message;
                subsystem.Status = "Unhealthy";
            }

            subsystem.Components.Add(mainDb);
            return subsystem;
        }

        private async Task<SubsystemHealth> GetCachingSubsystemHealth()
        {
            var subsystem = new SubsystemHealth
            {
                Name = "Caching",
                Status = "Healthy",
                Components = new List<ComponentHealth>()
            };

            // Check Redis
            var redis = new ComponentHealth { Name = "Redis Cache", Status = "Healthy" };
            try
            {
                var redisConnection = _configuration.GetConnectionString("Redis") ?? "localhost:6379";
                using var conn = await ConnectionMultiplexer.ConnectAsync(redisConnection);
                var db = conn.GetDatabase();
                
                var pingTime = await db.PingAsync();
                var server = conn.GetServer(conn.GetEndPoints().First());
                var info = await server.InfoAsync();

                redis.Metrics = new Dictionary<string, object>
                {
                    { "ping_ms", pingTime.TotalMilliseconds },
                    { "connected_clients", info.FirstOrDefault(s => s.Key == "Clients").FirstOrDefault(i => i.Key == "connected_clients").Value ?? "0" },
                    { "used_memory", info.FirstOrDefault(s => s.Key == "Memory").FirstOrDefault(i => i.Key == "used_memory_human").Value ?? "0" }
                };
            }
            catch (Exception ex)
            {
                redis.Status = "Unhealthy";
                redis.Error = ex.Message;
                subsystem.Status = "Unhealthy";
            }

            subsystem.Components.Add(redis);
            return subsystem;
        }

        private SubsystemHealth GetAIAgentSubsystemHealth()
        {
            var subsystem = new SubsystemHealth
            {
                Name = "AI Agents",
                Status = "Healthy",
                Components = new List<ComponentHealth>()
            };

            var agents = _agentRegistry.GetAllAgents();
            foreach (var agent in agents)
            {
                var status = _agentRegistry.GetAgentStatus(agent.Id);
                var component = new ComponentHealth
                {
                    Name = agent.Name,
                    Status = status == AgentStatus.Running ? "Healthy" : 
                             status == AgentStatus.Failed ? "Unhealthy" : "Degraded",
                    Metrics = new Dictionary<string, object>
                    {
                        { "agent_id", agent.Id },
                        { "status", status.ToString() },
                        { "execution_time", agent.ExecutionTime.TotalMilliseconds },
                        { "last_error", agent.LastError ?? "" }
                    }
                };

                subsystem.Components.Add(component);
                
                if (component.Status == "Unhealthy")
                {
                    subsystem.Status = "Unhealthy";
                }
                else if (component.Status == "Degraded" && subsystem.Status == "Healthy")
                {
                    subsystem.Status = "Degraded";
                }
            }

            return subsystem;
        }

        private async Task<SubsystemHealth> GetLLMSubsystemHealth()
        {
            var subsystem = new SubsystemHealth
            {
                Name = "LLM Providers",
                Status = "Healthy",
                Components = new List<ComponentHealth>()
            };

            var providers = new[] { "openai", "anthropic", "gemini", "grok" };
            
            foreach (var providerName in providers)
            {
                var component = new ComponentHealth { Name = providerName.ToUpper(), Status = "Healthy" };
                
                try
                {
                    var provider = _llmProviderFactory.GetProvider(providerName);
                    if (provider != null)
                    {
                        var isAvailable = await provider.ValidateConnectionAsync();
                        component.Status = isAvailable ? "Healthy" : "Unhealthy";
                        component.Metrics = new Dictionary<string, object>
                        {
                            { "available", isAvailable },
                            { "provider_type", provider.GetType().Name }
                        };
                    }
                    else
                    {
                        component.Status = "Unhealthy";
                        component.Error = "Provider not configured";
                    }
                }
                catch (Exception ex)
                {
                    component.Status = "Unhealthy";
                    component.Error = ex.Message;
                }

                subsystem.Components.Add(component);
                
                if (component.Status == "Unhealthy" && subsystem.Status != "Unhealthy")
                {
                    subsystem.Status = subsystem.Components.Any(c => c.Status == "Healthy") ? "Degraded" : "Unhealthy";
                }
            }

            return subsystem;
        }

        private SubsystemHealth GetMonitoringSubsystemHealth()
        {
            var subsystem = new SubsystemHealth
            {
                Name = "Monitoring",
                Status = "Healthy",
                Components = new List<ComponentHealth>()
            };

            var monitoring = new ComponentHealth { Name = "Monitoring Service", Status = "Healthy" };
            
            try
            {
                var status = _monitoringService.GetSystemStatus();
                monitoring.Metrics = new Dictionary<string, object>
                {
                    { "active_monitors", status.Result?.ActiveMonitors ?? 0 },
                    { "total_events", status.Result?.TotalEvents ?? 0 }
                };
            }
            catch (Exception ex)
            {
                monitoring.Status = "Unhealthy";
                monitoring.Error = ex.Message;
                subsystem.Status = "Unhealthy";
            }

            subsystem.Components.Add(monitoring);
            return subsystem;
        }

        private SubsystemHealth GetFileStorageSubsystemHealth()
        {
            var subsystem = new SubsystemHealth
            {
                Name = "File Storage",
                Status = "Healthy",
                Components = new List<ComponentHealth>()
            };

            var localStorage = new ComponentHealth { Name = "Local Storage", Status = "Healthy" };
            
            try
            {
                var basePath = _configuration["Storage:BasePath"] ?? "./storage";
                var directoryInfo = new System.IO.DirectoryInfo(basePath);
                
                if (directoryInfo.Exists)
                {
                    var driveInfo = new System.IO.DriveInfo(directoryInfo.Root.FullName);
                    localStorage.Metrics = new Dictionary<string, object>
                    {
                        { "available_space_gb", driveInfo.AvailableFreeSpace / (1024 * 1024 * 1024) },
                        { "total_space_gb", driveInfo.TotalSize / (1024 * 1024 * 1024) },
                        { "used_percentage", (driveInfo.TotalSize - driveInfo.AvailableFreeSpace) * 100.0 / driveInfo.TotalSize }
                    };
                }
                else
                {
                    localStorage.Status = "Unhealthy";
                    localStorage.Error = "Storage directory not found";
                    subsystem.Status = "Unhealthy";
                }
            }
            catch (Exception ex)
            {
                localStorage.Status = "Unhealthy";
                localStorage.Error = ex.Message;
                subsystem.Status = "Unhealthy";
            }

            subsystem.Components.Add(localStorage);
            return subsystem;
        }

        // Performance metric methods
        private double GetCpuUsage()
        {
            // Simplified CPU usage - in production, use performance counters
            return System.Diagnostics.Process.GetCurrentProcess().TotalProcessorTime.TotalMilliseconds / Environment.ProcessorCount / Environment.TickCount * 100;
        }

        private MemoryUsage GetMemoryUsage()
        {
            var process = System.Diagnostics.Process.GetCurrentProcess();
            return new MemoryUsage
            {
                WorkingSetMb = process.WorkingSet64 / (1024 * 1024),
                PrivateMemoryMb = process.PrivateMemorySize64 / (1024 * 1024),
                VirtualMemoryMb = process.VirtualMemorySize64 / (1024 * 1024),
                GcHeapMb = GC.GetTotalMemory(false) / (1024 * 1024)
            };
        }

        private int GetActiveConnections()
        {
            // This would be tracked by middleware in production
            return HttpContext.RequestServices.GetServices<IHttpContextAccessor>().Count();
        }

        private async Task<double> GetRequestsPerSecond()
        {
            // In production, this would come from monitoring service
            var analytics = await _monitoringService.GetAnalyticsAsync("minute");
            return 100; // Default value since RequestsPerSecond is not in AnalyticsData
        }

        private async Task<double> GetAverageResponseTime()
        {
            // In production, this would come from monitoring service
            var analytics = await _monitoringService.GetAnalyticsAsync("minute");
            return analytics?.AverageGenerationTime ?? 0;
        }

        private async Task<double> GetErrorRate()
        {
            // In production, this would come from monitoring service
            var analytics = await _monitoringService.GetAnalyticsAsync("minute");
            if (analytics != null && analytics.TotalDocumentsGenerated > 0)
            {
                return (double)analytics.FailedGenerations / analytics.TotalDocumentsGenerated;
            }
            return 0;
        }
    }

    // Response models
    public class HealthCheckResponse
    {
        public string Status { get; set; }
        public DateTime Timestamp { get; set; }
        public string Version { get; set; }
        public Dictionary<string, HealthCheckDetail> Checks { get; set; }
        public string Error { get; set; }
    }

    public class HealthCheckDetail
    {
        public string Status { get; set; }
        public long? ResponseTime { get; set; }
        public Dictionary<string, object> Details { get; set; }
        public string Error { get; set; }
    }

    public class DetailedHealthCheckResponse
    {
        public string Status { get; set; }
        public DateTime Timestamp { get; set; }
        public string Version { get; set; }
        public string Environment { get; set; }
        public Dictionary<string, SubsystemHealth> Subsystems { get; set; }
    }

    public class SubsystemHealth
    {
        public string Name { get; set; }
        public string Status { get; set; }
        public List<ComponentHealth> Components { get; set; }
    }

    public class ComponentHealth
    {
        public string Name { get; set; }
        public string Status { get; set; }
        public Dictionary<string, object> Metrics { get; set; }
        public string Error { get; set; }
    }

    public class PerformanceMetrics
    {
        public DateTime Timestamp { get; set; }
        public double Cpu { get; set; }
        public MemoryUsage Memory { get; set; }
        public int ActiveConnections { get; set; }
        public double RequestsPerSecond { get; set; }
        public double AverageResponseTime { get; set; }
        public double ErrorRate { get; set; }
    }

    public class MemoryUsage
    {
        public long WorkingSetMb { get; set; }
        public long PrivateMemoryMb { get; set; }
        public long VirtualMemoryMb { get; set; }
        public long GcHeapMb { get; set; }
    }
}