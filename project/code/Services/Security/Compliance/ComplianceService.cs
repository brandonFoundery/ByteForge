using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Security.Audit;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.Security.Compliance
{
    public class ComplianceService : IComplianceService
    {
        private readonly ApplicationDbContext _context;
        private readonly IAuditLoggingService _auditService;
        private readonly IConfiguration _configuration;
        private readonly ILogger<ComplianceService> _logger;

        public ComplianceService(
            ApplicationDbContext context,
            IAuditLoggingService auditService,
            IConfiguration configuration,
            ILogger<ComplianceService> logger = null)
        {
            _context = context;
            _auditService = auditService;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task<ComplianceValidationResult> ValidateGDPRComplianceAsync(string tenantId, string userId = null)
        {
            var result = new ComplianceValidationResult
            {
                IsCompliant = true
            };

            try
            {
                if (!string.IsNullOrEmpty(userId))
                {
                    // Validate user-specific compliance
                    var user = await _context.Users
                        .FirstOrDefaultAsync(u => u.Id == userId && u.TenantId == tenantId);

                    if (user == null)
                    {
                        result.IsCompliant = false;
                        result.Violations.Add(new ComplianceViolation
                        {
                            Type = "UserNotFound",
                            Description = "User not found in the specified tenant",
                            Severity = ComplianceSeverity.High
                        });
                        return result;
                    }

                    // Check data processing consent
                    if (!user.DataProcessingConsent)
                    {
                        result.IsCompliant = false;
                        result.Violations.Add(new ComplianceViolation
                        {
                            Type = "MissingConsent",
                            Description = "User has not provided data processing consent",
                            Severity = ComplianceSeverity.Critical,
                            RemediationGuidance = "Request user to provide explicit consent for data processing"
                        });
                    }
                    else
                    {
                        result.CompliantAreas.Add("DataProcessingConsent");

                        // Check consent age
                        if (user.DataProcessingConsentDate.HasValue && 
                            user.DataProcessingConsentDate.Value < DateTime.UtcNow.AddYears(-1))
                        {
                            result.IsCompliant = false;
                            result.Violations.Add(new ComplianceViolation
                            {
                                Type = "ExpiredConsent",
                                Description = "Data processing consent is over one year old",
                                Severity = ComplianceSeverity.Medium,
                                RemediationGuidance = "Request user to renew consent"
                            });
                            result.Recommendations.Add("Consider implementing annual consent renewal reminders");
                        }
                    }

                    // Check privacy policy acceptance
                    if (!user.LastPrivacyPolicyAcceptance.HasValue)
                    {
                        result.IsCompliant = false;
                        result.Violations.Add(new ComplianceViolation
                        {
                            Type = "MissingPrivacyPolicyAcceptance",
                            Description = "User has not accepted the privacy policy",
                            Severity = ComplianceSeverity.High
                        });
                    }
                    else
                    {
                        result.CompliantAreas.Add("PrivacyPolicyAcceptance");
                    }
                }

                // Check tenant-level compliance
                var retentionPolicy = await _context.DataRetentionPolicies
                    .FirstOrDefaultAsync(p => p.TenantId == tenantId && 
                                            p.DataType == "PersonalData" && 
                                            p.IsActive);

                if (retentionPolicy == null)
                {
                    result.IsCompliant = false;
                    result.Violations.Add(new ComplianceViolation
                    {
                        Type = "MissingRetentionPolicy",
                        Description = "No active data retention policy for personal data",
                        Severity = ComplianceSeverity.High,
                        RemediationGuidance = "Define and implement a data retention policy"
                    });
                }
                else
                {
                    result.CompliantAreas.Add("DataRetentionPolicy");
                }

                // Check audit logging
                var auditLogsExist = await _context.AuditLogs
                    .AnyAsync(l => l.TenantId == tenantId);

                if (!auditLogsExist)
                {
                    result.Recommendations.Add("Enable comprehensive audit logging for better compliance tracking");
                }
                else
                {
                    result.CompliantAreas.Add("AuditLogging");
                }

                // Check encryption settings
                var securityConfig = await _context.TenantSecurityConfigurations
                    .FirstOrDefaultAsync(c => c.TenantId == tenantId);

                if (securityConfig == null || !securityConfig.RequireEncryptionAtRest)
                {
                    result.Violations.Add(new ComplianceViolation
                    {
                        Type = "MissingEncryption",
                        Description = "Encryption at rest is not enabled",
                        Severity = ComplianceSeverity.High,
                        RemediationGuidance = "Enable encryption for all stored personal data"
                    });
                }

                return result;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error validating GDPR compliance");
                result.IsCompliant = false;
                result.Violations.Add(new ComplianceViolation
                {
                    Type = "ValidationError",
                    Description = "An error occurred during compliance validation",
                    Severity = ComplianceSeverity.Critical
                });
                return result;
            }
        }

        public async Task<SOC2ComplianceResult> ValidateSOC2ComplianceAsync(string tenantId)
        {
            var result = new SOC2ComplianceResult
            {
                IsCompliant = true
            };

            try
            {
                var securityConfig = await _context.TenantSecurityConfigurations
                    .FirstOrDefaultAsync(c => c.TenantId == tenantId);

                var accessControl = await _context.AccessControlPolicies
                    .FirstOrDefaultAsync(p => p.TenantId == tenantId);

                // Security controls (CC6)
                if (securityConfig != null)
                {
                    if (securityConfig.RequireTwoFactor)
                    {
                        result.CompliantControls.Add("CC6.1 - Multi-factor authentication");
                    }
                    else
                    {
                        result.IsCompliant = false;
                        result.ControlGaps.Add(new ControlGap
                        {
                            Control = "CC6.1",
                            Description = "Multi-factor authentication is not required",
                            Severity = ComplianceSeverity.High,
                            Recommendation = "Enable two-factor authentication for all users"
                        });
                    }

                    if (!string.IsNullOrEmpty(securityConfig.PasswordComplexityRules) && 
                        securityConfig.PasswordComplexityRules.Contains("MinLength:12"))
                    {
                        result.CompliantControls.Add("CC6.1 - Strong password requirements");
                    }
                    else
                    {
                        result.ControlGaps.Add(new ControlGap
                        {
                            Control = "CC6.1",
                            Description = "Password complexity requirements are insufficient",
                            Severity = ComplianceSeverity.Medium,
                            Recommendation = "Implement strong password requirements (min 12 characters, mixed case, numbers, symbols)"
                        });
                    }

                    if (securityConfig.RequireEncryptionAtRest && securityConfig.RequireEncryptionInTransit)
                    {
                        result.CompliantControls.Add("CC6.7 - Data encryption");
                    }
                    else
                    {
                        result.IsCompliant = false;
                        result.ControlGaps.Add(new ControlGap
                        {
                            Control = "CC6.7",
                            Description = "Data encryption is not fully implemented",
                            Severity = ComplianceSeverity.Critical,
                            Recommendation = "Enable encryption for data at rest and in transit"
                        });
                    }

                    if (securityConfig.EnableAuditLogging)
                    {
                        result.CompliantControls.Add("CC7.2 - System monitoring");
                    }
                    else
                    {
                        result.IsCompliant = false;
                        result.ControlGaps.Add(new ControlGap
                        {
                            Control = "CC7.2",
                            Description = "Audit logging is not enabled",
                            Severity = ComplianceSeverity.High,
                            Recommendation = "Enable comprehensive audit logging and monitoring"
                        });
                    }

                    // Check session timeout
                    if (securityConfig.SessionTimeoutMinutes <= 30)
                    {
                        result.CompliantControls.Add("CC6.8 - Session management");
                    }
                    else
                    {
                        result.ControlGaps.Add(new ControlGap
                        {
                            Control = "CC6.8",
                            Description = "Session timeout is too long",
                            Severity = ComplianceSeverity.Medium,
                            Recommendation = "Set session timeout to 30 minutes or less"
                        });
                    }
                }
                else
                {
                    result.IsCompliant = false;
                    result.ControlGaps.Add(new ControlGap
                    {
                        Control = "CC6",
                        Description = "No security configuration found",
                        Severity = ComplianceSeverity.Critical,
                        Recommendation = "Implement comprehensive security controls"
                    });
                }

                // Access control (CC6.3)
                if (accessControl != null)
                {
                    if (accessControl.RequireRoleBasedAccess)
                    {
                        result.CompliantControls.Add("CC6.3 - Role-based access control");
                    }

                    if (accessControl.EnableLeastPrivilege)
                    {
                        result.CompliantControls.Add("CC6.3 - Least privilege principle");
                    }

                    if (accessControl.RequireAccessReview)
                    {
                        result.CompliantControls.Add("CC6.2 - Periodic access reviews");
                    }
                }
                else
                {
                    result.ControlGaps.Add(new ControlGap
                    {
                        Control = "CC6.3",
                        Description = "Access control policies not defined",
                        Severity = ComplianceSeverity.High,
                        Recommendation = "Implement role-based access control with regular reviews"
                    });
                }

                // Availability controls
                result.CompliantControls.Add("Availability");

                // Processing integrity
                result.CompliantControls.Add("ProcessingIntegrity");

                // Confidentiality
                if (result.CompliantControls.Any(c => c.Contains("encryption")))
                {
                    result.CompliantControls.Add("Confidentiality");
                }

                // Privacy (if GDPR compliance is also maintained)
                var gdprCompliance = await ValidateGDPRComplianceAsync(tenantId);
                if (gdprCompliance.IsCompliant)
                {
                    result.CompliantControls.Add("Privacy");
                }

                // Add remediation steps
                if (result.ControlGaps.Any())
                {
                    result.RemediationSteps.Add("1. Review and address all identified control gaps");
                    result.RemediationSteps.Add("2. Implement missing security controls");
                    result.RemediationSteps.Add("3. Document all security policies and procedures");
                    result.RemediationSteps.Add("4. Conduct security awareness training");
                    result.RemediationSteps.Add("5. Schedule regular compliance reviews");
                }

                // Check audit statistics for monitoring evidence
                var auditStats = await _auditService.GetAuditStatisticsAsync(
                    tenantId, 
                    DateTime.UtcNow.AddMonths(-1), 
                    DateTime.UtcNow);

                if (auditStats.TotalEvents > 0)
                {
                    result.CompliantControls.Add("CC7.1 - Event logging");
                }

                return result;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error validating SOC2 compliance");
                result.IsCompliant = false;
                result.ControlGaps.Add(new ControlGap
                {
                    Control = "General",
                    Description = "Error during compliance validation",
                    Severity = ComplianceSeverity.Critical
                });
                return result;
            }
        }

        public async Task<DataPortabilityResult> HandleDataPortabilityRequestAsync(string tenantId, string userId)
        {
            try
            {
                var exportedData = new Dictionary<string, object>();

                // Export personal information
                var user = await _context.Users
                    .FirstOrDefaultAsync(u => u.Id == userId && u.TenantId == tenantId);

                if (user == null)
                {
                    return new DataPortabilityResult
                    {
                        Success = false,
                        ErrorMessage = "User not found"
                    };
                }

                exportedData["PersonalInformation"] = new Dictionary<string, object>
                {
                    ["Id"] = user.Id,
                    ["Email"] = user.Email,
                    ["UserName"] = user.UserName,
                    ["FirstName"] = user.FirstName,
                    ["LastName"] = user.LastName,
                    ["CreatedDate"] = user.CreatedDate,
                    ["DataProcessingConsent"] = user.DataProcessingConsent,
                    ["DataProcessingConsentDate"] = user.DataProcessingConsentDate,
                    ["MarketingConsent"] = user.MarketingConsent
                };

                // Export projects
                var projects = await _context.Projects
                    .Where(p => p.UserId == userId && p.TenantId == tenantId)
                    .Select(p => new
                    {
                        p.Id,
                        p.Name,
                        p.Description,
                        p.Status,
                        p.CreatedAt,
                        p.UpdatedAt
                    })
                    .ToListAsync();

                exportedData["Projects"] = projects;

                // Export API keys (without sensitive values)
                var apiKeys = await _context.ApiKeys
                    .Where(k => k.UserId == userId && k.TenantId == tenantId && !k.IsDeleted)
                    .Select(k => new
                    {
                        k.Id,
                        k.Name,
                        k.KeyType,
                        k.CreatedAt,
                        k.LastUsedAt,
                        k.ExpiresAt
                    })
                    .ToListAsync();

                exportedData["ApiKeys"] = apiKeys;

                // Export audit logs
                var auditLogs = await _auditService.GetAuditLogsAsync(
                    tenantId, 
                    userId, 
                    null, 
                    DateTime.UtcNow.AddYears(-1), 
                    DateTime.UtcNow);

                exportedData["AuditLogs"] = auditLogs.Select(log => new
                {
                    log.Action,
                    log.Resource,
                    log.Timestamp,
                    log.Success,
                    Details = log.Details.Where(d => !d.Key.Contains("password", StringComparison.OrdinalIgnoreCase))
                });

                // Log the data export request
                await _auditService.LogUserActionAsync(
                    userId,
                    tenantId,
                    "DataPortabilityRequest",
                    "UserData",
                    userId,
                    new Dictionary<string, object>
                    {
                        ["exportFormat"] = "JSON",
                        ["dataCategories"] = exportedData.Keys.ToList()
                    });

                return new DataPortabilityResult
                {
                    Success = true,
                    ExportedData = exportedData
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error handling data portability request");
                return new DataPortabilityResult
                {
                    Success = false,
                    ErrorMessage = "Failed to export user data"
                };
            }
        }

        public async Task<DataErasureResult> HandleDataErasureRequestAsync(string tenantId, string userId)
        {
            try
            {
                var result = new DataErasureResult();

                var user = await _context.Users
                    .FirstOrDefaultAsync(u => u.Id == userId && u.TenantId == tenantId);

                if (user == null)
                {
                    return new DataErasureResult
                    {
                        Success = false,
                        ErrorMessage = "User not found"
                    };
                }

                // Anonymize user data
                user.Email = $"anonymized_{Guid.NewGuid()}@deleted.local";
                user.UserName = $"deleted_user_{Guid.NewGuid().ToString().Substring(0, 8)}";
                user.FirstName = "[REDACTED]";
                user.LastName = "[REDACTED]";
                user.PhoneNumber = null;
                user.RefreshToken = null;
                user.TwoFactorSecret = null;

                result.AnonymizedFields.AddRange(new[]
                {
                    "Email", "UserName", "FirstName", "LastName", 
                    "PhoneNumber", "RefreshToken", "TwoFactorSecret"
                });

                // Update related projects
                var projects = await _context.Projects
                    .Where(p => p.UserId == userId && p.TenantId == tenantId)
                    .ToListAsync();

                foreach (var project in projects)
                {
                    if (project.Name.Contains(user.FirstName) || project.Name.Contains(user.LastName))
                    {
                        project.Name = project.Name
                            .Replace(user.FirstName, "[User Deleted]")
                            .Replace(user.LastName, "[User Deleted]");
                    }

                    project.UserId = null; // Disassociate from user
                }

                // Delete API keys
                var apiKeys = await _context.ApiKeys
                    .Where(k => k.UserId == userId && k.TenantId == tenantId)
                    .ToListAsync();

                foreach (var key in apiKeys)
                {
                    key.IsDeleted = true;
                    key.DeletedAt = DateTime.UtcNow;
                    key.DeletedBy = "GDPR_ERASURE";
                    result.DeletedRecords.Add($"ApiKey:{key.Id}");
                }

                await _context.SaveChangesAsync();

                // Log the erasure
                await _auditService.LogSecurityEventAsync(
                    userId,
                    tenantId,
                    SecurityEventType.AccountLocked,
                    new Dictionary<string, object>
                    {
                        ["reason"] = "GDPR Data Erasure Request",
                        ["anonymizedFields"] = result.AnonymizedFields,
                        ["deletedRecords"] = result.DeletedRecords
                    },
                    SecuritySeverity.High);

                result.Success = true;
                return result;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error handling data erasure request");
                return new DataErasureResult
                {
                    Success = false,
                    ErrorMessage = "Failed to erase user data"
                };
            }
        }

        public async Task<ComplianceDashboard> GenerateComplianceDashboardAsync(string tenantId)
        {
            var dashboard = new ComplianceDashboard
            {
                TenantId = tenantId
            };

            // Get GDPR status
            dashboard.GDPRStatus = await ValidateGDPRComplianceAsync(tenantId);

            // Get SOC2 status
            dashboard.SOC2Status = await ValidateSOC2ComplianceAsync(tenantId);

            // Get recent compliance events
            var recentLogs = await _auditService.GetAuditLogsAsync(
                tenantId,
                null,
                null,
                DateTime.UtcNow.AddDays(-7),
                DateTime.UtcNow,
                50);

            dashboard.RecentComplianceEvents = recentLogs
                .Where(log => log.Resource == "Security" || 
                             log.Resource == "User" || 
                             log.Action.Contains("Consent") ||
                             log.Action.Contains("Policy"))
                .Select(log => new ComplianceEvent
                {
                    Action = log.Action,
                    Timestamp = log.Timestamp,
                    UserId = log.UserId,
                    Details = log.Details
                })
                .ToList();

            // Calculate compliance score
            var totalChecks = 0;
            var passedChecks = 0;

            // GDPR checks
            totalChecks += 5;
            passedChecks += dashboard.GDPRStatus.CompliantAreas.Count;

            // SOC2 checks
            totalChecks += 10;
            passedChecks += dashboard.SOC2Status.CompliantControls.Count;

            dashboard.ComplianceScore = totalChecks > 0 
                ? (double)passedChecks / totalChecks * 100 
                : 0;

            // Generate upcoming actions
            dashboard.UpcomingActions = new List<string>();

            if (!dashboard.GDPRStatus.IsCompliant)
            {
                dashboard.UpcomingActions.Add("Address GDPR compliance violations");
            }

            if (!dashboard.SOC2Status.IsCompliant)
            {
                dashboard.UpcomingActions.Add("Implement missing SOC2 controls");
            }

            var nextReview = await _context.ComplianceReviews
                .Where(r => r.TenantId == tenantId && r.Status == ComplianceReviewStatus.Scheduled)
                .OrderBy(r => r.ScheduledDate)
                .FirstOrDefaultAsync();

            if (nextReview != null)
            {
                dashboard.UpcomingActions.Add($"Complete {nextReview.ReviewType} compliance review by {nextReview.ScheduledDate:yyyy-MM-dd}");
            }

            return dashboard;
        }

        public async Task<ComplianceReviewResult> ScheduleComplianceReviewAsync(
            string tenantId,
            ComplianceReviewType reviewType,
            DateTime scheduledDate)
        {
            try
            {
                var review = new ComplianceReview
                {
                    TenantId = tenantId,
                    ReviewType = reviewType,
                    ScheduledDate = scheduledDate,
                    Status = ComplianceReviewStatus.Scheduled
                };

                // Generate review tasks based on type
                switch (reviewType)
                {
                    case ComplianceReviewType.Monthly:
                        review.ReviewTasks.AddRange(new[]
                        {
                            "Review access logs",
                            "Verify user permissions",
                            "Check security alerts"
                        });
                        break;
                    case ComplianceReviewType.Quarterly:
                        review.ReviewTasks.AddRange(new[]
                        {
                            "Conduct access review",
                            "Update security policies",
                            "Review data retention compliance",
                            "Test disaster recovery procedures"
                        });
                        break;
                    case ComplianceReviewType.Annual:
                        review.ReviewTasks.AddRange(new[]
                        {
                            "Complete full SOC2 assessment",
                            "Review and update privacy policy",
                            "Conduct security training",
                            "Perform penetration testing",
                            "Review vendor compliance",
                            "Update risk assessment"
                        });
                        break;
                }

                _context.ComplianceReviews.Add(review);
                await _context.SaveChangesAsync();

                return new ComplianceReviewResult
                {
                    Success = true,
                    ReviewId = review.Id,
                    GeneratedTasks = review.ReviewTasks
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error scheduling compliance review");
                return new ComplianceReviewResult
                {
                    Success = false,
                    ErrorMessage = "Failed to schedule compliance review"
                };
            }
        }

        public async Task<ComplianceExportReport> ExportComplianceReportAsync(
            string tenantId,
            ComplianceReportType reportType,
            int year,
            int? month = null,
            int? quarter = null)
        {
            var report = new ComplianceExportReport
            {
                Type = reportType,
                Year = year,
                Month = month,
                Quarter = quarter
            };

            // Executive Summary
            var dashboard = await GenerateComplianceDashboardAsync(tenantId);
            report.Sections["Executive Summary"] = new
            {
                ComplianceScore = dashboard.ComplianceScore,
                GDPRCompliant = dashboard.GDPRStatus.IsCompliant,
                SOC2Compliant = dashboard.SOC2Status.IsCompliant,
                LastUpdated = dashboard.LastUpdated
            };

            // GDPR Compliance
            report.Sections["GDPR Compliance"] = dashboard.GDPRStatus;

            // SOC2 Compliance
            report.Sections["SOC2 Compliance"] = dashboard.SOC2Status;

            // Security Controls
            var securityConfig = await _context.TenantSecurityConfigurations
                .FirstOrDefaultAsync(c => c.TenantId == tenantId);
            report.Sections["Security Controls"] = securityConfig ?? new TenantSecurityConfiguration();

            // Audit Summary
            var startDate = GetReportStartDate(reportType, year, month, quarter);
            var endDate = GetReportEndDate(reportType, year, month, quarter);
            
            var auditStats = await _auditService.GetAuditStatisticsAsync(tenantId, startDate, endDate);
            report.Sections["Audit Summary"] = auditStats;

            // Recommendations
            var recommendations = new List<string>();
            recommendations.AddRange(dashboard.GDPRStatus.Recommendations);
            recommendations.AddRange(dashboard.SOC2Status.RemediationSteps);
            recommendations.AddRange(dashboard.UpcomingActions);
            report.Sections["Recommendations"] = recommendations.Distinct().ToList();

            // Add report metadata as attachment
            report.Attachments.Add($"Report generated on {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC");
            report.Attachments.Add($"Report period: {startDate:yyyy-MM-dd} to {endDate:yyyy-MM-dd}");

            return report;
        }

        public async Task<bool> UpdateConsentAsync(
            string tenantId,
            string userId,
            bool dataProcessingConsent,
            bool marketingConsent)
        {
            try
            {
                var user = await _context.Users
                    .FirstOrDefaultAsync(u => u.Id == userId && u.TenantId == tenantId);

                if (user == null)
                {
                    return false;
                }

                user.DataProcessingConsent = dataProcessingConsent;
                user.DataProcessingConsentDate = dataProcessingConsent ? DateTime.UtcNow : null;
                user.MarketingConsent = marketingConsent;
                user.MarketingConsentDate = marketingConsent ? DateTime.UtcNow : null;

                await _context.SaveChangesAsync();

                // Log consent update
                await _auditService.LogUserActionAsync(
                    userId,
                    tenantId,
                    "ConsentUpdate",
                    "User",
                    userId,
                    new Dictionary<string, object>
                    {
                        ["dataProcessingConsent"] = dataProcessingConsent,
                        ["marketingConsent"] = marketingConsent
                    });

                return true;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error updating consent");
                return false;
            }
        }

        public async Task<bool> AcceptPrivacyPolicyAsync(string tenantId, string userId, string policyVersion)
        {
            try
            {
                var user = await _context.Users
                    .FirstOrDefaultAsync(u => u.Id == userId && u.TenantId == tenantId);

                if (user == null)
                {
                    return false;
                }

                user.LastPrivacyPolicyAcceptance = DateTime.UtcNow;

                await _context.SaveChangesAsync();

                // Log policy acceptance
                await _auditService.LogUserActionAsync(
                    userId,
                    tenantId,
                    "PrivacyPolicyAcceptance",
                    "Policy",
                    policyVersion,
                    new Dictionary<string, object>
                    {
                        ["version"] = policyVersion,
                        ["acceptedAt"] = DateTime.UtcNow
                    });

                return true;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error accepting privacy policy");
                return false;
            }
        }

        private DateTime GetReportStartDate(ComplianceReportType type, int year, int? month, int? quarter)
        {
            return type switch
            {
                ComplianceReportType.Monthly => new DateTime(year, month ?? 1, 1),
                ComplianceReportType.Quarterly => new DateTime(year, ((quarter ?? 1) - 1) * 3 + 1, 1),
                ComplianceReportType.Annual => new DateTime(year, 1, 1),
                _ => DateTime.UtcNow.AddMonths(-1)
            };
        }

        private DateTime GetReportEndDate(ComplianceReportType type, int year, int? month, int? quarter)
        {
            return type switch
            {
                ComplianceReportType.Monthly => new DateTime(year, month ?? 1, 1).AddMonths(1).AddDays(-1),
                ComplianceReportType.Quarterly => new DateTime(year, ((quarter ?? 1) - 1) * 3 + 1, 1).AddMonths(3).AddDays(-1),
                ComplianceReportType.Annual => new DateTime(year, 12, 31),
                _ => DateTime.UtcNow
            };
        }
    }
}