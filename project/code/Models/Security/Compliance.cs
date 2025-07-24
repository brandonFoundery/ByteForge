using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace ByteForgeFrontend.Models.Security
{
    public enum ComplianceType
    {
        GDPR = 1,
        SOC2 = 2,
        HIPAA = 3,
        PCI_DSS = 4,
        ISO27001 = 5
    }

    public enum ComplianceSeverity
    {
        Low = 1,
        Medium = 2,
        High = 3,
        Critical = 4
    }

    public enum ComplianceReviewType
    {
        Monthly = 1,
        Quarterly = 2,
        SemiAnnual = 3,
        Annual = 4
    }

    public enum ComplianceReviewStatus
    {
        Scheduled = 1,
        InProgress = 2,
        Completed = 3,
        Overdue = 4
    }

    public enum ComplianceReportType
    {
        Monthly = 1,
        Quarterly = 2,
        Annual = 3,
        OnDemand = 4
    }

    public class ComplianceValidationResult
    {
        public bool IsCompliant { get; set; }
        public List<ComplianceViolation> Violations { get; set; } = new List<ComplianceViolation>();
        public List<string> CompliantAreas { get; set; } = new List<string>();
        public List<string> Recommendations { get; set; } = new List<string>();
        public DateTime ValidationDate { get; set; } = DateTime.UtcNow;
    }

    public class ComplianceViolation
    {
        public string Type { get; set; }
        public string Description { get; set; }
        public ComplianceSeverity Severity { get; set; }
        public string RemediationGuidance { get; set; }
        public DateTime DetectedAt { get; set; } = DateTime.UtcNow;
    }

    public class SOC2ComplianceResult
    {
        public bool IsCompliant { get; set; }
        public List<string> CompliantControls { get; set; } = new List<string>();
        public List<ControlGap> ControlGaps { get; set; } = new List<ControlGap>();
        public List<string> RemediationSteps { get; set; } = new List<string>();
        public DateTime AssessmentDate { get; set; } = DateTime.UtcNow;
    }

    public class ControlGap
    {
        public string Control { get; set; }
        public string Description { get; set; }
        public ComplianceSeverity Severity { get; set; }
        public string Recommendation { get; set; }
    }

    public class DataPortabilityResult
    {
        public bool Success { get; set; }
        public Dictionary<string, object> ExportedData { get; set; } = new Dictionary<string, object>();
        public string ExportFormat { get; set; } = "JSON";
        public DateTime ExportDate { get; set; } = DateTime.UtcNow;
        public string ErrorMessage { get; set; }
    }

    public class DataErasureResult
    {
        public bool Success { get; set; }
        public List<string> AnonymizedFields { get; set; } = new List<string>();
        public List<string> DeletedRecords { get; set; } = new List<string>();
        public DateTime ProcessedAt { get; set; } = DateTime.UtcNow;
        public string ErrorMessage { get; set; }
    }

    public class TenantSecurityConfiguration
    {
        [Key]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string TenantId { get; set; }
        
        public bool RequireTwoFactor { get; set; }
        
        public string PasswordComplexityRules { get; set; }
        
        public int SessionTimeoutMinutes { get; set; } = 30;
        
        public int MaxFailedLoginAttempts { get; set; } = 5;
        
        public bool RequireEncryptionAtRest { get; set; } = true;
        
        public bool RequireEncryptionInTransit { get; set; } = true;
        
        public bool EnableAuditLogging { get; set; } = true;
        
        public bool EnableIPWhitelisting { get; set; }
        
        public List<string> WhitelistedIPs { get; set; } = new List<string>();
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime? UpdatedAt { get; set; }
    }

    public class AccessControlPolicy
    {
        [Key]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string TenantId { get; set; }
        
        public bool RequireRoleBasedAccess { get; set; } = true;
        
        public bool RequireDataClassification { get; set; } = true;
        
        public bool EnableLeastPrivilege { get; set; } = true;
        
        public bool RequireAccessReview { get; set; } = true;
        
        public int AccessReviewFrequencyDays { get; set; } = 90;
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

    public class ComplianceReport
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public string TenantId { get; set; }
        public ComplianceType ComplianceType { get; set; }
        public Dictionary<string, ComplianceCategory> Categories { get; set; } = new Dictionary<string, ComplianceCategory>();
        public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
        public string GeneratedBy { get; set; }
    }

    public class ComplianceCategory
    {
        public string Name { get; set; }
        public int Count { get; set; }
        public List<ComplianceEvent> Events { get; set; } = new List<ComplianceEvent>();
    }

    public class ComplianceEvent
    {
        public string Action { get; set; }
        public DateTime Timestamp { get; set; }
        public string UserId { get; set; }
        public Dictionary<string, object> Details { get; set; }
    }

    public class ComplianceDashboard
    {
        public string TenantId { get; set; }
        public ComplianceValidationResult GDPRStatus { get; set; }
        public SOC2ComplianceResult SOC2Status { get; set; }
        public List<ComplianceEvent> RecentComplianceEvents { get; set; } = new List<ComplianceEvent>();
        public List<string> UpcomingActions { get; set; } = new List<string>();
        public double ComplianceScore { get; set; }
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    }

    public class ComplianceReview
    {
        [Key]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string TenantId { get; set; }
        
        [Required]
        public ComplianceReviewType ReviewType { get; set; }
        
        public DateTime ScheduledDate { get; set; }
        
        public DateTime? CompletedDate { get; set; }
        
        public ComplianceReviewStatus Status { get; set; } = ComplianceReviewStatus.Scheduled;
        
        public List<string> ReviewTasks { get; set; } = new List<string>();
        
        public string AssignedTo { get; set; }
        
        public Dictionary<string, object> Results { get; set; } = new Dictionary<string, object>();
    }

    public class ComplianceReviewResult
    {
        public bool Success { get; set; }
        public string ReviewId { get; set; }
        public List<string> GeneratedTasks { get; set; } = new List<string>();
        public string ErrorMessage { get; set; }
    }

    public class ComplianceExportReport
    {
        public ComplianceReportType Type { get; set; }
        public int Year { get; set; }
        public int? Month { get; set; }
        public int? Quarter { get; set; }
        public Dictionary<string, object> Sections { get; set; } = new Dictionary<string, object>();
        public List<string> Attachments { get; set; } = new List<string>();
        public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    }
}