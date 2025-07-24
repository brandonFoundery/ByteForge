using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;
using ByteForgeFrontend.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.Security.Audit
{
    public class AuditLoggingService : IAuditLoggingService
    {
        private readonly ApplicationDbContext _context;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly IConfiguration _configuration;
        private readonly ILogger<AuditLoggingService> _logger;

        public AuditLoggingService(
            ApplicationDbContext context,
            IHttpContextAccessor httpContextAccessor,
            IConfiguration configuration,
            ILogger<AuditLoggingService> logger = null)
        {
            _context = context;
            _httpContextAccessor = httpContextAccessor;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task<AuditLogResult> LogUserActionAsync(
            string userId,
            string tenantId,
            string action,
            string resource,
            string resourceId,
            Dictionary<string, object> details = null)
        {
            try
            {
                var auditLog = new AuditLog
                {
                    TenantId = tenantId,
                    UserId = userId,
                    LogType = AuditLogType.UserAction,
                    Action = action,
                    Resource = resource,
                    ResourceId = resourceId,
                    Details = details ?? new Dictionary<string, object>(),
                    IpAddress = GetClientIpAddress(),
                    UserAgent = GetUserAgent(),
                    Success = true
                };

                _context.AuditLogs.Add(auditLog);
                await _context.SaveChangesAsync();

                return new AuditLogResult
                {
                    Success = true,
                    AuditLogId = auditLog.Id
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error logging user action");
                return new AuditLogResult
                {
                    Success = false,
                    ErrorMessage = "Failed to log user action"
                };
            }
        }

        public async Task<AuditLogResult> LogApiCallAsync(
            string apiKey,
            string tenantId,
            string endpoint,
            string method,
            int statusCode,
            int responseTimeMs,
            object requestBody = null,
            object responseBody = null)
        {
            try
            {
                var details = new Dictionary<string, object>
                {
                    ["apiKey"] = apiKey.Substring(0, Math.Min(apiKey.Length, 10)) + "...",
                    ["method"] = method,
                    ["statusCode"] = statusCode,
                    ["responseTime"] = responseTimeMs,
                    ["endpoint"] = endpoint
                };

                if (requestBody != null)
                {
                    details["requestBody"] = requestBody;
                }

                if (responseBody != null && _configuration.GetValue<bool>("AuditLog:IncludeResponseBody", false))
                {
                    details["responseBody"] = responseBody;
                }

                var auditLog = new AuditLog
                {
                    TenantId = tenantId,
                    LogType = AuditLogType.ApiCall,
                    Action = "API_CALL",
                    Resource = endpoint,
                    Details = details,
                    IpAddress = GetClientIpAddress(),
                    UserAgent = GetUserAgent(),
                    Success = statusCode >= 200 && statusCode < 300
                };

                _context.AuditLogs.Add(auditLog);
                await _context.SaveChangesAsync();

                return new AuditLogResult
                {
                    Success = true,
                    AuditLogId = auditLog.Id
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error logging API call");
                return new AuditLogResult
                {
                    Success = false,
                    ErrorMessage = "Failed to log API call"
                };
            }
        }

        public async Task<AuditLogResult> LogDocumentGenerationAsync(
            string userId,
            string tenantId,
            string documentType,
            string projectId,
            string llmProvider,
            int tokenCount,
            TimeSpan generationTime,
            bool success)
        {
            try
            {
                var details = new Dictionary<string, object>
                {
                    ["documentType"] = documentType,
                    ["projectId"] = projectId,
                    ["llmProvider"] = llmProvider,
                    ["tokenCount"] = tokenCount,
                    ["generationTimeMs"] = generationTime.TotalMilliseconds
                };

                var auditLog = new AuditLog
                {
                    TenantId = tenantId,
                    UserId = userId,
                    LogType = AuditLogType.DocumentGeneration,
                    Action = "GenerateDocument",
                    Resource = documentType,
                    ResourceId = projectId,
                    Details = details,
                    Success = success
                };

                _context.AuditLogs.Add(auditLog);
                await _context.SaveChangesAsync();

                return new AuditLogResult
                {
                    Success = true,
                    AuditLogId = auditLog.Id
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error logging document generation");
                return new AuditLogResult
                {
                    Success = false,
                    ErrorMessage = "Failed to log document generation"
                };
            }
        }

        public async Task<AuditLogResult> LogAgentActivityAsync(
            string agentName,
            string agentId,
            string tenantId,
            string projectId,
            string operation,
            Dictionary<string, object> details,
            bool success)
        {
            try
            {
                var enhancedDetails = new Dictionary<string, object>(details ?? new Dictionary<string, object>())
                {
                    ["agentName"] = agentName,
                    ["projectId"] = projectId,
                    ["operation"] = operation
                };

                var auditLog = new AuditLog
                {
                    TenantId = tenantId,
                    LogType = AuditLogType.AgentActivity,
                    Action = $"Agent_{operation}",
                    Resource = "Agent",
                    ResourceId = agentId,
                    Details = enhancedDetails,
                    Success = success
                };

                _context.AuditLogs.Add(auditLog);
                await _context.SaveChangesAsync();

                return new AuditLogResult
                {
                    Success = true,
                    AuditLogId = auditLog.Id
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error logging agent activity");
                return new AuditLogResult
                {
                    Success = false,
                    ErrorMessage = "Failed to log agent activity"
                };
            }
        }

        public async Task<AuditLogResult> LogSecurityEventAsync(
            string userId,
            string tenantId,
            SecurityEventType eventType,
            Dictionary<string, object> details,
            SecuritySeverity severity = SecuritySeverity.Medium)
        {
            try
            {
                var enhancedDetails = new Dictionary<string, object>(details ?? new Dictionary<string, object>())
                {
                    ["eventType"] = eventType.ToString(),
                    ["severity"] = severity.ToString()
                };

                var auditLog = new AuditLog
                {
                    TenantId = tenantId,
                    UserId = userId,
                    LogType = AuditLogType.SecurityEvent,
                    Action = eventType.ToString(),
                    Resource = "Security",
                    Details = enhancedDetails,
                    IpAddress = GetClientIpAddress(),
                    UserAgent = GetUserAgent(),
                    Success = false // Security events typically indicate issues
                };

                _context.AuditLogs.Add(auditLog);
                await _context.SaveChangesAsync();

                // For high/critical severity, additional actions could be taken
                if (severity >= SecuritySeverity.High)
                {
                    _logger?.LogWarning("High severity security event: {EventType} for user {UserId} in tenant {TenantId}", 
                        eventType, userId, tenantId);
                }

                return new AuditLogResult
                {
                    Success = true,
                    AuditLogId = auditLog.Id
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error logging security event");
                return new AuditLogResult
                {
                    Success = false,
                    ErrorMessage = "Failed to log security event"
                };
            }
        }

        public async Task<IEnumerable<AuditLog>> GetAuditLogsAsync(
            string tenantId,
            string userId = null,
            string resource = null,
            DateTime? startDate = null,
            DateTime? endDate = null,
            int? limit = null)
        {
            var query = _context.AuditLogs
                .Where(log => log.TenantId == tenantId);

            if (!string.IsNullOrEmpty(userId))
            {
                query = query.Where(log => log.UserId == userId);
            }

            if (!string.IsNullOrEmpty(resource))
            {
                query = query.Where(log => log.Resource == resource);
            }

            if (startDate.HasValue)
            {
                query = query.Where(log => log.Timestamp >= startDate.Value);
            }

            if (endDate.HasValue)
            {
                query = query.Where(log => log.Timestamp <= endDate.Value);
            }

            query = query.OrderByDescending(log => log.Timestamp);

            if (limit.HasValue)
            {
                query = query.Take(limit.Value);
            }

            return await query.ToListAsync();
        }

        public async Task<AuditStatistics> GetAuditStatisticsAsync(
            string tenantId,
            DateTime startDate,
            DateTime endDate)
        {
            var logs = await _context.AuditLogs
                .Where(log => log.TenantId == tenantId && 
                             log.Timestamp >= startDate && 
                             log.Timestamp <= endDate)
                .ToListAsync();

            var stats = new AuditStatistics
            {
                TotalEvents = logs.Count,
                UserActionCount = logs.Count(l => l.LogType == AuditLogType.UserAction),
                ApiCallCount = logs.Count(l => l.LogType == AuditLogType.ApiCall),
                SecurityEventCount = logs.Count(l => l.LogType == AuditLogType.SecurityEvent),
                DocumentGenerationCount = logs.Count(l => l.LogType == AuditLogType.DocumentGeneration),
                AgentActivityCount = logs.Count(l => l.LogType == AuditLogType.AgentActivity),
                UniqueUserCount = logs.Where(l => !string.IsNullOrEmpty(l.UserId))
                    .Select(l => l.UserId)
                    .Distinct()
                    .Count()
            };

            // Top actions
            stats.TopActions = logs
                .GroupBy(l => l.Action)
                .OrderByDescending(g => g.Count())
                .Take(10)
                .ToDictionary(g => g.Key, g => g.Count());

            // Events by type
            stats.EventsByType = logs
                .GroupBy(l => l.LogType.ToString())
                .ToDictionary(g => g.Key, g => g.Count());

            // Events by hour
            stats.EventsByHour = logs
                .GroupBy(l => l.Timestamp.Hour)
                .ToDictionary(g => g.Key, g => g.Count());

            return stats;
        }

        public async Task<ComplianceReport> GetComplianceReportAsync(
            string tenantId,
            ComplianceType complianceType,
            DateTime? startDate = null,
            DateTime? endDate = null,
            string userId = null)
        {
            var start = startDate ?? DateTime.UtcNow.AddMonths(-1);
            var end = endDate ?? DateTime.UtcNow;

            var logs = await GetAuditLogsAsync(tenantId, userId, null, start, end);
            var report = new ComplianceReport
            {
                TenantId = tenantId,
                ComplianceType = complianceType,
                GeneratedBy = _httpContextAccessor?.HttpContext?.User?.Identity?.Name ?? "System"
            };

            switch (complianceType)
            {
                case ComplianceType.GDPR:
                    report.Categories = GenerateGDPRCategories(logs, userId);
                    break;
                case ComplianceType.SOC2:
                    report.Categories = GenerateSOC2Categories(logs);
                    break;
                default:
                    report.Categories = GenerateGenericCategories(logs);
                    break;
            }

            return report;
        }

        public async Task<DataRetentionResult> EnforceDataRetentionPolicyAsync(
            string tenantId,
            int retentionDays)
        {
            try
            {
                var cutoffDate = DateTime.UtcNow.AddDays(-retentionDays);
                
                var logsToArchive = await _context.AuditLogs
                    .Where(log => log.TenantId == tenantId && 
                                 log.Timestamp < cutoffDate && 
                                 !log.IsArchived)
                    .ToListAsync();

                foreach (var log in logsToArchive)
                {
                    log.IsArchived = true;
                    log.ArchivedAt = DateTime.UtcNow;
                }

                await _context.SaveChangesAsync();

                var activeLogsCount = await _context.AuditLogs
                    .CountAsync(log => log.TenantId == tenantId && !log.IsArchived);

                return new DataRetentionResult
                {
                    Success = true,
                    ArchivedCount = logsToArchive.Count,
                    RetainedCount = activeLogsCount
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error enforcing data retention policy");
                return new DataRetentionResult
                {
                    Success = false,
                    ErrorMessage = "Failed to enforce data retention policy"
                };
            }
        }

        private string GetClientIpAddress()
        {
            return _httpContextAccessor?.HttpContext?.Connection?.RemoteIpAddress?.ToString() ?? "Unknown";
        }

        private string GetUserAgent()
        {
            return _httpContextAccessor?.HttpContext?.Request?.Headers["User-Agent"].ToString() ?? "Unknown";
        }

        private Dictionary<string, ComplianceCategory> GenerateGDPRCategories(IEnumerable<AuditLog> logs, string userId)
        {
            var categories = new Dictionary<string, ComplianceCategory>();

            // User data access
            var userDataLogs = logs.Where(l => l.LogType == AuditLogType.UserAction && 
                                              (l.Resource == "User" || l.Resource == "Profile"));
            categories["userDataAccess"] = new ComplianceCategory
            {
                Name = "User Data Access",
                Count = userDataLogs.Count(),
                Events = userDataLogs.Select(l => new ComplianceEvent
                {
                    Action = l.Action,
                    Timestamp = l.Timestamp,
                    UserId = l.UserId,
                    Details = l.Details
                }).ToList()
            };

            // Data processing
            var processingLogs = logs.Where(l => l.LogType == AuditLogType.DocumentGeneration || 
                                               l.LogType == AuditLogType.AgentActivity);
            categories["dataProcessing"] = new ComplianceCategory
            {
                Name = "Data Processing Activities",
                Count = processingLogs.Count(),
                Events = processingLogs.Select(l => new ComplianceEvent
                {
                    Action = l.Action,
                    Timestamp = l.Timestamp,
                    UserId = l.UserId,
                    Details = l.Details
                }).ToList()
            };

            return categories;
        }

        private Dictionary<string, ComplianceCategory> GenerateSOC2Categories(IEnumerable<AuditLog> logs)
        {
            var categories = new Dictionary<string, ComplianceCategory>();

            // Security events
            var securityLogs = logs.Where(l => l.LogType == AuditLogType.SecurityEvent);
            categories["security"] = new ComplianceCategory
            {
                Name = "Security Events",
                Count = securityLogs.Count(),
                Events = securityLogs.Select(l => new ComplianceEvent
                {
                    Action = l.Action,
                    Timestamp = l.Timestamp,
                    UserId = l.UserId,
                    Details = l.Details
                }).ToList()
            };

            // Access control
            var accessLogs = logs.Where(l => l.Action.Contains("Login") || 
                                           l.Action.Contains("Permission") || 
                                           l.Action.Contains("Auth"));
            categories["accessControl"] = new ComplianceCategory
            {
                Name = "Access Control",
                Count = accessLogs.Count(),
                Events = accessLogs.Select(l => new ComplianceEvent
                {
                    Action = l.Action,
                    Timestamp = l.Timestamp,
                    UserId = l.UserId,
                    Details = l.Details
                }).ToList()
            };

            // API security
            var apiLogs = logs.Where(l => l.LogType == AuditLogType.ApiCall);
            categories["apiSecurity"] = new ComplianceCategory
            {
                Name = "API Security",
                Count = apiLogs.Count(),
                Events = apiLogs.Select(l => new ComplianceEvent
                {
                    Action = l.Action,
                    Timestamp = l.Timestamp,
                    UserId = l.UserId,
                    Details = l.Details
                }).ToList()
            };

            return categories;
        }

        private Dictionary<string, ComplianceCategory> GenerateGenericCategories(IEnumerable<AuditLog> logs)
        {
            return logs
                .GroupBy(l => l.LogType.ToString())
                .ToDictionary(
                    g => g.Key,
                    g => new ComplianceCategory
                    {
                        Name = g.Key,
                        Count = g.Count(),
                        Events = g.Select(l => new ComplianceEvent
                        {
                            Action = l.Action,
                            Timestamp = l.Timestamp,
                            UserId = l.UserId,
                            Details = l.Details
                        }).ToList()
                    });
        }
    }
}