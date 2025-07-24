using Xunit;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using Microsoft.Extensions.FileProviders;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.DocumentGeneration;

public class DocumentTemplateServiceTests
{
    private readonly Mock<IFileProvider> _mockFileProvider;
    private readonly Mock<ILogger<DocumentTemplateService>> _mockLogger;
    private readonly DocumentTemplateService _service;

    public DocumentTemplateServiceTests()
    {
        _mockFileProvider = new Mock<IFileProvider>();
        _mockLogger = new Mock<ILogger<DocumentTemplateService>>();
        _service = new DocumentTemplateService(_mockFileProvider.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task LoadTemplateAsync_WithExistingTemplate_ReturnsContent()
    {
        // Arrange
        var templateName = "BRD";
        var templateContent = "# Business Requirements Document\n## {{ProjectName}}";
        var mockFileInfo = new Mock<IFileInfo>();
        
        mockFileInfo.Setup(x => x.Exists).Returns(true);
        mockFileInfo.Setup(x => x.CreateReadStream())
            .Returns(new MemoryStream(System.Text.Encoding.UTF8.GetBytes(templateContent)));
        
        _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateName}.md"))
            .Returns(mockFileInfo.Object);

        // Act
        var result = await _service.LoadTemplateAsync(templateName);

        // Assert
        result.Should().NotBeNull();
        result.Should().Be(templateContent);
    }

    [Fact]
    public async Task LoadTemplateAsync_WithNonExistentTemplate_ThrowsException()
    {
        // Arrange
        var templateName = "NonExistent";
        var mockFileInfo = new Mock<IFileInfo>();
        
        mockFileInfo.Setup(x => x.Exists).Returns(false);
        
        _mockFileProvider.Setup(x => x.GetFileInfo($"Templates/{templateName}.md"))
            .Returns(mockFileInfo.Object);

        // Act & Assert
        await Assert.ThrowsAsync<FileNotFoundException>(
            () => _service.LoadTemplateAsync(templateName));
    }

    [Fact]
    public void GetAvailableTemplates_ReturnsAllTemplateNames()
    {
        // Arrange
        var mockDirectoryContents = new Mock<IDirectoryContents>();
        var templateFiles = new List<IFileInfo>
        {
            CreateMockFileInfo("BRD.md"),
            CreateMockFileInfo("PRD.md"),
            CreateMockFileInfo("FRD.md"),
            CreateMockFileInfo("TRD.md"),
            CreateMockFileInfo("README.md"), // Should be excluded
            CreateMockFileInfo("template.txt") // Should be excluded
        };
        
        mockDirectoryContents.Setup(x => x.GetEnumerator())
            .Returns(templateFiles.GetEnumerator());
        
        _mockFileProvider.Setup(x => x.GetDirectoryContents("Templates"))
            .Returns(mockDirectoryContents.Object);

        // Act
        var templates = _service.GetAvailableTemplates();

        // Assert
        templates.Should().HaveCount(4);
        templates.Should().Contain("BRD");
        templates.Should().Contain("PRD");
        templates.Should().Contain("FRD");
        templates.Should().Contain("TRD");
        templates.Should().NotContain("README");
    }

    [Fact]
    public async Task ProcessTemplateAsync_WithValidData_ReturnsProcessedContent()
    {
        // Arrange
        var templateContent = @"# {{DocumentType}} for {{ProjectName}}
## Created by {{Author}}
### Date: {{Date}}

{{Content}}";
        
        var data = new Dictionary<string, object>
        {
            ["DocumentType"] = "Business Requirements Document",
            ["ProjectName"] = "ByteForge",
            ["Author"] = "Test User",
            ["Date"] = "2025-01-24",
            ["Content"] = "This is the main content."
        };

        // Act
        var result = await _service.ProcessTemplateAsync(templateContent, data);

        // Assert
        result.Should().Contain("Business Requirements Document");
        result.Should().Contain("ByteForge");
        result.Should().Contain("Test User");
        result.Should().Contain("2025-01-24");
        result.Should().Contain("This is the main content.");
        result.Should().NotContain("{{");
        result.Should().NotContain("}}");
    }

    [Fact]
    public async Task ProcessTemplateAsync_WithMissingData_LeavesPlaceholders()
    {
        // Arrange
        var templateContent = "Project: {{ProjectName}}, Status: {{Status}}";
        var data = new Dictionary<string, object>
        {
            ["ProjectName"] = "ByteForge"
            // Status is missing
        };

        // Act
        var result = await _service.ProcessTemplateAsync(templateContent, data);

        // Assert
        result.Should().Contain("ByteForge");
        result.Should().Contain("{{Status}}"); // Placeholder should remain
    }

    [Fact]
    public async Task ProcessTemplateAsync_WithComplexData_HandlesNestedProperties()
    {
        // Arrange
        var templateContent = @"{{#each Requirements}}
- {{Name}}: {{Description}}
{{/each}}";
        
        var data = new Dictionary<string, object>
        {
            ["Requirements"] = new[]
            {
                new { Name = "REQ-001", Description = "User authentication" },
                new { Name = "REQ-002", Description = "Data validation" }
            }
        };

        // Act
        var result = await _service.ProcessTemplateAsync(templateContent, data);

        // Assert
        result.Should().Contain("REQ-001: User authentication");
        result.Should().Contain("REQ-002: Data validation");
    }

    private IFileInfo CreateMockFileInfo(string fileName)
    {
        var mockFileInfo = new Mock<IFileInfo>();
        mockFileInfo.Setup(x => x.Name).Returns(fileName);
        mockFileInfo.Setup(x => x.IsDirectory).Returns(false);
        return mockFileInfo.Object;
    }
}