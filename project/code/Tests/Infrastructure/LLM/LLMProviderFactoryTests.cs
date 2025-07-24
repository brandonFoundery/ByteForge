using Xunit;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.LLM.Providers;
using ByteForgeFrontend.Services;
using System.Net.Http;
using System;
namespace ByteForgeFrontend.Tests.Infrastructure.LLM;

public class LLMProviderFactoryTests
{
    private readonly Mock<ILLMConfigurationService> _mockConfigService;
    private readonly Mock<ILoggerFactory> _mockLoggerFactory;
    private readonly Mock<IHttpClientFactory> _mockHttpClientFactory;
    private readonly LLMProviderFactory _factory;

    public LLMProviderFactoryTests()
    {
        _mockConfigService = new Mock<ILLMConfigurationService>();
        _mockLoggerFactory = new Mock<ILoggerFactory>();
        _mockHttpClientFactory = new Mock<IHttpClientFactory>();
        _factory = new LLMProviderFactory(_mockConfigService.Object, _mockLoggerFactory.Object, _mockHttpClientFactory.Object);
    }

    [Fact]
    public void GetProvider_WithOpenAI_ReturnsOpenAIProvider()
    {
        // Arrange
        var openAISettings = new OpenAISettings
        {
            ApiKey = "test-api-key",
            Model = "gpt-4o",
            BaseUrl = "https://api.openai.com/v1"
        };
        _mockConfigService.Setup(x => x.GetProviderSettings<OpenAISettings>())
            .Returns(openAISettings);

        // Act
        var provider = _factory.GetProvider("openai");

        // Assert
        provider.Should().NotBeNull();
        provider.Should().BeOfType<OpenAIProvider>();
    }

    [Fact]
    public void GetProvider_WithAnthropic_ReturnsAnthropicProvider()
    {
        // Arrange
        var anthropicSettings = new AnthropicSettings
        {
            ApiKey = "test-api-key",
            Model = "claude-3-5-sonnet",
            BaseUrl = "https://api.anthropic.com/v1"
        };
        _mockConfigService.Setup(x => x.GetProviderSettings<AnthropicSettings>())
            .Returns(anthropicSettings);

        // Act
        var provider = _factory.GetProvider("anthropic");

        // Assert
        provider.Should().NotBeNull();
        provider.Should().BeOfType<AnthropicProvider>();
    }

    [Fact]
    public void GetProvider_WithGoogleGemini_ReturnsGeminiProvider()
    {
        // Arrange
        var geminiSettings = new GoogleGeminiSettings
        {
            ApiKey = "test-api-key",
            Model = "gemini-pro",
            BaseUrl = "https://generativelanguage.googleapis.com/v1beta"
        };
        _mockConfigService.Setup(x => x.GetProviderSettings<GoogleGeminiSettings>())
            .Returns(geminiSettings);

        // Act
        var provider = _factory.GetProvider("googlegemini");

        // Assert
        provider.Should().NotBeNull();
        provider.Should().BeOfType<GoogleGeminiProvider>();
    }

    [Fact]
    public void GetProvider_WithGrok_ReturnsGrokProvider()
    {
        // Arrange
        var grokSettings = new GrokSettings
        {
            ApiKey = "test-api-key",
            Model = "grok-beta",
            BaseUrl = "https://api.x.ai/v1"
        };
        _mockConfigService.Setup(x => x.GetProviderSettings<GrokSettings>())
            .Returns(grokSettings);

        // Act
        var provider = _factory.GetProvider("grok");

        // Assert
        provider.Should().NotBeNull();
        provider.Should().BeOfType<GrokProvider>();
    }

    [Fact]
    public void GetProvider_WithInvalidProvider_ThrowsArgumentException()
    {
        // Act & Assert
        var action = () => _factory.GetProvider("invalid");
        action.Should().Throw<ArgumentException>()
            .WithMessage("*Unknown LLM provider*");
    }

    [Fact]
    public void GetProvider_WithNullProvider_ThrowsArgumentNullException()
    {
        // Act & Assert
        var action = () => _factory.GetProvider(null);
        action.Should().Throw<ArgumentNullException>();
    }

    [Fact]
    public void GetAvailableProviders_ReturnsConfiguredProviders()
    {
        // Arrange
        _mockConfigService.Setup(x => x.IsProviderConfigured("openai")).Returns(true);
        _mockConfigService.Setup(x => x.IsProviderConfigured("anthropic")).Returns(false);
        _mockConfigService.Setup(x => x.IsProviderConfigured("googlegemini")).Returns(true);
        _mockConfigService.Setup(x => x.IsProviderConfigured("grok")).Returns(false);

        // Act
        var providers = _factory.GetAvailableProviders();

        // Assert
        providers.Should().HaveCount(2);
        providers.Should().Contain("openai");
        providers.Should().Contain("googlegemini");
        providers.Should().NotContain("anthropic");
        providers.Should().NotContain("grok");
    }
}