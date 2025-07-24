using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Models.ProjectManagement;

using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.TestHelpers;

public static class TestDatabaseHelper
{
    public static ApplicationDbContext CreateTestDatabase(string? databaseName = null)
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: databaseName ?? Guid.NewGuid().ToString())
            .Options;

        var context = new ApplicationDbContext(options);
        context.Database.EnsureCreated();
        return context;
    }

    public static async Task SeedTestDataAsync(ApplicationDbContext context)
    {
        // Add test projects
        var projects = new[]
        {
            new Project
            {
                Id = Guid.Parse("11111111-1111-1111-1111-111111111111"),
                Name = "Test Project 1",
                Description = "First test project",
                Status = ProjectStatus.InProgress,
                TemplateId = "CRM",
                CreatedAt = DateTime.UtcNow.AddDays(-5),
                UpdatedAt = DateTime.UtcNow.AddDays(-1)
            },
            new Project
            {
                Id = Guid.Parse("22222222-2222-2222-2222-222222222222"),
                Name = "Test Project 2",
                Description = "Second test project",
                Status = ProjectStatus.Created,
                TemplateId = "ECommerce",
                CreatedAt = DateTime.UtcNow.AddDays(-3)
            }
        };

        await context.Projects.AddRangeAsync(projects);

        // Add test documents
        var documents = new[]
        {
            new ProjectDocument
            {
                Id = Guid.Parse("33333333-3333-3333-3333-333333333333"),
                ProjectId = projects[0].Id,
                DocumentType = "BRD",
                Content = "# Business Requirements Document\n\nTest content",
                Version = "1.0.0",
                CreatedAt = DateTime.UtcNow.AddDays(-4)
            },
            new ProjectDocument
            {
                Id = Guid.Parse("44444444-4444-4444-4444-444444444444"),
                ProjectId = projects[0].Id,
                DocumentType = "PRD",
                Content = "# Product Requirements Document\n\nTest content",
                Version = "1.0.0",
                CreatedAt = DateTime.UtcNow.AddDays(-3)
            }
        };

        await context.ProjectDocuments.AddRangeAsync(documents);
        await context.SaveChangesAsync();
    }

    public static IServiceProvider CreateServiceProvider(ApplicationDbContext? context = null)
    {
        var services = new ServiceCollection();

        if (context != null)
        {
            services.AddSingleton(context);
        }
        else
        {
            services.AddDbContext<ApplicationDbContext>(options =>
                options.UseInMemoryDatabase(Guid.NewGuid().ToString()));
        }

        // Add other test services as needed
        services.AddLogging();

        return services.BuildServiceProvider();
    }

    public static async Task CleanupDatabaseAsync(ApplicationDbContext context)
    {
        context.Projects.RemoveRange(context.Projects);
        context.ProjectDocuments.RemoveRange(context.ProjectDocuments);
        // Add cleanup for other entities as they are added
        
        await context.SaveChangesAsync();
    }
}