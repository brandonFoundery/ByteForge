using System;
using System.Collections.Generic;

namespace ByteForgeFrontend.Models.SignalR;

public class MetricsUpdateMessage
{
    public string Type { get; set; } = "METRICS_UPDATE";
    public string MetricCategory { get; set; } = "System";
    public MetricsData Metrics { get; set; } = new();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class MetricsData
{
    // Generic counters
    public Dictionary<string, long> Counters { get; set; } = new();
    
    // Generic percentages/rates
    public Dictionary<string, decimal> Rates { get; set; } = new();
    
    // Generic time-based metrics
    public Dictionary<string, decimal> Timings { get; set; } = new();
    
    // Generic status counts
    public Dictionary<string, Dictionary<string, int>> StatusCounts { get; set; } = new();
    
    // ByteForge specific metrics
    public int ActiveProjects { get; set; }
    public int CompletedDocuments { get; set; }
    public int ActiveAgents { get; set; }
    public int PendingRequests { get; set; }
    public decimal AverageGenerationTime { get; set; }
    public decimal SuccessRate { get; set; }
    public Dictionary<string, int> DocumentsByType { get; set; } = new();
    public Dictionary<string, int> RequestsByProvider { get; set; } = new();
}