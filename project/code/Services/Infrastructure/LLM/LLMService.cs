using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services;
using Polly;
using Polly.Retry;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.LLM;

public class LLMService : ILLMService
{
    private readonly ILLMProviderFactory _providerFactory;
    private readonly ILLMConfigurationService _configService;
    private readonly ILogger<LLMService> _logger;
    private readonly AsyncRetryPolicy _retryPolicy;

    public LLMService(
        ILLMProviderFactory providerFactory,
        ILLMConfigurationService configService,
        ILogger<LLMService> logger)
    {
        _providerFactory = providerFactory ?? throw new ArgumentNullException(nameof(providerFactory));
        _configService = configService ?? throw new ArgumentNullException(nameof(configService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));

        // Configure retry policy with exponential backoff
        _retryPolicy = Policy
            .Handle<HttpRequestException>()
            .Or<TaskCanceledException>()
            .Or<TimeoutException>()
            .WaitAndRetryAsync(
                _configService.Configuration.MaxRetries,
                retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                (exception, timeSpan, retryCount, context) =>
                {
                    _logger.LogWarning(
                        "Retry {RetryCount} after {TimeSpan}s due to: {ExceptionMessage}",
                        retryCount,
                        timeSpan.TotalSeconds,
                        exception.Message);
                });
    }

    public async Task<LLMGenerationResponse> GenerateAsync(
        LLMGenerationRequest request,
        CancellationToken cancellationToken = default)
    {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        cts.CancelAfter(TimeSpan.FromSeconds(_configService.Configuration.TimeoutSeconds));

        // If a specific provider is requested, use only that one
        if (!string.IsNullOrEmpty(request.PreferredProvider))
        {
            try
            {
                var provider = _providerFactory.GetProvider(request.PreferredProvider);
                return await ExecuteWithRetryAsync(provider, request, cts.Token);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to use preferred provider {Provider}", request.PreferredProvider);
                return new LLMGenerationResponse
                {
                    Success = false,
                    Error = $"Preferred provider {request.PreferredProvider} failed: {ex.Message}",
                    Provider = request.PreferredProvider
                };
            }
        }

        // Try providers with failover
        var availableProviders = _providerFactory.GetAvailableProviders().ToList();
        if (!availableProviders.Any())
        {
            return new LLMGenerationResponse
            {
                Success = false,
                Error = "No LLM providers are configured"
            };
        }

        // Start with the default provider if configured
        var orderedProviders = new List<string>();
        if (availableProviders.Contains(_configService.DefaultProvider))
        {
            orderedProviders.Add(_configService.DefaultProvider);
            availableProviders.Remove(_configService.DefaultProvider);
        }
        orderedProviders.AddRange(availableProviders);

        var errors = new List<string>();

        foreach (var providerName in orderedProviders)
        {
            try
            {
                _logger.LogInformation("Attempting generation with {Provider}", providerName);
                var provider = _providerFactory.GetProvider(providerName);
                var response = await ExecuteWithRetryAsync(provider, request, cts.Token);
                
                if (response.Success)
                {
                    return response;
                }
                
                errors.Add($"{providerName}: {response.Error}");
                _logger.LogWarning("Provider {Provider} returned unsuccessful response: {Error}", providerName, response.Error);
            }
            catch (Exception ex)
            {
                errors.Add($"{providerName}: {ex.Message}");
                _logger.LogError(ex, "Provider {Provider} failed with exception", providerName);
            }
        }

        // All providers failed
        return new LLMGenerationResponse
        {
            Success = false,
            Error = $"All LLM providers failed. Errors: {string.Join("; ", errors)}"
        };
    }

    public async Task<IEnumerable<LLMGenerationResponse>> GenerateBatchAsync(
        IEnumerable<LLMGenerationRequest> requests,
        CancellationToken cancellationToken = default)
    {
        var tasks = requests.Select(request => GenerateAsync(request, cancellationToken));
        return await Task.WhenAll(tasks);
    }

    public IEnumerable<string> GetAvailableProviders()
    {
        return _providerFactory.GetAvailableProviders();
    }

    private async Task<LLMGenerationResponse> ExecuteWithRetryAsync(
        ILLMProvider provider,
        LLMGenerationRequest request,
        CancellationToken cancellationToken)
    {
        return await _retryPolicy.ExecuteAsync(async (ct) =>
        {
            return await provider.GenerateAsync(request, ct);
        }, cancellationToken);
    }
}