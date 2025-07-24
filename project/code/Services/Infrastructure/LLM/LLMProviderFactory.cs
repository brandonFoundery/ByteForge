using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services;
using ByteForgeFrontend.Services.Infrastructure.LLM.Providers;

using System;
using System.Collections.Generic;
using System.Net.Http;
namespace ByteForgeFrontend.Services.Infrastructure.LLM;

public class LLMProviderFactory : ILLMProviderFactory
{
    private readonly ILLMConfigurationService _configService;
    private readonly ILoggerFactory _loggerFactory;
    private readonly ILogger<LLMProviderFactory> _logger;
    private readonly IHttpClientFactory _httpClientFactory;

    public LLMProviderFactory(
        ILLMConfigurationService configService,
        ILoggerFactory loggerFactory,
        IHttpClientFactory httpClientFactory)
    {
        _configService = configService ?? throw new ArgumentNullException(nameof(configService));
        _loggerFactory = loggerFactory ?? throw new ArgumentNullException(nameof(loggerFactory));
        _logger = _loggerFactory.CreateLogger<LLMProviderFactory>();
        _httpClientFactory = httpClientFactory ?? throw new ArgumentNullException(nameof(httpClientFactory));
    }

    public ILLMProvider GetProvider(string providerName)
    {
        if (string.IsNullOrWhiteSpace(providerName))
            throw new ArgumentNullException(nameof(providerName));

        // Check if mock mode is enabled
        if (_configService.UseMockResponses)
        {
            _logger.LogInformation("Mock mode enabled, returning MockLLMProvider");
            return new MockLLMProvider(_loggerFactory.CreateLogger<MockLLMProvider>());
        }

        var httpClient = _httpClientFactory.CreateClient($"LLM_{providerName}");

        return providerName.ToLower() switch
        {
            "openai" => new OpenAIProvider(
                httpClient,
                _configService.GetProviderSettings<OpenAISettings>(),
                _loggerFactory.CreateLogger<OpenAIProvider>()),
            
            "anthropic" => new AnthropicProvider(
                httpClient,
                _configService.GetProviderSettings<AnthropicSettings>(),
                _loggerFactory.CreateLogger<AnthropicProvider>()),
            
            "googlegemini" or "gemini" => new GoogleGeminiProvider(
                httpClient,
                _configService.GetProviderSettings<GoogleGeminiSettings>(),
                _loggerFactory.CreateLogger<GoogleGeminiProvider>()),
            
            "grok" => new GrokProvider(
                httpClient,
                _configService.GetProviderSettings<GrokSettings>(),
                _loggerFactory.CreateLogger<GrokProvider>()),
            
            _ => throw new ArgumentException($"Unknown LLM provider: {providerName}")
        };
    }

    public IEnumerable<string> GetAvailableProviders()
    {
        // In mock mode, always return mock provider
        if (_configService.UseMockResponses)
        {
            return new[] { "mock" };
        }

        var providers = new List<string>();

        if (_configService.IsProviderConfigured("openai"))
            providers.Add("openai");

        if (_configService.IsProviderConfigured("anthropic"))
            providers.Add("anthropic");

        if (_configService.IsProviderConfigured("googlegemini"))
            providers.Add("googlegemini");

        if (_configService.IsProviderConfigured("grok"))
            providers.Add("grok");

        return providers;
    }
}