using Microsoft.Extensions.Configuration;

namespace ByteForgeFrontend.Services;

public class LLMServicesConfiguration
{
    public bool UseMockResponses { get; set; } = false;
    public string DefaultProvider { get; set; } = "openai";
    public int MaxRetries { get; set; } = 3;
    public int TimeoutSeconds { get; set; } = 120;
    
    public OpenAISettings OpenAI { get; set; } = new();
    public AnthropicSettings Anthropic { get; set; } = new();
    public GoogleGeminiSettings GoogleGemini { get; set; } = new();
    public GrokSettings Grok { get; set; } = new();
}

public class OpenAISettings
{
    public string ApiKey { get; set; } = string.Empty;
    public string Model { get; set; } = "gpt-4o";
    public string BaseUrl { get; set; } = "https://api.openai.com/v1";
    public double Temperature { get; set; } = 0.7;
    public int MaxTokens { get; set; } = 4096;
    
    public bool IsConfigured => !string.IsNullOrWhiteSpace(ApiKey);
}

public class AnthropicSettings
{
    public string ApiKey { get; set; } = string.Empty;
    public string Model { get; set; } = "claude-3-5-sonnet-20241022";
    public string BaseUrl { get; set; } = "https://api.anthropic.com/v1";
    public double Temperature { get; set; } = 0.7;
    public int MaxTokens { get; set; } = 4096;
    
    public bool IsConfigured => !string.IsNullOrWhiteSpace(ApiKey);
}

public class GoogleGeminiSettings
{
    public string ApiKey { get; set; } = string.Empty;
    public string Model { get; set; } = "gemini-pro";
    public string BaseUrl { get; set; } = "https://generativelanguage.googleapis.com/v1beta";
    public double Temperature { get; set; } = 0.7;
    public int MaxTokens { get; set; } = 4096;
    
    public bool IsConfigured => !string.IsNullOrWhiteSpace(ApiKey);
}

public class GrokSettings
{
    public string ApiKey { get; set; } = string.Empty;
    public string Model { get; set; } = "grok-beta";
    public string BaseUrl { get; set; } = "https://api.x.ai/v1";
    public double Temperature { get; set; } = 0.7;
    public int MaxTokens { get; set; } = 4096;
    
    public bool IsConfigured => !string.IsNullOrWhiteSpace(ApiKey);
}

public interface ILLMConfigurationService
{
    LLMServicesConfiguration Configuration { get; }
    bool UseMockResponses { get; }
    string DefaultProvider { get; }
    bool IsProviderConfigured(string providerName);
    T GetProviderSettings<T>() where T : class, new();
    LLMServicesConfiguration GetConfiguration();
}

public class LLMConfigurationService : ILLMConfigurationService
{
    private readonly LLMServicesConfiguration _configuration;

    public LLMConfigurationService(IConfiguration configuration)
    {
        _configuration = new LLMServicesConfiguration();
        configuration.GetSection("LLMServices").Bind(_configuration);
    }

    public LLMServicesConfiguration Configuration => _configuration;

    public bool UseMockResponses => _configuration.UseMockResponses;
    
    public string DefaultProvider => _configuration.DefaultProvider;

    public bool IsProviderConfigured(string providerName)
    {
        return providerName.ToLower() switch
        {
            "openai" => _configuration.OpenAI.IsConfigured,
            "anthropic" => _configuration.Anthropic.IsConfigured,
            "googlegemini" or "gemini" => _configuration.GoogleGemini.IsConfigured,
            "grok" => _configuration.Grok.IsConfigured,
            _ => false
        };
    }

    public T GetProviderSettings<T>() where T : class, new()
    {
        return typeof(T).Name switch
        {
            nameof(OpenAISettings) => (_configuration.OpenAI as T) ?? new T(),
            nameof(AnthropicSettings) => (_configuration.Anthropic as T) ?? new T(),
            nameof(GoogleGeminiSettings) => (_configuration.GoogleGemini as T) ?? new T(),
            nameof(GrokSettings) => (_configuration.Grok as T) ?? new T(),
            _ => new T()
        };
    }

    public LLMServicesConfiguration GetConfiguration()
    {
        return _configuration;
    }
}