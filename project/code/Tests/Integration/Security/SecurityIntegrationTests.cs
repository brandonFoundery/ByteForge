using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Api;
using ByteForgeFrontend.Models.Security;
using ByteForgeFrontend.Services.Security.Authentication;
using ByteForgeFrontend.Services.Security.Audit;
using ByteForgeFrontend.Services.Security.Compliance;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Newtonsoft.Json;
using Xunit;
using Xunit.Abstractions;

namespace ByteForgeFrontend.Tests.Integration.Security
{
    /// <summary>
    /// Comprehensive security integration tests covering authentication, authorization, 
    /// multi-tenancy, audit logging, and compliance features
    /// </summary>
    public class SecurityIntegrationTests : IClassFixture<WebApplicationFactory<Program>>, IAsyncLifetime
    {
        private readonly WebApplicationFactory<Program> _factory;
        private readonly ITestOutputHelper _output;
        private HttpClient _client;
        private IServiceScope _scope;
        private IApiKeyManagementService _apiKeyService;
        private IAuditLoggingService _auditService;
        private IComplianceService _complianceService;
        private UserManager<Models.ApplicationUser> _userManager;

        public SecurityIntegrationTests(WebApplicationFactory<Program> factory, ITestOutputHelper output)
        {
            _factory = factory;
            _output = output;
        }

        public async Task InitializeAsync()
        {
            _client = _factory.WithWebHostBuilder(builder =>
            {
                builder.ConfigureServices(services =>
                {
                    // Ensure test environment
                    services.Configure<IdentityOptions>(options =>
                    {
                        // Weaken password requirements for testing
                        options.Password.RequireDigit = false;
                        options.Password.RequiredLength = 6;
                        options.Password.RequireNonAlphanumeric = false;
                        options.Password.RequireUppercase = false;
                    });
                });
            }).CreateClient(new WebApplicationFactoryClientOptions
            {
                AllowAutoRedirect = false
            });

            _scope = _factory.Services.CreateScope();
            _apiKeyService = _scope.ServiceProvider.GetRequiredService<IApiKeyManagementService>();
            _auditService = _scope.ServiceProvider.GetRequiredService<IAuditLoggingService>();
            _complianceService = _scope.ServiceProvider.GetRequiredService<IComplianceService>();
            _userManager = _scope.ServiceProvider.GetRequiredService<UserManager<Models.ApplicationUser>>();
        }

        public async Task DisposeAsync()
        {
            _scope?.Dispose();
            _client?.Dispose();
        }

        [Fact]
        public async Task Authentication_CompleteFlow_ShouldEnforceSecurely()
        {
            _output.WriteLine("=== Testing Authentication Security ===");

            // Test 1: Unauthenticated access should be blocked
            _output.WriteLine("\nTest 1: Verifying unauthenticated access is blocked");
            var response = await _client.GetAsync("/api/monitoring/status");
            Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
            _output.WriteLine("✓ Unauthenticated access blocked correctly");

            // Test 2: Register new user
            _output.WriteLine("\nTest 2: Testing user registration");
            var registerData = new
            {
                email = "security-test@example.com",
                password = "Test123!",
                confirmPassword = "Test123!"
            };

            response = await _client.PostAsync("/api/auth/register",
                new StringContent(JsonConvert.SerializeObject(registerData), Encoding.UTF8, "application/json"));
            
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            var registerResult = JsonConvert.DeserializeObject<ApiResponse<AuthResponse>>(
                await response.Content.ReadAsStringAsync());
            Assert.True(registerResult.Success);
            Assert.NotNull(registerResult.Data.Token);
            _output.WriteLine("✓ User registration successful");

            // Test 3: Login with correct credentials
            _output.WriteLine("\nTest 3: Testing login with correct credentials");
            var loginData = new
            {
                email = "security-test@example.com",
                password = "Test123!"
            };

            response = await _client.PostAsync("/api/auth/login",
                new StringContent(JsonConvert.SerializeObject(loginData), Encoding.UTF8, "application/json"));
            
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            var loginResult = JsonConvert.DeserializeObject<ApiResponse<AuthResponse>>(
                await response.Content.ReadAsStringAsync());
            Assert.True(loginResult.Success);
            Assert.NotNull(loginResult.Data.Token);
            var authToken = loginResult.Data.Token;
            _output.WriteLine("✓ Login successful");

            // Test 4: Access protected endpoint with token
            _output.WriteLine("\nTest 4: Testing authenticated access");
            _client.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue("Bearer", authToken);
            
            response = await _client.GetAsync("/api/monitoring/status");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            _output.WriteLine("✓ Authenticated access successful");

            // Test 5: Invalid token should be rejected
            _output.WriteLine("\nTest 5: Testing invalid token rejection");
            _client.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue("Bearer", "invalid-token");
            
            response = await _client.GetAsync("/api/monitoring/status");
            Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
            _output.WriteLine("✓ Invalid token rejected correctly");

            // Test 6: Login with wrong password
            _output.WriteLine("\nTest 6: Testing login with wrong password");
            loginData = new
            {
                email = "security-test@example.com",
                password = "WrongPassword123!"
            };

            response = await _client.PostAsync("/api/auth/login",
                new StringContent(JsonConvert.SerializeObject(loginData), Encoding.UTF8, "application/json"));
            
            Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
            _output.WriteLine("✓ Wrong password rejected correctly");

            // Verify audit logs
            var auditLogs = await _auditService.GetAuditLogsAsync(new AuditLogQuery
            {
                UserEmail = "security-test@example.com"
            });
            
            Assert.Contains(auditLogs, log => log.Action == "User_Registration");
            Assert.Contains(auditLogs, log => log.Action == "User_Login_Success");
            Assert.Contains(auditLogs, log => log.Action == "User_Login_Failed");
            _output.WriteLine("\n✓ All authentication events properly audited");
        }

        [Fact]
        public async Task ApiKeyAuthentication_CompleteFlow_ShouldWorkCorrectly()
        {
            _output.WriteLine("=== Testing API Key Authentication ===");

            // Create a user and API key
            var user = new Models.ApplicationUser
            {
                UserName = "apikey-test@example.com",
                Email = "apikey-test@example.com",
                TenantId = Guid.NewGuid().ToString()
            };
            
            await _userManager.CreateAsync(user, "Test123!");

            // Test 1: Create API key
            _output.WriteLine("\nTest 1: Creating API key");
            var apiKeyResult = await _apiKeyService.CreateApiKeyAsync(user.Id, "Test API Key");
            Assert.True(apiKeyResult.Success);
            Assert.NotNull(apiKeyResult.Data);
            var apiKey = apiKeyResult.Data.Key;
            _output.WriteLine($"✓ API key created: {apiKey.Substring(0, 10)}...");

            // Test 2: Authenticate with API key
            _output.WriteLine("\nTest 2: Testing API key authentication");
            _client.DefaultRequestHeaders.Clear();
            _client.DefaultRequestHeaders.Add("X-API-Key", apiKey);
            
            var response = await _client.GetAsync("/api/monitoring/status");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            _output.WriteLine("✓ API key authentication successful");

            // Test 3: Invalid API key should fail
            _output.WriteLine("\nTest 3: Testing invalid API key");
            _client.DefaultRequestHeaders.Clear();
            _client.DefaultRequestHeaders.Add("X-API-Key", "invalid-api-key");
            
            response = await _client.GetAsync("/api/monitoring/status");
            Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
            _output.WriteLine("✓ Invalid API key rejected");

            // Test 4: Revoke API key
            _output.WriteLine("\nTest 4: Testing API key revocation");
            var revokeResult = await _apiKeyService.RevokeApiKeyAsync(apiKeyResult.Data.Id);
            Assert.True(revokeResult.Success);
            
            _client.DefaultRequestHeaders.Clear();
            _client.DefaultRequestHeaders.Add("X-API-Key", apiKey);
            
            response = await _client.GetAsync("/api/monitoring/status");
            Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
            _output.WriteLine("✓ Revoked API key rejected");

            // Test 5: API key rate limiting
            _output.WriteLine("\nTest 5: Testing API key rate limiting");
            var newKeyResult = await _apiKeyService.CreateApiKeyAsync(user.Id, "Rate Limit Test Key");
            Assert.True(newKeyResult.Success);
            
            _client.DefaultRequestHeaders.Clear();
            _client.DefaultRequestHeaders.Add("X-API-Key", newKeyResult.Data.Key);
            
            // Make multiple rapid requests
            var tasks = new List<Task<HttpResponseMessage>>();
            for (int i = 0; i < 100; i++)
            {
                tasks.Add(_client.GetAsync("/api/monitoring/status"));
            }
            
            var responses = await Task.WhenAll(tasks);
            var rateLimitedCount = responses.Count(r => r.StatusCode == HttpStatusCode.TooManyRequests);
            
            Assert.True(rateLimitedCount > 0, "Rate limiting should have triggered");
            _output.WriteLine($"✓ Rate limiting working: {rateLimitedCount} requests limited");

            // Verify audit logs
            var auditLogs = await _auditService.GetAuditLogsAsync(new AuditLogQuery
            {
                Action = "API_Key_Created"
            });
            Assert.NotEmpty(auditLogs);
            _output.WriteLine("\n✓ API key operations properly audited");
        }

        [Fact]
        public async Task MultiTenancy_IsolationAndAccess_ShouldBeEnforced()
        {
            _output.WriteLine("=== Testing Multi-Tenant Security ===");

            // Create two tenants with users
            var tenant1Id = Guid.NewGuid().ToString();
            var tenant2Id = Guid.NewGuid().ToString();

            // Create users for each tenant
            var user1 = await CreateTenantUser("tenant1-user@example.com", tenant1Id);
            var user2 = await CreateTenantUser("tenant2-user@example.com", tenant2Id);

            // Get auth tokens for both users
            var token1 = await GetAuthToken("tenant1-user@example.com", "Test123!");
            var token2 = await GetAuthToken("tenant2-user@example.com", "Test123!");

            _output.WriteLine($"Created Tenant 1: {tenant1Id}");
            _output.WriteLine($"Created Tenant 2: {tenant2Id}");

            // Test 1: Create project as tenant 1
            _output.WriteLine("\nTest 1: Creating project for tenant 1");
            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token1);
            
            var projectData = new
            {
                name = "Tenant 1 Project",
                description = "This should only be visible to tenant 1"
            };
            
            var response = await _client.PostAsync("/api/infrastructure/projects",
                new StringContent(JsonConvert.SerializeObject(projectData), Encoding.UTF8, "application/json"));
            
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            var projectResult = JsonConvert.DeserializeObject<ApiResponse<dynamic>>(
                await response.Content.ReadAsStringAsync());
            Assert.True(projectResult.Success);
            var project1Id = projectResult.Data.id;
            _output.WriteLine($"✓ Project created for tenant 1: {project1Id}");

            // Test 2: Try to access tenant 1's project as tenant 2
            _output.WriteLine("\nTest 2: Attempting cross-tenant access");
            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token2);
            
            response = await _client.GetAsync($"/api/infrastructure/projects/{project1Id}");
            Assert.Equal(HttpStatusCode.NotFound, response.StatusCode); // Should appear as not found
            _output.WriteLine("✓ Cross-tenant access blocked correctly");

            // Test 3: Verify tenant 1 can access their own project
            _output.WriteLine("\nTest 3: Verifying same-tenant access");
            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token1);
            
            response = await _client.GetAsync($"/api/infrastructure/projects/{project1Id}");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            _output.WriteLine("✓ Same-tenant access allowed correctly");

            // Test 4: List projects should only show tenant's own projects
            _output.WriteLine("\nTest 4: Testing project listing isolation");
            
            // Create project for tenant 2
            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token2);
            var project2Data = new
            {
                name = "Tenant 2 Project",
                description = "This should only be visible to tenant 2"
            };
            
            response = await _client.PostAsync("/api/infrastructure/projects",
                new StringContent(JsonConvert.SerializeObject(project2Data), Encoding.UTF8, "application/json"));
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);

            // Get projects for tenant 1
            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token1);
            response = await _client.GetAsync("/api/infrastructure/projects");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            
            var tenant1Projects = JsonConvert.DeserializeObject<ApiResponse<List<dynamic>>>(
                await response.Content.ReadAsStringAsync());
            Assert.Single(tenant1Projects.Data);
            Assert.Equal("Tenant 1 Project", tenant1Projects.Data[0].name.ToString());
            
            // Get projects for tenant 2
            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token2);
            response = await _client.GetAsync("/api/infrastructure/projects");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            
            var tenant2Projects = JsonConvert.DeserializeObject<ApiResponse<List<dynamic>>>(
                await response.Content.ReadAsStringAsync());
            Assert.Single(tenant2Projects.Data);
            Assert.Equal("Tenant 2 Project", tenant2Projects.Data[0].name.ToString());
            
            _output.WriteLine("✓ Project listing properly isolated by tenant");

            // Test 5: Audit logs should be tenant-isolated
            _output.WriteLine("\nTest 5: Testing audit log isolation");
            var tenant1Logs = await _auditService.GetAuditLogsAsync(new AuditLogQuery
            {
                TenantId = tenant1Id
            });
            
            var tenant2Logs = await _auditService.GetAuditLogsAsync(new AuditLogQuery
            {
                TenantId = tenant2Id
            });
            
            // Verify no cross-contamination
            Assert.All(tenant1Logs, log => Assert.Equal(tenant1Id, log.TenantId));
            Assert.All(tenant2Logs, log => Assert.Equal(tenant2Id, log.TenantId));
            
            _output.WriteLine("✓ Audit logs properly isolated by tenant");

            _output.WriteLine("\n=== Multi-tenant security verified ===");
        }

        [Fact]
        public async Task SecurityHeaders_AllEndpoints_ShouldBePresent()
        {
            _output.WriteLine("=== Testing Security Headers ===");

            var endpoints = new[]
            {
                "/",
                "/api/monitoring/status",
                "/api/auth/login",
                "/dashboard/monitoring"
            };

            foreach (var endpoint in endpoints)
            {
                _output.WriteLine($"\nTesting endpoint: {endpoint}");
                
                var response = await _client.GetAsync(endpoint);
                
                // Check security headers
                Assert.True(response.Headers.Contains("X-Content-Type-Options"));
                Assert.Equal("nosniff", response.Headers.GetValues("X-Content-Type-Options").First());
                _output.WriteLine("✓ X-Content-Type-Options: nosniff");

                Assert.True(response.Headers.Contains("X-Frame-Options"));
                Assert.Equal("DENY", response.Headers.GetValues("X-Frame-Options").First());
                _output.WriteLine("✓ X-Frame-Options: DENY");

                Assert.True(response.Headers.Contains("X-XSS-Protection"));
                Assert.Equal("1; mode=block", response.Headers.GetValues("X-XSS-Protection").First());
                _output.WriteLine("✓ X-XSS-Protection: 1; mode=block");

                // Check for HTTPS redirect in production (simulated)
                if (endpoint.StartsWith("/api"))
                {
                    Assert.True(response.Headers.Contains("Strict-Transport-Security"));
                    _output.WriteLine("✓ Strict-Transport-Security present");
                }
            }

            _output.WriteLine("\n=== All security headers verified ===");
        }

        [Fact]
        public async Task ComplianceFeatures_DataProtection_ShouldWork()
        {
            _output.WriteLine("=== Testing Compliance Features ===");

            // Create test user
            var user = await CreateTenantUser("compliance-test@example.com", Guid.NewGuid().ToString());
            var token = await GetAuthToken("compliance-test@example.com", "Test123!");

            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

            // Test 1: Data export (GDPR right to data portability)
            _output.WriteLine("\nTest 1: Testing data export");
            var exportResult = await _complianceService.ExportUserDataAsync(user.Id);
            Assert.True(exportResult.Success);
            Assert.NotNull(exportResult.Data);
            Assert.Contains("UserProfile", exportResult.Data);
            Assert.Contains("AuditLogs", exportResult.Data);
            _output.WriteLine("✓ User data export successful");

            // Test 2: Data anonymization
            _output.WriteLine("\nTest 2: Testing data anonymization");
            var anonymizeResult = await _complianceService.AnonymizeUserDataAsync(user.Id);
            Assert.True(anonymizeResult.Success);
            
            // Verify user data is anonymized
            var anonymizedUser = await _userManager.FindByIdAsync(user.Id);
            Assert.NotEqual("compliance-test@example.com", anonymizedUser.Email);
            Assert.StartsWith("anonymized-", anonymizedUser.Email);
            _output.WriteLine("✓ User data anonymized successfully");

            // Test 3: Audit trail for compliance actions
            _output.WriteLine("\nTest 3: Verifying compliance audit trail");
            var complianceLogs = await _auditService.GetAuditLogsAsync(new AuditLogQuery
            {
                Category = "Compliance"
            });
            
            Assert.Contains(complianceLogs, log => log.Action == "User_Data_Exported");
            Assert.Contains(complianceLogs, log => log.Action == "User_Data_Anonymized");
            _output.WriteLine("✓ Compliance actions properly audited");

            // Test 4: Data retention policies
            _output.WriteLine("\nTest 4: Testing data retention");
            var retentionResult = await _complianceService.ApplyDataRetentionPolicyAsync();
            Assert.True(retentionResult.Success);
            _output.WriteLine($"✓ Data retention policy applied: {retentionResult.Data.RecordsProcessed} records processed");

            _output.WriteLine("\n=== Compliance features verified ===");
        }

        [Fact]
        public async Task AuditLogging_ComprehensiveCoverage_ShouldCaptureAllEvents()
        {
            _output.WriteLine("=== Testing Comprehensive Audit Logging ===");

            var tenantId = Guid.NewGuid().ToString();
            var user = await CreateTenantUser("audit-test@example.com", tenantId);
            var token = await GetAuthToken("audit-test@example.com", "Test123!");

            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

            // Perform various actions to generate audit logs
            var actions = new List<(string action, Func<Task>)>
            {
                ("Login", async () => await GetAuthToken("audit-test@example.com", "Test123!")),
                ("Create Project", async () => await _client.PostAsync("/api/infrastructure/projects",
                    new StringContent(JsonConvert.SerializeObject(new { name = "Audit Test Project" }), 
                    Encoding.UTF8, "application/json"))),
                ("Generate Document", async () => await _client.PostAsync("/api/requirements/generate",
                    new StringContent(JsonConvert.SerializeObject(new { projectId = Guid.NewGuid(), documentType = "BRD" }), 
                    Encoding.UTF8, "application/json"))),
                ("Update Settings", async () => await _client.PutAsync("/api/settings/workflow",
                    new StringContent(JsonConvert.SerializeObject(new { enableNotifications = true }), 
                    Encoding.UTF8, "application/json")))
            };

            foreach (var (actionName, action) in actions)
            {
                _output.WriteLine($"\nPerforming action: {actionName}");
                await action();
                _output.WriteLine($"✓ {actionName} completed");
            }

            // Wait a moment for audit logs to be written
            await Task.Delay(500);

            // Retrieve and verify audit logs
            _output.WriteLine("\nVerifying audit logs...");
            var auditLogs = await _auditService.GetAuditLogsAsync(new AuditLogQuery
            {
                TenantId = tenantId,
                StartDate = DateTime.UtcNow.AddMinutes(-5),
                EndDate = DateTime.UtcNow
            });

            Assert.NotEmpty(auditLogs);
            _output.WriteLine($"Found {auditLogs.Count()} audit log entries");

            // Verify critical fields are present
            foreach (var log in auditLogs)
            {
                Assert.NotNull(log.Id);
                Assert.NotNull(log.Timestamp);
                Assert.NotNull(log.Action);
                Assert.NotNull(log.UserId);
                Assert.Equal(tenantId, log.TenantId);
                Assert.NotNull(log.IpAddress);
                
                _output.WriteLine($"  - {log.Timestamp:HH:mm:ss} {log.Action} by {log.UserEmail}");
            }

            // Test audit log search functionality
            _output.WriteLine("\nTesting audit log search...");
            var searchResults = await _auditService.SearchAuditLogsAsync("Project");
            Assert.NotEmpty(searchResults);
            _output.WriteLine($"✓ Search found {searchResults.Count()} results");

            // Test audit log export
            _output.WriteLine("\nTesting audit log export...");
            var exportResult = await _auditService.ExportAuditLogsAsync(new AuditLogQuery
            {
                TenantId = tenantId
            }, "csv");
            
            Assert.True(exportResult.Success);
            Assert.NotNull(exportResult.Data);
            _output.WriteLine("✓ Audit logs exported successfully");

            _output.WriteLine("\n=== Audit logging comprehensively verified ===");
        }

        // Helper methods
        private async Task<Models.ApplicationUser> CreateTenantUser(string email, string tenantId)
        {
            var user = new Models.ApplicationUser
            {
                UserName = email,
                Email = email,
                TenantId = tenantId
            };
            
            var result = await _userManager.CreateAsync(user, "Test123!");
            Assert.True(result.Succeeded);
            
            return user;
        }

        private async Task<string> GetAuthToken(string email, string password)
        {
            var loginData = new { email, password };
            var response = await _client.PostAsync("/api/auth/login",
                new StringContent(JsonConvert.SerializeObject(loginData), Encoding.UTF8, "application/json"));
            
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            var loginResult = JsonConvert.DeserializeObject<ApiResponse<AuthResponse>>(
                await response.Content.ReadAsStringAsync());
            
            return loginResult.Data.Token;
        }

        private class AuthResponse
        {
            public string Token { get; set; }
            public string Email { get; set; }
            public string UserId { get; set; }
        }
    }
}