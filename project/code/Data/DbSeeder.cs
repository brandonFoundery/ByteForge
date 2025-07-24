using Microsoft.AspNetCore.Identity;
using ByteForgeFrontend.Models;
using Microsoft.EntityFrameworkCore;

using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Data;

public static class DbSeeder
{
    public static async Task SeedAsync(ApplicationDbContext context, UserManager<ApplicationUser> userManager, ILogger logger)
    {
        logger.LogInformation("Starting database seeding");

        try
        {
            // Seed Users
            await SeedUsersAsync(userManager, logger);
            
            // Seed Leads
            await SeedLeadsAsync(context, logger);
            
            // Seed NPPES Filter Configurations
            await SeedNppesFilterConfigurationsAsync(context, logger);
            
            // Seed NPPES Temp Data
            await SeedNppesTempDataAsync(context, logger);
            
            logger.LogInformation("Database seeding completed successfully");
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "An error occurred while seeding the database");
            throw;
        }
    }

    private static async Task SeedUsersAsync(UserManager<ApplicationUser> userManager, ILogger logger)
    {
        // Create admin user
        var adminEmail = "admin@leadprocessing.com";
        if (await userManager.FindByEmailAsync(adminEmail) == null)
        {
            var adminUser = new ApplicationUser
            {
                UserName = adminEmail,
                Email = adminEmail,
                FirstName = "Admin",
                LastName = "User",
                EmailConfirmed = true
            };

            var result = await userManager.CreateAsync(adminUser, "Admin123!");
            if (result.Succeeded)
            {
                logger.LogInformation("Admin user created successfully");
            }
            else
            {
                logger.LogWarning("Failed to create admin user: {Errors}", string.Join(", ", result.Errors.Select(e => e.Description)));
            }
        }

        // Create test user
        var testEmail = "test@leadprocessing.com";
        if (await userManager.FindByEmailAsync(testEmail) == null)
        {
            var testUser = new ApplicationUser
            {
                UserName = testEmail,
                Email = testEmail,
                FirstName = "Test",
                LastName = "User",
                EmailConfirmed = true
            };

            var result = await userManager.CreateAsync(testUser, "Test123!");
            if (result.Succeeded)
            {
                logger.LogInformation("Test user created successfully");
            }
            else
            {
                logger.LogWarning("Failed to create test user: {Errors}", string.Join(", ", result.Errors.Select(e => e.Description)));
            }
        }
    }

    private static async Task SeedLeadsAsync(ApplicationDbContext context, ILogger logger)
    {
        logger.LogInformation("Checking if leads exist in database...");
        var existingLeadCount = context.Leads.Count();
        logger.LogInformation("Found {ExistingCount} existing leads", existingLeadCount);
        
        if (context.Leads.Any())
        {
            logger.LogInformation("Leads already exist, skipping seed");
            return;
        }

        var leads = new List<Lead>
        {
            // New leads from different sources
            new Lead
            {
                Email = "john.doe@techcorp.com",
                Name = "John Doe",
                Company = "Tech Corp",
                Phone = "555-0001",
                Source = "Google",
                Status = "New",
                CreatedDate = DateTime.UtcNow.AddHours(-2)
            },
            new Lead
            {
                Email = "jane.smith@innovate.com",
                Name = "Jane Smith",
                Company = "Innovate Solutions",
                Phone = "555-0002",
                Source = "Google",
                Status = "New",
                CreatedDate = DateTime.UtcNow.AddHours(-1)
            },
            new Lead
            {
                Email = "bob.wilson@startup.io",
                Name = "Bob Wilson",
                Source = "Superpages",
                Status = "New",
                CreatedDate = DateTime.UtcNow.AddMinutes(-30)
            },

            // Enriched leads
            new Lead
            {
                Email = "sarah.johnson@bigcorp.com",
                Name = "Sarah Johnson",
                Company = "Big Corp",
                Phone = "555-0003",
                Source = "Google",
                Status = "New",
                IsEnriched = true,
                ModifiedDate = DateTime.UtcNow.AddMinutes(-15),
                CreatedDate = DateTime.UtcNow.AddHours(-3)
            },

            // Vetted leads
            new Lead
            {
                Email = "mike.brown@enterprise.com",
                Name = "Mike Brown",
                Company = "Enterprise Solutions",
                Phone = "555-0004",
                Source = "Google",
                Status = "Vetted",
                IsEnriched = true,
                IsVetted = true,
                ModifiedDate = DateTime.UtcNow.AddMinutes(-10),
                CreatedDate = DateTime.UtcNow.AddHours(-4)
            },

            // Scored leads
            new Lead
            {
                Email = "lisa.davis@consulting.com",
                Name = "Lisa Davis",
                Company = "Davis Consulting",
                Phone = "555-0005",
                Source = "Google",
                Status = "Hot",
                IsEnriched = true,
                IsVetted = true,
                Score = 75,
                ModifiedDate = DateTime.UtcNow.AddMinutes(-5),
                CreatedDate = DateTime.UtcNow.AddHours(-5)
            },

            // Processed leads
            new Lead
            {
                Email = "david.miller@solutions.org",
                Name = "David Miller",
                Company = "Miller Solutions",
                Phone = "555-0006",
                Source = "Google",
                Status = "Processed",
                IsEnriched = true,
                IsVetted = true,
                IsUpsertedToZoho = true,
                Score = 65,
                ModifiedDate = DateTime.UtcNow.AddMinutes(-2),
                CreatedDate = DateTime.UtcNow.AddHours(-6)
            },

            // Failed leads
            new Lead
            {
                Email = "invalid-email",
                Name = "Invalid Lead",
                Source = "Google",
                Status = "Invalid",
                Notes = "Lead validation failed: Email format is invalid",
                ModifiedDate = DateTime.UtcNow.AddMinutes(-20),
                CreatedDate = DateTime.UtcNow.AddHours(-2)
            },

            // Cold leads
            new Lead
            {
                Email = "peter.parker@gmail.com",
                Name = "Peter Parker",
                Source = "Google",
                Status = "Cold",
                IsEnriched = true,
                IsVetted = true,
                Score = 15,
                ModifiedDate = DateTime.UtcNow.AddMinutes(-8),
                CreatedDate = DateTime.UtcNow.AddHours(-7)
            },

            // Warm leads
            new Lead
            {
                Email = "bruce.wayne@waynecorp.com",
                Name = "Bruce Wayne",
                Company = "Wayne Corp",
                Source = "Superpages",
                Status = "Warm",
                IsEnriched = true,
                IsVetted = true,
                Score = 45,
                ModifiedDate = DateTime.UtcNow.AddMinutes(-12),
                CreatedDate = DateTime.UtcNow.AddHours(-8)
            },

            // Lead with workflow instance
            new Lead
            {
                Email = "clark.kent@dailyplanet.com",
                Name = "Clark Kent",
                Company = "Daily Planet",
                Phone = "555-0007",
                Source = "Google",
                Status = "Processing",
                WorkflowInstanceId = Guid.NewGuid().ToString(),
                CreatedDate = DateTime.UtcNow.AddMinutes(-45)
            }
        };

        context.Leads.AddRange(leads);
        await context.SaveChangesAsync();
        
        logger.LogInformation("Seeded {LeadCount} leads", leads.Count);
    }

    private static async Task SeedNppesFilterConfigurationsAsync(ApplicationDbContext context, ILogger logger)
    {
        logger.LogInformation("Checking if NPPES filter configurations exist in database...");
        
        if (context.NppesFilterConfigurations.Any())
        {
            logger.LogInformation("NPPES filter configurations already exist, skipping seed");
            return;
        }

        var configurations = new List<NppesFilterConfiguration>
        {
            new NppesFilterConfiguration
            {
                ConfigurationName = "Default Active Configuration",
                Description = "Default configuration for processing NPPES data with basic filters",
                IsActive = true,
                IsDefault = true,
                FilterByState = true,
                AllowedStates = "CA,NY,TX,FL,IL", // Major states
                FilterBySpecialty = true,
                AllowedSpecialties = "Family Medicine,Internal Medicine,Pediatrics,Cardiology,Orthopedic Surgery",
                RequirePhoneNumber = true,
                MaxRecordsToProcess = 1000,
                CreatedBy = "System",
                CreatedDate = DateTime.UtcNow,
                Notes = "Default configuration created during database seeding"
            },
            new NppesFilterConfiguration
            {
                ConfigurationName = "Test Configuration",
                Description = "Test configuration for development and testing",
                IsActive = true,
                IsDefault = false,
                FilterByEntityType = true,
                AllowedEntityTypes = "1", // Individual providers only
                RequirePhoneNumber = true,
                MaxRecordsToProcess = 100,
                CreatedBy = "System",
                CreatedDate = DateTime.UtcNow,
                Notes = "Test configuration for development purposes"
            }
        };

        context.NppesFilterConfigurations.AddRange(configurations);
        await context.SaveChangesAsync();
        
        logger.LogInformation("Seeded {ConfigCount} NPPES filter configurations", configurations.Count);
    }

    private static async Task SeedNppesTempDataAsync(ApplicationDbContext context, ILogger logger)
    {
        logger.LogInformation("Checking if NPPES temp data exists in database...");
        
        if (context.NppesProviderTemp.Any())
        {
            logger.LogInformation("NPPES temp data already exists, skipping seed");
            return;
        }

        var tempProviders = new List<NppesProviderTemp>
        {
            new NppesProviderTemp
            {
                NPI = "1234567890",
                EntityTypeCode = "1", // Individual
                ProviderFirstName = "John",
                ProviderLastName = "Smith",
                ProviderOrganizationName = null,
                ProviderBusinessPracticeLocationAddressStateName = "CA",
                ProviderBusinessPracticeLocationAddressCityName = "Los Angeles",
                ProviderBusinessPracticeLocationAddressPostalCode = "90210",
                ProviderBusinessPracticeLocationAddressTelephoneNumber = "555-0001",
                ProviderTaxonomyCode1 = "207Q00000X", // Family Medicine
                ProviderGenderCode = "M",
                ProviderEnumerationDate = new DateTime(2020, 1, 15),
                ImportedDate = DateTime.UtcNow,
                IsProcessed = false,
                ComputedFullName = "John Smith",
                ComputedBusinessAddress = "123 Main St, Los Angeles, CA 90210"
            },
            new NppesProviderTemp
            {
                NPI = "2345678901",
                EntityTypeCode = "1", // Individual
                ProviderFirstName = "Sarah",
                ProviderLastName = "Johnson",
                ProviderOrganizationName = null,
                ProviderBusinessPracticeLocationAddressStateName = "NY",
                ProviderBusinessPracticeLocationAddressCityName = "New York",
                ProviderBusinessPracticeLocationAddressPostalCode = "10001",
                ProviderBusinessPracticeLocationAddressTelephoneNumber = "555-0002",
                ProviderTaxonomyCode1 = "207R00000X", // Internal Medicine
                ProviderGenderCode = "F",
                ProviderEnumerationDate = new DateTime(2021, 3, 20),
                ImportedDate = DateTime.UtcNow,
                IsProcessed = false,
                ComputedFullName = "Sarah Johnson",
                ComputedBusinessAddress = "456 Broadway, New York, NY 10001"
            },
            new NppesProviderTemp
            {
                NPI = "3456789012",
                EntityTypeCode = "1", // Individual
                ProviderFirstName = "Michael",
                ProviderLastName = "Davis",
                ProviderOrganizationName = null,
                ProviderBusinessPracticeLocationAddressStateName = "TX",
                ProviderBusinessPracticeLocationAddressCityName = "Houston",
                ProviderBusinessPracticeLocationAddressPostalCode = "77001",
                ProviderBusinessPracticeLocationAddressTelephoneNumber = "555-0003",
                ProviderTaxonomyCode1 = "208000000X", // Pediatrics
                ProviderGenderCode = "M",
                ProviderEnumerationDate = new DateTime(2019, 11, 10),
                ImportedDate = DateTime.UtcNow,
                IsProcessed = false,
                ComputedFullName = "Michael Davis",
                ComputedBusinessAddress = "789 Medical Center Dr, Houston, TX 77001"
            },
            new NppesProviderTemp
            {
                NPI = "4567890123",
                EntityTypeCode = "2", // Organization
                ProviderFirstName = null,
                ProviderLastName = null,
                ProviderOrganizationName = "Heart Care Medical Group",
                ProviderBusinessPracticeLocationAddressStateName = "FL",
                ProviderBusinessPracticeLocationAddressCityName = "Miami",
                ProviderBusinessPracticeLocationAddressPostalCode = "33101",
                ProviderBusinessPracticeLocationAddressTelephoneNumber = "555-0004",
                ProviderTaxonomyCode1 = "207RC0000X", // Cardiology
                ProviderGenderCode = null,
                ProviderEnumerationDate = new DateTime(2018, 5, 25),
                ImportedDate = DateTime.UtcNow,
                IsProcessed = false,
                ComputedFullName = "Heart Care Medical Group",
                ComputedBusinessAddress = "321 Heart Ave, Miami, FL 33101"
            },
            new NppesProviderTemp
            {
                NPI = "5678901234",
                EntityTypeCode = "1", // Individual
                ProviderFirstName = "Emily",
                ProviderLastName = "Wilson",
                ProviderOrganizationName = null,
                ProviderBusinessPracticeLocationAddressStateName = "IL",
                ProviderBusinessPracticeLocationAddressCityName = "Chicago",
                ProviderBusinessPracticeLocationAddressPostalCode = "60601",
                ProviderBusinessPracticeLocationAddressTelephoneNumber = "555-0005",
                ProviderTaxonomyCode1 = "207X00000X", // Orthopedic Surgery
                ProviderGenderCode = "F",
                ProviderEnumerationDate = new DateTime(2022, 2, 14),
                ImportedDate = DateTime.UtcNow,
                IsProcessed = false,
                ComputedFullName = "Emily Wilson",
                ComputedBusinessAddress = "654 Surgery Blvd, Chicago, IL 60601"
            }
        };

        context.NppesProviderTemp.AddRange(tempProviders);
        await context.SaveChangesAsync();
        
        logger.LogInformation("Seeded {ProviderCount} NPPES temp providers", tempProviders.Count);
    }
}