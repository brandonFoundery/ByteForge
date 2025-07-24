using System.Net.Http;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.LLM.Providers;

public class AnthropicProvider : BaseLLMProvider
{
    private readonly AnthropicSettings _settings;

    public AnthropicProvider(HttpClient httpClient, AnthropicSettings settings, ILogger<AnthropicProvider> logger)
        : base(httpClient, logger)
    {
        _settings = settings ?? throw new ArgumentNullException(nameof(settings));
        
        if (!string.IsNullOrEmpty(_settings.ApiKey))
        {
            _httpClient.DefaultRequestHeaders.Add("x-api-key", _settings.ApiKey);
            _httpClient.DefaultRequestHeaders.Add("anthropic-version", "2023-06-01");
        }
    }

    public override string Name => "Anthropic";
    public override bool IsAvailable => _settings.IsConfigured;

    protected override async Task<HttpRequestMessage> BuildHttpRequestAsync(LLMGenerationRequest request)
    {
        var messages = new List<object>();
        messages.Add(new { role = "user", content = request.Prompt });

        var payload = new
        {
            model = _settings.Model,
            messages = messages,
            system = request.SystemPrompt,
            temperature = request.Temperature ?? _settings.Temperature,
            max_tokens = request.MaxTokens ?? _settings.MaxTokens
        };

        var json = BuildJsonContent(payload);
        
        return new HttpRequestMessage(HttpMethod.Post, $"{_settings.BaseUrl}/messages")
        {
            Content = CreateJsonContent(json)
        };
    }

    protected override async Task<LLMGenerationResponse> ParseResponseAsync(string responseContent)
    {
        using var document = JsonDocument.Parse(responseContent);
        var root = document.RootElement;

        if (root.TryGetProperty("content", out var content) && content.GetArrayLength() > 0)
        {
            var firstContent = content[0];
            var text = firstContent.GetProperty("text").GetString() ?? string.Empty;
            
            var usage = root.GetProperty("usage");
            var totalTokens = usage.GetProperty("input_tokens").GetInt32() + 
                             usage.GetProperty("output_tokens").GetInt32();

            return new LLMGenerationResponse
            {
                Success = true,
                Content = text,
                Model = _settings.Model,
                TokensUsed = totalTokens,
                Metadata = new Dictionary<string, object>
                {
                    ["input_tokens"] = usage.GetProperty("input_tokens").GetInt32(),
                    ["output_tokens"] = usage.GetProperty("output_tokens").GetInt32()
                }
            };
        }

        return new LLMGenerationResponse
        {
            Success = false,
            Error = "Invalid response format from Anthropic API",
            Model = _settings.Model
        };
    }

    protected override string ExtractErrorMessage(string errorResponse)
    {
        try
        {
            using var document = JsonDocument.Parse(errorResponse);
            if (document.RootElement.TryGetProperty("error", out var error))
            {
                if (error.TryGetProperty("message", out var message))
                {
                    return message.GetString() ?? "Unknown error";
                }
            }
        }
        catch
        {
            // If we can't parse the error, return the raw response
        }
        
        return errorResponse;
    }
}