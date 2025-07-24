using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;
using ByteForgeFrontend.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Collections.Concurrent;

namespace ByteForgeFrontend.Services.Security.Authentication
{
    public class ApiKeyManagementService : IApiKeyManagementService
    {
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _configuration;
        private readonly ILogger<ApiKeyManagementService> _logger;
        private readonly byte[] _encryptionKey;
        private readonly byte[] _encryptionIV;
        
        // Simple in-memory rate limiting for demo purposes
        private static readonly ConcurrentDictionary<string, RateLimitInfo> _rateLimits = new();

        public ApiKeyManagementService(
            ApplicationDbContext context,
            IConfiguration configuration,
            ILogger<ApiKeyManagementService> logger = null)
        {
            _context = context;
            _configuration = configuration;
            _logger = logger;
            
            // Initialize encryption keys
            var encryptionSection = _configuration.GetSection("Encryption");
            _encryptionKey = Convert.FromBase64String(encryptionSection["Key"] ?? GenerateDefaultKey());
            _encryptionIV = Convert.FromBase64String(encryptionSection["IV"] ?? GenerateDefaultIV());
        }

        public async Task<ApiKeyCreateResult> CreateApiKeyAsync(
            string tenantId, 
            string name, 
            string value, 
            ApiKeyType keyType,
            Dictionary<string, string> metadata = null,
            int? expiresInDays = null)
        {
            try
            {
                var apiKey = new ApiKey
                {
                    TenantId = tenantId,
                    Name = name,
                    KeyType = keyType,
                    Metadata = metadata ?? new Dictionary<string, string>(),
                    CreatedAt = DateTime.UtcNow
                };

                // Generate key if not provided
                string actualKey = value;
                if (string.IsNullOrEmpty(value))
                {
                    actualKey = GenerateApiKey(keyType);
                }

                // Extract and store key prefix
                apiKey.KeyPrefix = GenerateKeyPrefix(actualKey);
                
                // Encrypt and store the key
                apiKey.EncryptedValue = await EncryptApiKeyAsync(actualKey);

                // Set expiration if specified
                if (expiresInDays.HasValue)
                {
                    apiKey.ExpiresAt = DateTime.UtcNow.AddDays(expiresInDays.Value);
                    apiKey.IsExpired = apiKey.ExpiresAt <= DateTime.UtcNow;
                }

                // Extract rate limit from metadata
                if (metadata != null)
                {
                    if (metadata.TryGetValue("rateLimit", out var rateLimitStr) && 
                        int.TryParse(rateLimitStr, out var rateLimit))
                    {
                        apiKey.RateLimit = rateLimit;
                    }
                    
                    if (metadata.TryGetValue("rateLimitWindow", out var windowStr) && 
                        int.TryParse(windowStr, out var window))
                    {
                        apiKey.RateLimitWindowSeconds = window;
                    }

                    if (metadata.TryGetValue("userId", out var userId))
                    {
                        apiKey.UserId = userId;
                    }
                }

                _context.ApiKeys.Add(apiKey);
                await _context.SaveChangesAsync();

                // Log the creation
                await LogApiKeyEventAsync(apiKey.Id, tenantId, "Created", 
                    new Dictionary<string, object> { ["keyType"] = keyType.ToString() });

                return new ApiKeyCreateResult
                {
                    Success = true,
                    KeyId = apiKey.Id,
                    KeyPrefix = apiKey.KeyPrefix,
                    GeneratedKey = string.IsNullOrEmpty(value) ? actualKey : null
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error creating API key");
                return new ApiKeyCreateResult
                {
                    Success = false,
                    ErrorMessage = "Failed to create API key"
                };
            }
        }

        public async Task<IEnumerable<ApiKeyInfo>> GetApiKeysAsync(string tenantId, bool includeValues = false)
        {
            var keys = await _context.ApiKeys
                .Where(k => k.TenantId == tenantId)
                .Select(k => new ApiKeyInfo
                {
                    Id = k.Id,
                    Name = k.Name,
                    KeyPrefix = k.KeyPrefix,
                    KeyType = k.KeyType,
                    Metadata = k.Metadata,
                    CreatedAt = k.CreatedAt,
                    LastUsedAt = k.LastUsedAt,
                    ExpiresAt = k.ExpiresAt
                })
                .ToListAsync();

            if (includeValues)
            {
                foreach (var key in keys)
                {
                    var apiKey = await _context.ApiKeys.FindAsync(key.Id);
                    if (apiKey != null)
                    {
                        key.DecryptedValue = await DecryptApiKeyAsync(apiKey.EncryptedValue);
                    }
                }
            }

            return keys;
        }

        public async Task<ApiKeyUpdateResult> UpdateApiKeyAsync(string keyId, string tenantId, string newValue)
        {
            try
            {
                var apiKey = await _context.ApiKeys
                    .FirstOrDefaultAsync(k => k.Id == keyId && k.TenantId == tenantId);

                if (apiKey == null)
                {
                    return new ApiKeyUpdateResult
                    {
                        Success = false,
                        ErrorMessage = "API key not found"
                    };
                }

                // Update encrypted value
                apiKey.EncryptedValue = await EncryptApiKeyAsync(newValue);
                apiKey.KeyPrefix = GenerateKeyPrefix(newValue);

                await _context.SaveChangesAsync();

                // Log the update
                await LogApiKeyEventAsync(keyId, tenantId, "Updated");

                return new ApiKeyUpdateResult { Success = true };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error updating API key");
                return new ApiKeyUpdateResult
                {
                    Success = false,
                    ErrorMessage = "Failed to update API key"
                };
            }
        }

        public async Task<ApiKeyDeleteResult> DeleteApiKeyAsync(string keyId, string tenantId)
        {
            try
            {
                var apiKey = await _context.ApiKeys
                    .FirstOrDefaultAsync(k => k.Id == keyId && k.TenantId == tenantId);

                if (apiKey == null)
                {
                    return new ApiKeyDeleteResult
                    {
                        Success = false,
                        ErrorMessage = "API key not found"
                    };
                }

                // Soft delete
                apiKey.IsDeleted = true;
                apiKey.DeletedAt = DateTime.UtcNow;

                await _context.SaveChangesAsync();

                // Log the deletion
                await LogApiKeyEventAsync(keyId, tenantId, "Deleted");

                return new ApiKeyDeleteResult { Success = true };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error deleting API key");
                return new ApiKeyDeleteResult
                {
                    Success = false,
                    ErrorMessage = "Failed to delete API key"
                };
            }
        }

        public async Task<ApiKeyRotateResult> RotateApiKeyAsync(string keyId, string tenantId)
        {
            try
            {
                var oldKey = await _context.ApiKeys
                    .FirstOrDefaultAsync(k => k.Id == keyId && k.TenantId == tenantId);

                if (oldKey == null)
                {
                    return new ApiKeyRotateResult
                    {
                        Success = false,
                        ErrorMessage = "API key not found"
                    };
                }

                // Mark old key as expired
                oldKey.IsExpired = true;
                oldKey.ExpiresAt = DateTime.UtcNow;

                // Create new key with same properties
                var newKeyValue = GenerateApiKey(oldKey.KeyType);
                var newKey = new ApiKey
                {
                    TenantId = oldKey.TenantId,
                    UserId = oldKey.UserId,
                    Name = oldKey.Name + " (Rotated)",
                    KeyType = oldKey.KeyType,
                    KeyPrefix = GenerateKeyPrefix(newKeyValue),
                    EncryptedValue = await EncryptApiKeyAsync(newKeyValue),
                    Metadata = new Dictionary<string, string>(oldKey.Metadata),
                    RateLimit = oldKey.RateLimit,
                    RateLimitWindowSeconds = oldKey.RateLimitWindowSeconds
                };

                _context.ApiKeys.Add(newKey);
                await _context.SaveChangesAsync();

                // Log the rotation
                await LogApiKeyEventAsync(keyId, tenantId, "Rotated", 
                    new Dictionary<string, object> { ["newKeyId"] = newKey.Id });

                return new ApiKeyRotateResult
                {
                    Success = true,
                    NewKey = newKeyValue,
                    NewKeyId = newKey.Id
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error rotating API key");
                return new ApiKeyRotateResult
                {
                    Success = false,
                    ErrorMessage = "Failed to rotate API key"
                };
            }
        }

        public async Task<ApiKeyValidationResult> ValidateApiKeyAsync(string apiKey)
        {
            try
            {
                // Find key by comparing encrypted values
                var allKeys = await _context.ApiKeys
                    .Where(k => !k.IsDeleted && !k.IsExpired)
                    .ToListAsync();

                ApiKey validKey = null;
                foreach (var key in allKeys)
                {
                    var decryptedValue = await DecryptApiKeyAsync(key.EncryptedValue);
                    if (decryptedValue == apiKey)
                    {
                        validKey = key;
                        break;
                    }
                }

                if (validKey == null)
                {
                    return new ApiKeyValidationResult
                    {
                        IsValid = false,
                        ErrorMessage = "Invalid API key"
                    };
                }

                // Check expiration
                if (validKey.ExpiresAt.HasValue && validKey.ExpiresAt <= DateTime.UtcNow)
                {
                    validKey.IsExpired = true;
                    await _context.SaveChangesAsync();
                    
                    return new ApiKeyValidationResult
                    {
                        IsValid = false,
                        ErrorMessage = "API key has expired"
                    };
                }

                // Check rate limiting
                if (validKey.RateLimit.HasValue)
                {
                    var rateLimitKey = $"{validKey.Id}_ratelimit";
                    var now = DateTime.UtcNow;
                    
                    if (_rateLimits.TryGetValue(rateLimitKey, out var rateLimitInfo))
                    {
                        // Reset window if expired
                        if (now > rateLimitInfo.WindowEnd)
                        {
                            rateLimitInfo = new RateLimitInfo
                            {
                                WindowStart = now,
                                WindowEnd = now.AddSeconds(validKey.RateLimitWindowSeconds ?? 60),
                                RequestCount = 0
                            };
                        }

                        if (rateLimitInfo.RequestCount >= validKey.RateLimit.Value)
                        {
                            return new ApiKeyValidationResult
                            {
                                IsValid = false,
                                ErrorMessage = "Rate limit exceeded"
                            };
                        }

                        rateLimitInfo.RequestCount++;
                        _rateLimits[rateLimitKey] = rateLimitInfo;
                    }
                    else
                    {
                        _rateLimits[rateLimitKey] = new RateLimitInfo
                        {
                            WindowStart = now,
                            WindowEnd = now.AddSeconds(validKey.RateLimitWindowSeconds ?? 60),
                            RequestCount = 1
                        };
                    }
                }

                // Update last used
                validKey.LastUsedAt = DateTime.UtcNow;
                await _context.SaveChangesAsync();

                // Log validation
                await LogApiKeyEventAsync(validKey.Id, validKey.TenantId, "Validated");

                // Build result
                var result = new ApiKeyValidationResult
                {
                    IsValid = true,
                    TenantId = validKey.TenantId,
                    UserId = validKey.UserId
                };

                if (validKey.Metadata != null)
                {
                    if (validKey.Metadata.TryGetValue("service", out var service))
                    {
                        result.ServiceName = service;
                    }
                    
                    if (validKey.Metadata.TryGetValue("allowedEndpoints", out var endpoints))
                    {
                        result.AllowedEndpoints = endpoints.Split(',').ToList();
                    }
                }

                return result;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error validating API key");
                return new ApiKeyValidationResult
                {
                    IsValid = false,
                    ErrorMessage = "Error validating API key"
                };
            }
        }

        public async Task<IEnumerable<ApiKeyAuditLog>> GetApiKeyAuditLogsAsync(string keyId, string tenantId)
        {
            return await _context.ApiKeyAuditLogs
                .Where(log => log.ApiKeyId == keyId && log.TenantId == tenantId)
                .OrderByDescending(log => log.Timestamp)
                .ToListAsync();
        }

        public async Task<bool> SetRateLimitAsync(string keyId, string tenantId, int limit, int windowSeconds)
        {
            try
            {
                var apiKey = await _context.ApiKeys
                    .FirstOrDefaultAsync(k => k.Id == keyId && k.TenantId == tenantId);

                if (apiKey == null)
                {
                    return false;
                }

                apiKey.RateLimit = limit;
                apiKey.RateLimitWindowSeconds = windowSeconds;
                
                if (apiKey.Metadata == null)
                {
                    apiKey.Metadata = new Dictionary<string, string>();
                }
                
                apiKey.Metadata["rateLimit"] = limit.ToString();
                apiKey.Metadata["rateLimitWindow"] = windowSeconds.ToString();

                await _context.SaveChangesAsync();
                return true;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error setting rate limit");
                return false;
            }
        }

        public async Task<string> EncryptApiKeyAsync(string plainValue)
        {
            using var aes = Aes.Create();
            aes.Key = _encryptionKey;
            aes.IV = _encryptionIV;

            using var encryptor = aes.CreateEncryptor();
            var plainBytes = Encoding.UTF8.GetBytes(plainValue);
            var encryptedBytes = encryptor.TransformFinalBlock(plainBytes, 0, plainBytes.Length);
            
            return Convert.ToBase64String(encryptedBytes);
        }

        public async Task<string> DecryptApiKeyAsync(string encryptedValue)
        {
            using var aes = Aes.Create();
            aes.Key = _encryptionKey;
            aes.IV = _encryptionIV;

            using var decryptor = aes.CreateDecryptor();
            var encryptedBytes = Convert.FromBase64String(encryptedValue);
            var decryptedBytes = decryptor.TransformFinalBlock(encryptedBytes, 0, encryptedBytes.Length);
            
            return Encoding.UTF8.GetString(decryptedBytes);
        }

        private string GenerateApiKey(ApiKeyType keyType)
        {
            var prefix = keyType switch
            {
                ApiKeyType.LLMProvider => "byteforge_llm_",
                ApiKeyType.UserAccess => "byteforge_",
                ApiKeyType.ServiceToService => "byteforge_svc_",
                _ => "byteforge_"
            };

            var randomBytes = new byte[32];
            using var rng = RandomNumberGenerator.Create();
            rng.GetBytes(randomBytes);
            
            return prefix + Convert.ToBase64String(randomBytes)
                .Replace("+", "")
                .Replace("/", "")
                .Replace("=", "")
                .Substring(0, 32);
        }

        private string GenerateKeyPrefix(string fullKey)
        {
            if (string.IsNullOrEmpty(fullKey))
                return "";

            var prefixLength = Math.Min(fullKey.Length / 3, 10);
            var suffixLength = Math.Min(3, fullKey.Length - prefixLength);
            
            return $"{fullKey.Substring(0, prefixLength)}...{fullKey.Substring(fullKey.Length - suffixLength)}";
        }

        private async Task LogApiKeyEventAsync(string keyId, string tenantId, string action, 
            Dictionary<string, object> details = null)
        {
            var auditLog = new ApiKeyAuditLog
            {
                ApiKeyId = keyId,
                TenantId = tenantId,
                Action = action,
                Timestamp = DateTime.UtcNow,
                Details = details ?? new Dictionary<string, object>()
            };

            _context.ApiKeyAuditLogs.Add(auditLog);
            await _context.SaveChangesAsync();
        }

        private string GenerateDefaultKey()
        {
            var key = new byte[32];
            using var rng = RandomNumberGenerator.Create();
            rng.GetBytes(key);
            return Convert.ToBase64String(key);
        }

        private string GenerateDefaultIV()
        {
            var iv = new byte[16];
            using var rng = RandomNumberGenerator.Create();
            rng.GetBytes(iv);
            return Convert.ToBase64String(iv);
        }

        private class RateLimitInfo
        {
            public DateTime WindowStart { get; set; }
            public DateTime WindowEnd { get; set; }
            public int RequestCount { get; set; }
        }
    }
}