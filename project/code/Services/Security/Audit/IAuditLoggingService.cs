using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;

namespace ByteForgeFrontend.Services.Security.Audit
{
    public interface IAuditLoggingService
    {
        Task<AuditLogResult> LogUserActionAsync(
            string userId,
            string tenantId,
            string action,
            string resource,
            string resourceId,
            Dictionary<string, object> details = null);
            
        Task<AuditLogResult> LogApiCallAsync(
            string apiKey,
            string tenantId,
            string endpoint,
            string method,
            int statusCode,
            int responseTimeMs,
            object requestBody = null,
            object responseBody = null);
            
        Task<AuditLogResult> LogDocumentGenerationAsync(
            string userId,
            string tenantId,
            string documentType,
            string projectId,
            string llmProvider,
            int tokenCount,
            TimeSpan generationTime,
            bool success);
            
        Task<AuditLogResult> LogAgentActivityAsync(
            string agentName,
            string agentId,
            string tenantId,
            string projectId,
            string operation,
            Dictionary<string, object> details,
            bool success);
            
        Task<AuditLogResult> LogSecurityEventAsync(
            string userId,
            string tenantId,
            SecurityEventType eventType,
            Dictionary<string, object> details,
            SecuritySeverity severity = SecuritySeverity.Medium);
            
        Task<IEnumerable<AuditLog>> GetAuditLogsAsync(
            string tenantId,
            string userId = null,
            string resource = null,
            DateTime? startDate = null,
            DateTime? endDate = null,
            int? limit = null);
            
        Task<AuditStatistics> GetAuditStatisticsAsync(
            string tenantId,
            DateTime startDate,
            DateTime endDate);
            
        Task<ComplianceReport> GetComplianceReportAsync(
            string tenantId,
            ComplianceType complianceType,
            DateTime? startDate = null,
            DateTime? endDate = null,
            string userId = null);
            
        Task<DataRetentionResult> EnforceDataRetentionPolicyAsync(
            string tenantId,
            int retentionDays);
    }
}