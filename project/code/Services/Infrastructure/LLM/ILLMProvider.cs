using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Infrastructure.LLM;

public interface ILLMProvider
{
    Task<LLMGenerationResponse> GenerateAsync(LLMGenerationRequest request, CancellationToken cancellationToken = default);
    Task<bool> ValidateConnectionAsync();
    string Name { get; }
    bool IsAvailable { get; }
}

public class LLMGenerationRequest
{
    public string Prompt { get; set; } = string.Empty;
    public string? SystemPrompt { get; set; }
    public double? Temperature { get; set; }
    public int? MaxTokens { get; set; }
    public string? PreferredProvider { get; set; }
    public Dictionary<string, object>? AdditionalParameters { get; set; }
}

public class LLMGenerationResponse
{
    public bool Success { get; set; }
    public string Content { get; set; } = string.Empty;
    public string? Error { get; set; }
    public string Provider { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public int TokensUsed { get; set; }
    public TimeSpan ResponseTime { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
}