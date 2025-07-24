using Microsoft.EntityFrameworkCore;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Extensions;
using Hangfire;
using Microsoft.AspNetCore.Identity;
using ByteForgeFrontend.Models;

using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services;

public class DatabaseInitializationService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<DatabaseInitializationService> _logger;

    public DatabaseInitializationService(IServiceProvider serviceProvider, ILogger<DatabaseInitializationService> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    public async Task InitializeAsync()
    {
        using var scope = _serviceProvider.CreateScope();
        var services = scope.ServiceProvider;

        try
        {
            // Step 1: Initialize Entity Framework database
            _logger.LogInformation("Initializing Entity Framework database...");
            await InitializeEntityFrameworkAsync(services);

            // Step 2: Initialize Hangfire schema
            _logger.LogInformation("Initializing Hangfire schema...");
            await InitializeHangfireAsync(services);

            // Step 3: Seed initial data
            _logger.LogInformation("Seeding initial data...");
            await SeedDataAsync(services);

            _logger.LogInformation("Database initialization completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Database initialization failed");
            throw;
        }
    }

    private async Task InitializeEntityFrameworkAsync(IServiceProvider services)
    {
        var context = services.GetRequiredService<ApplicationDbContext>();
        
        // For SQLite, use EnsureCreated instead of migrations to avoid schema issues
        await context.Database.EnsureCreatedAsync();
        _logger.LogInformation("Database created/verified successfully using EnsureCreated");
    }

    private async Task InitializeHangfireAsync(IServiceProvider services)
    {
        var configuration = services.GetRequiredService<IConfiguration>();
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        
        // Force Hangfire to create its schema for SQLite
        var maxRetries = 5;
        var retryDelay = TimeSpan.FromSeconds(2);
        
        for (int i = 0; i < maxRetries; i++)
        {
            try
            {
                // Test database connectivity first
                using var connection = new Microsoft.Data.Sqlite.SqliteConnection(connectionString);
                await connection.OpenAsync();
                connection.Close();
                
                // Create Hangfire SQLite storage instance to force schema creation
                var storage = new Hangfire.Storage.SQLite.SQLiteStorage(connectionString);
                
                // Force initialization by getting a connection
                using var storageConnection = storage.GetConnection();
                
                // Simple test to ensure schema is ready (try with a numeric job ID)
                try 
                {
                    _ = storageConnection.GetStateData("999999");
                }
                catch (ArgumentException)
                {
                    // Job doesn't exist - this is expected and means schema is working
                }
                
                _logger.LogInformation("Hangfire SQLite schema initialized successfully");
                break;
            }
            catch (Exception ex) when (i < maxRetries - 1)
            {
                _logger.LogWarning(ex, "Hangfire initialization attempt {Attempt} failed, retrying in {Delay}ms", i + 1, retryDelay.TotalMilliseconds);
                await Task.Delay(retryDelay);
            }
        }
    }

    private async Task SeedDataAsync(IServiceProvider services)
    {
        var context = services.GetRequiredService<ApplicationDbContext>();
        var userManager = services.GetRequiredService<UserManager<ApplicationUser>>();
        var logger = services.GetRequiredService<ILogger<DatabaseInitializationService>>();
        
        await DbSeeder.SeedAsync(context, userManager, logger);
    }
}