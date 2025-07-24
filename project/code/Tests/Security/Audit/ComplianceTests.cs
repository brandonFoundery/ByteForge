using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;
using ByteForgeFrontend.Services.Security.Audit;
using ByteForgeFrontend.Services.Security.Compliance;
using ByteForgeFrontend.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace ByteForgeFrontend.Tests.Security.Audit
{
    public class ComplianceTests : IDisposable
    {
        private readonly ApplicationDbContext _context;
        private readonly Mock<IConfiguration> _configurationMock;
        private readonly Mock<ILogger<ComplianceService>> _loggerMock;
        private readonly Mock<IAuditLoggingService> _auditServiceMock;
        private readonly ComplianceService _complianceService;

        public ComplianceTests()
        {
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
                .Options;
            
            _context = new ApplicationDbContext(options);
            _configurationMock = new Mock<IConfiguration>();
            _loggerMock = new Mock<ILogger<ComplianceService>>();
            _auditServiceMock = new Mock<IAuditLoggingService>();
            
            _complianceService = new ComplianceService(
                _context,
                _auditServiceMock.Object,
                _configurationMock.Object,
                _loggerMock.Object);
        }

        [Fact]
        public async Task ValidateGDPRComplianceAsync_WithCompliantData_ShouldPass()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            
            // Setup user with proper consent
            var user = new ApplicationUser
            {
                Id = userId,
                Email = "user@example.com",
                TenantId = tenantId,
                DataProcessingConsent = true,
                DataProcessingConsentDate = DateTime.UtcNow.AddDays(-30),
                MarketingConsent = false,
                LastPrivacyPolicyAcceptance = DateTime.UtcNow.AddDays(-15)
            };
            _context.Users.Add(user);
            
            // Setup data retention policy
            var retentionPolicy = new DataRetentionPolicy
            {
                TenantId = tenantId,
                DataType = "PersonalData",
                RetentionDays = 365,
                IsActive = true
            };
            _context.DataRetentionPolicies.Add(retentionPolicy);
            
            await _context.SaveChangesAsync();

            // Act
            var result = await _complianceService.ValidateGDPRComplianceAsync(tenantId, userId);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.IsCompliant);
            Assert.Empty(result.Violations);
            Assert.Contains("DataProcessingConsent", result.CompliantAreas);
            Assert.Contains("DataRetentionPolicy", result.CompliantAreas);
            Assert.Contains("PrivacyPolicyAcceptance", result.CompliantAreas);
        }

        [Fact]
        public async Task ValidateGDPRComplianceAsync_WithMissingConsent_ShouldFail()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            
            var user = new ApplicationUser
            {
                Id = userId,
                Email = "user@example.com",
                TenantId = tenantId,
                DataProcessingConsent = false,
                DataProcessingConsentDate = null
            };
            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            // Act
            var result = await _complianceService.ValidateGDPRComplianceAsync(tenantId, userId);

            // Assert
            Assert.NotNull(result);
            Assert.False(result.IsCompliant);
            Assert.NotEmpty(result.Violations);
            Assert.Contains(result.Violations, v => v.Type == "MissingConsent");
            Assert.Contains(result.Violations, v => v.Severity == ComplianceSeverity.Critical);
        }

        [Fact]
        public async Task ValidateGDPRComplianceAsync_WithExpiredConsent_ShouldRequireRenewal()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            
            var user = new ApplicationUser
            {
                Id = userId,
                Email = "user@example.com",
                TenantId = tenantId,
                DataProcessingConsent = true,
                DataProcessingConsentDate = DateTime.UtcNow.AddDays(-400) // Over a year old
            };
            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            // Act
            var result = await _complianceService.ValidateGDPRComplianceAsync(tenantId, userId);

            // Assert
            Assert.NotNull(result);
            Assert.False(result.IsCompliant);
            Assert.Contains(result.Violations, v => v.Type == "ExpiredConsent");
            Assert.Contains(result.Recommendations, r => r.Contains("renew consent"));
        }

        [Fact]
        public async Task HandleDataPortabilityRequestAsync_ShouldExportUserData()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            
            // Setup user data
            var user = new ApplicationUser
            {
                Id = userId,
                Email = "user@example.com",
                TenantId = tenantId,
                FirstName = "John",
                LastName = "Doe",
                CreatedDate = DateTime.UtcNow.AddMonths(-6)
            };
            _context.Users.Add(user);
            
            // Add some projects
            var project = new Project
            {
                Id = "proj1",
                Name = "Test Project",
                UserId = userId,
                TenantId = tenantId,
                CreatedAt = DateTime.UtcNow.AddMonths(-3)
            };
            _context.Projects.Add(project);
            
            // Add some API keys
            var apiKey = new ApiKey
            {
                Id = "key1",
                Name = "User API Key",
                UserId = userId,
                TenantId = tenantId,
                KeyType = ApiKeyType.UserAccess,
                CreatedAt = DateTime.UtcNow.AddMonths(-2)
            };
            _context.ApiKeys.Add(apiKey);
            
            await _context.SaveChangesAsync();

            // Act
            var result = await _complianceService.HandleDataPortabilityRequestAsync(tenantId, userId);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.NotEmpty(result.ExportedData);
            Assert.Contains("PersonalInformation", result.ExportedData.Keys);
            Assert.Contains("Projects", result.ExportedData.Keys);
            Assert.Contains("ApiKeys", result.ExportedData.Keys);
            Assert.Contains("AuditLogs", result.ExportedData.Keys);
            
            var personalInfo = result.ExportedData["PersonalInformation"] as Dictionary<string, object>;
            Assert.Equal("user@example.com", personalInfo["Email"]);
            Assert.Equal("John", personalInfo["FirstName"]);
            
            var projects = result.ExportedData["Projects"] as List<object>;
            Assert.Single(projects);
        }

        [Fact]
        public async Task HandleDataErasureRequestAsync_ShouldAnonymizeData()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            
            // Setup user and related data
            var user = new ApplicationUser
            {
                Id = userId,
                Email = "user@example.com",
                UserName = "johndoe",
                TenantId = tenantId,
                FirstName = "John",
                LastName = "Doe"
            };
            _context.Users.Add(user);
            
            var project = new Project
            {
                Id = "proj1",
                Name = "John's Project",
                UserId = userId,
                TenantId = tenantId
            };
            _context.Projects.Add(project);
            
            await _context.SaveChangesAsync();

            // Act
            var result = await _complianceService.HandleDataErasureRequestAsync(tenantId, userId);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.NotEmpty(result.AnonymizedFields);
            
            // Verify user data is anonymized
            var anonymizedUser = await _context.Users.FindAsync(userId);
            Assert.NotEqual("user@example.com", anonymizedUser.Email);
            Assert.True(anonymizedUser.Email.StartsWith("anonymized_"));
            Assert.Equal("[REDACTED]", anonymizedUser.FirstName);
            Assert.Equal("[REDACTED]", anonymizedUser.LastName);
            
            // Verify related data is updated
            var updatedProject = await _context.Projects.FindAsync("proj1");
            Assert.Equal("[User Deleted]'s Project", updatedProject.Name);
        }

        [Fact]
        public async Task ValidateSOC2ComplianceAsync_WithProperControls_ShouldPass()
        {
            // Arrange
            var tenantId = "tenant1";
            
            // Setup security controls
            var securityConfig = new TenantSecurityConfiguration
            {
                TenantId = tenantId,
                RequireTwoFactor = true,
                PasswordComplexityRules = "MinLength:12;RequireUppercase:true;RequireLowercase:true;RequireDigit:true;RequireSpecial:true",
                SessionTimeoutMinutes = 30,
                MaxFailedLoginAttempts = 5,
                RequireEncryptionAtRest = true,
                RequireEncryptionInTransit = true,
                EnableAuditLogging = true,
                EnableIPWhitelisting = false
            };
            _context.TenantSecurityConfigurations.Add(securityConfig);
            
            // Setup access controls
            var accessControl = new AccessControlPolicy
            {
                TenantId = tenantId,
                RequireRoleBasedAccess = true,
                RequireDataClassification = true,
                EnableLeastPrivilege = true,
                RequireAccessReview = true,
                AccessReviewFrequencyDays = 90
            };
            _context.AccessControlPolicies.Add(accessControl);
            
            await _context.SaveChangesAsync();

            // Mock audit logs showing proper monitoring
            _auditServiceMock.Setup(x => x.GetAuditStatisticsAsync(
                    It.IsAny<string>(), 
                    It.IsAny<DateTime>(), 
                    It.IsAny<DateTime>()))
                .ReturnsAsync(new AuditStatistics
                {
                    TotalEvents = 1000,
                    SecurityEventCount = 50,
                    UniqueUserCount = 25
                });

            // Act
            var result = await _complianceService.ValidateSOC2ComplianceAsync(tenantId);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.IsCompliant);
            Assert.Contains("Security", result.CompliantControls);
            Assert.Contains("Availability", result.CompliantControls);
            Assert.Contains("Confidentiality", result.CompliantControls);
            Assert.Contains("ProcessingIntegrity", result.CompliantControls);
            Assert.Empty(result.ControlGaps);
        }

        [Fact]
        public async Task ValidateSOC2ComplianceAsync_WithWeakSecurity_ShouldIdentifyGaps()
        {
            // Arrange
            var tenantId = "tenant1";
            
            var securityConfig = new TenantSecurityConfiguration
            {
                TenantId = tenantId,
                RequireTwoFactor = false, // Gap
                PasswordComplexityRules = "MinLength:6", // Weak
                SessionTimeoutMinutes = 480, // Too long
                MaxFailedLoginAttempts = 20, // Too high
                RequireEncryptionAtRest = false, // Gap
                EnableAuditLogging = false // Gap
            };
            _context.TenantSecurityConfigurations.Add(securityConfig);
            await _context.SaveChangesAsync();

            // Act
            var result = await _complianceService.ValidateSOC2ComplianceAsync(tenantId);

            // Assert
            Assert.NotNull(result);
            Assert.False(result.IsCompliant);
            Assert.NotEmpty(result.ControlGaps);
            Assert.Contains(result.ControlGaps, g => g.Control == "CC6.1" && g.Description.Contains("multi-factor"));
            Assert.Contains(result.ControlGaps, g => g.Control == "CC6.7" && g.Description.Contains("encryption"));
            Assert.Contains(result.ControlGaps, g => g.Control == "CC7.2" && g.Description.Contains("monitoring"));
            Assert.NotEmpty(result.RemediationSteps);
        }

        [Fact]
        public async Task GenerateComplianceDashboardAsync_ShouldProvideOverview()
        {
            // Arrange
            var tenantId = "tenant1";
            
            // Setup various compliance data
            await SetupComplianceData(tenantId);

            // Act
            var dashboard = await _complianceService.GenerateComplianceDashboardAsync(tenantId);

            // Assert
            Assert.NotNull(dashboard);
            Assert.Equal(tenantId, dashboard.TenantId);
            Assert.NotNull(dashboard.GDPRStatus);
            Assert.NotNull(dashboard.SOC2Status);
            Assert.NotEmpty(dashboard.RecentComplianceEvents);
            Assert.NotEmpty(dashboard.UpcomingActions);
            Assert.NotNull(dashboard.ComplianceScore);
            Assert.True(dashboard.ComplianceScore >= 0 && dashboard.ComplianceScore <= 100);
        }

        [Fact]
        public async Task ScheduleComplianceReviewAsync_ShouldCreateReviewTasks()
        {
            // Arrange
            var tenantId = "tenant1";
            var reviewType = ComplianceReviewType.Quarterly;
            var reviewDate = DateTime.UtcNow.AddDays(7);

            // Act
            var result = await _complianceService.ScheduleComplianceReviewAsync(
                tenantId,
                reviewType,
                reviewDate);

            // Assert
            Assert.True(result.Success);
            Assert.NotEmpty(result.ReviewId);
            Assert.NotEmpty(result.GeneratedTasks);
            
            var review = await _context.ComplianceReviews.FindAsync(result.ReviewId);
            Assert.NotNull(review);
            Assert.Equal(reviewType, review.ReviewType);
            Assert.Equal(reviewDate.Date, review.ScheduledDate.Date);
            Assert.Equal(ComplianceReviewStatus.Scheduled, review.Status);
        }

        [Fact]
        public async Task ExportComplianceReportAsync_ShouldGenerateDetailedReport()
        {
            // Arrange
            var tenantId = "tenant1";
            var reportType = ComplianceReportType.Annual;
            var year = DateTime.UtcNow.Year;
            
            await SetupComplianceData(tenantId);

            // Act
            var report = await _complianceService.ExportComplianceReportAsync(
                tenantId,
                reportType,
                year);

            // Assert
            Assert.NotNull(report);
            Assert.Equal(reportType, report.Type);
            Assert.Equal(year, report.Year);
            Assert.NotEmpty(report.Sections);
            Assert.Contains("Executive Summary", report.Sections.Keys);
            Assert.Contains("GDPR Compliance", report.Sections.Keys);
            Assert.Contains("SOC2 Compliance", report.Sections.Keys);
            Assert.Contains("Security Controls", report.Sections.Keys);
            Assert.Contains("Audit Summary", report.Sections.Keys);
            Assert.Contains("Recommendations", report.Sections.Keys);
            Assert.NotEmpty(report.Attachments);
        }

        private async Task SetupComplianceData(string tenantId)
        {
            // Add users with various consent states
            for (int i = 0; i < 10; i++)
            {
                var user = new ApplicationUser
                {
                    Id = $"user{i}",
                    Email = $"user{i}@example.com",
                    TenantId = tenantId,
                    DataProcessingConsent = i % 2 == 0,
                    DataProcessingConsentDate = i % 2 == 0 ? DateTime.UtcNow.AddDays(-30) : null
                };
                _context.Users.Add(user);
            }
            
            // Add security configuration
            var securityConfig = new TenantSecurityConfiguration
            {
                TenantId = tenantId,
                RequireTwoFactor = true,
                EnableAuditLogging = true
            };
            _context.TenantSecurityConfigurations.Add(securityConfig);
            
            // Add retention policies
            var retentionPolicy = new DataRetentionPolicy
            {
                TenantId = tenantId,
                DataType = "AuditLogs",
                RetentionDays = 2555, // 7 years
                IsActive = true
            };
            _context.DataRetentionPolicies.Add(retentionPolicy);
            
            await _context.SaveChangesAsync();
        }

        public void Dispose()
        {
            _context.Dispose();
        }
    }
}