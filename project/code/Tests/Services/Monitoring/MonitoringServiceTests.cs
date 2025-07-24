using ByteForgeFrontend.Models.Monitoring;
using ByteForgeFrontend.Services.Monitoring;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using ByteForgeFrontend.Hubs;

namespace ByteForgeFrontend.Tests.Services.Monitoring;

public class MonitoringServiceTests
{
    private readonly Mock<IHubContext<NotificationHub>> _hubContextMock;
    private readonly Mock<ILogger<MonitoringService>> _loggerMock;
    private readonly MonitoringService _monitoringService;
    private readonly Mock<IHubClients> _mockClients;
    private readonly Mock<IClientProxy> _mockClientProxy;

    public MonitoringServiceTests()
    {
        _hubContextMock = new Mock<IHubContext<NotificationHub>>();
        _loggerMock = new Mock<ILogger<MonitoringService>>();
        _mockClients = new Mock<IHubClients>();
        _mockClientProxy = new Mock<IClientProxy>();

        _hubContextMock.Setup(x => x.Clients).Returns(_mockClients.Object);
        _mockClients.Setup(x => x.All).Returns(_mockClientProxy.Object);
        _mockClients.Setup(x => x.Group(It.IsAny<string>())).Returns(_mockClientProxy.Object);

        _monitoringService = new MonitoringService(_hubContextMock.Object, _loggerMock.Object);
    }

    #region Document Generation Monitoring Tests

    [Fact]
    public async Task GetDocumentGenerationStatusAsync_ReturnsCorrectStatus()
    {
        // Arrange
        var projectId = "test-project-123";
        await _monitoringService.StartDocumentGenerationMonitoringAsync(projectId, "BRD");
        await _monitoringService.UpdateDocumentProgressAsync(projectId, "BRD", 50, "In Progress");

        // Act
        var status = await _monitoringService.GetDocumentGenerationStatusAsync(projectId);

        // Assert
        Assert.NotNull(status);
        Assert.Equal(projectId, status.ProjectId);
        Assert.True(status.Documents.ContainsKey("BRD"));
        Assert.Equal(50, status.Documents["BRD"].Progress);
    }

    [Fact]
    public async Task UpdateDocumentProgressAsync_SendsSignalRNotification()
    {
        // Arrange
        var projectId = "test-project-123";
        var documentType = "PRD";
        var progress = 75;
        var status = "Generating sections";

        // Act
        await _monitoringService.UpdateDocumentProgressAsync(projectId, documentType, progress, status);

        // Assert
        _mockClientProxy.Verify(
            x => x.SendCoreAsync(
                "DocumentProgress",
                It.Is<object[]>(o => o.Length > 0),
                System.Threading.CancellationToken.None
            ),
            Times.AtLeastOnce
        );
    }

    [Fact]
    public async Task CompleteDocumentGenerationAsync_UpdatesStatusCorrectly()
    {
        // Arrange
        var projectId = "test-project-123";
        var documentType = "FRD";
        await _monitoringService.StartDocumentGenerationMonitoringAsync(projectId, documentType);

        // Act
        await _monitoringService.CompleteDocumentGenerationAsync(projectId, documentType, true);
        var status = await _monitoringService.GetDocumentGenerationStatusAsync(projectId);

        // Assert
        Assert.NotNull(status.Documents[documentType].CompletedAt);
        Assert.Equal(100, status.Documents[documentType].Progress);
        Assert.Equal("Completed", status.Documents[documentType].Status);
    }

    [Fact]
    public async Task CompleteDocumentGenerationAsync_WithError_SetsErrorStatus()
    {
        // Arrange
        var projectId = "test-project-123";
        var documentType = "TRD";
        var errorMessage = "LLM API rate limit exceeded";
        await _monitoringService.StartDocumentGenerationMonitoringAsync(projectId, documentType);

        // Act
        await _monitoringService.CompleteDocumentGenerationAsync(projectId, documentType, false, errorMessage);
        var status = await _monitoringService.GetDocumentGenerationStatusAsync(projectId);

        // Assert
        Assert.Equal(errorMessage, status.Documents[documentType].Error);
        Assert.Equal("Failed", status.Documents[documentType].Status);
        Assert.True(status.HasErrors);
    }

    #endregion

    #region AI Agent Monitoring Tests

    [Fact]
    public async Task GetActiveAgentsAsync_ReturnsOnlyActiveAgents()
    {
        // Arrange
        await _monitoringService.StartAgentMonitoringAsync("agent-1", "BackendAgent", "project-1");
        await _monitoringService.StartAgentMonitoringAsync("agent-2", "FrontendAgent", "project-1");
        await _monitoringService.UpdateAgentStatusAsync("agent-1", AgentState.Completed);

        // Act
        var activeAgents = await _monitoringService.GetActiveAgentsAsync();

        // Assert
        Assert.Single(activeAgents);
        Assert.Equal("agent-2", activeAgents[0].AgentId);
        Assert.Equal(AgentState.Running, activeAgents[0].State);
    }

    [Fact]
    public async Task UpdateAgentStatusAsync_TracksStateTransitions()
    {
        // Arrange
        var agentId = "test-agent-1";
        await _monitoringService.StartAgentMonitoringAsync(agentId, "SecurityAgent", "project-1");

        // Act
        await _monitoringService.UpdateAgentStatusAsync(agentId, AgentState.Running, "Processing authentication module");
        await _monitoringService.UpdateAgentStatusAsync(agentId, AgentState.Paused, "Waiting for dependency");
        await _monitoringService.UpdateAgentStatusAsync(agentId, AgentState.Running, "Resuming work");

        var agents = await _monitoringService.GetActiveAgentsAsync();
        var agent = agents.FirstOrDefault(a => a.AgentId == agentId);

        // Assert
        Assert.NotNull(agent);
        Assert.Equal(AgentState.Running, agent.State);
        Assert.Equal("Resuming work", agent.CurrentTask);
    }

    [Fact]
    public async Task RecordAgentMetricsAsync_UpdatesHealthReport()
    {
        // Arrange
        var agentId = "test-agent-2";
        await _monitoringService.StartAgentMonitoringAsync(agentId, "InfrastructureAgent", "project-2");

        var metrics = new AgentMetrics
        {
            CpuUsage = 45.5,
            MemoryUsage = 512.0,
            RequestCount = 100,
            ResponseTime = 250.0,
            CustomMetrics = new Dictionary<string, object> { { "CacheHitRate", 0.85 } }
        };

        // Act
        await _monitoringService.RecordAgentMetricsAsync(agentId, metrics);
        var healthReport = await _monitoringService.GetAgentHealthAsync(agentId);

        // Assert
        Assert.NotNull(healthReport);
        Assert.Equal(45.5, healthReport.CpuUsage);
        Assert.Equal(512.0, healthReport.MemoryUsage);
        Assert.True(healthReport.IsHealthy);
    }

    [Fact]
    public async Task GetAgentHealthAsync_DetectsUnhealthyAgent()
    {
        // Arrange
        var agentId = "test-agent-3";
        await _monitoringService.StartAgentMonitoringAsync(agentId, "BackendAgent", "project-3");

        // Simulate high resource usage
        var metrics = new AgentMetrics
        {
            CpuUsage = 95.0,
            MemoryUsage = 4096.0,
            RequestCount = 1000,
            ResponseTime = 5000.0
        };

        // Act
        await _monitoringService.RecordAgentMetricsAsync(agentId, metrics);
        var healthReport = await _monitoringService.GetAgentHealthAsync(agentId);

        // Assert
        Assert.False(healthReport.IsHealthy);
    }

    #endregion

    #region Project Monitoring Tests

    [Fact]
    public async Task GetProjectOverviewAsync_AggregatesProjectData()
    {
        // Arrange
        var projectId = "test-project-456";
        
        // Start document generation
        await _monitoringService.StartDocumentGenerationMonitoringAsync(projectId, "BRD");
        await _monitoringService.UpdateDocumentProgressAsync(projectId, "BRD", 100, "Completed");
        await _monitoringService.StartDocumentGenerationMonitoringAsync(projectId, "PRD");
        await _monitoringService.UpdateDocumentProgressAsync(projectId, "PRD", 50, "In Progress");

        // Start agents
        await _monitoringService.StartAgentMonitoringAsync("agent-p1", "BackendAgent", projectId);
        await _monitoringService.StartAgentMonitoringAsync("agent-p2", "FrontendAgent", projectId);

        // Act
        var overview = await _monitoringService.GetProjectOverviewAsync(projectId);

        // Assert
        Assert.Equal(projectId, overview.ProjectId);
        Assert.Equal(2, overview.DocumentProgress.Count);
        Assert.Equal(100, overview.DocumentProgress["BRD"]);
        Assert.Equal(50, overview.DocumentProgress["PRD"]);
        Assert.Equal(2, overview.ActiveAgents.Count);
        Assert.Equal(75, overview.OverallProgress); // Average of 100 and 50
    }

    [Fact]
    public async Task UpdateProjectProgressAsync_SendsRealtimeUpdate()
    {
        // Arrange
        var projectId = "test-project-789";
        var progress = 85;

        // Act
        await _monitoringService.UpdateProjectProgressAsync(projectId, progress);

        // Assert
        _mockClientProxy.Verify(
            x => x.SendCoreAsync(
                "ProjectProgress",
                It.Is<object[]>(o => o.Length > 0),
                System.Threading.CancellationToken.None
            ),
            Times.Once
        );
    }

    #endregion

    #region System Metrics Tests

    [Fact]
    public async Task GetSystemMetricsAsync_ReturnsCurrentMetrics()
    {
        // Act
        var metrics = await _monitoringService.GetSystemMetricsAsync();

        // Assert
        Assert.NotNull(metrics);
        Assert.True(metrics.CpuUsage >= 0 && metrics.CpuUsage <= 100);
        Assert.True(metrics.MemoryUsage >= 0);
        Assert.True(metrics.DiskSpaceAvailable > 0);
        Assert.NotNull(metrics.ServiceHealth);
    }

    [Fact]
    public async Task RecordSystemEventAsync_StoresEventWithCorrectSeverity()
    {
        // Arrange
        var systemEvent = new SystemEvent
        {
            EventType = "LLM_API_ERROR",
            Source = "OpenAIProvider",
            Message = "Rate limit exceeded",
            Severity = EventSeverity.Warning,
            Data = new Dictionary<string, object> { { "RetryAfter", 60 } }
        };

        // Act
        await _monitoringService.RecordSystemEventAsync(systemEvent);

        // Assert
        _mockClientProxy.Verify(
            x => x.SendCoreAsync(
                "SystemEvent",
                It.Is<object[]>(o => o.Length > 0),
                System.Threading.CancellationToken.None
            ),
            Times.Once
        );
    }

    #endregion

    #region Analytics Tests

    [Fact]
    public async Task GetDocumentGenerationAnalyticsAsync_CalculatesCorrectMetrics()
    {
        // Arrange
        var from = DateTime.UtcNow.AddDays(-7);
        var to = DateTime.UtcNow;

        // Simulate document generation history
        await _monitoringService.StartDocumentGenerationMonitoringAsync("proj-1", "BRD");
        await _monitoringService.CompleteDocumentGenerationAsync("proj-1", "BRD", true);
        
        await _monitoringService.StartDocumentGenerationMonitoringAsync("proj-2", "PRD");
        await _monitoringService.CompleteDocumentGenerationAsync("proj-2", "PRD", true);
        
        await _monitoringService.StartDocumentGenerationMonitoringAsync("proj-3", "FRD");
        await _monitoringService.CompleteDocumentGenerationAsync("proj-3", "FRD", false, "Error");

        // Act
        var analytics = await _monitoringService.GetDocumentGenerationAnalyticsAsync(from, to);

        // Assert
        Assert.Equal(3, analytics.TotalDocumentsGenerated);
        Assert.Equal(2, analytics.SuccessfulGenerations);
        Assert.Equal(1, analytics.FailedGenerations);
        Assert.Equal(66.67, analytics.SuccessRate, 2);
    }

    [Fact]
    public async Task GenerateSystemHealthReportAsync_IncludesAllComponents()
    {
        // Arrange
        await _monitoringService.RecordSystemEventAsync(new SystemEvent
        {
            EventType = "SERVICE_ERROR",
            Source = "Database",
            Message = "Connection timeout",
            Severity = EventSeverity.Error
        });

        // Act
        var report = await _monitoringService.GenerateSystemHealthReportAsync();

        // Assert
        Assert.NotNull(report);
        Assert.NotNull(report.CurrentMetrics);
        Assert.NotEmpty(report.Issues);
        Assert.NotEmpty(report.ServiceHealthHistory);
        Assert.True(report.GeneratedAt <= DateTime.UtcNow);
    }

    [Fact]
    public async Task ExportAnalyticsAsync_SupportsMultipleFormats()
    {
        // Arrange
        var from = DateTime.UtcNow.AddDays(-30);
        var to = DateTime.UtcNow;

        // Act & Assert for each format
        var formats = new[] { 
            AnalyticsExportFormat.CSV, 
            AnalyticsExportFormat.JSON, 
            AnalyticsExportFormat.PDF 
        };

        foreach (var format in formats)
        {
            var exportData = await _monitoringService.ExportAnalyticsAsync(format, from, to);
            Assert.NotNull(exportData);
            Assert.NotEmpty(exportData);
        }
    }

    #endregion

    #region Real-time Updates Tests

    [Fact]
    public async Task SubscribeToProjectUpdatesAsync_ReceivesUpdates()
    {
        // Arrange
        var projectId = "test-project-sub";
        var receivedUpdates = new List<ProjectUpdate>();
        
        await _monitoringService.SubscribeToProjectUpdatesAsync(projectId, update =>
        {
            receivedUpdates.Add(update);
        });

        // Act
        await _monitoringService.UpdateDocumentProgressAsync(projectId, "BRD", 25, "Starting");
        await Task.Delay(100); // Allow time for async processing

        // Assert
        Assert.NotEmpty(receivedUpdates);
        Assert.Contains(receivedUpdates, u => u.Component == "BRD" && u.Progress == 25);
    }

    [Fact]
    public async Task UnsubscribeFromProjectUpdatesAsync_StopsReceivingUpdates()
    {
        // Arrange
        var projectId = "test-project-unsub";
        var updateCount = 0;
        
        await _monitoringService.SubscribeToProjectUpdatesAsync(projectId, _ => updateCount++);
        await _monitoringService.UpdateDocumentProgressAsync(projectId, "BRD", 10, "Starting");
        await Task.Delay(50);
        
        var initialCount = updateCount;
        
        // Act
        await _monitoringService.UnsubscribeFromProjectUpdatesAsync(projectId);
        await _monitoringService.UpdateDocumentProgressAsync(projectId, "BRD", 20, "Continuing");
        await Task.Delay(50);

        // Assert
        Assert.Equal(initialCount, updateCount); // No new updates after unsubscribe
    }

    #endregion

    #region File System Monitoring Tests

    [Fact]
    public async Task StartFileSystemMonitoringAsync_RaisesEventsOnChanges()
    {
        // Arrange
        var monitoringPath = "/test/path";
        var eventRaised = false;
        FileSystemChangeEventArgs? capturedArgs = null;

        _monitoringService.FileSystemChanged += (sender, args) =>
        {
            eventRaised = true;
            capturedArgs = args;
        };

        // Act
        await _monitoringService.StartFileSystemMonitoringAsync(monitoringPath);
        
        // Simulate file change (this would normally come from FileSystemWatcher)
        await _monitoringService.SimulateFileChangeForTestingAsync(
            monitoringPath + "/test.md", 
            FileSystemChangeType.Created
        );

        // Assert
        Assert.True(eventRaised);
        Assert.NotNull(capturedArgs);
        Assert.Equal(FileSystemChangeType.Created, capturedArgs.ChangeType);
        Assert.Contains("test.md", capturedArgs.Path);
    }

    [Fact]
    public async Task StopFileSystemMonitoringAsync_StopsRaisingEvents()
    {
        // Arrange
        var monitoringPath = "/test/path";
        var eventCount = 0;

        _monitoringService.FileSystemChanged += (sender, args) => eventCount++;

        await _monitoringService.StartFileSystemMonitoringAsync(monitoringPath);
        await _monitoringService.SimulateFileChangeForTestingAsync(
            monitoringPath + "/test1.md", 
            FileSystemChangeType.Created
        );
        await Task.Delay(50);
        
        var initialCount = eventCount;

        // Act
        await _monitoringService.StopFileSystemMonitoringAsync(monitoringPath);
        await _monitoringService.SimulateFileChangeForTestingAsync(
            monitoringPath + "/test2.md", 
            FileSystemChangeType.Created
        );
        await Task.Delay(50);

        // Assert
        Assert.Equal(initialCount, eventCount); // No new events after stopping
    }

    #endregion
}