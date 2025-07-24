using Xunit;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.FileProviders;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Models.ProjectManagement;
using System.Text.Json;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.ProjectManagement;

public class ProjectTemplateServiceTests
{
    private readonly Mock<IFileProvider> _mockFileProvider;
    private readonly Mock<ILogger<ProjectTemplateService>> _mockLogger;
    private readonly ProjectTemplateService _service;

    public ProjectTemplateServiceTests()
    {
        _mockFileProvider = new Mock<IFileProvider>();
        _mockLogger = new Mock<ILogger<ProjectTemplateService>>();
        _service = new ProjectTemplateService(_mockFileProvider.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task GetTemplateAsync_WithExistingTemplate_ReturnsTemplate()
    {
        // Arrange
        var templateId = "CRM";
        var templateMetadata = new ProjectTemplate
        {
            Id = "CRM",
            Name = "CRM Application",
            Description = "Customer Relationship Management template",
            Category = "Business",
            Version = "1.0.0",
            RequiredDocuments = new[] { "BRD", "PRD", "FRD", "TRD" },
            DefaultSettings = new Dictionary<string, object>
            {
                ["database"] = "sqlserver",
                ["authentication"] = "jwt"
            }
        };

        var mockFileInfo = new Mock<IFileInfo>();
        mockFileInfo.Setup(x => x.Exists).Returns(true);
        mockFileInfo.Setup(x => x.CreateReadStream())
            .Returns(new MemoryStream(JsonSerializer.SerializeToUtf8Bytes(templateMetadata)));

        _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateId}/metadata.json"))
            .Returns(mockFileInfo.Object);

        // Act
        var result = await _service.GetTemplateAsync(templateId);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be("CRM");
        result.Name.Should().Be("CRM Application");
        result.Category.Should().Be("Business");
        result.RequiredDocuments.Should().HaveCount(4);
    }

    [Fact]
    public async Task GetTemplateAsync_WithNonExistentTemplate_ReturnsNull()
    {
        // Arrange
        var templateId = "NonExistent";
        var mockFileInfo = new Mock<IFileInfo>();
        mockFileInfo.Setup(x => x.Exists).Returns(false);

        _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateId}/metadata.json"))
            .Returns(mockFileInfo.Object);

        // Act
        var result = await _service.GetTemplateAsync(templateId);

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetAllTemplatesAsync_ReturnsAllAvailableTemplates()
    {
        // Arrange
        var mockDirectoryContents = new Mock<IDirectoryContents>();
        var templateDirectories = new List<IFileInfo>
        {
            CreateMockDirectory("CRM"),
            CreateMockDirectory("ECommerce"),
            CreateMockDirectory("SaaS"),
            CreateMockFile("README.md") // Should be ignored
        };

        mockDirectoryContents.Setup(x => x.GetEnumerator())
            .Returns(templateDirectories.GetEnumerator());

        _mockFileProvider.Setup(x => x.GetDirectoryContents("Templates"))
            .Returns(mockDirectoryContents.Object);

        // Setup metadata for each template
        SetupTemplateMetadata("CRM", "CRM Application", "Business");
        SetupTemplateMetadata("ECommerce", "E-Commerce Platform", "Retail");
        SetupTemplateMetadata("SaaS", "SaaS Application", "Software");

        // Act
        var templates = await _service.GetAllTemplatesAsync();

        // Assert
        templates.Should().HaveCount(3);
        templates.Should().Contain(t => t.Id == "CRM");
        templates.Should().Contain(t => t.Id == "ECommerce");
        templates.Should().Contain(t => t.Id == "SaaS");
    }

    [Fact]
    public async Task GetTemplatesByCategory_ReturnsFilteredTemplates()
    {
        // Arrange
        var mockDirectoryContents = new Mock<IDirectoryContents>();
        var templateDirectories = new List<IFileInfo>
        {
            CreateMockDirectory("CRM"),
            CreateMockDirectory("ERP"),
            CreateMockDirectory("SaaS")
        };

        mockDirectoryContents.Setup(x => x.GetEnumerator())
            .Returns(templateDirectories.GetEnumerator());

        _mockFileProvider.Setup(x => x.GetDirectoryContents("Templates"))
            .Returns(mockDirectoryContents.Object);

        SetupTemplateMetadata("CRM", "CRM Application", "Business");
        SetupTemplateMetadata("ERP", "ERP System", "Business");
        SetupTemplateMetadata("SaaS", "SaaS Application", "Software");

        // Act
        var templates = await _service.GetTemplatesByCategoryAsync("Business");

        // Assert
        templates.Should().HaveCount(2);
        templates.Should().AllSatisfy(t => t.Category.Should().Be("Business"));
    }

    [Fact]
    public async Task GetTemplateStructureAsync_ReturnsTemplateFiles()
    {
        // Arrange
        var templateId = "CRM";
        var mockDirectoryContents = new Mock<IDirectoryContents>();
        var templateFiles = new List<IFileInfo>
        {
            CreateMockFile("metadata.json"),
            CreateMockFile("README.md"),
            CreateMockFile("template.yaml"),
            CreateMockDirectory("src"),
            CreateMockDirectory("docs")
        };

        mockDirectoryContents.Setup(x => x.GetEnumerator())
            .Returns(templateFiles.GetEnumerator());

        _mockFileProvider.Setup(x => x.GetDirectoryContents($"Templates/{templateId}"))
            .Returns(mockDirectoryContents.Object);

        // Act
        var structure = await _service.GetTemplateStructureAsync(templateId);

        // Assert
        structure.Should().NotBeNull();
        structure!.Files.Should().HaveCount(3);
        structure.Directories.Should().HaveCount(2);
        structure.Files.Should().Contain("metadata.json");
        structure.Directories.Should().Contain("src");
    }

    [Fact]
    public async Task ValidateTemplateAsync_WithValidTemplate_ReturnsSuccess()
    {
        // Arrange
        var templateId = "CRM";
        var template = new ProjectTemplate
        {
            Id = "CRM",
            Name = "CRM Application",
            RequiredDocuments = new[] { "BRD", "PRD" }
        };

        SetupTemplateWithFiles(templateId, template, new[]
        {
            "metadata.json",
            "template.yaml",
            "Documents/BRD.md",
            "Documents/PRD.md"
        });

        // Act
        var result = await _service.ValidateTemplateAsync(templateId);

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public async Task ValidateTemplateAsync_WithMissingRequiredFiles_ReturnsError()
    {
        // Arrange
        var templateId = "CRM";
        var template = new ProjectTemplate
        {
            Id = "CRM",
            Name = "CRM Application",
            RequiredDocuments = new[] { "BRD", "PRD", "FRD" }
        };

        SetupTemplateWithFiles(templateId, template, new[]
        {
            "metadata.json",
            "template.yaml",
            "Documents/BRD.md",
            "Documents/PRD.md"
            // FRD.md is missing
        });

        // Act
        var result = await _service.ValidateTemplateAsync(templateId);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Contains("FRD"));
    }

    [Fact]
    public async Task CloneTemplateAsync_CreatesNewTemplateFromExisting()
    {
        // Arrange
        var sourceId = "CRM";
        var targetId = "CustomCRM";
        var template = new ProjectTemplate
        {
            Id = "CRM",
            Name = "CRM Application",
            Description = "Base CRM template"
        };

        SetupTemplateMetadata(sourceId, template.Name, "Business");

        // Act
        var result = await _service.CloneTemplateAsync(sourceId, targetId, "Custom CRM");

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(targetId);
        result.Name.Should().Be("Custom CRM");
        result.Description.Should().Contain("Cloned from");
    }

    private IFileInfo CreateMockDirectory(string name)
    {
        var mock = new Mock<IFileInfo>();
        mock.Setup(x => x.Name).Returns(name);
        mock.Setup(x => x.IsDirectory).Returns(true);
        mock.Setup(x => x.Exists).Returns(true);
        return mock.Object;
    }

    private IFileInfo CreateMockFile(string name)
    {
        var mock = new Mock<IFileInfo>();
        mock.Setup(x => x.Name).Returns(name);
        mock.Setup(x => x.IsDirectory).Returns(false);
        mock.Setup(x => x.Exists).Returns(true);
        return mock.Object;
    }

    private void SetupTemplateMetadata(string templateId, string name, string category)
    {
        var template = new ProjectTemplate
        {
            Id = templateId,
            Name = name,
            Category = category,
            Version = "1.0.0",
            RequiredDocuments = new[] { "BRD", "PRD" }
        };

        var mockFileInfo = new Mock<IFileInfo>();
        mockFileInfo.Setup(x => x.Exists).Returns(true);
        mockFileInfo.Setup(x => x.CreateReadStream())
            .Returns(new MemoryStream(JsonSerializer.SerializeToUtf8Bytes(template)));

        _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateId}/metadata.json"))
            .Returns(mockFileInfo.Object);
    }

    private void SetupTemplateWithFiles(string templateId, ProjectTemplate template, string[] files)
    {
        // Setup metadata
        var mockMetadataFile = new Mock<IFileInfo>();
        mockMetadataFile.Setup(x => x.Exists).Returns(true);
        mockMetadataFile.Setup(x => x.CreateReadStream())
            .Returns(new MemoryStream(JsonSerializer.SerializeToUtf8Bytes(template)));

        _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateId}/metadata.json"))
            .Returns(mockMetadataFile.Object);

        // Setup file existence checks
        foreach (var file in files)
        {
            var mockFile = new Mock<IFileInfo>();
            mockFile.Setup(x => x.Exists).Returns(true);
            _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateId}/{file}"))
                .Returns(mockFile.Object);
        }

        // Setup missing files
        foreach (var doc in template.RequiredDocuments)
        {
            var docPath = $"Documents/{doc}.md";
            if (!files.Contains(docPath))
            {
                var mockFile = new Mock<IFileInfo>();
                mockFile.Setup(x => x.Exists).Returns(false);
                _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateId}/{docPath}"))
                    .Returns(mockFile.Object);
            }
        }
    }
}