using ByteForgeFrontend.Models.Monitoring;
using ByteForgeFrontend.Models.SignalR;
using ByteForgeFrontend.Hubs;
using ByteForgeFrontend.Models.SignalR;
using Microsoft.AspNetCore.SignalR;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Text;
using System.Text.Json;

using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Monitoring;

public class MonitoringService : IMonitoringService
{
    private readonly IHubContext<NotificationHub> _hubContext;
    private readonly ILogger<MonitoringService> _logger;
    
    // In-memory storage for monitoring data
    private readonly ConcurrentDictionary<string, DocumentGenerationStatus> _documentStatus = new();
    private readonly ConcurrentDictionary<string, AgentStatus> _agentStatus = new();
    private readonly ConcurrentDictionary<string, AgentHealthReport> _agentHealth = new();
    private readonly ConcurrentDictionary<string, ProjectOverview> _projectOverviews = new();
    private readonly ConcurrentDictionary<string, ResourceUsage> _resourceHistory = new();
    private readonly List<SystemEvent> _systemEvents = new();
    private readonly List<DocumentGenerationProgress> _documentHistory = new();
    private readonly ConcurrentDictionary<string, List<AgentMetrics>> _agentMetricsHistory = new();
    
    // File system watchers
    private readonly ConcurrentDictionary<string, FileSystemWatcher> _fileWatchers = new();
    
    // Subscription management
    private readonly ConcurrentDictionary<string, List<Action<ProjectUpdate>>> _projectSubscriptions = new();
    private readonly List<Action<SystemMetrics>> _systemMetricsSubscriptions = new();

    public event EventHandler<FileSystemChangeEventArgs>? FileSystemChanged;

    public MonitoringService(IHubContext<NotificationHub> hubContext, ILogger<MonitoringService> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
        
        // Initialize resource monitoring
        Task.Run(async () => await StartResourceMonitoringAsync());
    }

    #region Document Generation Monitoring

    public async Task<DocumentGenerationStatus> GetDocumentGenerationStatusAsync(string projectId)
    {
        _documentStatus.TryGetValue(projectId, out var status);
        return await Task.FromResult(status ?? new DocumentGenerationStatus { ProjectId = projectId });
    }

    public async Task<List<DocumentGenerationProgress>> GetDocumentProgressAsync(string projectId)
    {
        var progress = _documentHistory.Where(p => p.ProjectId == projectId).ToList();
        return await Task.FromResult(progress);
    }

    public async Task StartDocumentGenerationMonitoringAsync(string projectId, string documentType)
    {
        var status = _documentStatus.GetOrAdd(projectId, new DocumentGenerationStatus 
        { 
            ProjectId = projectId,
            StartedAt = DateTime.UtcNow
        });

        status.Documents[documentType] = new DocumentProgress
        {
            DocumentType = documentType,
            Progress = 0,
            Status = "Starting",
            StartedAt = DateTime.UtcNow
        };

        await NotifyDocumentProgressAsync(projectId, documentType, 0, "Starting");
        _logger.LogInformation("Started monitoring document generation for {DocumentType} in project {ProjectId}", 
            documentType, projectId);
    }

    public async Task UpdateDocumentProgressAsync(string projectId, string documentType, int progress, string status)
    {
        if (_documentStatus.TryGetValue(projectId, out var docStatus))
        {
            if (docStatus.Documents.TryGetValue(documentType, out var doc))
            {
                doc.Progress = progress;
                doc.Status = status;
                doc.Milestones.Add($"{DateTime.UtcNow:HH:mm:ss} - {status}");
                
                // Update overall progress
                docStatus.OverallProgress = (int)docStatus.Documents.Values.Average(d => d.Progress);
            }
        }

        // Record progress history
        _documentHistory.Add(new DocumentGenerationProgress
        {
            ProjectId = projectId,
            DocumentType = documentType,
            Progress = progress,
            Status = status,
            Timestamp = DateTime.UtcNow
        });

        await NotifyDocumentProgressAsync(projectId, documentType, progress, status);
        await NotifyProjectUpdateAsync(projectId, "DocumentProgress", documentType, 
            $"Document {documentType} is {progress}% complete", progress);
    }

    public async Task CompleteDocumentGenerationAsync(string projectId, string documentType, bool success, string? error = null)
    {
        if (_documentStatus.TryGetValue(projectId, out var docStatus))
        {
            if (docStatus.Documents.TryGetValue(documentType, out var doc))
            {
                doc.CompletedAt = DateTime.UtcNow;
                doc.Progress = success ? 100 : doc.Progress;
                doc.Status = success ? "Completed" : "Failed";
                doc.Error = error;
                
                if (!success)
                {
                    docStatus.HasErrors = true;
                }
                
                // Check if all documents are complete
                docStatus.IsComplete = docStatus.Documents.Values.All(d => d.CompletedAt.HasValue);
                if (docStatus.IsComplete)
                {
                    docStatus.CompletedAt = DateTime.UtcNow;
                }
            }
        }

        await NotifyDocumentProgressAsync(projectId, documentType, 
            success ? 100 : 0, success ? "Completed" : "Failed");
        
        _logger.LogInformation("Document generation {Status} for {DocumentType} in project {ProjectId}. {Error}",
            success ? "completed" : "failed", documentType, projectId, error ?? "");
    }

    #endregion

    #region AI Agent Monitoring

    public async Task<List<AgentStatus>> GetActiveAgentsAsync()
    {
        var activeAgents = _agentStatus.Values
            .Where(a => a.State != AgentState.Completed && a.State != AgentState.Failed && a.State != AgentState.Stopped)
            .ToList();
        return await Task.FromResult(activeAgents);
    }

    public async Task<AgentHealthReport> GetAgentHealthAsync(string agentId)
    {
        _agentHealth.TryGetValue(agentId, out var health);
        return await Task.FromResult(health ?? new AgentHealthReport { AgentId = agentId });
    }

    public async Task StartAgentMonitoringAsync(string agentId, string agentType, string projectId)
    {
        var agent = new AgentStatus
        {
            AgentId = agentId,
            AgentType = agentType,
            ProjectId = projectId,
            State = AgentState.Starting,
            StartedAt = DateTime.UtcNow,
            LastHeartbeat = DateTime.UtcNow
        };

        _agentStatus[agentId] = agent;
        _agentHealth[agentId] = new AgentHealthReport
        {
            AgentId = agentId,
            AgentType = agentType,
            IsHealthy = true
        };

        // Auto-transition to Running state
        await Task.Delay(100);
        agent.State = AgentState.Running;

        await NotifyAgentStatusAsync(agentId, AgentState.Starting);
        _logger.LogInformation("Started monitoring agent {AgentId} of type {AgentType} for project {ProjectId}",
            agentId, agentType, projectId);
    }

    public async Task UpdateAgentStatusAsync(string agentId, AgentState state, string? message = null)
    {
        if (_agentStatus.TryGetValue(agentId, out var agent))
        {
            agent.State = state;
            agent.CurrentTask = message;
            agent.LastHeartbeat = DateTime.UtcNow;
            
            if (state == AgentState.Completed)
            {
                agent.TasksCompleted++;
            }
            else if (state == AgentState.Failed)
            {
                agent.TasksFailed++;
            }
        }

        await NotifyAgentStatusAsync(agentId, state);
        _logger.LogInformation("Updated agent {AgentId} status to {State}: {Message}",
            agentId, state, message ?? "");
    }

    public async Task RecordAgentMetricsAsync(string agentId, AgentMetrics metrics)
    {
        if (_agentHealth.TryGetValue(agentId, out var health))
        {
            health.CpuUsage = metrics.CpuUsage;
            health.MemoryUsage = metrics.MemoryUsage;
            health.RequestsPerMinute = metrics.RequestCount;
            health.AverageResponseTime = metrics.ResponseTime;
            health.CustomMetrics = metrics.CustomMetrics;
            
            // Determine health status based on thresholds
            health.IsHealthy = metrics.CpuUsage < 90 && 
                               metrics.MemoryUsage < 2048 && 
                               metrics.ResponseTime < 2000;
        }

        // Store metrics history
        var history = _agentMetricsHistory.GetOrAdd(agentId, new List<AgentMetrics>());
        history.Add(metrics);
        
        // Keep only last 1000 entries
        if (history.Count > 1000)
        {
            history.RemoveRange(0, history.Count - 1000);
        }

        await NotifyAgentMetricsAsync(agentId, metrics);
    }

    #endregion

    #region Project Monitoring

    public async Task<ProjectOverview> GetProjectOverviewAsync(string projectId)
    {
        var overview = _projectOverviews.GetOrAdd(projectId, new ProjectOverview
        {
            ProjectId = projectId,
            ProjectName = $"Project {projectId}",
            ProjectType = "AI-Generated Application",
            CreatedAt = DateTime.UtcNow
        });

        // Update document progress
        if (_documentStatus.TryGetValue(projectId, out var docStatus))
        {
            overview.DocumentProgress = docStatus.Documents.ToDictionary(
                kvp => kvp.Key,
                kvp => kvp.Value.Progress
            );
            overview.OverallProgress = docStatus.OverallProgress;
            overview.HasErrors = docStatus.HasErrors;
        }

        // Update active agents
        overview.ActiveAgents = _agentStatus.Values
            .Where(a => a.ProjectId == projectId && 
                        a.State != AgentState.Completed && 
                        a.State != AgentState.Failed)
            .Select(a => a.AgentId)
            .ToList();

        // Determine current phase based on progress
        overview.CurrentPhase = DetermineProjectPhase(overview);

        return await Task.FromResult(overview);
    }

    public async Task<List<ProjectStatus>> GetAllProjectsStatusAsync()
    {
        var projects = _projectOverviews.Values.Select(p => new ProjectStatus
        {
            ProjectId = p.ProjectId,
            ProjectName = p.ProjectName,
            Status = p.CurrentPhase.ToString(),
            Progress = p.OverallProgress,
            LastUpdated = DateTime.UtcNow
        }).ToList();

        return await Task.FromResult(projects);
    }

    public async Task UpdateProjectProgressAsync(string projectId, int overallProgress)
    {
        var overview = _projectOverviews.GetOrAdd(projectId, new ProjectOverview
        {
            ProjectId = projectId,
            CreatedAt = DateTime.UtcNow
        });

        overview.OverallProgress = overallProgress;

        await NotifyProjectProgressAsync(projectId, overallProgress);
        await NotifyProjectUpdateAsync(projectId, "ProjectProgress", "Overall", 
            $"Project progress updated to {overallProgress}%", overallProgress);
    }

    #endregion

    #region System Metrics

    public async Task<SystemMetrics> GetSystemMetricsAsync()
    {
        var metrics = new SystemMetrics
        {
            CpuUsage = GetCpuUsage(),
            MemoryUsage = GetMemoryUsage(),
            DiskSpaceUsed = GetDiskSpaceUsed(),
            DiskSpaceAvailable = GetDiskSpaceAvailable(),
            ActiveProjects = _projectOverviews.Count,
            ActiveAgents = _agentStatus.Count(a => a.Value.State == AgentState.Running),
            QueuedTasks = 0, // This would come from a task queue service
            SystemLoad = GetSystemLoad()
        };

        // Check service health
        metrics.ServiceHealth["Database"] = new ServiceHealth
        {
            ServiceName = "Database",
            IsHealthy = true,
            LastCheck = DateTime.UtcNow
        };

        metrics.ServiceHealth["LLM Service"] = new ServiceHealth
        {
            ServiceName = "LLM Service",
            IsHealthy = true,
            LastCheck = DateTime.UtcNow
        };

        metrics.ServiceHealth["SignalR"] = new ServiceHealth
        {
            ServiceName = "SignalR",
            IsHealthy = true,
            LastCheck = DateTime.UtcNow
        };

        return await Task.FromResult(metrics);
    }

    public async Task<ResourceUsage> GetResourceUsageAsync()
    {
        var projectId = "system";
        var usage = _resourceHistory.GetOrAdd(projectId, new ResourceUsage());
        return await Task.FromResult(usage);
    }

    public async Task<SystemStatus> GetSystemStatus()
    {
        var status = new SystemStatus
        {
            ActiveMonitors = _fileWatchers.Count + _projectSubscriptions.Count,
            TotalEvents = _systemEvents.Count,
            LastUpdated = DateTime.UtcNow,
            IsHealthy = true
        };
        return await Task.FromResult(status);
    }

    public async Task RecordSystemEventAsync(SystemEvent systemEvent)
    {
        _systemEvents.Add(systemEvent);
        
        // Keep only last 10000 events
        if (_systemEvents.Count > 10000)
        {
            _systemEvents.RemoveRange(0, _systemEvents.Count - 10000);
        }

        await NotifySystemEventAsync(systemEvent);
        
        _logger.Log(systemEvent.Severity switch
        {
            EventSeverity.Debug => LogLevel.Debug,
            EventSeverity.Info => LogLevel.Information,
            EventSeverity.Warning => LogLevel.Warning,
            EventSeverity.Error => LogLevel.Error,
            EventSeverity.Critical => LogLevel.Critical,
            _ => LogLevel.Information
        }, "System Event: {EventType} from {Source} - {Message}", 
            systemEvent.EventType, systemEvent.Source, systemEvent.Message);
    }

    #endregion

    #region Real-time Updates

    public async Task SubscribeToProjectUpdatesAsync(string projectId, Action<ProjectUpdate> callback)
    {
        var subscriptions = _projectSubscriptions.GetOrAdd(projectId, new List<Action<ProjectUpdate>>());
        subscriptions.Add(callback);
        await Task.CompletedTask;
    }

    public async Task UnsubscribeFromProjectUpdatesAsync(string projectId)
    {
        _projectSubscriptions.TryRemove(projectId, out _);
        await Task.CompletedTask;
    }

    public async Task SubscribeToSystemMetricsAsync(Action<SystemMetrics> callback)
    {
        _systemMetricsSubscriptions.Add(callback);
        await Task.CompletedTask;
    }

    public async Task UnsubscribeFromSystemMetricsAsync()
    {
        _systemMetricsSubscriptions.Clear();
        await Task.CompletedTask;
    }

    #endregion

    #region Analytics and Reporting

    public async Task<DocumentGenerationAnalytics> GetDocumentGenerationAnalyticsAsync(DateTime from, DateTime to)
    {
        var relevantHistory = _documentHistory
            .Where(h => h.Timestamp >= from && h.Timestamp <= to)
            .ToList();

        var completedDocs = _documentStatus.Values
            .SelectMany(s => s.Documents.Values)
            .Where(d => d.CompletedAt.HasValue && d.CompletedAt.Value >= from && d.CompletedAt.Value <= to)
            .ToList();

        var analytics = new DocumentGenerationAnalytics
        {
            TotalDocumentsGenerated = completedDocs.Count,
            SuccessfulGenerations = completedDocs.Count(d => d.Status == "Completed"),
            FailedGenerations = completedDocs.Count(d => d.Status == "Failed")
        };

        analytics.SuccessRate = analytics.TotalDocumentsGenerated > 0
            ? (double)analytics.SuccessfulGenerations / analytics.TotalDocumentsGenerated * 100
            : 0;

        // Calculate average generation time
        var completedSuccessfully = completedDocs.Where(d => d.Status == "Completed" && d.CompletedAt.HasValue);
        analytics.AverageGenerationTime = completedSuccessfully.Any()
            ? completedSuccessfully.Average(d => (d.CompletedAt!.Value - d.StartedAt).TotalMinutes)
            : 0;

        // Document type counts
        analytics.DocumentTypeCounts = completedDocs
            .GroupBy(d => d.DocumentType)
            .ToDictionary(g => g.Key, g => g.Count());

        // Document type average times
        analytics.DocumentTypeAverageTimes = completedSuccessfully
            .GroupBy(d => d.DocumentType)
            .ToDictionary(
                g => g.Key,
                g => g.Average(d => (d.CompletedAt!.Value - d.StartedAt).TotalMinutes)
            );

        // Daily trends
        analytics.DailyTrends = completedDocs
            .GroupBy(d => d.CompletedAt!.Value.Date)
            .Select(g => new GenerationTrend
            {
                Date = g.Key,
                Count = g.Count(),
                AverageTime = g.Where(d => d.Status == "Completed")
                    .Average(d => (d.CompletedAt!.Value - d.StartedAt).TotalMinutes),
                SuccessRate = (double)g.Count(d => d.Status == "Completed") / g.Count() * 100
            })
            .OrderBy(t => t.Date)
            .ToList();

        return await Task.FromResult(analytics);
    }

    public async Task<AgentPerformanceAnalytics> GetAgentPerformanceAnalyticsAsync(DateTime from, DateTime to)
    {
        var analytics = new AgentPerformanceAnalytics();

        // Aggregate metrics by agent type
        foreach (var agentGroup in _agentStatus.Values.GroupBy(a => a.AgentType))
        {
            var performance = new AgentPerformance
            {
                AgentType = agentGroup.Key,
                TasksCompleted = agentGroup.Sum(a => a.TasksCompleted),
                TasksFailed = agentGroup.Sum(a => a.TasksFailed)
            };

            performance.SuccessRate = performance.TasksCompleted + performance.TasksFailed > 0
                ? (double)performance.TasksCompleted / (performance.TasksCompleted + performance.TasksFailed) * 100
                : 0;

            // Get metrics for agents of this type
            var agentIds = agentGroup.Select(a => a.AgentId).ToList();
            var relevantMetrics = agentIds
                .SelectMany(id => _agentMetricsHistory.TryGetValue(id, out var metrics) ? metrics : new List<AgentMetrics>())
                .Where(m => m.Timestamp >= from && m.Timestamp <= to)
                .ToList();

            if (relevantMetrics.Any())
            {
                performance.AverageCpuUsage = relevantMetrics.Average(m => m.CpuUsage);
                performance.AverageMemoryUsage = relevantMetrics.Average(m => m.MemoryUsage);
                performance.AverageTaskDuration = relevantMetrics.Average(m => m.ResponseTime);
            }

            analytics.AgentPerformance[agentGroup.Key] = performance;
        }

        // Calculate overall metrics
        var allPerformance = analytics.AgentPerformance.Values.ToList();
        analytics.TotalTasksCompleted = allPerformance.Sum(p => p.TasksCompleted);
        analytics.TotalTasksFailed = allPerformance.Sum(p => p.TasksFailed);
        analytics.OverallSuccessRate = analytics.TotalTasksCompleted + analytics.TotalTasksFailed > 0
            ? (double)analytics.TotalTasksCompleted / (analytics.TotalTasksCompleted + analytics.TotalTasksFailed) * 100
            : 0;
        analytics.AverageTaskDuration = allPerformance.Any() && allPerformance.Any(p => p.AverageTaskDuration > 0)
            ? allPerformance.Where(p => p.AverageTaskDuration > 0).Average(p => p.AverageTaskDuration)
            : 0;

        return await Task.FromResult(analytics);
    }

    public async Task<SystemHealthReport> GenerateSystemHealthReportAsync()
    {
        var report = new SystemHealthReport
        {
            CurrentMetrics = await GetSystemMetricsAsync()
        };

        // Determine overall health
        var healthyServices = report.CurrentMetrics.ServiceHealth.Values.Count(s => s.IsHealthy);
        var totalServices = report.CurrentMetrics.ServiceHealth.Count;
        
        if (healthyServices == totalServices)
        {
            report.OverallHealth = "Healthy";
        }
        else if (healthyServices >= totalServices * 0.75)
        {
            report.OverallHealth = "Degraded";
        }
        else
        {
            report.OverallHealth = "Critical";
        }

        // Identify issues
        var recentErrors = _systemEvents
            .Where(e => e.Severity >= EventSeverity.Error && e.Timestamp >= DateTime.UtcNow.AddHours(-24))
            .ToList();

        foreach (var error in recentErrors)
        {
            report.Issues.Add(new SystemIssue
            {
                IssueType = error.EventType,
                Description = error.Message,
                Severity = error.Severity,
                DetectedAt = error.Timestamp,
                IsResolved = false
            });
        }

        // Generate recommendations
        if (report.CurrentMetrics.CpuUsage > 80)
        {
            report.Recommendations.Add(new SystemRecommendation
            {
                Category = "Performance",
                Recommendation = "High CPU usage detected. Consider scaling up resources or optimizing workloads.",
                Impact = "System performance may degrade under load",
                Priority = 1
            });
        }

        if (report.CurrentMetrics.DiskSpaceAvailable < 10L * 1024 * 1024 * 1024) // Less than 10GB
        {
            report.Recommendations.Add(new SystemRecommendation
            {
                Category = "Storage",
                Recommendation = "Low disk space available. Clean up old files or increase storage capacity.",
                Impact = "System may fail to generate new documents",
                Priority = 2
            });
        }

        // Service health history
        foreach (var service in report.CurrentMetrics.ServiceHealth)
        {
            report.ServiceHealthHistory[service.Key] = new ServiceHealthHistory
            {
                ServiceName = service.Key,
                Uptime = 99.9, // This would be calculated from historical data
                ErrorCount = _systemEvents.Count(e => e.Source == service.Key && e.Severity >= EventSeverity.Error),
                Incidents = new List<ServiceIncident>() // Would populate from incident tracking
            };
        }

        return await Task.FromResult(report);
    }
    
    public async Task<AnalyticsData> GetAnalyticsAsync(string period)
    {
        var (from, to) = GetDateRangeFromPeriod(period);
        var docAnalytics = await GetDocumentGenerationAnalyticsAsync(from, to);
        var agentAnalytics = await GetAgentPerformanceAnalyticsAsync(from, to);
        
        return new AnalyticsData
        {
            Period = period,
            TotalDocumentsGenerated = docAnalytics.TotalDocumentsGenerated,
            SuccessfulGenerations = docAnalytics.SuccessfulGenerations,
            FailedGenerations = docAnalytics.FailedGenerations,
            AverageGenerationTime = docAnalytics.AverageGenerationTime,
            DocumentTypeBreakdown = docAnalytics.DocumentTypeCounts,
            AgentPerformance = agentAnalytics.AgentPerformance.ToDictionary(
                kvp => kvp.Key,
                kvp => kvp.Value.AverageTaskDuration
            ),
            StartDate = from,
            EndDate = to
        };
    }
    
    private (DateTime from, DateTime to) GetDateRangeFromPeriod(string period)
    {
        var to = DateTime.UtcNow;
        var from = period.ToLower() switch
        {
            "day" => to.AddDays(-1),
            "week" => to.AddDays(-7),
            "month" => to.AddMonths(-1),
            "year" => to.AddYears(-1),
            _ => to.AddDays(-7)
        };
        return (from, to);
    }

    public async Task<byte[]> ExportAnalyticsAsync(AnalyticsExportFormat format, DateTime from, DateTime to)
    {
        var documentAnalytics = await GetDocumentGenerationAnalyticsAsync(from, to);
        var agentAnalytics = await GetAgentPerformanceAnalyticsAsync(from, to);
        var healthReport = await GenerateSystemHealthReportAsync();

        switch (format)
        {
            case AnalyticsExportFormat.JSON:
                var jsonData = new
                {
                    ExportDate = DateTime.UtcNow,
                    DateRange = new { From = from, To = to },
                    DocumentAnalytics = documentAnalytics,
                    AgentAnalytics = agentAnalytics,
                    SystemHealth = healthReport
                };
                return Encoding.UTF8.GetBytes(JsonSerializer.Serialize(jsonData, new JsonSerializerOptions { WriteIndented = true }));

            case AnalyticsExportFormat.CSV:
                var csv = new StringBuilder();
                csv.AppendLine("Metric,Value");
                csv.AppendLine($"Total Documents Generated,{documentAnalytics.TotalDocumentsGenerated}");
                csv.AppendLine($"Success Rate,{documentAnalytics.SuccessRate:F2}%");
                csv.AppendLine($"Average Generation Time,{documentAnalytics.AverageGenerationTime:F2} minutes");
                csv.AppendLine($"Total Tasks Completed,{agentAnalytics.TotalTasksCompleted}");
                csv.AppendLine($"Agent Success Rate,{agentAnalytics.OverallSuccessRate:F2}%");
                csv.AppendLine($"System Health,{healthReport.OverallHealth}");
                return Encoding.UTF8.GetBytes(csv.ToString());

            case AnalyticsExportFormat.PDF:
                // For PDF generation, we would use a library like iTextSharp
                // For now, return a placeholder
                return Encoding.UTF8.GetBytes("PDF export would be implemented with a PDF library");

            case AnalyticsExportFormat.Excel:
                // For Excel generation, we would use a library like EPPlus
                // For now, return a placeholder
                return Encoding.UTF8.GetBytes("Excel export would be implemented with an Excel library");

            default:
                throw new NotSupportedException($"Export format {format} is not supported");
        }
    }

    #endregion

    #region File System Monitoring

    public async Task StartFileSystemMonitoringAsync(string path)
    {
        if (_fileWatchers.ContainsKey(path))
        {
            _logger.LogWarning("File system monitoring already active for path: {Path}", path);
            return;
        }

        var watcher = new FileSystemWatcher(path)
        {
            NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite | NotifyFilters.Size,
            IncludeSubdirectories = true,
            EnableRaisingEvents = true
        };

        watcher.Created += OnFileSystemChange;
        watcher.Changed += OnFileSystemChange;
        watcher.Deleted += OnFileSystemChange;
        watcher.Renamed += OnFileSystemRenamed;

        _fileWatchers[path] = watcher;
        _logger.LogInformation("Started file system monitoring for path: {Path}", path);
        
        await Task.CompletedTask;
    }

    public async Task StopFileSystemMonitoringAsync(string path)
    {
        if (_fileWatchers.TryRemove(path, out var watcher))
        {
            watcher.EnableRaisingEvents = false;
            watcher.Created -= OnFileSystemChange;
            watcher.Changed -= OnFileSystemChange;
            watcher.Deleted -= OnFileSystemChange;
            watcher.Renamed -= OnFileSystemRenamed;
            watcher.Dispose();
            
            _logger.LogInformation("Stopped file system monitoring for path: {Path}", path);
        }
        
        await Task.CompletedTask;
    }

    private void OnFileSystemChange(object sender, FileSystemEventArgs e)
    {
        var changeType = e.ChangeType switch
        {
            WatcherChangeTypes.Created => FileSystemChangeType.Created,
            WatcherChangeTypes.Changed => FileSystemChangeType.Modified,
            WatcherChangeTypes.Deleted => FileSystemChangeType.Deleted,
            _ => FileSystemChangeType.Modified
        };

        var args = new FileSystemChangeEventArgs
        {
            Path = e.FullPath,
            ChangeType = changeType,
            Timestamp = DateTime.UtcNow
        };

        FileSystemChanged?.Invoke(this, args);
        
        Task.Run(async () => await NotifyFileSystemChangeAsync(args));
    }

    private void OnFileSystemRenamed(object sender, RenamedEventArgs e)
    {
        var args = new FileSystemChangeEventArgs
        {
            Path = e.FullPath,
            OldPath = e.OldFullPath,
            ChangeType = FileSystemChangeType.Renamed,
            Timestamp = DateTime.UtcNow
        };

        FileSystemChanged?.Invoke(this, args);
        
        Task.Run(async () => await NotifyFileSystemChangeAsync(args));
    }

    // For testing purposes
    public async Task SimulateFileChangeForTestingAsync(string path, FileSystemChangeType changeType)
    {
        var args = new FileSystemChangeEventArgs
        {
            Path = path,
            ChangeType = changeType,
            Timestamp = DateTime.UtcNow
        };

        FileSystemChanged?.Invoke(this, args);
        await Task.CompletedTask;
    }

    #endregion

    #region Private Helper Methods

    private ProjectPhase DetermineProjectPhase(ProjectOverview overview)
    {
        if (overview.OverallProgress == 0)
            return ProjectPhase.Initialization;
        
        if (overview.DocumentProgress.Count == 0)
            return ProjectPhase.RequirementsGathering;
        
        var avgDocProgress = overview.DocumentProgress.Any() 
            ? overview.DocumentProgress.Values.Average() 
            : 0;
        
        if (avgDocProgress < 100)
            return ProjectPhase.DocumentGeneration;
        
        if (overview.ActiveAgents.Any())
            return ProjectPhase.CodeGeneration;
        
        if (overview.OverallProgress < 100)
            return ProjectPhase.Testing;
        
        return ProjectPhase.Completed;
    }

    private async Task StartResourceMonitoringAsync()
    {
        while (true)
        {
            try
            {
                var metrics = await GetSystemMetricsAsync();
                
                // Store resource history
                var usage = _resourceHistory.GetOrAdd("system", new ResourceUsage());
                
                usage.CpuHistory.Add(new ResourceSnapshot { Value = metrics.CpuUsage, Timestamp = DateTime.UtcNow });
                usage.MemoryHistory.Add(new ResourceSnapshot { Value = metrics.MemoryUsage, Timestamp = DateTime.UtcNow });
                usage.DiskHistory.Add(new ResourceSnapshot { Value = metrics.DiskSpaceUsed, Timestamp = DateTime.UtcNow });
                
                // Keep only last 1000 snapshots
                if (usage.CpuHistory.Count > 1000)
                {
                    usage.CpuHistory.RemoveAt(0);
                    usage.MemoryHistory.RemoveAt(0);
                    usage.DiskHistory.RemoveAt(0);
                }
                
                // Notify subscribers
                foreach (var callback in _systemMetricsSubscriptions)
                {
                    try
                    {
                        callback(metrics);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, "Error notifying system metrics subscriber");
                    }
                }
                
                // Broadcast to SignalR
                await _hubContext.Clients.Group("dashboard").SendAsync("SystemMetrics", metrics);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in resource monitoring");
            }
            
            await Task.Delay(TimeSpan.FromSeconds(10)); // Update every 10 seconds
        }
    }

    private double GetCpuUsage()
    {
        // In a real implementation, this would use PerformanceCounter or similar
        return Random.Shared.Next(10, 60);
    }

    private double GetMemoryUsage()
    {
        // In a real implementation, this would check actual memory usage
        return Random.Shared.Next(500, 2000);
    }

    private long GetDiskSpaceUsed()
    {
        // In a real implementation, this would check actual disk usage
        return Random.Shared.Next(10, 50) * 1024L * 1024L * 1024L; // GB to bytes
    }

    private long GetDiskSpaceAvailable()
    {
        // In a real implementation, this would check actual available space
        return Random.Shared.Next(50, 200) * 1024L * 1024L * 1024L; // GB to bytes
    }

    private double GetSystemLoad()
    {
        // In a real implementation, this would calculate actual system load
        return Random.Shared.NextDouble() * 2; // 0.0 to 2.0
    }

    private async Task NotifyProjectUpdateAsync(string projectId, string updateType, string component, string message, int? progress = null)
    {
        var update = new ProjectUpdate
        {
            ProjectId = projectId,
            UpdateType = updateType,
            Component = component,
            Message = message,
            Progress = progress,
            Timestamp = DateTime.UtcNow
        };

        // Notify local subscribers
        if (_projectSubscriptions.TryGetValue(projectId, out var subscribers))
        {
            foreach (var callback in subscribers)
            {
                try
                {
                    callback(update);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error notifying project update subscriber");
                }
            }
        }

        // Broadcast via SignalR
        await _hubContext.Clients.Group($"project-{projectId}").SendAsync("ProjectUpdate", update);
    }

    #endregion

    #region SignalR Notifications

    private async Task NotifyDocumentProgressAsync(string projectId, string documentType, int progress, string status)
    {
        var notification = new NotificationMessage
        {
            Type = NotificationTypes.DOCUMENT_GENERATED,
            EntityType = "Document",
            EntityId = $"{projectId}-{documentType}",
            Title = $"Document Generation Progress",
            Message = $"{documentType}: {progress}% - {status}",
            Severity = progress == 100 ? NotificationSeverity.Success : NotificationSeverity.Info,
            Data = new Dictionary<string, object>
            {
                ["projectId"] = projectId,
                ["documentType"] = documentType,
                ["progress"] = progress,
                ["status"] = status
            }
        };

        await _hubContext.Clients.Group($"project-{projectId}").SendAsync("DocumentProgress", notification);
        await _hubContext.Clients.Group("dashboard").SendAsync("DocumentProgress", notification);
    }

    private async Task NotifyAgentStatusAsync(string agentId, AgentState state)
    {
        if (!_agentStatus.TryGetValue(agentId, out var agent))
            return;

        var notificationType = state switch
        {
            AgentState.Starting => NotificationTypes.AGENT_STARTED,
            AgentState.Completed => NotificationTypes.AGENT_COMPLETED,
            AgentState.Failed => NotificationTypes.AGENT_FAILED,
            _ => NotificationTypes.SYSTEM_UPDATE
        };

        var notification = new NotificationMessage
        {
            Type = notificationType,
            EntityType = "Agent",
            EntityId = agentId,
            Title = $"Agent Status Update",
            Message = $"{agent.AgentType} is now {state}",
            Severity = state == AgentState.Failed ? NotificationSeverity.Error : NotificationSeverity.Info,
            Data = new Dictionary<string, object>
            {
                ["agentId"] = agentId,
                ["agentType"] = agent.AgentType,
                ["state"] = state.ToString(),
                ["projectId"] = agent.ProjectId
            }
        };

        await _hubContext.Clients.Group($"project-{agent.ProjectId}").SendAsync("AgentStatus", notification);
        await _hubContext.Clients.Group("dashboard").SendAsync("AgentStatus", notification);
    }

    private async Task NotifyAgentMetricsAsync(string agentId, AgentMetrics metrics)
    {
        if (!_agentStatus.TryGetValue(agentId, out var agent))
            return;

        await _hubContext.Clients.Group($"project-{agent.ProjectId}").SendAsync("AgentMetrics", new
        {
            agentId,
            metrics
        });
    }

    private async Task NotifyProjectProgressAsync(string projectId, int progress)
    {
        await _hubContext.Clients.Group($"project-{projectId}").SendAsync("ProjectProgress", new
        {
            projectId,
            progress
        });
    }

    private async Task NotifySystemEventAsync(SystemEvent systemEvent)
    {
        var notification = new NotificationMessage
        {
            Type = NotificationTypes.SYSTEM_UPDATE,
            EntityType = "System",
            EntityId = systemEvent.Source,
            Title = "System Event",
            Message = systemEvent.Message,
            Severity = systemEvent.Severity switch
            {
                EventSeverity.Critical => NotificationSeverity.Critical,
                EventSeverity.Error => NotificationSeverity.Error,
                EventSeverity.Warning => NotificationSeverity.Warning,
                _ => NotificationSeverity.Info
            },
            Data = systemEvent.Data
        };

        await _hubContext.Clients.Group("dashboard").SendAsync("SystemEvent", notification);
    }

    private async Task NotifyFileSystemChangeAsync(FileSystemChangeEventArgs args)
    {
        await _hubContext.Clients.Group("dashboard").SendAsync("FileSystemChange", args);
    }

    #endregion
}