using Xunit;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using YamlDotNet.RepresentationModel;

using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.DocumentGeneration;

public class DocumentValidationServiceTests
{
    private readonly Mock<ILogger<DocumentValidationService>> _mockLogger;
    private readonly DocumentValidationService _service;

    public DocumentValidationServiceTests()
    {
        _mockLogger = new Mock<ILogger<DocumentValidationService>>();
        _service = new DocumentValidationService(_mockLogger.Object);
    }

    [Fact]
    public async Task ValidateMarkdownStructureAsync_WithValidMarkdown_ReturnsSuccess()
    {
        // Arrange
        var markdown = @"# Document Title

## Section 1
This is content.

### Subsection 1.1
More content here.

## Section 2
- Item 1
- Item 2

### Requirements
| ID | Description |
|----|-------------|
| R1 | Requirement 1 |";

        // Act
        var result = await _service.ValidateMarkdownStructureAsync(markdown);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
        result.Warnings.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateMarkdownStructureAsync_WithMissingTitle_ReturnsError()
    {
        // Arrange
        var markdown = @"## Section 1
Content without a main title.";

        // Act
        var result = await _service.ValidateMarkdownStructureAsync(markdown);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("title"));
    }

    [Fact]
    public async Task ValidateMarkdownStructureAsync_WithEmptyContent_ReturnsError()
    {
        // Arrange
        var markdown = "";

        // Act
        var result = await _service.ValidateMarkdownStructureAsync(markdown);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("empty"));
    }

    [Fact]
    public async Task ValidateYamlAsync_WithValidYaml_ReturnsSuccess()
    {
        // Arrange
        var yaml = @"project:
  name: ByteForge
  version: 1.0.0
  description: AI-powered development platform
  
requirements:
  - id: REQ-001
    description: User authentication
    priority: high
  - id: REQ-002
    description: Document generation
    priority: medium";

        // Act
        var result = await _service.ValidateYamlAsync(yaml);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateYamlAsync_WithInvalidYaml_ReturnsError()
    {
        // Arrange
        var yaml = @"project:
  name: ByteForge
  version: 1.0.0
    description: Invalid indentation";

        // Act
        var result = await _service.ValidateYamlAsync(yaml);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().NotBeEmpty();
    }

    [Fact]
    public async Task ValidateDocumentAsync_WithBRD_ValidatesRequiredSections()
    {
        // Arrange
        var brdContent = @"# Business Requirements Document

## Executive Summary
Overview of the project.

## Business Objectives
- Objective 1
- Objective 2

## Stakeholders
- Product Owner
- Development Team

## Business Requirements
- BR-001: Core functionality
- BR-002: User management

## Success Criteria
- Metric 1
- Metric 2";

        // Act
        var result = await _service.ValidateDocumentAsync("BRD", brdContent);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateDocumentAsync_WithBRD_MissingRequiredSection_ReturnsError()
    {
        // Arrange
        var brdContent = @"# Business Requirements Document

## Executive Summary
Overview of the project.

## Business Objectives
- Objective 1";
        // Missing Stakeholders, Business Requirements, and Success Criteria

        // Act
        var result = await _service.ValidateDocumentAsync("BRD", brdContent);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Stakeholders"));
        result.Errors.Should().Contain(e => e.Contains("Business Requirements"));
        result.Errors.Should().Contain(e => e.Contains("Success Criteria"));
    }

    [Fact]
    public async Task ValidateDocumentAsync_WithPRD_ValidatesRequiredSections()
    {
        // Arrange
        var prdContent = @"# Product Requirements Document

## Product Overview
Product description.

## Features
- Feature 1
- Feature 2

## User Stories
- As a user, I want...

## Technical Requirements
- Requirement 1

## Acceptance Criteria
- Criteria 1";

        // Act
        var result = await _service.ValidateDocumentAsync("PRD", prdContent);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public async Task ValidateDocumentAsync_WithFRD_ValidatesRequiredSections()
    {
        // Arrange
        var frdContent = @"# Functional Requirements Document

## System Overview
System description.

## Functional Requirements
- FR-001: Login functionality
- FR-002: Data processing

## Use Cases
- UC-001: User login

## Data Requirements
- Data model description

## Interface Requirements
- API specifications";

        // Act
        var result = await _service.ValidateDocumentAsync("FRD", frdContent);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public async Task ValidateDocumentAsync_WithTRD_ValidatesRequiredSections()
    {
        // Arrange
        var trdContent = @"# Technical Requirements Document

## Architecture Overview
System architecture.

## Technology Stack
- .NET 8
- React

## Database Design
Schema details.

## API Design
API specifications.

## Security Requirements
Security measures.

## Performance Requirements
Performance metrics.";

        // Act
        var result = await _service.ValidateDocumentAsync("TRD", trdContent);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public async Task ValidateDocumentAsync_WithUnknownDocumentType_ReturnsWarning()
    {
        // Arrange
        var content = @"# Some Document
## Content
Some content here.";

        // Act
        var result = await _service.ValidateDocumentAsync("UNKNOWN", content);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Warnings.Should().Contain(w => w.Contains("Unknown document type"));
    }

    [Fact]
    public async Task ValidateDocumentCompleteness_ChecksMinimumContentLength()
    {
        // Arrange
        var shortContent = @"# Document
## Section
Too short.";

        // Act
        var result = await _service.ValidateDocumentAsync("BRD", shortContent);

        // Assert
        result.Warnings.Should().Contain(w => w.Contains("appears to be incomplete"));
    }
}