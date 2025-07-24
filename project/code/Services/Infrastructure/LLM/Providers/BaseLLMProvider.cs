using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using Microsoft.Extensions.Logging;

using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.LLM.Providers;

public abstract class BaseLLMProvider : ILLMProvider
{
    protected readonly HttpClient _httpClient;
    protected readonly ILogger _logger;

    protected BaseLLMProvider(HttpClient httpClient, ILogger logger)
    {
        _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public abstract string Name { get; }
    public abstract bool IsAvailable { get; }

    public async Task<LLMGenerationResponse> GenerateAsync(LLMGenerationRequest request, CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            _logger.LogInformation("Starting {Provider} generation request", Name);
            
            var httpRequest = await BuildHttpRequestAsync(request);
            var response = await _httpClient.SendAsync(httpRequest, cancellationToken);
            
            var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);
            
            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("{Provider} API error: {StatusCode} - {Content}", Name, response.StatusCode, responseContent);
                return new LLMGenerationResponse
                {
                    Success = false,
                    Error = $"API error: {response.StatusCode} - {ExtractErrorMessage(responseContent)}",
                    Provider = Name,
                    ResponseTime = stopwatch.Elapsed
                };
            }

            var result = await ParseResponseAsync(responseContent);
            result.Provider = Name;
            result.ResponseTime = stopwatch.Elapsed;
            
            _logger.LogInformation("{Provider} generation completed in {Time}ms", Name, stopwatch.ElapsedMilliseconds);
            
            return result;
        }
        catch (TaskCanceledException)
        {
            _logger.LogWarning("{Provider} request was cancelled", Name);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "{Provider} generation failed", Name);
            return new LLMGenerationResponse
            {
                Success = false,
                Error = $"Provider error: {ex.Message}",
                Provider = Name,
                ResponseTime = stopwatch.Elapsed
            };
        }
    }

    public virtual async Task<bool> ValidateConnectionAsync()
    {
        try
        {
            var testRequest = new LLMGenerationRequest 
            { 
                Prompt = "Test connection",
                MaxTokens = 10
            };
            
            var response = await GenerateAsync(testRequest);
            return response.Success;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Connection validation failed for {Provider}", Name);
            return false;
        }
    }
    
    protected abstract Task<HttpRequestMessage> BuildHttpRequestAsync(LLMGenerationRequest request);
    protected abstract Task<LLMGenerationResponse> ParseResponseAsync(string responseContent);
    protected abstract string ExtractErrorMessage(string errorResponse);

    protected string BuildJsonContent(object payload)
    {
        return JsonSerializer.Serialize(payload, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false
        });
    }

    protected StringContent CreateJsonContent(string json)
    {
        return new StringContent(json, Encoding.UTF8, "application/json");
    }
}