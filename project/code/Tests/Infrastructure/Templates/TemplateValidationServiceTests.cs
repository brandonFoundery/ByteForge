using Xunit;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.Templates;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.Templates;

public class TemplateValidationServiceTests
{
    private readonly Mock<ILogger<TemplateValidationService>> _loggerMock;
    private readonly TemplateValidationService _service;

    public TemplateValidationServiceTests()
    {
        _loggerMock = new Mock<ILogger<TemplateValidationService>>();
        _service = new TemplateValidationService(_loggerMock.Object);
    }

    [Fact]
    public async Task ValidateTemplateAsync_ValidTemplate_ReturnsValid()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "valid-template",
            Name = "Valid Template",
            Description = "A valid template for testing",
            Category = "Test",
            Version = "1.0.0",
            RequiredDocuments = new[] { "BRD", "PRD", "FRD", "TRD" },
            OptionalDocuments = new[] { "UX_SPEC", "TEST_PLAN" },
            DefaultSettings = new Dictionary<string, object>
            {
                { "multiTenant", true },
                { "authProvider", "JWT" }
            },
            FileStructure = new Dictionary<string, string>
            {
                { "/src", "directory" },
                { "/src/Controllers", "directory" },
                { "/src/Services", "directory" },
                { "/src/Models", "directory" },
                { "/tests", "directory" },
                { "/docs", "directory" },
                { "README.md", "file" },
                { ".gitignore", "file" }
            }
        };

        // Act
        var result = await _service.ValidateTemplateAsync(template);

        // Assert
        result.Should().NotBeNull();
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
        result.Warnings.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateTemplateAsync_MissingRequiredFields_ReturnsInvalid()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "", // Empty ID
            Name = "", // Empty Name
            Category = "Test"
        };

        // Act
        var result = await _service.ValidateTemplateAsync(template);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain("Template ID is required");
        result.Errors.Should().Contain("Template name is required");
    }

    [Fact]
    public async Task ValidateTemplateAsync_InvalidVersion_ReturnsInvalid()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "test-template",
            Name = "Test Template",
            Category = "Test",
            Version = "invalid-version" // Invalid semantic version
        };

        // Act
        var result = await _service.ValidateTemplateAsync(template);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Invalid version format"));
    }

    [Fact]
    public async Task ValidateTemplateAsync_InvalidDocumentReferences_ReturnsInvalid()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "test-template",
            Name = "Test Template",
            Category = "Test",
            Version = "1.0.0",
            RequiredDocuments = new[] { "BRD", "INVALID_DOC", "FRD" }
        };

        // Act
        var result = await _service.ValidateTemplateAsync(template);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Invalid document type: INVALID_DOC"));
    }

    [Fact]
    public async Task ValidateTemplateAsync_InvalidFileStructure_ReturnsInvalid()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "test-template",
            Name = "Test Template",
            Category = "Test",
            Version = "1.0.0",
            FileStructure = new Dictionary<string, string>
            {
                { "valid/path", "directory" },
                { "another/valid/file.txt", "file" },
                { "invalid*path", "directory" }, // Invalid characters
                { "path/with/type", "invalid_type" } // Invalid type
            }
        };

        // Act
        var result = await _service.ValidateTemplateAsync(template);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Invalid path"));
        result.Errors.Should().Contain(e => e.Contains("Invalid file structure type"));
    }

    [Fact]
    public async Task ValidateTemplateAsync_MissingCriticalDirectories_ReturnsWarning()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "test-template",
            Name = "Test Template",
            Category = "Test",
            Version = "1.0.0",
            FileStructure = new Dictionary<string, string>
            {
                { "README.md", "file" }
                // Missing common directories like src, tests, docs
            }
        };

        // Act
        var result = await _service.ValidateTemplateAsync(template);

        // Assert
        result.IsValid.Should().BeTrue(); // Still valid but with warnings
        result.Warnings.Should().Contain(w => w.Contains("Missing recommended directory"));
    }

    [Fact]
    public async Task ValidateTemplateStructureAsync_ValidStructure_ReturnsValid()
    {
        // Arrange
        var structure = new TemplateStructure
        {
            Files = new List<string> { "README.md", ".gitignore", "appsettings.json" },
            Directories = new List<string> { "/src", "/tests", "/docs" },
            Metadata = new Dictionary<string, object>
            {
                { "author", "ByteForge" },
                { "created", DateTime.UtcNow },
                { "tags", new[] { "crm", "business" } }
            }
        };

        // Act
        var result = await _service.ValidateTemplateStructureAsync(structure);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateTemplateStructureAsync_DuplicatePaths_ReturnsInvalid()
    {
        // Arrange
        var structure = new TemplateStructure
        {
            Files = new List<string> { "README.md", "readme.md", "README.md" }, // Duplicates
            Directories = new List<string> { "/src", "/SRC" } // Case-sensitive duplicates
        };

        // Act
        var result = await _service.ValidateTemplateStructureAsync(structure);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Duplicate"));
    }

    [Fact]
    public async Task ValidateDefaultSettingsAsync_ValidSettings_ReturnsValid()
    {
        // Arrange
        var settings = new Dictionary<string, object>
        {
            { "multiTenant", true },
            { "authProvider", "JWT" },
            { "database", "SQL Server" },
            { "cacheProvider", "Redis" },
            { "apiVersion", "1.0" },
            { "features", new[] { "audit", "reporting", "notifications" } }
        };

        // Act
        var result = await _service.ValidateDefaultSettingsAsync(settings);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateDefaultSettingsAsync_InvalidAuthProvider_ReturnsInvalid()
    {
        // Arrange
        var settings = new Dictionary<string, object>
        {
            { "authProvider", "InvalidAuth" } // Should be JWT, OAuth, Azure AD, etc.
        };

        // Act
        var result = await _service.ValidateDefaultSettingsAsync(settings);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Invalid auth provider"));
    }

    [Fact]
    public async Task ValidateDefaultSettingsAsync_InvalidDatabase_ReturnsInvalid()
    {
        // Arrange
        var settings = new Dictionary<string, object>
        {
            { "database", "InvalidDB" } // Should be SQL Server, PostgreSQL, MySQL, etc.
        };

        // Act
        var result = await _service.ValidateDefaultSettingsAsync(settings);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Invalid database"));
    }

    [Fact]
    public async Task ValidateTemplateMetadataAsync_ValidMetadata_ReturnsValid()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "crm-template",
            Name = "CRM Template",
            Description = "A comprehensive CRM template",
            Category = "Business",
            Version = "2.1.0"
        };

        // Act
        var result = await _service.ValidateTemplateMetadataAsync(template);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateTemplateMetadataAsync_InvalidCategory_ReturnsInvalid()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "test-template",
            Name = "Test Template",
            Category = "InvalidCategory", // Should be from predefined list
            Version = "1.0.0"
        };

        // Act
        var result = await _service.ValidateTemplateMetadataAsync(template);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Invalid category"));
    }

    [Fact]
    public async Task ValidateTemplateMetadataAsync_TooLongDescription_ReturnsWarning()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "test-template",
            Name = "Test Template",
            Category = "Business",
            Description = new string('x', 1001), // Exceeds 1000 char limit
            Version = "1.0.0"
        };

        // Act
        var result = await _service.ValidateTemplateMetadataAsync(template);

        // Assert
        result.IsValid.Should().BeTrue(); // Still valid but with warning
        result.Warnings.Should().Contain(w => w.Contains("Description exceeds"));
    }
}