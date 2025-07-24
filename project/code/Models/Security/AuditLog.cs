using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace ByteForgeFrontend.Models.Security
{
    public class AuditLog
    {
        [Key]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string TenantId { get; set; }
        
        public string UserId { get; set; }
        
        [Required]
        public AuditLogType LogType { get; set; }
        
        [Required]
        [MaxLength(100)]
        public string Action { get; set; }
        
        [Required]
        [MaxLength(100)]
        public string Resource { get; set; }
        
        public string ResourceId { get; set; }
        
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        
        public string IpAddress { get; set; }
        
        public string UserAgent { get; set; }
        
        public bool Success { get; set; } = true;
        
        public Dictionary<string, object> Details { get; set; } = new Dictionary<string, object>();
        
        public bool IsArchived { get; set; }
        
        public DateTime? ArchivedAt { get; set; }
    }

    public enum AuditLogType
    {
        UserAction = 1,
        ApiCall = 2,
        DocumentGeneration = 3,
        AgentActivity = 4,
        SecurityEvent = 5,
        SystemEvent = 6
    }

    public enum SecurityEventType
    {
        SuccessfulLogin = 1,
        FailedLogin = 2,
        PasswordChange = 3,
        PermissionChange = 4,
        ApiKeyCreated = 5,
        ApiKeyDeleted = 6,
        TwoFactorEnabled = 7,
        TwoFactorDisabled = 8,
        AccountLocked = 9,
        AccountUnlocked = 10,
        SuspiciousActivity = 11
    }

    public enum SecuritySeverity
    {
        Low = 1,
        Medium = 2,
        High = 3,
        Critical = 4
    }

    public class AuditLogResult
    {
        public bool Success { get; set; }
        public string AuditLogId { get; set; }
        public string ErrorMessage { get; set; }
    }

    public class AuditStatistics
    {
        public int TotalEvents { get; set; }
        public int UserActionCount { get; set; }
        public int ApiCallCount { get; set; }
        public int SecurityEventCount { get; set; }
        public int DocumentGenerationCount { get; set; }
        public int AgentActivityCount { get; set; }
        public int UniqueUserCount { get; set; }
        public Dictionary<string, int> TopActions { get; set; } = new Dictionary<string, int>();
        public Dictionary<string, int> EventsByType { get; set; } = new Dictionary<string, int>();
        public Dictionary<int, int> EventsByHour { get; set; } = new Dictionary<int, int>();
    }

    public class DataRetentionPolicy
    {
        [Key]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string TenantId { get; set; }
        
        [Required]
        [MaxLength(100)]
        public string DataType { get; set; }
        
        [Required]
        public int RetentionDays { get; set; }
        
        public bool IsActive { get; set; } = true;
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime? LastEnforcedAt { get; set; }
    }

    public class DataRetentionResult
    {
        public bool Success { get; set; }
        public int ArchivedCount { get; set; }
        public int RetainedCount { get; set; }
        public int DeletedCount { get; set; }
        public string ErrorMessage { get; set; }
    }
}