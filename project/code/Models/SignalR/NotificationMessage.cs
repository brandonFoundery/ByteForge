using System;
using System.Collections.Generic;

namespace ByteForgeFrontend.Models.SignalR;

public class NotificationMessage
{
    public string Type { get; set; } = string.Empty;
    public string EntityType { get; set; } = string.Empty;
    public string EntityId { get; set; } = string.Empty;
    public string? Title { get; set; }
    public string? Message { get; set; }
    public NotificationSeverity Severity { get; set; } = NotificationSeverity.Info;
    public Dictionary<string, object> Data { get; set; } = new();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? UserId { get; set; }
    public string? GroupId { get; set; }
}

public enum NotificationSeverity
{
    Info,
    Success,
    Warning,
    Error,
    Critical
}

public static class NotificationTypes
{
    // Generic notifications
    public const string ENTITY_CREATED = "ENTITY_CREATED";
    public const string ENTITY_UPDATED = "ENTITY_UPDATED";
    public const string ENTITY_DELETED = "ENTITY_DELETED";
    
    // Workflow notifications
    public const string WORKFLOW_STARTED = "WORKFLOW_STARTED";
    public const string WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED";
    public const string WORKFLOW_FAILED = "WORKFLOW_FAILED";
    public const string WORKFLOW_PROGRESS = "WORKFLOW_PROGRESS";
    
    // Job notifications
    public const string JOB_STARTED = "JOB_STARTED";
    public const string JOB_COMPLETED = "JOB_COMPLETED";
    public const string JOB_FAILED = "JOB_FAILED";
    
    // System notifications
    public const string SYSTEM_UPDATE = "SYSTEM_UPDATE";
    public const string SYSTEM_ALERT = "SYSTEM_ALERT";
    public const string SYSTEM_ERROR = "SYSTEM_ERROR";
    
    // ByteForge specific
    public const string DOCUMENT_GENERATED = "DOCUMENT_GENERATED";
    public const string AGENT_STARTED = "AGENT_STARTED";
    public const string AGENT_COMPLETED = "AGENT_COMPLETED";
    public const string AGENT_FAILED = "AGENT_FAILED";
    public const string LLM_REQUEST_STARTED = "LLM_REQUEST_STARTED";
    public const string LLM_REQUEST_COMPLETED = "LLM_REQUEST_COMPLETED";
    public const string LLM_REQUEST_FAILED = "LLM_REQUEST_FAILED";
}