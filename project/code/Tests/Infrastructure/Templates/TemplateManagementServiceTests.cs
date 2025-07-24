using Xunit;
using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Moq;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.Templates;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.Templates;

public class TemplateManagementServiceTests : IDisposable
{
    private readonly ApplicationDbContext _context;
    private readonly Mock<ILogger<TemplateManagementService>> _loggerMock;
    private readonly TemplateManagementService _service;

    public TemplateManagementServiceTests()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: $"TestDb_{Guid.NewGuid()}")
            .Options;
        _context = new ApplicationDbContext(options);
        _loggerMock = new Mock<ILogger<TemplateManagementService>>();
        _service = new TemplateManagementService(_context, _loggerMock.Object);
    }

    public void Dispose()
    {
        _context.Dispose();
    }

    #region Create Template Tests

    [Fact]
    public async Task CreateTemplateAsync_ValidTemplate_ReturnsCreatedTemplate()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "crm-template",
            Name = "CRM Template",
            Description = "Customer Relationship Management template",
            Category = "Business",
            Version = "1.0.0",
            RequiredDocuments = new[] { "BRD", "PRD", "FRD", "TRD" },
            OptionalDocuments = new[] { "UX_SPEC", "TEST_PLAN" },
            DefaultSettings = new Dictionary<string, object>
            {
                { "multiTenant", true },
                { "authProvider", "JWT" },
                { "database", "SQL Server" }
            }
        };

        // Act
        var result = await _service.CreateTemplateAsync(template);

        // Assert
        result.Should().NotBeNull();
        result.Id.Should().Be(template.Id);
        result.Name.Should().Be(template.Name);
        result.CreatedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(1));

        var savedTemplate = await _context.ProjectTemplates.FindAsync(template.Id);
        savedTemplate.Should().NotBeNull();
    }

    [Fact]
    public async Task CreateTemplateAsync_DuplicateId_ThrowsException()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "duplicate-id",
            Name = "Template 1",
            Category = "Test"
        };

        await _service.CreateTemplateAsync(template);

        var duplicateTemplate = new ProjectTemplate
        {
            Id = "duplicate-id",
            Name = "Template 2",
            Category = "Test"
        };

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(
            () => _service.CreateTemplateAsync(duplicateTemplate));
    }

    [Fact]
    public async Task CreateTemplateAsync_InvalidTemplate_ThrowsException()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "", // Invalid empty ID
            Name = "Invalid Template",
            Category = "Test"
        };

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(
            () => _service.CreateTemplateAsync(template));
    }

    #endregion

    #region Update Template Tests

    [Fact]
    public async Task UpdateTemplateAsync_ExistingTemplate_UpdatesSuccessfully()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "update-test",
            Name = "Original Name",
            Category = "Test",
            Version = "1.0.0"
        };

        await _service.CreateTemplateAsync(template);

        template.Name = "Updated Name";
        template.Version = "1.1.0";
        template.Description = "Updated description";

        // Act
        var result = await _service.UpdateTemplateAsync(template);

        // Assert
        result.Should().NotBeNull();
        result.Name.Should().Be("Updated Name");
        result.Version.Should().Be("1.1.0");
        result.UpdatedAt.Should().NotBeNull();
        result.UpdatedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public async Task UpdateTemplateAsync_NonExistentTemplate_ThrowsException()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "non-existent",
            Name = "Template",
            Category = "Test"
        };

        // Act & Assert
        await Assert.ThrowsAsync<KeyNotFoundException>(
            () => _service.UpdateTemplateAsync(template));
    }

    #endregion

    #region Delete Template Tests

    [Fact]
    public async Task DeleteTemplateAsync_ExistingTemplate_DeletesSuccessfully()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "delete-test",
            Name = "Template to Delete",
            Category = "Test"
        };

        await _service.CreateTemplateAsync(template);

        // Act
        var result = await _service.DeleteTemplateAsync(template.Id);

        // Assert
        result.Should().BeTrue();

        var deletedTemplate = await _context.ProjectTemplates.FindAsync(template.Id);
        deletedTemplate.Should().BeNull();
    }

    [Fact]
    public async Task DeleteTemplateAsync_NonExistentTemplate_ReturnsFalse()
    {
        // Act
        var result = await _service.DeleteTemplateAsync("non-existent");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task DeleteTemplateAsync_TemplateInUse_ThrowsException()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "in-use-template",
            Name = "Template In Use",
            Category = "Test"
        };

        await _service.CreateTemplateAsync(template);

        // Create a project using this template
        var project = new Project
        {
            Id = Guid.NewGuid(),
            Name = "Test Project",
            TemplateId = template.Id,
            ClientName = "Test Client"
        };

        _context.Projects.Add(project);
        await _context.SaveChangesAsync();

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(
            () => _service.DeleteTemplateAsync(template.Id));
    }

    #endregion

    #region Retrieve Template Tests

    [Fact]
    public async Task GetTemplateAsync_ExistingTemplate_ReturnsTemplate()
    {
        // Arrange
        var template = new ProjectTemplate
        {
            Id = "get-test",
            Name = "Template to Get",
            Category = "Test"
        };

        await _service.CreateTemplateAsync(template);

        // Act
        var result = await _service.GetTemplateAsync(template.Id);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(template.Id);
        result.Name.Should().Be(template.Name);
    }

    [Fact]
    public async Task GetTemplateAsync_NonExistentTemplate_ReturnsNull()
    {
        // Act
        var result = await _service.GetTemplateAsync("non-existent");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetAllTemplatesAsync_ReturnsAllActiveTemplates()
    {
        // Arrange
        var templates = new[]
        {
            new ProjectTemplate { Id = "template1", Name = "Template 1", Category = "Test", IsActive = true },
            new ProjectTemplate { Id = "template2", Name = "Template 2", Category = "Test", IsActive = true },
            new ProjectTemplate { Id = "template3", Name = "Template 3", Category = "Test", IsActive = false }
        };

        foreach (var template in templates)
        {
            await _service.CreateTemplateAsync(template);
        }

        // Act
        var result = await _service.GetAllTemplatesAsync();

        // Assert
        result.Should().HaveCount(2);
        result.Should().AllSatisfy(t => t.IsActive.Should().BeTrue());
    }

    [Fact]
    public async Task GetTemplatesByCategoryAsync_ReturnsFilteredTemplates()
    {
        // Arrange
        var templates = new[]
        {
            new ProjectTemplate { Id = "crm1", Name = "CRM 1", Category = "Business" },
            new ProjectTemplate { Id = "crm2", Name = "CRM 2", Category = "Business" },
            new ProjectTemplate { Id = "ecom1", Name = "E-commerce 1", Category = "E-commerce" }
        };

        foreach (var template in templates)
        {
            await _service.CreateTemplateAsync(template);
        }

        // Act
        var result = await _service.GetTemplatesByCategoryAsync("Business");

        // Assert
        result.Should().HaveCount(2);
        result.Should().AllSatisfy(t => t.Category.Should().Be("Business"));
    }

    #endregion
}