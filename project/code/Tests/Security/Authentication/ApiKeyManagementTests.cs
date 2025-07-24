using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;
using ByteForgeFrontend.Services.Security.Authentication;
using ByteForgeFrontend.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace ByteForgeFrontend.Tests.Security.Authentication
{
    public class ApiKeyManagementTests : IDisposable
    {
        private readonly ApplicationDbContext _context;
        private readonly Mock<IConfiguration> _configurationMock;
        private readonly Mock<ILogger<ApiKeyManagementService>> _loggerMock;
        private readonly ApiKeyManagementService _apiKeyService;

        public ApiKeyManagementTests()
        {
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
                .Options;
            
            _context = new ApplicationDbContext(options);
            _configurationMock = new Mock<IConfiguration>();
            _loggerMock = new Mock<ILogger<ApiKeyManagementService>>();
            
            SetupEncryptionConfiguration();
            
            _apiKeyService = new ApiKeyManagementService(
                _context,
                _configurationMock.Object,
                _loggerMock.Object);
        }

        [Fact]
        public async Task CreateApiKeyAsync_ForLLMProvider_ShouldStoreEncrypted()
        {
            // Arrange
            var tenantId = "tenant1";
            var keyName = "OpenAI API Key";
            var keyValue = "sk-1234567890abcdef";
            var keyType = ApiKeyType.LLMProvider;
            var metadata = new Dictionary<string, string>
            {
                ["provider"] = "openai",
                ["model"] = "gpt-4"
            };

            // Act
            var result = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                keyName,
                keyValue,
                keyType,
                metadata);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.NotEmpty(result.KeyId);
            Assert.NotEmpty(result.KeyPrefix);
            Assert.True(result.KeyPrefix.StartsWith("sk-"));
            Assert.True(result.KeyPrefix.EndsWith("..."));
            
            // Verify the key is stored encrypted
            var storedKey = await _context.ApiKeys.FirstOrDefaultAsync(k => k.Id == result.KeyId);
            Assert.NotNull(storedKey);
            Assert.NotEqual(keyValue, storedKey.EncryptedValue); // Should be encrypted
            Assert.Equal(keyName, storedKey.Name);
            Assert.Equal(tenantId, storedKey.TenantId);
            Assert.Equal(keyType, storedKey.KeyType);
            Assert.NotNull(storedKey.Metadata);
            Assert.Contains("provider", storedKey.Metadata);
        }

        [Fact]
        public async Task CreateApiKeyAsync_ForUserAccess_ShouldGenerateSecureKey()
        {
            // Arrange
            var tenantId = "tenant1";
            var userId = "user123";
            var keyName = "My API Access Key";
            var keyType = ApiKeyType.UserAccess;
            var metadata = new Dictionary<string, string>
            {
                ["userId"] = userId,
                ["permissions"] = "read,write"
            };

            // Act
            var result = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                keyName,
                null, // Let the service generate the key
                keyType,
                metadata);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.NotEmpty(result.GeneratedKey); // Should return the generated key
            Assert.True(result.GeneratedKey.StartsWith("byteforge_"));
            Assert.True(result.GeneratedKey.Length >= 32);
            
            // Verify we can authenticate with the generated key
            var authResult = await _apiKeyService.ValidateApiKeyAsync(result.GeneratedKey);
            Assert.True(authResult.IsValid);
            Assert.Equal(tenantId, authResult.TenantId);
            Assert.Equal(userId, authResult.UserId);
        }

        [Fact]
        public async Task CreateApiKeyAsync_ForServiceToService_ShouldIncludeServiceIdentifier()
        {
            // Arrange
            var tenantId = "system";
            var serviceName = "RequirementsGenerationService";
            var keyType = ApiKeyType.ServiceToService;
            var metadata = new Dictionary<string, string>
            {
                ["service"] = serviceName,
                ["scope"] = "internal",
                ["allowedEndpoints"] = "/api/internal/*"
            };

            // Act
            var result = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                $"{serviceName} Service Key",
                null,
                keyType,
                metadata);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.NotEmpty(result.GeneratedKey);
            Assert.True(result.GeneratedKey.StartsWith("byteforge_svc_"));
            
            // Verify service authentication
            var authResult = await _apiKeyService.ValidateApiKeyAsync(result.GeneratedKey);
            Assert.True(authResult.IsValid);
            Assert.Equal(serviceName, authResult.ServiceName);
            Assert.Contains("/api/internal/*", authResult.AllowedEndpoints);
        }

        [Fact]
        public async Task GetApiKeysAsync_ShouldReturnDecryptedKeysForAuthorizedUser()
        {
            // Arrange
            var tenantId = "tenant1";
            var keys = new[]
            {
                ("OpenAI Key", "sk-openai123", ApiKeyType.LLMProvider),
                ("Claude Key", "sk-claude456", ApiKeyType.LLMProvider),
                ("User Access Key", "byteforge_user789", ApiKeyType.UserAccess)
            };

            foreach (var (name, value, type) in keys)
            {
                await _apiKeyService.CreateApiKeyAsync(tenantId, name, value, type);
            }

            // Act
            var retrievedKeys = await _apiKeyService.GetApiKeysAsync(tenantId, includeValues: true);

            // Assert
            Assert.Equal(3, retrievedKeys.Count());
            
            var openAiKey = retrievedKeys.First(k => k.Name == "OpenAI Key");
            Assert.Equal("sk-openai123", openAiKey.DecryptedValue);
            Assert.Equal("sk-ope...123", openAiKey.KeyPrefix);
        }

        [Fact]
        public async Task GetApiKeysAsync_WithoutIncludeValues_ShouldNotReturnDecryptedKeys()
        {
            // Arrange
            var tenantId = "tenant1";
            await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                "Secret Key",
                "super-secret-value",
                ApiKeyType.LLMProvider);

            // Act
            var retrievedKeys = await _apiKeyService.GetApiKeysAsync(tenantId, includeValues: false);

            // Assert
            var key = retrievedKeys.First();
            Assert.Null(key.DecryptedValue);
            Assert.NotEmpty(key.KeyPrefix); // Should still show prefix
        }

        [Fact]
        public async Task UpdateApiKeyAsync_ShouldReEncryptValue()
        {
            // Arrange
            var tenantId = "tenant1";
            var createResult = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                "API Key",
                "old-value",
                ApiKeyType.LLMProvider);
            
            var newValue = "new-secret-value";

            // Act
            var updateResult = await _apiKeyService.UpdateApiKeyAsync(
                createResult.KeyId,
                tenantId,
                newValue);

            // Assert
            Assert.True(updateResult.Success);
            
            // Verify the new value works
            var keys = await _apiKeyService.GetApiKeysAsync(tenantId, includeValues: true);
            var updatedKey = keys.First(k => k.Id == createResult.KeyId);
            Assert.Equal(newValue, updatedKey.DecryptedValue);
        }

        [Fact]
        public async Task DeleteApiKeyAsync_ShouldSoftDelete()
        {
            // Arrange
            var tenantId = "tenant1";
            var createResult = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                "Temporary Key",
                "temp-value",
                ApiKeyType.UserAccess);

            // Act
            var deleteResult = await _apiKeyService.DeleteApiKeyAsync(
                createResult.KeyId,
                tenantId);

            // Assert
            Assert.True(deleteResult.Success);
            
            // Verify soft delete
            var deletedKey = await _context.ApiKeys
                .IgnoreQueryFilters()
                .FirstOrDefaultAsync(k => k.Id == createResult.KeyId);
            
            Assert.NotNull(deletedKey);
            Assert.True(deletedKey.IsDeleted);
            Assert.NotNull(deletedKey.DeletedAt);
        }

        [Fact]
        public async Task RotateApiKeyAsync_ShouldCreateNewKeyAndExpireOld()
        {
            // Arrange
            var tenantId = "tenant1";
            var originalResult = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                "Rotating Key",
                null,
                ApiKeyType.UserAccess);

            // Act
            var rotateResult = await _apiKeyService.RotateApiKeyAsync(
                originalResult.KeyId,
                tenantId);

            // Assert
            Assert.True(rotateResult.Success);
            Assert.NotEmpty(rotateResult.NewKey);
            Assert.NotEqual(originalResult.GeneratedKey, rotateResult.NewKey);
            
            // Verify old key is expired
            var oldKey = await _context.ApiKeys.FindAsync(originalResult.KeyId);
            Assert.True(oldKey.IsExpired);
            Assert.NotNull(oldKey.ExpiresAt);
            Assert.True(oldKey.ExpiresAt <= DateTime.UtcNow);
            
            // Verify new key works
            var authResult = await _apiKeyService.ValidateApiKeyAsync(rotateResult.NewKey);
            Assert.True(authResult.IsValid);
        }

        [Fact]
        public async Task ValidateApiKeyAsync_WithExpiredKey_ShouldReturnInvalid()
        {
            // Arrange
            var tenantId = "tenant1";
            var createResult = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                "Expiring Key",
                null,
                ApiKeyType.UserAccess,
                expiresInDays: -1); // Already expired

            // Act
            var validationResult = await _apiKeyService.ValidateApiKeyAsync(createResult.GeneratedKey);

            // Assert
            Assert.False(validationResult.IsValid);
            Assert.Equal("API key has expired", validationResult.ErrorMessage);
        }

        [Fact]
        public async Task ValidateApiKeyAsync_WithRateLimiting_ShouldEnforce()
        {
            // Arrange
            var tenantId = "tenant1";
            var metadata = new Dictionary<string, string>
            {
                ["rateLimit"] = "10",
                ["rateLimitWindow"] = "60" // 10 requests per 60 seconds
            };
            
            var createResult = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                "Rate Limited Key",
                null,
                ApiKeyType.UserAccess,
                metadata: metadata);

            // Act - Make multiple requests
            var results = new List<ApiKeyValidationResult>();
            for (int i = 0; i < 15; i++)
            {
                var result = await _apiKeyService.ValidateApiKeyAsync(createResult.GeneratedKey);
                results.Add(result);
            }

            // Assert
            Assert.True(results.Take(10).All(r => r.IsValid));
            Assert.True(results.Skip(10).All(r => !r.IsValid && r.ErrorMessage.Contains("Rate limit exceeded")));
        }

        [Fact]
        public async Task GetApiKeyAuditLogsAsync_ShouldTrackAllOperations()
        {
            // Arrange
            var tenantId = "tenant1";
            var createResult = await _apiKeyService.CreateApiKeyAsync(
                tenantId,
                "Audited Key",
                "secret",
                ApiKeyType.LLMProvider);
            
            // Perform some operations
            await _apiKeyService.ValidateApiKeyAsync(createResult.KeyId);
            await _apiKeyService.UpdateApiKeyAsync(createResult.KeyId, tenantId, "new-secret");
            await _apiKeyService.DeleteApiKeyAsync(createResult.KeyId, tenantId);

            // Act
            var auditLogs = await _apiKeyService.GetApiKeyAuditLogsAsync(createResult.KeyId, tenantId);

            // Assert
            Assert.NotEmpty(auditLogs);
            Assert.Contains(auditLogs, log => log.Action == "Created");
            Assert.Contains(auditLogs, log => log.Action == "Validated");
            Assert.Contains(auditLogs, log => log.Action == "Updated");
            Assert.Contains(auditLogs, log => log.Action == "Deleted");
            
            // Verify audit logs contain proper information
            var createLog = auditLogs.First(log => log.Action == "Created");
            Assert.Equal(tenantId, createLog.TenantId);
            Assert.NotNull(createLog.Timestamp);
            Assert.NotNull(createLog.PerformedBy);
        }

        private void SetupEncryptionConfiguration()
        {
            var encryptionSection = new Mock<IConfigurationSection>();
            encryptionSection.Setup(x => x["Key"]).Returns(Convert.ToBase64String(GenerateKey(32)));
            encryptionSection.Setup(x => x["IV"]).Returns(Convert.ToBase64String(GenerateKey(16)));
            
            _configurationMock.Setup(x => x.GetSection("Encryption"))
                .Returns(encryptionSection.Object);
        }

        private byte[] GenerateKey(int size)
        {
            using var rng = RandomNumberGenerator.Create();
            var key = new byte[size];
            rng.GetBytes(key);
            return key;
        }

        public void Dispose()
        {
            _context.Dispose();
        }
    }
}