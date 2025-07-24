using Xunit;
using FluentAssertions;
using Moq;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Data;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.ProjectManagement;

public class ProjectServiceTests : IDisposable
{
    private readonly ApplicationDbContext _context;
    private readonly Mock<ILogger<ProjectService>> _mockLogger;
    private readonly ProjectService _service;

    public ProjectServiceTests()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;

        _context = new ApplicationDbContext(options);
        _mockLogger = new Mock<ILogger<ProjectService>>();
        _service = new ProjectService(_context, _mockLogger.Object);
    }

    [Fact]
    public async Task CreateProjectAsync_WithValidData_CreatesProject()
    {
        // Arrange
        var request = new CreateProjectRequest
        {
            Name = "Test Project",
            Description = "A test project description",
            TemplateId = "CRM",
            ClientRequirements = "Client wants a CRM system"
        };

        // Act
        var project = await _service.CreateProjectAsync(request);

        // Assert
        project.Should().NotBeNull();
        project.Id.Should().NotBeEmpty();
        project.Name.Should().Be("Test Project");
        project.Description.Should().Be("A test project description");
        project.TemplateId.Should().Be("CRM");
        project.Status.Should().Be(ProjectStatus.Created);
        project.CreatedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));

        // Verify database
        var savedProject = await _context.Projects.FindAsync(project.Id);
        savedProject.Should().NotBeNull();
        savedProject!.Name.Should().Be("Test Project");
    }

    [Fact]
    public async Task CreateProjectAsync_WithDuplicateName_ThrowsException()
    {
        // Arrange
        var existingProject = new Project
        {
            Id = Guid.NewGuid(),
            Name = "Existing Project",
            Status = ProjectStatus.Created,
            CreatedAt = DateTime.UtcNow
        };
        await _context.Projects.AddAsync(existingProject);
        await _context.SaveChangesAsync();

        var request = new CreateProjectRequest
        {
            Name = "Existing Project",
            Description = "Another project with same name"
        };

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(
            () => _service.CreateProjectAsync(request));
    }

    [Fact]
    public async Task GetProjectAsync_WithExistingId_ReturnsProject()
    {
        // Arrange
        var project = new Project
        {
            Id = Guid.NewGuid(),
            Name = "Test Project",
            Status = ProjectStatus.InProgress,
            CreatedAt = DateTime.UtcNow
        };
        await _context.Projects.AddAsync(project);
        await _context.SaveChangesAsync();

        // Act
        var result = await _service.GetProjectAsync(project.Id);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(project.Id);
        result.Name.Should().Be("Test Project");
        result.Status.Should().Be(ProjectStatus.InProgress);
    }

    [Fact]
    public async Task GetProjectAsync_WithNonExistentId_ReturnsNull()
    {
        // Act
        var result = await _service.GetProjectAsync(Guid.NewGuid());

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetProjectsAsync_ReturnsAllProjects()
    {
        // Arrange
        var projects = new[]
        {
            new Project { Id = Guid.NewGuid(), Name = "Project 1", Status = ProjectStatus.Created, CreatedAt = DateTime.UtcNow.AddDays(-2) },
            new Project { Id = Guid.NewGuid(), Name = "Project 2", Status = ProjectStatus.InProgress, CreatedAt = DateTime.UtcNow.AddDays(-1) },
            new Project { Id = Guid.NewGuid(), Name = "Project 3", Status = ProjectStatus.Completed, CreatedAt = DateTime.UtcNow }
        };
        await _context.Projects.AddRangeAsync(projects);
        await _context.SaveChangesAsync();

        // Act
        var result = await _service.GetProjectsAsync();

        // Assert
        result.Should().HaveCount(3);
        result.Should().BeInDescendingOrder(p => p.CreatedAt);
    }

    [Fact]
    public async Task GetProjectsAsync_WithStatusFilter_ReturnsFilteredProjects()
    {
        // Arrange
        var projects = new[]
        {
            new Project { Id = Guid.NewGuid(), Name = "Project 1", Status = ProjectStatus.Created, CreatedAt = DateTime.UtcNow },
            new Project { Id = Guid.NewGuid(), Name = "Project 2", Status = ProjectStatus.InProgress, CreatedAt = DateTime.UtcNow },
            new Project { Id = Guid.NewGuid(), Name = "Project 3", Status = ProjectStatus.Completed, CreatedAt = DateTime.UtcNow }
        };
        await _context.Projects.AddRangeAsync(projects);
        await _context.SaveChangesAsync();

        // Act
        var result = await _service.GetProjectsAsync(status: ProjectStatus.InProgress);

        // Assert
        result.Should().HaveCount(1);
        result.First().Name.Should().Be("Project 2");
    }

    [Fact]
    public async Task UpdateProjectStatusAsync_WithValidProject_UpdatesStatus()
    {
        // Arrange
        var project = new Project
        {
            Id = Guid.NewGuid(),
            Name = "Test Project",
            Status = ProjectStatus.Created,
            CreatedAt = DateTime.UtcNow
        };
        await _context.Projects.AddAsync(project);
        await _context.SaveChangesAsync();

        // Act
        var result = await _service.UpdateProjectStatusAsync(project.Id, ProjectStatus.InProgress);

        // Assert
        result.Should().NotBeNull();
        result!.Status.Should().Be(ProjectStatus.InProgress);
        result.UpdatedAt.Should().NotBeNull();
        result.UpdatedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));

        // Verify database
        var updatedProject = await _context.Projects.FindAsync(project.Id);
        updatedProject!.Status.Should().Be(ProjectStatus.InProgress);
    }

    [Fact]
    public async Task DeleteProjectAsync_WithExistingProject_DeletesProject()
    {
        // Arrange
        var project = new Project
        {
            Id = Guid.NewGuid(),
            Name = "Test Project",
            Status = ProjectStatus.Created,
            CreatedAt = DateTime.UtcNow
        };
        await _context.Projects.AddAsync(project);
        await _context.SaveChangesAsync();

        // Act
        var result = await _service.DeleteProjectAsync(project.Id);

        // Assert
        result.Should().BeTrue();

        // Verify database
        var deletedProject = await _context.Projects.FindAsync(project.Id);
        deletedProject.Should().BeNull();
    }

    [Fact]
    public async Task AddDocumentToProjectAsync_AddsDocument()
    {
        // Arrange
        var project = new Project
        {
            Id = Guid.NewGuid(),
            Name = "Test Project",
            Status = ProjectStatus.Created,
            CreatedAt = DateTime.UtcNow,
            Documents = new List<ProjectDocument>()
        };
        await _context.Projects.AddAsync(project);
        await _context.SaveChangesAsync();

        var documentRequest = new AddDocumentRequest
        {
            ProjectId = project.Id,
            DocumentType = "BRD",
            Content = "# Business Requirements Document",
            Version = "1.0.0"
        };

        // Act
        var document = await _service.AddDocumentToProjectAsync(documentRequest);

        // Assert
        document.Should().NotBeNull();
        document.Id.Should().NotBeEmpty();
        document.ProjectId.Should().Be(project.Id);
        document.DocumentType.Should().Be("BRD");
        document.Content.Should().Be("# Business Requirements Document");
        document.Version.Should().Be("1.0.0");

        // Verify database
        var updatedProject = await _context.Projects
            .Include(p => p.Documents)
            .FirstAsync(p => p.Id == project.Id);
        updatedProject.Documents.Should().HaveCount(1);
    }

    [Fact]
    public async Task GetProjectDocumentsAsync_ReturnsAllDocuments()
    {
        // Arrange
        var project = new Project
        {
            Id = Guid.NewGuid(),
            Name = "Test Project",
            Status = ProjectStatus.Created,
            CreatedAt = DateTime.UtcNow,
            Documents = new List<ProjectDocument>
            {
                new ProjectDocument { Id = Guid.NewGuid(), DocumentType = "BRD", Content = "BRD Content", Version = "1.0", CreatedAt = DateTime.UtcNow.AddHours(-2) },
                new ProjectDocument { Id = Guid.NewGuid(), DocumentType = "PRD", Content = "PRD Content", Version = "1.0", CreatedAt = DateTime.UtcNow.AddHours(-1) },
                new ProjectDocument { Id = Guid.NewGuid(), DocumentType = "FRD", Content = "FRD Content", Version = "1.0", CreatedAt = DateTime.UtcNow }
            }
        };
        await _context.Projects.AddAsync(project);
        await _context.SaveChangesAsync();

        // Act
        var documents = await _service.GetProjectDocumentsAsync(project.Id);

        // Assert
        documents.Should().HaveCount(3);
        documents.Should().BeInDescendingOrder(d => d.CreatedAt);
        documents.Select(d => d.DocumentType).Should().BeEquivalentTo(new[] { "FRD", "PRD", "BRD" });
    }

    public void Dispose()
    {
        _context.Dispose();
    }
}