using Xunit;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using System.IO.Abstractions;
using System.IO.Abstractions.TestingHelpers;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.Templates;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.Templates;

public class TemplateGeneratorTests
{
    private readonly MockFileSystem _fileSystem;
    private readonly Mock<IDocumentTemplateService> _documentTemplateServiceMock;
    private readonly Mock<ILogger<TemplateGenerator>> _loggerMock;
    private readonly TemplateGenerator _generator;

    public TemplateGeneratorTests()
    {
        _fileSystem = new MockFileSystem();
        _documentTemplateServiceMock = new Mock<IDocumentTemplateService>();
        _loggerMock = new Mock<ILogger<TemplateGenerator>>();
        _generator = new TemplateGenerator(
            _fileSystem,
            _documentTemplateServiceMock.Object,
            _loggerMock.Object);
    }

    #region CRM Template Tests

    [Fact]
    public async Task GenerateCRMTemplateAsync_CreatesCompleteStructure()
    {
        // Arrange
        var outputPath = "/output/crm-project";
        var projectName = "TestCRM";
        var options = new TemplateGenerationOptions
        {
            ProjectName = projectName,
            IncludeSampleData = true,
            MultiTenant = true,
            AuthProvider = "JWT",
            Database = "SQL Server"
        };

        // Act
        var result = await _generator.GenerateCRMTemplateAsync(outputPath, options);

        // Assert
        result.Should().NotBeNull();
        result.Success.Should().BeTrue();
        result.GeneratedFiles.Should().NotBeEmpty();

        // Verify directory structure
        _fileSystem.Directory.Exists($"{outputPath}/src").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/src/Controllers").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/src/Services").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/src/Models").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/tests").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/docs").Should().BeTrue();

        // Verify key files
        _fileSystem.File.Exists($"{outputPath}/README.md").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/.gitignore").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/appsettings.json").Should().BeTrue();
    }

    [Fact]
    public async Task GenerateCRMTemplateAsync_IncludesRequiredDocuments()
    {
        // Arrange
        var outputPath = "/output/crm-project";
        var options = new TemplateGenerationOptions { ProjectName = "TestCRM" };

        _documentTemplateServiceMock
            .Setup(x => x.GenerateDocumentAsync(It.IsAny<string>(), It.IsAny<object>()))
            .ReturnsAsync("Generated document content");

        // Act
        var result = await _generator.GenerateCRMTemplateAsync(outputPath, options);

        // Assert
        _fileSystem.File.Exists($"{outputPath}/docs/requirements/BRD.md").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/docs/requirements/PRD.md").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/docs/requirements/FRD.md").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/docs/requirements/TRD.md").Should().BeTrue();
    }

    [Fact]
    public async Task GenerateCRMTemplateAsync_WithSampleData_CreatesSampleFiles()
    {
        // Arrange
        var outputPath = "/output/crm-project";
        var options = new TemplateGenerationOptions
        {
            ProjectName = "TestCRM",
            IncludeSampleData = true
        };

        // Act
        var result = await _generator.GenerateCRMTemplateAsync(outputPath, options);

        // Assert
        _fileSystem.File.Exists($"{outputPath}/data/sample-customers.json").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/data/sample-contacts.json").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/data/sample-opportunities.json").Should().BeTrue();
    }

    [Fact]
    public async Task GenerateCRMTemplateAsync_ConfiguresMultiTenancy()
    {
        // Arrange
        var outputPath = "/output/crm-project";
        var options = new TemplateGenerationOptions
        {
            ProjectName = "TestCRM",
            MultiTenant = true
        };

        // Act
        await _generator.GenerateCRMTemplateAsync(outputPath, options);

        // Assert
        var appSettings = _fileSystem.File.ReadAllText($"{outputPath}/appsettings.json");
        appSettings.Should().Contain("\"MultiTenancy\": true");
        
        _fileSystem.File.Exists($"{outputPath}/src/Services/TenantService.cs").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/src/Middleware/TenantMiddleware.cs").Should().BeTrue();
    }

    #endregion

    #region E-commerce Template Tests

    [Fact]
    public async Task GenerateEcommerceTemplateAsync_CreatesCompleteStructure()
    {
        // Arrange
        var outputPath = "/output/ecommerce-project";
        var options = new TemplateGenerationOptions
        {
            ProjectName = "TestStore",
            IncludeSampleData = true,
            PaymentProviders = new[] { "Stripe", "PayPal" },
            ShippingProviders = new[] { "FedEx", "UPS" }
        };

        // Act
        var result = await _generator.GenerateEcommerceTemplateAsync(outputPath, options);

        // Assert
        result.Success.Should().BeTrue();

        // Verify e-commerce specific directories
        _fileSystem.Directory.Exists($"{outputPath}/src/Services/Payment").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/src/Services/Shipping").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/src/Services/Inventory").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/src/Models/Products").Should().BeTrue();
        _fileSystem.Directory.Exists($"{outputPath}/src/Models/Orders").Should().BeTrue();
    }

    [Fact]
    public async Task GenerateEcommerceTemplateAsync_ConfiguresPaymentProviders()
    {
        // Arrange
        var outputPath = "/output/ecommerce-project";
        var options = new TemplateGenerationOptions
        {
            ProjectName = "TestStore",
            PaymentProviders = new[] { "Stripe", "PayPal" }
        };

        // Act
        await _generator.GenerateEcommerceTemplateAsync(outputPath, options);

        // Assert
        _fileSystem.File.Exists($"{outputPath}/src/Services/Payment/StripePaymentService.cs").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/src/Services/Payment/PayPalPaymentService.cs").Should().BeTrue();
        
        var appSettings = _fileSystem.File.ReadAllText($"{outputPath}/appsettings.json");
        appSettings.Should().Contain("\"PaymentProviders\"");
        appSettings.Should().Contain("Stripe");
        appSettings.Should().Contain("PayPal");
    }

    [Fact]
    public async Task GenerateEcommerceTemplateAsync_WithSampleData_CreatesProductCatalog()
    {
        // Arrange
        var outputPath = "/output/ecommerce-project";
        var options = new TemplateGenerationOptions
        {
            ProjectName = "TestStore",
            IncludeSampleData = true
        };

        // Act
        await _generator.GenerateEcommerceTemplateAsync(outputPath, options);

        // Assert
        _fileSystem.File.Exists($"{outputPath}/data/sample-products.json").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/data/sample-categories.json").Should().BeTrue();
        _fileSystem.File.Exists($"{outputPath}/data/sample-inventory.json").Should().BeTrue();
    }

    #endregion

    #region Template Customization Tests

    [Fact]
    public async Task CustomizeTemplateAsync_AppliesCustomSettings()
    {
        // Arrange
        var templatePath = "/templates/base-template";
        var outputPath = "/output/custom-project";
        
        // Setup base template
        _fileSystem.AddDirectory(templatePath);
        _fileSystem.AddFile($"{templatePath}/config.json", 
            new MockFileData(@"{""name"": ""{{ProjectName}}"", ""version"": ""1.0.0""}"));
        _fileSystem.AddFile($"{templatePath}/README.md.template", 
            new MockFileData("# {{ProjectName}}\n\n{{Description}}"));

        var customization = new TemplateCustomization
        {
            Variables = new Dictionary<string, string>
            {
                { "ProjectName", "CustomProject" },
                { "Description", "A customized project" }
            },
            ExcludeFiles = new[] { "*.sample" },
            AdditionalFiles = new Dictionary<string, string>
            {
                { "CUSTOM.md", "Custom documentation" }
            }
        };

        // Act
        var result = await _generator.CustomizeTemplateAsync(templatePath, outputPath, customization);

        // Assert
        result.Success.Should().BeTrue();
        
        var config = _fileSystem.File.ReadAllText($"{outputPath}/config.json");
        config.Should().Contain("\"name\": \"CustomProject\"");
        
        var readme = _fileSystem.File.ReadAllText($"{outputPath}/README.md");
        readme.Should().Contain("# CustomProject");
        readme.Should().Contain("A customized project");
        
        _fileSystem.File.Exists($"{outputPath}/CUSTOM.md").Should().BeTrue();
    }

    [Fact]
    public async Task CustomizeTemplateAsync_HandlesConditionalSections()
    {
        // Arrange
        var templatePath = "/templates/conditional-template";
        var outputPath = "/output/conditional-project";
        
        _fileSystem.AddDirectory(templatePath);
        _fileSystem.AddFile($"{templatePath}/config.template", new MockFileData(@"
{
    ""multiTenant"": {{#if MultiTenant}}true{{else}}false{{/if}},
    {{#if IncludeCache}}
    ""cache"": {
        ""provider"": ""{{CacheProvider}}"",
        ""connectionString"": ""{{CacheConnection}}""
    },
    {{/if}}
    ""database"": ""{{Database}}""
}"));

        var customization = new TemplateCustomization
        {
            Variables = new Dictionary<string, string>
            {
                { "MultiTenant", "true" },
                { "IncludeCache", "true" },
                { "CacheProvider", "Redis" },
                { "CacheConnection", "localhost:6379" },
                { "Database", "SQL Server" }
            }
        };

        // Act
        await _generator.CustomizeTemplateAsync(templatePath, outputPath, customization);

        // Assert
        var config = _fileSystem.File.ReadAllText($"{outputPath}/config");
        config.Should().Contain("\"multiTenant\": true");
        config.Should().Contain("\"provider\": \"Redis\"");
        config.Should().Contain("\"connectionString\": \"localhost:6379\"");
    }

    [Fact]
    public async Task CustomizeTemplateAsync_MergesWithExistingProject()
    {
        // Arrange
        var templatePath = "/templates/update-template";
        var outputPath = "/output/existing-project";
        
        // Existing project
        _fileSystem.AddDirectory(outputPath);
        _fileSystem.AddFile($"{outputPath}/existing.txt", new MockFileData("Existing content"));
        _fileSystem.AddFile($"{outputPath}/config.json", new MockFileData(@"{""version"": ""1.0.0""}"));
        
        // Template
        _fileSystem.AddDirectory(templatePath);
        _fileSystem.AddFile($"{templatePath}/new-feature.txt", new MockFileData("New feature"));
        _fileSystem.AddFile($"{templatePath}/config.json.merge", new MockFileData(@"{""newFeature"": true}"));

        var customization = new TemplateCustomization
        {
            MergeMode = true,
            PreserveExisting = true
        };

        // Act
        var result = await _generator.CustomizeTemplateAsync(templatePath, outputPath, customization);

        // Assert
        result.Success.Should().BeTrue();
        
        // Existing file preserved
        _fileSystem.File.Exists($"{outputPath}/existing.txt").Should().BeTrue();
        
        // New file added
        _fileSystem.File.Exists($"{outputPath}/new-feature.txt").Should().BeTrue();
        
        // Config merged
        var config = _fileSystem.File.ReadAllText($"{outputPath}/config.json");
        config.Should().Contain("\"version\": \"1.0.0\"");
        config.Should().Contain("\"newFeature\": true");
    }

    #endregion

    #region Error Handling Tests

    [Fact]
    public async Task GenerateTemplateAsync_InvalidOutputPath_ReturnsError()
    {
        // Arrange
        var invalidPath = ":::invalid:::path:::";
        var options = new TemplateGenerationOptions { ProjectName = "Test" };

        // Act
        var result = await _generator.GenerateCRMTemplateAsync(invalidPath, options);

        // Assert
        result.Success.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("Invalid path"));
    }

    [Fact]
    public async Task GenerateTemplateAsync_ExistingDirectory_WithoutOverwrite_ReturnsError()
    {
        // Arrange
        var outputPath = "/output/existing";
        _fileSystem.AddDirectory(outputPath);
        _fileSystem.AddFile($"{outputPath}/file.txt", new MockFileData("content"));
        
        var options = new TemplateGenerationOptions 
        { 
            ProjectName = "Test",
            OverwriteExisting = false
        };

        // Act
        var result = await _generator.GenerateCRMTemplateAsync(outputPath, options);

        // Assert
        result.Success.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("already exists"));
    }

    #endregion
}