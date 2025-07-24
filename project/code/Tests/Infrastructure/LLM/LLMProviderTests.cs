using Xunit;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using System.Net;
using Moq.Protected;

using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.LLM;

public class LLMProviderTests
{
    [Fact]
    public async Task GenerateAsync_WithValidRequest_ReturnsResponse()
    {
        // Arrange
        var mockHttpHandler = new Mock<HttpMessageHandler>();
        mockHttpHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = new StringContent(@"{""choices"":[{""message"":{""content"":""Test response""}}]}")
            });

        var httpClient = new HttpClient(mockHttpHandler.Object);
        var mockLogger = new Mock<ILogger<OpenAIProvider>>();
        
        var settings = new OpenAISettings
        {
            ApiKey = "test-key",
            Model = "gpt-4o",
            BaseUrl = "https://api.openai.com/v1",
            Temperature = 0.7,
            MaxTokens = 4096
        };

        var provider = new OpenAIProvider(httpClient, settings, mockLogger.Object);

        var request = new LLMGenerationRequest
        {
            Prompt = "Test prompt",
            SystemPrompt = "You are a helpful assistant",
            Temperature = 0.7,
            MaxTokens = 1000
        };

        // Act
        var response = await provider.GenerateAsync(request);

        // Assert
        response.Should().NotBeNull();
        response.Success.Should().BeTrue();
        response.Content.Should().Be("Test response");
        response.Provider.Should().Be("OpenAI");
        response.Model.Should().Be("gpt-4o");
        response.TokensUsed.Should().BeGreaterThan(0);
    }

    [Fact]
    public async Task GenerateAsync_WithApiError_ReturnsErrorResponse()
    {
        // Arrange
        var mockHttpHandler = new Mock<HttpMessageHandler>();
        mockHttpHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.BadRequest,
                Content = new StringContent(@"{""error"":{""message"":""Invalid request""}}")
            });

        var httpClient = new HttpClient(mockHttpHandler.Object);
        var mockLogger = new Mock<ILogger<OpenAIProvider>>();
        
        var settings = new OpenAISettings
        {
            ApiKey = "test-key",
            Model = "gpt-4o",
            BaseUrl = "https://api.openai.com/v1"
        };

        var provider = new OpenAIProvider(httpClient, settings, mockLogger.Object);

        var request = new LLMGenerationRequest
        {
            Prompt = "Test prompt"
        };

        // Act
        var response = await provider.GenerateAsync(request);

        // Assert
        response.Should().NotBeNull();
        response.Success.Should().BeFalse();
        response.Error.Should().Contain("Invalid request");
        response.Provider.Should().Be("OpenAI");
    }

    [Fact]
    public async Task GenerateAsync_WithTimeout_ThrowsTimeoutException()
    {
        // Arrange
        var mockHttpHandler = new Mock<HttpMessageHandler>();
        mockHttpHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ThrowsAsync(new TaskCanceledException());

        var httpClient = new HttpClient(mockHttpHandler.Object);
        var mockLogger = new Mock<ILogger<OpenAIProvider>>();
        
        var settings = new OpenAISettings
        {
            ApiKey = "test-key",
            Model = "gpt-4o",
            BaseUrl = "https://api.openai.com/v1"
        };

        var provider = new OpenAIProvider(httpClient, settings, mockLogger.Object);

        var request = new LLMGenerationRequest
        {
            Prompt = "Test prompt"
        };

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(() => provider.GenerateAsync(request));
    }
}