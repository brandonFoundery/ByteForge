using System.Net.Http;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.LLM.Providers;

public class OpenAIProvider : BaseLLMProvider
{
    private readonly OpenAISettings _settings;

    public OpenAIProvider(HttpClient httpClient, OpenAISettings settings, ILogger<OpenAIProvider> logger)
        : base(httpClient, logger)
    {
        _settings = settings ?? throw new ArgumentNullException(nameof(settings));
        
        if (!string.IsNullOrEmpty(_settings.ApiKey))
        {
            _httpClient.DefaultRequestHeaders.Authorization = 
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _settings.ApiKey);
        }
    }

    public override string Name => "OpenAI";
    public override bool IsAvailable => _settings.IsConfigured;

    protected override async Task<HttpRequestMessage> BuildHttpRequestAsync(LLMGenerationRequest request)
    {
        var messages = new List<object>();
        
        if (!string.IsNullOrEmpty(request.SystemPrompt))
        {
            messages.Add(new { role = "system", content = request.SystemPrompt });
        }
        
        messages.Add(new { role = "user", content = request.Prompt });

        var payload = new
        {
            model = _settings.Model,
            messages = messages,
            temperature = request.Temperature ?? _settings.Temperature,
            max_tokens = request.MaxTokens ?? _settings.MaxTokens
        };

        var json = BuildJsonContent(payload);
        
        return new HttpRequestMessage(HttpMethod.Post, $"{_settings.BaseUrl}/chat/completions")
        {
            Content = CreateJsonContent(json)
        };
    }

    protected override async Task<LLMGenerationResponse> ParseResponseAsync(string responseContent)
    {
        using var document = JsonDocument.Parse(responseContent);
        var root = document.RootElement;

        if (root.TryGetProperty("choices", out var choices) && choices.GetArrayLength() > 0)
        {
            var firstChoice = choices[0];
            var message = firstChoice.GetProperty("message");
            var content = message.GetProperty("content").GetString() ?? string.Empty;
            
            var usage = root.GetProperty("usage");
            var totalTokens = usage.GetProperty("total_tokens").GetInt32();

            return new LLMGenerationResponse
            {
                Success = true,
                Content = content,
                Model = _settings.Model,
                TokensUsed = totalTokens,
                Metadata = new Dictionary<string, object>
                {
                    ["prompt_tokens"] = usage.GetProperty("prompt_tokens").GetInt32(),
                    ["completion_tokens"] = usage.GetProperty("completion_tokens").GetInt32()
                }
            };
        }

        return new LLMGenerationResponse
        {
            Success = false,
            Error = "Invalid response format from OpenAI API",
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