using System;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using StackExchange.Redis;

namespace ByteForgeFrontend.Services.Infrastructure.Caching
{
    /// <summary>
    /// Redis caching service for performance optimization
    /// </summary>
    public interface IRedisCachingService
    {
        Task<T> GetAsync<T>(string key);
        Task<string> GetStringAsync(string key);
        Task SetAsync<T>(string key, T value, TimeSpan? expiry = null);
        Task SetStringAsync(string key, string value, TimeSpan? expiry = null);
        Task<bool> ExistsAsync(string key);
        Task<bool> DeleteAsync(string key);
        Task<long> IncrementAsync(string key, long value = 1);
        Task<bool> SetAddAsync(string key, string value);
        Task<bool> SetRemoveAsync(string key, string value);
        Task<string[]> SetMembersAsync(string key);
        Task InvalidatePatternAsync(string pattern);
    }

    public class RedisCachingService : IRedisCachingService
    {
        private readonly IConnectionMultiplexer _redis;
        private readonly IDatabase _database;
        private readonly ILogger<RedisCachingService> _logger;
        private readonly JsonSerializerOptions _jsonOptions;
        private readonly int _defaultExpiryMinutes;

        public RedisCachingService(
            IConfiguration configuration,
            ILogger<RedisCachingService> logger)
        {
            _logger = logger;
            
            var redisConnection = configuration.GetConnectionString("Redis") ?? "localhost:6379";
            _redis = ConnectionMultiplexer.Connect(redisConnection);
            _database = _redis.GetDatabase();
            
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,
                WriteIndented = false
            };
            
            _defaultExpiryMinutes = configuration.GetValue<int>("Redis:DefaultExpiryMinutes", 60);
        }

        public async Task<T> GetAsync<T>(string key)
        {
            try
            {
                var value = await _database.StringGetAsync(key);
                
                if (value.IsNullOrEmpty)
                {
                    return default(T);
                }

                return JsonSerializer.Deserialize<T>(value, _jsonOptions);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting cached value for key: {Key}", key);
                return default(T);
            }
        }

        public async Task<string> GetStringAsync(string key)
        {
            try
            {
                var value = await _database.StringGetAsync(key);
                return value.IsNullOrEmpty ? null : value.ToString();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting cached string for key: {Key}", key);
                return null;
            }
        }

        public async Task SetAsync<T>(string key, T value, TimeSpan? expiry = null)
        {
            try
            {
                var serialized = JsonSerializer.Serialize(value, _jsonOptions);
                var actualExpiry = expiry ?? TimeSpan.FromMinutes(_defaultExpiryMinutes);
                
                await _database.StringSetAsync(key, serialized, actualExpiry);
                _logger.LogDebug("Cached value for key: {Key} with expiry: {Expiry}", key, actualExpiry);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error setting cached value for key: {Key}", key);
            }
        }

        public async Task SetStringAsync(string key, string value, TimeSpan? expiry = null)
        {
            try
            {
                var actualExpiry = expiry ?? TimeSpan.FromMinutes(_defaultExpiryMinutes);
                await _database.StringSetAsync(key, value, actualExpiry);
                _logger.LogDebug("Cached string for key: {Key} with expiry: {Expiry}", key, actualExpiry);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error setting cached string for key: {Key}", key);
            }
        }

        public async Task<bool> ExistsAsync(string key)
        {
            try
            {
                return await _database.KeyExistsAsync(key);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking existence for key: {Key}", key);
                return false;
            }
        }

        public async Task<bool> DeleteAsync(string key)
        {
            try
            {
                return await _database.KeyDeleteAsync(key);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting key: {Key}", key);
                return false;
            }
        }

        public async Task<long> IncrementAsync(string key, long value = 1)
        {
            try
            {
                return await _database.StringIncrementAsync(key, value);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error incrementing key: {Key}", key);
                return 0;
            }
        }

        public async Task<bool> SetAddAsync(string key, string value)
        {
            try
            {
                return await _database.SetAddAsync(key, value);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error adding to set: {Key}", key);
                return false;
            }
        }

        public async Task<bool> SetRemoveAsync(string key, string value)
        {
            try
            {
                return await _database.SetRemoveAsync(key, value);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error removing from set: {Key}", key);
                return false;
            }
        }

        public async Task<string[]> SetMembersAsync(string key)
        {
            try
            {
                var members = await _database.SetMembersAsync(key);
                return Array.ConvertAll(members, m => m.ToString());
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting set members: {Key}", key);
                return Array.Empty<string>();
            }
        }

        public async Task InvalidatePatternAsync(string pattern)
        {
            try
            {
                var endpoints = _redis.GetEndPoints();
                var server = _redis.GetServer(endpoints[0]);
                
                var keys = server.Keys(pattern: pattern);
                foreach (var key in keys)
                {
                    await _database.KeyDeleteAsync(key);
                }
                
                _logger.LogDebug("Invalidated cache keys matching pattern: {Pattern}", pattern);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error invalidating cache pattern: {Pattern}", pattern);
            }
        }
    }

    /// <summary>
    /// Cache key builder to ensure consistent key naming
    /// </summary>
    public static class CacheKeys
    {
        private const string Prefix = "byteforge";

        // Project-related cache keys
        public static string Project(Guid projectId) => $"{Prefix}:project:{projectId}";
        public static string ProjectsByTenant(string tenantId) => $"{Prefix}:projects:tenant:{tenantId}";
        public static string ProjectDocuments(Guid projectId) => $"{Prefix}:project:{projectId}:documents";
        public static string ProjectDocument(Guid projectId, Guid documentId) => $"{Prefix}:project:{projectId}:document:{documentId}";

        // User-related cache keys
        public static string User(string userId) => $"{Prefix}:user:{userId}";
        public static string UserPermissions(string userId) => $"{Prefix}:user:{userId}:permissions";
        public static string UserApiKey(string hashedKey) => $"{Prefix}:apikey:{hashedKey}";

        // Template-related cache keys
        public static string Template(Guid templateId) => $"{Prefix}:template:{templateId}";
        public static string TemplatesByCategory(string category) => $"{Prefix}:templates:category:{category}";
        public static string PublicTemplates() => $"{Prefix}:templates:public";

        // Monitoring-related cache keys
        public static string MonitoringStatus(Guid projectId) => $"{Prefix}:monitoring:project:{projectId}";
        public static string AgentStatus(string agentId) => $"{Prefix}:monitoring:agent:{agentId}";
        public static string SystemMetrics() => $"{Prefix}:monitoring:system";

        // LLM-related cache keys
        public static string LLMResponse(string promptHash) => $"{Prefix}:llm:response:{promptHash}";
        public static string LLMProviderStatus(string provider) => $"{Prefix}:llm:provider:{provider}:status";

        // Rate limiting keys
        public static string RateLimit(string identifier, string action) => $"{Prefix}:ratelimit:{action}:{identifier}";

        // Pattern generators for invalidation
        public static string ProjectPattern(Guid projectId) => $"{Prefix}:project:{projectId}:*";
        public static string TenantPattern(string tenantId) => $"{Prefix}:*:tenant:{tenantId}*";
        public static string UserPattern(string userId) => $"{Prefix}:user:{userId}:*";
    }

    /// <summary>
    /// Caching decorator for services that need caching
    /// </summary>
    public abstract class CachedServiceBase
    {
        protected readonly IRedisCachingService _cache;
        protected readonly ILogger _logger;

        protected CachedServiceBase(IRedisCachingService cache, ILogger logger)
        {
            _cache = cache;
            _logger = logger;
        }

        protected async Task<T> GetOrSetAsync<T>(
            string key, 
            Func<Task<T>> factory, 
            TimeSpan? expiry = null)
        {
            // Try to get from cache
            var cached = await _cache.GetAsync<T>(key);
            if (cached != null)
            {
                _logger.LogDebug("Cache hit for key: {Key}", key);
                return cached;
            }

            // Cache miss - get from source
            _logger.LogDebug("Cache miss for key: {Key}", key);
            var value = await factory();
            
            if (value != null)
            {
                await _cache.SetAsync(key, value, expiry);
            }

            return value;
        }

        protected async Task InvalidateRelatedCacheAsync(params string[] patterns)
        {
            foreach (var pattern in patterns)
            {
                await _cache.InvalidatePatternAsync(pattern);
            }
        }
    }
}