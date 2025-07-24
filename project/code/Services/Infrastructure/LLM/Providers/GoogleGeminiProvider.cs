using System.Net.Http;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.LLM.Providers;

public class GoogleGeminiProvider : BaseLLMProvider
{
    private readonly GoogleGeminiSettings _settings;

    public GoogleGeminiProvider(HttpClient httpClient, GoogleGeminiSettings settings, ILogger<GoogleGeminiProvider> logger)
        : base(httpClient, logger)
    {
        _settings = settings ?? throw new ArgumentNullException(nameof(settings));
    }

    public override string Name => "Google Gemini";
    public override bool IsAvailable => _settings.IsConfigured;

    protected override async Task<HttpRequestMessage> BuildHttpRequestAsync(LLMGenerationRequest request)
    {
        var parts = new List<object>();
        
        if (!string.IsNullOrEmpty(request.SystemPrompt))
        {
            parts.Add(new { text = request.SystemPrompt });
        }
        
        parts.Add(new { text = request.Prompt });

        var payload = new
        {
            contents = new[]
            {
                new
                {
                    parts = parts
                }
            },
            generationConfig = new
            {
                temperature = request.Temperature ?? _settings.Temperature,
                maxOutputTokens = request.MaxTokens ?? _settings.MaxTokens
            }
        };

        var json = BuildJsonContent(payload);
        var url = $"{_settings.BaseUrl}/models/{_settings.Model}:generateContent?key={_settings.ApiKey}";
        
        return new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = CreateJsonContent(json)
        };
    }

    protected override async Task<LLMGenerationResponse> ParseResponseAsync(string responseContent)
    {
        using var document = JsonDocument.Parse(responseContent);
        var root = document.RootElement;

        if (root.TryGetProperty("candidates", out var candidates) && candidates.GetArrayLength() > 0)
        {
            var firstCandidate = candidates[0];
            var content = firstCandidate.GetProperty("content");
            var parts = content.GetProperty("parts");
            
            if (parts.GetArrayLength() > 0)
            {
                var text = parts[0].GetProperty("text").GetString() ?? string.Empty;
                
                // Gemini doesn't provide direct token counts in the same way
                var estimatedTokens = EstimateTokenCount(text);

                return new LLMGenerationResponse
                {
                    Success = true,
                    Content = text,
                    Model = _settings.Model,
                    TokensUsed = estimatedTokens,
                    Metadata = new Dictionary<string, object>
                    {
                        ["safety_ratings"] = ExtractSafetyRatings(firstCandidate)
                    }
                };
            }
        }

        return new LLMGenerationResponse
        {
            Success = false,
            Error = "Invalid response format from Google Gemini API",
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

    private int EstimateTokenCount(string text)
    {
        // Rough estimation: 1 token ≈ 4 characters
        return text.Length / 4;
    }

    private object ExtractSafetyRatings(JsonElement candidate)
    {
        if (candidate.TryGetProperty("safetyRatings", out var ratings))
        {
            var safetyRatings = new List<object>();
            foreach (var rating in ratings.EnumerateArray())
            {
                safetyRatings.Add(new
                {
                    category = rating.GetProperty("category").GetString(),
                    probability = rating.GetProperty("probability").GetString()
                });
            }
            return safetyRatings;
        }
        return new List<object>();
    }
}