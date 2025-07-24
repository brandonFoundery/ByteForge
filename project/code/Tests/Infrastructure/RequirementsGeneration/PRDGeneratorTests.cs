using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.DocumentGenerators;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.RequirementsGeneration;

public class PRDGeneratorTests
{
    private readonly Mock<ILLMService> _mockLLMService;
    private readonly Mock<IDocumentTemplateService> _mockTemplateService;
    private readonly Mock<IDocumentValidationService> _mockValidationService;
    private readonly Mock<ILogger<PRDGenerator>> _mockLogger;
    private readonly PRDGenerator _generator;

    public PRDGeneratorTests()
    {
        _mockLLMService = new Mock<ILLMService>();
        _mockTemplateService = new Mock<IDocumentTemplateService>();
        _mockValidationService = new Mock<IDocumentValidationService>();
        _mockLogger = new Mock<ILogger<PRDGenerator>>();

        _generator = new PRDGenerator(
            _mockLLMService.Object,
            _mockTemplateService.Object,
            _mockValidationService.Object,
            _mockLogger.Object
        );
    }

    [Fact]
    public async Task GenerateAsync_ShouldCreatePRDWithProductFeatures()
    {
        // Arrange
        var request = new PRDGenerationRequest
        {
            ProjectName = "E-commerce Platform",
            ProjectDescription = "Modern e-commerce solution",
            TargetUsers = new List<string> { "Online Shoppers", "Merchants", "Administrators" },
            ProductVision = "Create the most user-friendly e-commerce platform",
            Dependencies = new Dictionary<string, string>
            {
                ["BRD"] = "Business requirements content..."
            }
        };

        var template = "# Product Requirements Document\n{{content}}";
        _mockTemplateService.Setup(x => x.GetTemplateAsync("PRD"))
            .ReturnsAsync(template);

        var llmResponse = @"## Product Overview
The E-commerce Platform is designed to revolutionize online shopping...

## Target Audience
- Online Shoppers: Individuals seeking convenient shopping
- Merchants: Businesses wanting to sell online
- Administrators: Platform managers

## Product Features
1. User Management
   - PR001: User registration and authentication
   - PR002: User profile management
2. Product Catalog
   - PR003: Product listing and search
   - PR004: Category navigation
3. Shopping Cart
   - PR005: Add/remove items from cart
   - PR006: Cart persistence across sessions

## User Stories
- As an online shopper, I want to search for products easily
- As a merchant, I want to manage my inventory
- As an administrator, I want to monitor platform activity

## Success Metrics
- 100,000 active users within 6 months
- 50% conversion rate improvement";

        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = llmResponse,
                Provider = "openai"
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse
            {
                IsValid = true,
                ValidationPassed = true
            });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Contains("Product Overview", result.Content);
        Assert.Contains("Product Features", result.Content);
        Assert.Contains("User Stories", result.Content);
        Assert.Contains("PR001", result.Content); // Verify requirement IDs
        Assert.NotEmpty(result.ProductFeatures);
        Assert.NotEmpty(result.UserStories);
    }

    [Fact]
    public async Task GenerateAsync_ShouldIncorporateBRDDependency()
    {
        // Arrange
        var brdContent = @"Business Requirements:
- BR001: System shall support multiple payment methods
- BR002: System shall provide real-time inventory tracking";

        var request = new PRDGenerationRequest
        {
            ProjectName = "Inventory System",
            Dependencies = new Dictionary<string, string>
            {
                ["BRD"] = brdContent
            }
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("PRD"))
            .ReturnsAsync("{{content}}");

        _mockLLMService.Setup(x => x.GenerateAsync(
            It.Is<LLMGenerationRequest>(r => r.Prompt.Contains("BR001") && r.Prompt.Contains("BR002")), 
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = "Product features aligned with BR001 and BR002..."
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse { IsValid = true, ValidationPassed = true });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.True(result.Success);
        _mockLLMService.Verify(x => x.GenerateAsync(
            It.Is<LLMGenerationRequest>(r => r.Prompt.Contains("Business Requirements from BRD")), 
            It.IsAny<CancellationToken>()), 
            Times.Once);
    }

    [Fact]
    public async Task GenerateAsync_ShouldExtractProductFeatures()
    {
        // Arrange
        var request = new PRDGenerationRequest
        {
            ProjectName = "Mobile App"
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("PRD"))
            .ReturnsAsync("{{content}}");

        var llmContent = @"Product Features:
1. Authentication System
   - PR001: Biometric login support
   - PR002: Social media integration
2. Messaging
   - PR003: Real-time chat
   - PR004: File sharing";

        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = llmContent
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse { IsValid = true, ValidationPassed = true });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Equal(2, result.ProductFeatures.Count);
        Assert.Contains("Authentication System", result.ProductFeatures);
        Assert.Contains("Messaging", result.ProductFeatures);
        Assert.Equal(4, result.RequirementIds.Count);
    }

    [Fact]
    public async Task GenerateAsync_ShouldIncludeMarketAnalysis()
    {
        // Arrange
        var request = new PRDGenerationRequest
        {
            ProjectName = "Fitness Tracker",
            MarketAnalysis = "The fitness tracker market is growing at 15% annually",
            CompetitorProducts = new List<string> { "Fitbit", "Apple Watch", "Garmin" }
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("PRD"))
            .ReturnsAsync("{{content}}");

        _mockLLMService.Setup(x => x.GenerateAsync(
            It.Is<LLMGenerationRequest>(r => 
                r.Prompt.Contains("15% annually") && 
                r.Prompt.Contains("Fitbit") && 
                r.Prompt.Contains("Apple Watch")), 
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = "Market Analysis: Growing market... Competitors: Fitbit, Apple Watch, Garmin..."
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse { IsValid = true, ValidationPassed = true });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Contains("Fitbit", result.Content);
        Assert.Contains("Apple Watch", result.Content);
        Assert.Contains("15% annually", result.Content);
    }

    [Fact]
    public async Task GenerateAsync_ShouldExtractUserStories()
    {
        // Arrange
        var request = new PRDGenerationRequest
        {
            ProjectName = "Task Manager"
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("PRD"))
            .ReturnsAsync("{{content}}");

        var llmContent = @"User Stories:
- As a project manager, I want to create tasks so that I can organize work
- As a team member, I want to update task status so that everyone knows progress
- As a stakeholder, I want to view reports so that I can track project health";

        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = llmContent
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse { IsValid = true, ValidationPassed = true });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Equal(3, result.UserStories.Count);
        Assert.All(result.UserStories, story => Assert.StartsWith("As a", story));
    }
}