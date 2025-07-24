using ByteForgeFrontend.Models.Monitoring;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Monitoring;

public interface IMonitoringService
{
    // Document Generation Monitoring
    Task<DocumentGenerationStatus> GetDocumentGenerationStatusAsync(string projectId);
    Task<List<DocumentGenerationProgress>> GetDocumentProgressAsync(string projectId);
    Task StartDocumentGenerationMonitoringAsync(string projectId, string documentType);
    Task UpdateDocumentProgressAsync(string projectId, string documentType, int progress, string status);
    Task CompleteDocumentGenerationAsync(string projectId, string documentType, bool success, string? error = null);

    // AI Agent Monitoring
    Task<List<AgentStatus>> GetActiveAgentsAsync();
    Task<AgentHealthReport> GetAgentHealthAsync(string agentId);
    Task StartAgentMonitoringAsync(string agentId, string agentType, string projectId);
    Task UpdateAgentStatusAsync(string agentId, AgentState state, string? message = null);
    Task RecordAgentMetricsAsync(string agentId, AgentMetrics metrics);

    // Project Monitoring
    Task<ProjectOverview> GetProjectOverviewAsync(string projectId);
    Task<List<ProjectStatus>> GetAllProjectsStatusAsync();
    Task UpdateProjectProgressAsync(string projectId, int overallProgress);

    // System Metrics
    Task<SystemMetrics> GetSystemMetricsAsync();
    Task<ResourceUsage> GetResourceUsageAsync();
    Task<SystemStatus> GetSystemStatus();
    Task RecordSystemEventAsync(SystemEvent systemEvent);

    // Real-time Updates
    Task SubscribeToProjectUpdatesAsync(string projectId, Action<ProjectUpdate> callback);
    Task UnsubscribeFromProjectUpdatesAsync(string projectId);
    Task SubscribeToSystemMetricsAsync(Action<SystemMetrics> callback);
    Task UnsubscribeFromSystemMetricsAsync();

    // Analytics and Reporting
    Task<DocumentGenerationAnalytics> GetDocumentGenerationAnalyticsAsync(DateTime from, DateTime to);
    Task<AgentPerformanceAnalytics> GetAgentPerformanceAnalyticsAsync(DateTime from, DateTime to);
    Task<SystemHealthReport> GenerateSystemHealthReportAsync();
    Task<byte[]> ExportAnalyticsAsync(AnalyticsExportFormat format, DateTime from, DateTime to);
    Task<AnalyticsData> GetAnalyticsAsync(string period);

    // File System Monitoring
    Task StartFileSystemMonitoringAsync(string path);
    Task StopFileSystemMonitoringAsync(string path);
    event EventHandler<FileSystemChangeEventArgs> FileSystemChanged;
}

public enum AnalyticsExportFormat
{
    CSV,
    JSON,
    PDF,
    Excel
}