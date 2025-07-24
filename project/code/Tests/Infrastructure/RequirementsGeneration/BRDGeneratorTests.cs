using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.DocumentGenerators;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.RequirementsGeneration;

public class BRDGeneratorTests
{
    private readonly Mock<ILLMService> _mockLLMService;
    private readonly Mock<IDocumentTemplateService> _mockTemplateService;
    private readonly Mock<IDocumentValidationService> _mockValidationService;
    private readonly Mock<ILogger<BRDGenerator>> _mockLogger;
    private readonly BRDGenerator _generator;

    public BRDGeneratorTests()
    {
        _mockLLMService = new Mock<ILLMService>();
        _mockTemplateService = new Mock<IDocumentTemplateService>();
        _mockValidationService = new Mock<IDocumentValidationService>();
        _mockLogger = new Mock<ILogger<BRDGenerator>>();

        _generator = new BRDGenerator(
            _mockLLMService.Object,
            _mockTemplateService.Object,
            _mockValidationService.Object,
            _mockLogger.Object
        );
    }

    [Fact]
    public async Task GenerateAsync_ShouldCreateBRDWithProperStructure()
    {
        // Arrange
        var request = new BRDGenerationRequest
        {
            ProjectName = "Test CRM System",
            ProjectDescription = "A customer relationship management system",
            ClientRequirements = "We need a system to manage our customers and sales pipeline",
            Stakeholders = new List<string> { "Sales Team", "Management", "IT Department" }
        };

        var template = "# Business Requirements Document\n{{content}}";
        _mockTemplateService.Setup(x => x.GetTemplateAsync("BRD"))
            .ReturnsAsync(template);

        var llmResponse = @"## Executive Summary
The Test CRM System is designed to streamline customer relationship management...

## Business Objectives
1. Improve customer data management
2. Enhance sales pipeline visibility
3. Increase team collaboration

## Stakeholder Analysis
- Sales Team: Primary users requiring efficient customer tracking
- Management: Needs reporting and analytics
- IT Department: Responsible for system maintenance

## Business Requirements
1. Customer Management
   - BR001: System shall store customer contact information
   - BR002: System shall track customer interactions
2. Sales Pipeline
   - BR003: System shall track opportunities through stages
   - BR004: System shall provide sales forecasting

## Success Criteria
- 50% reduction in data entry time
- 30% improvement in sales conversion rate";

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
        Assert.Contains("Executive Summary", result.Content);
        Assert.Contains("Business Objectives", result.Content);
        Assert.Contains("Stakeholder Analysis", result.Content);
        Assert.Contains("Business Requirements", result.Content);
        Assert.Contains("BR001", result.Content); // Verify requirement IDs
        Assert.Contains("Success Criteria", result.Content);
    }

    [Fact]
    public async Task GenerateAsync_ShouldIncludeStakeholderAnalysis()
    {
        // Arrange
        var request = new BRDGenerationRequest
        {
            ProjectName = "E-commerce Platform",
            Stakeholders = new List<string> { "Customers", "Vendors", "Admin Team" }
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("BRD"))
            .ReturnsAsync("{{content}}");

        _mockLLMService.Setup(x => x.GenerateAsync(
            It.Is<LLMGenerationRequest>(r => r.Prompt.Contains("Customers") && r.Prompt.Contains("Vendors")), 
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = "Stakeholder Analysis:\n- Customers: Need easy shopping experience\n- Vendors: Require inventory management\n- Admin Team: Need system control"
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse { IsValid = true, ValidationPassed = true });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Contains("Customers", result.Content);
        Assert.Contains("Vendors", result.Content);
        Assert.Contains("Admin Team", result.Content);
    }

    [Fact]
    public async Task GenerateAsync_ShouldGenerateUniqueRequirementIds()
    {
        // Arrange
        var request = new BRDGenerationRequest
        {
            ProjectName = "Test Project"
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("BRD"))
            .ReturnsAsync("{{content}}");

        var llmContent = @"Business Requirements:
1. User Management
   - System shall provide user authentication
   - System shall support role-based access
2. Data Security
   - System shall encrypt sensitive data
   - System shall maintain audit logs";

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
        Assert.Contains("BR-", result.Content); // Should have requirement IDs
        Assert.NotNull(result.RequirementIds);
        Assert.NotEmpty(result.RequirementIds);
        Assert.All(result.RequirementIds, id => Assert.StartsWith("BR-", id));
    }

    [Fact]
    public async Task GenerateAsync_ShouldHandleValidationFailure()
    {
        // Arrange
        var request = new BRDGenerationRequest
        {
            ProjectName = "Test Project"
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("BRD"))
            .ReturnsAsync("{{content}}");

        _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<LLMGenerationRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = "Invalid BRD content without required sections"
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse
            {
                IsValid = false,
                ValidationPassed = false,
                Errors = new List<string> { "Missing Executive Summary section", "Missing Business Requirements section" }
            });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.False(result.Success);
        Assert.Contains("validation", result.Error.ToLower());
        Assert.NotEmpty(result.ValidationErrors);
    }

    [Fact]
    public async Task GenerateAsync_ShouldIncludeBusinessConstraints()
    {
        // Arrange
        var request = new BRDGenerationRequest
        {
            ProjectName = "Banking System",
            BusinessConstraints = new List<string>
            {
                "Must comply with PCI-DSS standards",
                "Maximum budget of $500,000",
                "Go-live date by Q4 2024"
            }
        };

        _mockTemplateService.Setup(x => x.GetTemplateAsync("BRD"))
            .ReturnsAsync("{{content}}");

        _mockLLMService.Setup(x => x.GenerateAsync(
            It.Is<LLMGenerationRequest>(r => r.Prompt.Contains("PCI-DSS") && r.Prompt.Contains("budget")), 
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(new LLMGenerationResponse
            {
                Success = true,
                Content = "Business Constraints:\n- Regulatory: Must comply with PCI-DSS standards\n- Financial: Maximum budget of $500,000\n- Timeline: Go-live date by Q4 2024"
            });

        _mockValidationService.Setup(x => x.ValidateDocumentAsync(It.IsAny<DocumentValidationRequest>()))
            .ReturnsAsync(new DocumentValidationResponse { IsValid = true, ValidationPassed = true });

        // Act
        var result = await _generator.GenerateAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Contains("PCI-DSS", result.Content);
        Assert.Contains("$500,000", result.Content);
        Assert.Contains("Q4 2024", result.Content);
    }
}