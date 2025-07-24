using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;
using ByteForgeFrontend.Services.Security.Audit;
using ByteForgeFrontend.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Moq;
using Xunit;
using System.Security.Claims;

namespace ByteForgeFrontend.Tests.Security.Audit
{
    public class AuditLoggingTests : IDisposable
    {
        private readonly ApplicationDbContext _context;
        private readonly Mock<IConfiguration> _configurationMock;
        private readonly Mock<ILogger<AuditLoggingService>> _loggerMock;
        private readonly Mock<IHttpContextAccessor> _httpContextAccessorMock;
        private readonly AuditLoggingService _auditService;

        public AuditLoggingTests()
        {
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
                .Options;
            
            _context = new ApplicationDbContext(options);
            _configurationMock = new Mock<IConfiguration>();
            _loggerMock = new Mock<ILogger<AuditLoggingService>>();
            _httpContextAccessorMock = new Mock<IHttpContextAccessor>();
            
            SetupConfiguration();
            SetupHttpContext();
            
            _auditService = new AuditLoggingService(
                _context,
                _httpContextAccessorMock.Object,
                _configurationMock.Object,
                _loggerMock.Object);
        }

        [Fact]
        public async Task LogUserActionAsync_ShouldCreateAuditEntry()
        {
            // Arrange
            var userId = "user123";
            var tenantId = "tenant1";
            var action = "CreateProject";
            var resource = "Project";
            var resourceId = "proj456";
            var details = new Dictionary<string, object>
            {
                ["projectName"] = "New CRM System",
                ["templateUsed"] = "CRM_Template"
            };

            // Act
            var result = await _auditService.LogUserActionAsync(
                userId,
                tenantId,
                action,
                resource,
                resourceId,
                details);

            // Assert
            Assert.True(result.Success);
            Assert.NotEmpty(result.AuditLogId);
            
            var auditLog = await _context.AuditLogs.FindAsync(result.AuditLogId);
            Assert.NotNull(auditLog);
            Assert.Equal(userId, auditLog.UserId);
            Assert.Equal(tenantId, auditLog.TenantId);
            Assert.Equal(action, auditLog.Action);
            Assert.Equal(resource, auditLog.Resource);
            Assert.Equal(resourceId, auditLog.ResourceId);
            Assert.NotNull(auditLog.Details);
            Assert.Contains("projectName", auditLog.Details);
            Assert.Equal("127.0.0.1", auditLog.IpAddress);
            Assert.Equal("Test User Agent", auditLog.UserAgent);
        }

        [Fact]
        public async Task LogApiCallAsync_ShouldTrackApiUsage()
        {
            // Arrange
            var apiKey = "byteforge_123456";
            var tenantId = "tenant1";
            var endpoint = "/api/v1/requirements/generate";
            var method = "POST";
            var statusCode = 200;
            var responseTime = 1234;
            var requestBody = new { documentType = "BRD", projectId = "proj123" };

            // Act
            var result = await _auditService.LogApiCallAsync(
                apiKey,
                tenantId,
                endpoint,
                method,
                statusCode,
                responseTime,
                requestBody);

            // Assert
            Assert.True(result.Success);
            
            var auditLog = await _context.AuditLogs
                .FirstOrDefaultAsync(a => a.Id == result.AuditLogId);
            
            Assert.NotNull(auditLog);
            Assert.Equal(AuditLogType.ApiCall, auditLog.LogType);
            Assert.Equal("API_CALL", auditLog.Action);
            Assert.Equal(endpoint, auditLog.Resource);
            Assert.Equal(tenantId, auditLog.TenantId);
            Assert.Contains("method", auditLog.Details);
            Assert.Contains("statusCode", auditLog.Details);
            Assert.Contains("responseTime", auditLog.Details);
            Assert.Contains("requestBody", auditLog.Details);
        }

        [Fact]
        public async Task LogDocumentGenerationAsync_ShouldTrackDocumentEvents()
        {
            // Arrange
            var userId = "user123";
            var tenantId = "tenant1";
            var documentType = "BusinessRequirementsDocument";
            var projectId = "proj789";
            var llmProvider = "OpenAI";
            var tokenCount = 5432;
            var generationTime = TimeSpan.FromSeconds(12.5);

            // Act
            var result = await _auditService.LogDocumentGenerationAsync(
                userId,
                tenantId,
                documentType,
                projectId,
                llmProvider,
                tokenCount,
                generationTime,
                success: true);

            // Assert
            Assert.True(result.Success);
            
            var auditLog = await _context.AuditLogs.FindAsync(result.AuditLogId);
            Assert.NotNull(auditLog);
            Assert.Equal(AuditLogType.DocumentGeneration, auditLog.LogType);
            Assert.Equal("GenerateDocument", auditLog.Action);
            Assert.Equal(documentType, auditLog.Resource);
            Assert.Equal(projectId, auditLog.ResourceId);
            Assert.Contains("llmProvider", auditLog.Details);
            Assert.Contains("tokenCount", auditLog.Details);
            Assert.Contains("generationTimeMs", auditLog.Details);
            Assert.True(auditLog.Success);
        }

        [Fact]
        public async Task LogAgentActivityAsync_ShouldTrackAgentOperations()
        {
            // Arrange
            var agentName = "BackendAgent";
            var agentId = "agent_backend_001";
            var tenantId = "tenant1";
            var projectId = "proj999";
            var operation = "GenerateAPIEndpoints";
            var filesGenerated = 15;
            var executionTime = TimeSpan.FromMinutes(3.5);

            // Act
            var result = await _auditService.LogAgentActivityAsync(
                agentName,
                agentId,
                tenantId,
                projectId,
                operation,
                new Dictionary<string, object>
                {
                    ["filesGenerated"] = filesGenerated,
                    ["executionTimeMs"] = executionTime.TotalMilliseconds,
                    ["llmCalls"] = 8
                },
                success: true);

            // Assert
            Assert.True(result.Success);
            
            var auditLog = await _context.AuditLogs.FindAsync(result.AuditLogId);
            Assert.NotNull(auditLog);
            Assert.Equal(AuditLogType.AgentActivity, auditLog.LogType);
            Assert.Equal($"Agent_{operation}", auditLog.Action);
            Assert.Equal("Agent", auditLog.Resource);
            Assert.Equal(agentId, auditLog.ResourceId);
            Assert.Contains("agentName", auditLog.Details);
            Assert.Contains("filesGenerated", auditLog.Details);
            Assert.Contains("llmCalls", auditLog.Details);
        }

        [Fact]
        public async Task LogSecurityEventAsync_ShouldTrackSecurityIncidents()
        {
            // Arrange
            var userId = "user123";
            var tenantId = "tenant1";
            var eventType = SecurityEventType.FailedLogin;
            var details = new Dictionary<string, object>
            {
                ["attemptCount"] = 3,
                ["email"] = "user@example.com",
                ["reason"] = "Invalid password"
            };

            // Act
            var result = await _auditService.LogSecurityEventAsync(
                userId,
                tenantId,
                eventType,
                details,
                severity: SecuritySeverity.Medium);

            // Assert
            Assert.True(result.Success);
            
            var auditLog = await _context.AuditLogs.FindAsync(result.AuditLogId);
            Assert.NotNull(auditLog);
            Assert.Equal(AuditLogType.SecurityEvent, auditLog.LogType);
            Assert.Equal(eventType.ToString(), auditLog.Action);
            Assert.Equal("Security", auditLog.Resource);
            Assert.Contains("severity", auditLog.Details);
            Assert.Contains("attemptCount", auditLog.Details);
            Assert.False(auditLog.Success); // Security events typically indicate issues
        }

        [Fact]
        public async Task GetAuditLogsAsync_WithFilters_ShouldReturnFilteredResults()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            
            // Create various audit logs
            await _auditService.LogUserActionAsync(userId, tenantId, "Login", "Auth", null);
            await _auditService.LogUserActionAsync(userId, tenantId, "CreateProject", "Project", "proj1");
            await _auditService.LogUserActionAsync("user456", tenantId, "UpdateProject", "Project", "proj2");
            await _auditService.LogApiCallAsync("api123", tenantId, "/api/test", "GET", 200, 100);
            
            // Act
            var userLogs = await _auditService.GetAuditLogsAsync(
                tenantId,
                userId: userId);
            
            var projectLogs = await _auditService.GetAuditLogsAsync(
                tenantId,
                resource: "Project");
            
            var recentLogs = await _auditService.GetAuditLogsAsync(
                tenantId,
                startDate: DateTime.UtcNow.AddMinutes(-5),
                endDate: DateTime.UtcNow);

            // Assert
            Assert.Equal(2, userLogs.Count());
            Assert.All(userLogs, log => Assert.Equal(userId, log.UserId));
            
            Assert.Equal(2, projectLogs.Count());
            Assert.All(projectLogs, log => Assert.Equal("Project", log.Resource));
            
            Assert.Equal(4, recentLogs.Count());
        }

        [Fact]
        public async Task GetComplianceReportAsync_ShouldGenerateGDPRCompliantReport()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            
            // Create audit logs for different activities
            await _auditService.LogUserActionAsync(userId, tenantId, "Login", "Auth", null);
            await _auditService.LogUserActionAsync(userId, tenantId, "UpdateProfile", "User", userId, 
                new Dictionary<string, object> { ["field"] = "email", ["oldValue"] = "old@email.com" });
            await _auditService.LogDocumentGenerationAsync(userId, tenantId, "PRD", "proj1", "OpenAI", 1000, TimeSpan.FromSeconds(5));
            
            // Act
            var report = await _auditService.GetComplianceReportAsync(
                tenantId,
                ComplianceType.GDPR,
                userId: userId);

            // Assert
            Assert.NotNull(report);
            Assert.Equal(ComplianceType.GDPR, report.ComplianceType);
            Assert.Equal(tenantId, report.TenantId);
            Assert.Contains("userDataAccess", report.Categories);
            Assert.Contains("dataProcessing", report.Categories);
            
            var userDataCategory = report.Categories["userDataAccess"];
            Assert.True(userDataCategory.Count > 0);
            Assert.Contains(userDataCategory.Events, e => e.Action == "UpdateProfile");
        }

        [Fact]
        public async Task GetComplianceReportAsync_ForSOC2_ShouldIncludeSecurityEvents()
        {
            // Arrange
            var tenantId = "tenant1";
            
            // Create security-related audit logs
            await _auditService.LogSecurityEventAsync(null, tenantId, SecurityEventType.FailedLogin, 
                new Dictionary<string, object> { ["ip"] = "192.168.1.100" });
            await _auditService.LogSecurityEventAsync("admin", tenantId, SecurityEventType.PermissionChange,
                new Dictionary<string, object> { ["role"] = "SuperAdmin", ["granted"] = true });
            await _auditService.LogApiCallAsync("api123", tenantId, "/api/admin", "POST", 403, 50);

            // Act
            var report = await _auditService.GetComplianceReportAsync(
                tenantId,
                ComplianceType.SOC2,
                startDate: DateTime.UtcNow.AddHours(-1));

            // Assert
            Assert.NotNull(report);
            Assert.Equal(ComplianceType.SOC2, report.ComplianceType);
            Assert.Contains("security", report.Categories);
            Assert.Contains("accessControl", report.Categories);
            Assert.Contains("apiSecurity", report.Categories);
            
            var securityCategory = report.Categories["security"];
            Assert.Contains(securityCategory.Events, e => e.Action == SecurityEventType.FailedLogin.ToString());
            Assert.Contains(securityCategory.Events, e => e.Action == SecurityEventType.PermissionChange.ToString());
        }

        [Fact]
        public async Task EnforceDataRetentionPolicyAsync_ShouldArchiveOldLogs()
        {
            // Arrange
            var tenantId = "tenant1";
            var retentionDays = 90;
            
            // Create old audit logs
            var oldDate = DateTime.UtcNow.AddDays(-100);
            for (int i = 0; i < 10; i++)
            {
                var log = new AuditLog
                {
                    Id = Guid.NewGuid().ToString(),
                    TenantId = tenantId,
                    Timestamp = oldDate,
                    Action = "OldAction",
                    Resource = "OldResource",
                    LogType = AuditLogType.UserAction
                };
                _context.AuditLogs.Add(log);
            }
            
            // Create recent logs
            for (int i = 0; i < 5; i++)
            {
                await _auditService.LogUserActionAsync($"user{i}", tenantId, "RecentAction", "Resource", null);
            }
            
            await _context.SaveChangesAsync();

            // Act
            var result = await _auditService.EnforceDataRetentionPolicyAsync(tenantId, retentionDays);

            // Assert
            Assert.True(result.Success);
            Assert.Equal(10, result.ArchivedCount);
            Assert.Equal(5, result.RetainedCount);
            
            // Verify old logs are archived (soft deleted)
            var activeLogs = await _context.AuditLogs
                .Where(a => a.TenantId == tenantId && !a.IsArchived)
                .CountAsync();
            Assert.Equal(5, activeLogs);
            
            // Verify archived logs still exist but are marked
            var archivedLogs = await _context.AuditLogs
                .IgnoreQueryFilters()
                .Where(a => a.TenantId == tenantId && a.IsArchived)
                .CountAsync();
            Assert.Equal(10, archivedLogs);
        }

        [Fact]
        public async Task GetAuditStatisticsAsync_ShouldProvideInsights()
        {
            // Arrange
            var tenantId = "tenant1";
            var startDate = DateTime.UtcNow.AddDays(-7);
            
            // Create various audit logs
            for (int i = 0; i < 20; i++)
            {
                await _auditService.LogUserActionAsync($"user{i % 3}", tenantId, "Action", "Resource", null);
            }
            
            for (int i = 0; i < 10; i++)
            {
                await _auditService.LogApiCallAsync($"api{i}", tenantId, "/api/test", "GET", 200, 100);
            }
            
            await _auditService.LogSecurityEventAsync("user1", tenantId, SecurityEventType.FailedLogin, null);

            // Act
            var stats = await _auditService.GetAuditStatisticsAsync(tenantId, startDate, DateTime.UtcNow);

            // Assert
            Assert.NotNull(stats);
            Assert.Equal(31, stats.TotalEvents);
            Assert.Equal(20, stats.UserActionCount);
            Assert.Equal(10, stats.ApiCallCount);
            Assert.Equal(1, stats.SecurityEventCount);
            Assert.Equal(3, stats.UniqueUserCount);
            Assert.NotEmpty(stats.TopActions);
            Assert.NotEmpty(stats.EventsByType);
            Assert.NotEmpty(stats.EventsByHour);
        }

        private void SetupConfiguration()
        {
            _configurationMock.Setup(x => x["AuditLog:RetentionDays"]).Returns("90");
            _configurationMock.Setup(x => x["AuditLog:EnableDetailedLogging"]).Returns("true");
        }

        private void SetupHttpContext()
        {
            var httpContext = new DefaultHttpContext();
            httpContext.Connection.RemoteIpAddress = System.Net.IPAddress.Parse("127.0.0.1");
            httpContext.Request.Headers["User-Agent"] = "Test User Agent";
            
            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.NameIdentifier, "user123"),
                new Claim("tenant_id", "tenant1")
            };
            httpContext.User = new ClaimsPrincipal(new ClaimsIdentity(claims, "Test"));
            
            _httpContextAccessorMock.Setup(x => x.HttpContext).Returns(httpContext);
        }

        public void Dispose()
        {
            _context.Dispose();
        }
    }
}