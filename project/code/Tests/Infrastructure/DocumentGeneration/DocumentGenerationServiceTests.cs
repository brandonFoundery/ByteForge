using Xunit;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.LLM;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.DocumentGeneration;

public class DocumentGenerationServiceTests
{
    private readonly Mock<IDocumentTemplateService> _mockTemplateService;
    private readonly Mock<IDocumentValidationService> _mockValidationService;
    private readonly Mock<ILLMService> _mockLLMService;
    private readonly Mock<ILogger<DocumentGenerationService>> _mockLogger;
    private readonly DocumentGenerationService _service;

    public DocumentGenerationServiceTests()
    {
        _mockTemplateService = new Mock<IDocumentTemplateService>();
        _mockValidationService = new Mock<IDocumentValidationService>();
        _mockLLMService = new Mock<ILLMService>();
        _mockLogger = new Mock<ILogger<DocumentGenerationService>>();
        
        _service = new DocumentGenerationService(
            _mockTemplateService.Object,
            _mockValidationService.Object,
            _mockLLMService.Object,
            _mockLogger.Object);
    }

    [Fact]
    public async Task GenerateDocumentAsync_WithValidRequest_ReturnsGeneratedDocument()
    {
        // Arrange
        var request = new DocumentGenerationRequest
        {
            DocumentType = "BRD",
            ProjectName = "TestProject",
            ProjectDescription = "A test project",
            AdditionalContext = new Dictionary<string, object>
            {
                ["Author"] = "Test User",
                ["Version"] = "1.0.0"
            }
        };

        var template = "# {{DocumentType}} for {{ProjectName}}\n{{Content}}";
        var llmResponse = new LLMGenerationResponse
        {
            Success = true,
            Content = "## Executive Summary\nThis is the generated BRD content."
        };
        var processedContent = "# Business Requirements Document for TestProject\n## Executive Summary\nThis is the generated BRD content.";
        var validationResult = new DocumentValidationResult { IsValid = true };

        _mockTemplateService.Setup(x => x.LoadTemplateAsync("BRD"))
            .ReturnsAsync(template);
        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(llmResponse);
        _mockTemplateService.Setup(x => x.ProcessTemplateAsync(template, It.IsAny<Dictionary<string, object>>()))
            .ReturnsAsync(processedContent);
        _mockValidationService.Setup(x => x.ValidateDocumentAsync("BRD", processedContent))
            .ReturnsAsync(validationResult);

        // Act
        var result = await _service.GenerateDocumentAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Success.Should().BeTrue();
        result.DocumentType.Should().Be("BRD");
        result.Content.Should().Be(processedContent);
        result.GeneratedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
    }

    [Fact]
    public async Task GenerateDocumentAsync_WithLLMFailure_ReturnsError()
    {
        // Arrange
        var request = new DocumentGenerationRequest
        {
            DocumentType = "PRD",
            ProjectName = "TestProject"
        };

        var template = "# {{DocumentType}}";
        var llmResponse = new LLMGenerationResponse
        {
            Success = false,
            Error = "LLM service unavailable"
        };

        _mockTemplateService.Setup(x => x.LoadTemplateAsync("PRD"))
            .ReturnsAsync(template);
        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(llmResponse);

        // Act
        var result = await _service.GenerateDocumentAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Success.Should().BeFalse();
        result.Error.Should().Contain("LLM service unavailable");
    }

    [Fact]
    public async Task GenerateDocumentAsync_WithValidationFailure_ReturnsErrorWithContent()
    {
        // Arrange
        var request = new DocumentGenerationRequest
        {
            DocumentType = "FRD",
            ProjectName = "TestProject"
        };

        var template = "# {{DocumentType}}";
        var llmResponse = new LLMGenerationResponse
        {
            Success = true,
            Content = "Invalid content"
        };
        var processedContent = "# Functional Requirements Document\nInvalid content";
        var validationResult = new DocumentValidationResult
        {
            IsValid = false,
            Errors = new[] { "Missing required section: Functional Requirements" }
        };

        _mockTemplateService.Setup(x => x.LoadTemplateAsync("FRD"))
            .ReturnsAsync(template);
        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(llmResponse);
        _mockTemplateService.Setup(x => x.ProcessTemplateAsync(template, It.IsAny<Dictionary<string, object>>()))
            .ReturnsAsync(processedContent);
        _mockValidationService.Setup(x => x.ValidateDocumentAsync("FRD", processedContent))
            .ReturnsAsync(validationResult);

        // Act
        var result = await _service.GenerateDocumentAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Success.Should().BeFalse();
        result.Content.Should().Be(processedContent); // Content is still returned
        result.ValidationErrors.Should().Contain("Missing required section: Functional Requirements");
        result.Error.Should().Contain("validation failed");
    }

    [Fact]
    public async Task GenerateDocumentAsync_WithDependencies_IncludesDependentContent()
    {
        // Arrange
        var request = new DocumentGenerationRequest
        {
            DocumentType = "PRD",
            ProjectName = "TestProject",
            Dependencies = new Dictionary<string, string>
            {
                ["BRD"] = "# BRD Content\n## Business Requirements\n- BR-001: Core feature"
            }
        };

        _mockTemplateService.Setup(x => x.LoadTemplateAsync("PRD"))
            .ReturnsAsync("# PRD Template");
        _mockLLMService.Setup(x => x.GenerateAsync(
            It.Is<LLMGenerationRequest>(r => r.SystemPrompt.Contains("BR-001")), 
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse { Success = true, Content = "Generated PRD" });
        _mockTemplateService.Setup(x => x.ProcessTemplateAsync(It.IsAny<string>(), It.IsAny<Dictionary<string, object>>()))
            .ReturnsAsync("Processed PRD");
        _mockValidationService.Setup(x => x.ValidateDocumentAsync("PRD", It.IsAny<string>()))
            .ReturnsAsync(new DocumentValidationResult { IsValid = true });

        // Act
        var result = await _service.GenerateDocumentAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Success.Should().BeTrue();
        
        _mockLLMService.Verify(x => x.GenerateAsync(
            It.Is<LLMGenerationRequest>(r => r.SystemPrompt.Contains("Business Requirements")), 
            It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task GenerateBatchAsync_GeneratesMultipleDocuments()
    {
        // Arrange
        var requests = new[]
        {
            new DocumentGenerationRequest { DocumentType = "BRD", ProjectName = "Test" },
            new DocumentGenerationRequest { DocumentType = "PRD", ProjectName = "Test" },
            new DocumentGenerationRequest { DocumentType = "FRD", ProjectName = "Test" }
        };

        _mockTemplateService.Setup(x => x.LoadTemplateAsync(It.IsAny<string>()))
            .ReturnsAsync("# Template");
        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse { Success = true, Content = "Generated" });
        _mockTemplateService.Setup(x => x.ProcessTemplateAsync(It.IsAny<string>(), It.IsAny<Dictionary<string, object>>()))
            .ReturnsAsync("Processed");
        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<string>(), It.IsAny<string>()))
            .ReturnsAsync(new DocumentValidationResult { IsValid = true });

        // Act
        var results = await _service.GenerateBatchAsync(requests);

        // Assert
        results.Should().HaveCount(3);
        results.Should().AllSatisfy(r => r.Success.Should().BeTrue());
        results.Select(r => r.DocumentType).Should().BeEquivalentTo(new[] { "BRD", "PRD", "FRD" });
    }

    [Fact]
    public async Task GenerateDocumentAsync_WithRetry_RetriesOnTransientFailure()
    {
        // Arrange
        var request = new DocumentGenerationRequest
        {
            DocumentType = "TRD",
            ProjectName = "TestProject",
            MaxRetries = 3
        };

        var callCount = 0;
        _mockTemplateService.Setup(x => x.LoadTemplateAsync("TRD"))
            .ReturnsAsync("# Template");
        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(() =>
            {
                callCount++;
                if (callCount < 3)
                {
                    return new LLMGenerationResponse { Success = false, Error = "Temporary error" };
                }
                return new LLMGenerationResponse { Success = true, Content = "Success" };
            });
        _mockTemplateService.Setup(x => x.ProcessTemplateAsync(It.IsAny<string>(), It.IsAny<Dictionary<string, object>>()))
            .ReturnsAsync("Processed");
        _mockValidationService.Setup(x => x.ValidateDocumentAsync("TRD", It.IsAny<string>()))
            .ReturnsAsync(new DocumentValidationResult { IsValid = true });

        // Act
        var result = await _service.GenerateDocumentAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Success.Should().BeTrue();
        callCount.Should().Be(3);
    }
}