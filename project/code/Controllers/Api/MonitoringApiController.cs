using ByteForgeFrontend.Models.Monitoring;
using ByteForgeFrontend.Services.Monitoring;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[ApiController]
[Route("api/monitoring")]
[Authorize]
public class MonitoringApiController : ControllerBase
{
    private readonly IMonitoringService _monitoringService;
    private readonly ILogger<MonitoringApiController> _logger;

    public MonitoringApiController(IMonitoringService monitoringService, ILogger<MonitoringApiController> logger)
    {
        _monitoringService = monitoringService;
        _logger = logger;
    }

    #region Document Generation Endpoints

    [HttpGet("documents/{projectId}/status")]
    public async Task<IActionResult> GetDocumentGenerationStatus(string projectId)
    {
        try
        {
            var status = await _monitoringService.GetDocumentGenerationStatusAsync(projectId);
            return Ok(status);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting document generation status for project {ProjectId}", projectId);
            return StatusCode(500, new { error = "Failed to retrieve document generation status" });
        }
    }

    [HttpGet("documents/{projectId}/progress")]
    public async Task<IActionResult> GetDocumentProgress(string projectId)
    {
        try
        {
            var progress = await _monitoringService.GetDocumentProgressAsync(projectId);
            return Ok(progress);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting document progress for project {ProjectId}", projectId);
            return StatusCode(500, new { error = "Failed to retrieve document progress" });
        }
    }

    [HttpPost("documents/{projectId}/start")]
    public async Task<IActionResult> StartDocumentGeneration(string projectId, [FromBody] StartDocumentGenerationRequest request)
    {
        try
        {
            await _monitoringService.StartDocumentGenerationMonitoringAsync(projectId, request.DocumentType);
            return Ok(new { message = "Document generation monitoring started" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting document generation monitoring for project {ProjectId}", projectId);
            return StatusCode(500, new { error = "Failed to start document generation monitoring" });
        }
    }

    [HttpPut("documents/{projectId}/progress")]
    public async Task<IActionResult> UpdateDocumentProgress(string projectId, [FromBody] UpdateDocumentProgressRequest request)
    {
        try
        {
            await _monitoringService.UpdateDocumentProgressAsync(projectId, request.DocumentType, request.Progress, request.Status);
            return Ok(new { message = "Document progress updated" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating document progress for project {ProjectId}", projectId);
            return StatusCode(500, new { error = "Failed to update document progress" });
        }
    }

    [HttpPost("documents/{projectId}/complete")]
    public async Task<IActionResult> CompleteDocumentGeneration(string projectId, [FromBody] CompleteDocumentGenerationRequest request)
    {
        try
        {
            await _monitoringService.CompleteDocumentGenerationAsync(projectId, request.DocumentType, request.Success, request.Error);
            return Ok(new { message = "Document generation completed" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error completing document generation for project {ProjectId}", projectId);
            return StatusCode(500, new { error = "Failed to complete document generation" });
        }
    }

    #endregion

    #region AI Agent Endpoints

    [HttpGet("agents/active")]
    public async Task<IActionResult> GetActiveAgents()
    {
        try
        {
            var agents = await _monitoringService.GetActiveAgentsAsync();
            return Ok(agents);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting active agents");
            return StatusCode(500, new { error = "Failed to retrieve active agents" });
        }
    }

    [HttpGet("agents/{agentId}/health")]
    public async Task<IActionResult> GetAgentHealth(string agentId)
    {
        try
        {
            var health = await _monitoringService.GetAgentHealthAsync(agentId);
            return Ok(health);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting agent health for {AgentId}", agentId);
            return StatusCode(500, new { error = "Failed to retrieve agent health" });
        }
    }

    [HttpPost("agents/{agentId}/start")]
    public async Task<IActionResult> StartAgentMonitoring(string agentId, [FromBody] StartAgentMonitoringRequest request)
    {
        try
        {
            await _monitoringService.StartAgentMonitoringAsync(agentId, request.AgentType, request.ProjectId);
            return Ok(new { message = "Agent monitoring started" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting agent monitoring for {AgentId}", agentId);
            return StatusCode(500, new { error = "Failed to start agent monitoring" });
        }
    }

    [HttpPut("agents/{agentId}/status")]
    public async Task<IActionResult> UpdateAgentStatus(string agentId, [FromBody] UpdateAgentStatusRequest request)
    {
        try
        {
            await _monitoringService.UpdateAgentStatusAsync(agentId, request.State, request.Message);
            return Ok(new { message = "Agent status updated" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating agent status for {AgentId}", agentId);
            return StatusCode(500, new { error = "Failed to update agent status" });
        }
    }

    [HttpPost("agents/{agentId}/metrics")]
    public async Task<IActionResult> RecordAgentMetrics(string agentId, [FromBody] AgentMetrics metrics)
    {
        try
        {
            await _monitoringService.RecordAgentMetricsAsync(agentId, metrics);
            return Ok(new { message = "Agent metrics recorded" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording agent metrics for {AgentId}", agentId);
            return StatusCode(500, new { error = "Failed to record agent metrics" });
        }
    }

    #endregion

    #region Project Monitoring Endpoints

    [HttpGet("projects/{projectId}/overview")]
    public async Task<IActionResult> GetProjectOverview(string projectId)
    {
        try
        {
            var overview = await _monitoringService.GetProjectOverviewAsync(projectId);
            return Ok(overview);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting project overview for {ProjectId}", projectId);
            return StatusCode(500, new { error = "Failed to retrieve project overview" });
        }
    }

    [HttpGet("projects/status")]
    public async Task<IActionResult> GetAllProjectsStatus()
    {
        try
        {
            var status = await _monitoringService.GetAllProjectsStatusAsync();
            return Ok(status);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting all projects status");
            return StatusCode(500, new { error = "Failed to retrieve projects status" });
        }
    }

    [HttpPut("projects/{projectId}/progress")]
    public async Task<IActionResult> UpdateProjectProgress(string projectId, [FromBody] UpdateProjectProgressRequest request)
    {
        try
        {
            await _monitoringService.UpdateProjectProgressAsync(projectId, request.Progress);
            return Ok(new { message = "Project progress updated" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating project progress for {ProjectId}", projectId);
            return StatusCode(500, new { error = "Failed to update project progress" });
        }
    }

    #endregion

    #region System Metrics Endpoints

    [HttpGet("system/metrics")]
    public async Task<IActionResult> GetSystemMetrics()
    {
        try
        {
            var metrics = await _monitoringService.GetSystemMetricsAsync();
            return Ok(metrics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting system metrics");
            return StatusCode(500, new { error = "Failed to retrieve system metrics" });
        }
    }

    [HttpGet("system/resources")]
    public async Task<IActionResult> GetResourceUsage()
    {
        try
        {
            var usage = await _monitoringService.GetResourceUsageAsync();
            return Ok(usage);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting resource usage");
            return StatusCode(500, new { error = "Failed to retrieve resource usage" });
        }
    }

    [HttpPost("system/events")]
    public async Task<IActionResult> RecordSystemEvent([FromBody] SystemEvent systemEvent)
    {
        try
        {
            await _monitoringService.RecordSystemEventAsync(systemEvent);
            return Ok(new { message = "System event recorded" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording system event");
            return StatusCode(500, new { error = "Failed to record system event" });
        }
    }

    #endregion

    #region Analytics Endpoints

    [HttpGet("analytics/documents")]
    public async Task<IActionResult> GetDocumentGenerationAnalytics([FromQuery] DateTime? from = null, [FromQuery] DateTime? to = null)
    {
        try
        {
            var fromDate = from ?? DateTime.UtcNow.AddDays(-30);
            var toDate = to ?? DateTime.UtcNow;
            
            var analytics = await _monitoringService.GetDocumentGenerationAnalyticsAsync(fromDate, toDate);
            return Ok(analytics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting document generation analytics");
            return StatusCode(500, new { error = "Failed to retrieve document generation analytics" });
        }
    }

    [HttpGet("analytics/agents")]
    public async Task<IActionResult> GetAgentPerformanceAnalytics([FromQuery] DateTime? from = null, [FromQuery] DateTime? to = null)
    {
        try
        {
            var fromDate = from ?? DateTime.UtcNow.AddDays(-30);
            var toDate = to ?? DateTime.UtcNow;
            
            var analytics = await _monitoringService.GetAgentPerformanceAnalyticsAsync(fromDate, toDate);
            return Ok(analytics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting agent performance analytics");
            return StatusCode(500, new { error = "Failed to retrieve agent performance analytics" });
        }
    }

    [HttpGet("analytics/health-report")]
    public async Task<IActionResult> GenerateSystemHealthReport()
    {
        try
        {
            var report = await _monitoringService.GenerateSystemHealthReportAsync();
            return Ok(report);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating system health report");
            return StatusCode(500, new { error = "Failed to generate system health report" });
        }
    }

    [HttpGet("analytics/export")]
    public async Task<IActionResult> ExportAnalytics([FromQuery] AnalyticsExportFormat format = AnalyticsExportFormat.JSON, 
        [FromQuery] DateTime? from = null, [FromQuery] DateTime? to = null)
    {
        try
        {
            var fromDate = from ?? DateTime.UtcNow.AddDays(-30);
            var toDate = to ?? DateTime.UtcNow;
            
            var data = await _monitoringService.ExportAnalyticsAsync(format, fromDate, toDate);
            
            string contentType = format switch
            {
                AnalyticsExportFormat.CSV => "text/csv",
                AnalyticsExportFormat.JSON => "application/json",
                AnalyticsExportFormat.PDF => "application/pdf",
                AnalyticsExportFormat.Excel => "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                _ => "application/octet-stream"
            };
            
            string fileName = $"analytics_{fromDate:yyyyMMdd}_{toDate:yyyyMMdd}.{format.ToString().ToLower()}";
            
            return File(data, contentType, fileName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error exporting analytics");
            return StatusCode(500, new { error = "Failed to export analytics" });
        }
    }

    #endregion

    #region File System Monitoring Endpoints

    [HttpPost("filesystem/start")]
    public async Task<IActionResult> StartFileSystemMonitoring([FromBody] FileSystemMonitoringRequest request)
    {
        try
        {
            await _monitoringService.StartFileSystemMonitoringAsync(request.Path);
            return Ok(new { message = "File system monitoring started" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting file system monitoring for {Path}", request.Path);
            return StatusCode(500, new { error = "Failed to start file system monitoring" });
        }
    }

    [HttpPost("filesystem/stop")]
    public async Task<IActionResult> StopFileSystemMonitoring([FromBody] FileSystemMonitoringRequest request)
    {
        try
        {
            await _monitoringService.StopFileSystemMonitoringAsync(request.Path);
            return Ok(new { message = "File system monitoring stopped" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping file system monitoring for {Path}", request.Path);
            return StatusCode(500, new { error = "Failed to stop file system monitoring" });
        }
    }

    #endregion
}

#region Request Models

public class StartDocumentGenerationRequest
{
    public string DocumentType { get; set; } = string.Empty;
}

public class UpdateDocumentProgressRequest
{
    public string DocumentType { get; set; } = string.Empty;
    public int Progress { get; set; }
    public string Status { get; set; } = string.Empty;
}

public class CompleteDocumentGenerationRequest
{
    public string DocumentType { get; set; } = string.Empty;
    public bool Success { get; set; }
    public string? Error { get; set; }
}

public class StartAgentMonitoringRequest
{
    public string AgentType { get; set; } = string.Empty;
    public string ProjectId { get; set; } = string.Empty;
}

public class UpdateAgentStatusRequest
{
    public AgentState State { get; set; }
    public string? Message { get; set; }
}

public class UpdateProjectProgressRequest
{
    public int Progress { get; set; }
}

public class FileSystemMonitoringRequest
{
    public string Path { get; set; } = string.Empty;
}

#endregion