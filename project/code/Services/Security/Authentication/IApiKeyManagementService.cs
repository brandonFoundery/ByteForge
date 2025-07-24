using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;

namespace ByteForgeFrontend.Services.Security.Authentication
{
    public interface IApiKeyManagementService
    {
        Task<ApiKeyCreateResult> CreateApiKeyAsync(
            string tenantId, 
            string name, 
            string value, 
            ApiKeyType keyType,
            Dictionary<string, string> metadata = null,
            int? expiresInDays = null);
            
        Task<IEnumerable<ApiKeyInfo>> GetApiKeysAsync(string tenantId, bool includeValues = false);
        
        Task<ApiKeyUpdateResult> UpdateApiKeyAsync(string keyId, string tenantId, string newValue);
        
        Task<ApiKeyDeleteResult> DeleteApiKeyAsync(string keyId, string tenantId);
        
        Task<ApiKeyRotateResult> RotateApiKeyAsync(string keyId, string tenantId);
        
        Task<ApiKeyValidationResult> ValidateApiKeyAsync(string apiKey);
        
        Task<IEnumerable<ApiKeyAuditLog>> GetApiKeyAuditLogsAsync(string keyId, string tenantId);
        
        Task<bool> SetRateLimitAsync(string keyId, string tenantId, int limit, int windowSeconds);
        
        Task<string> EncryptApiKeyAsync(string plainValue);
        
        Task<string> DecryptApiKeyAsync(string encryptedValue);
    }
}