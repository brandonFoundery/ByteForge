using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace ByteForgeFrontend.Models.Security
{
    public class ApiKey
    {
        [Key]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string TenantId { get; set; }
        
        public string UserId { get; set; }
        
        [Required]
        [MaxLength(200)]
        public string Name { get; set; }
        
        [Required]
        public string EncryptedValue { get; set; }
        
        [Required]
        [MaxLength(50)]
        public string KeyPrefix { get; set; }
        
        [Required]
        public ApiKeyType KeyType { get; set; }
        
        public Dictionary<string, string> Metadata { get; set; } = new Dictionary<string, string>();
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime? LastUsedAt { get; set; }
        
        public DateTime? ExpiresAt { get; set; }
        
        public bool IsExpired { get; set; }
        
        public bool IsDeleted { get; set; }
        
        public DateTime? DeletedAt { get; set; }
        
        public string DeletedBy { get; set; }
        
        // Rate limiting
        public int? RateLimit { get; set; }
        
        public int? RateLimitWindowSeconds { get; set; }
        
        // Navigation properties
        public virtual ApplicationUser User { get; set; }
        
        public virtual ICollection<ApiKeyAuditLog> AuditLogs { get; set; } = new List<ApiKeyAuditLog>();
    }

    public enum ApiKeyType
    {
        LLMProvider = 1,
        UserAccess = 2,
        ServiceToService = 3
    }

    public class ApiKeyAuditLog
    {
        [Key]
        public string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string ApiKeyId { get; set; }
        
        [Required]
        public string TenantId { get; set; }
        
        [Required]
        public string Action { get; set; }
        
        public string PerformedBy { get; set; }
        
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        
        public string IpAddress { get; set; }
        
        public string UserAgent { get; set; }
        
        public Dictionary<string, object> Details { get; set; } = new Dictionary<string, object>();
        
        // Navigation property
        public virtual ApiKey ApiKey { get; set; }
    }

    public class ApiKeyCreateResult
    {
        public bool Success { get; set; }
        public string KeyId { get; set; }
        public string KeyPrefix { get; set; }
        public string GeneratedKey { get; set; }
        public string ErrorMessage { get; set; }
    }

    public class ApiKeyUpdateResult
    {
        public bool Success { get; set; }
        public string ErrorMessage { get; set; }
    }

    public class ApiKeyDeleteResult
    {
        public bool Success { get; set; }
        public string ErrorMessage { get; set; }
    }

    public class ApiKeyRotateResult
    {
        public bool Success { get; set; }
        public string NewKey { get; set; }
        public string NewKeyId { get; set; }
        public string ErrorMessage { get; set; }
    }

    public class ApiKeyValidationResult
    {
        public bool IsValid { get; set; }
        public string TenantId { get; set; }
        public string UserId { get; set; }
        public string ServiceName { get; set; }
        public List<string> AllowedEndpoints { get; set; } = new List<string>();
        public string ErrorMessage { get; set; }
    }

    public class ApiKeyInfo
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string KeyPrefix { get; set; }
        public ApiKeyType KeyType { get; set; }
        public Dictionary<string, string> Metadata { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? LastUsedAt { get; set; }
        public DateTime? ExpiresAt { get; set; }
        public string DecryptedValue { get; set; }
    }
}