using Microsoft.Extensions.Logging;
using System.IO.Abstractions;
using System.Text;
using System.Text.Json;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using Scriban;

using System;
using System.Linq;
namespace ByteForgeFrontend.Services.Infrastructure.Templates;

public class TemplateGenerator : ITemplateGenerator
{
    private readonly IFileSystem _fileSystem;
    private readonly IDocumentTemplateService _documentTemplateService;
    private readonly ILogger<TemplateGenerator> _logger;

    public TemplateGenerator(
        IFileSystem fileSystem,
        IDocumentTemplateService documentTemplateService,
        ILogger<TemplateGenerator> logger)
    {
        _fileSystem = fileSystem;
        _documentTemplateService = documentTemplateService;
        _logger = logger;
    }

    public async Task<TemplateGenerationResult> GenerateCRMTemplateAsync(string outputPath, TemplateGenerationOptions options)
    {
        var result = new TemplateGenerationResult();

        try
        {
            // Validate output path
            if (!IsValidPath(outputPath))
            {
                result.Errors.Add($"Invalid output path: {outputPath}");
                return result;
            }

            // Check if directory exists
            if (_fileSystem.Directory.Exists(outputPath) && !options.OverwriteExisting)
            {
                result.Errors.Add($"Directory already exists: {outputPath}. Set OverwriteExisting to true to overwrite.");
                return result;
            }

            // Create directory structure
            CreateCRMDirectoryStructure(outputPath);
            result.GeneratedFiles.AddRange(new[]
            {
                _fileSystem.Path.Combine(outputPath, "src"),
                _fileSystem.Path.Combine(outputPath, "src", "Controllers"),
                _fileSystem.Path.Combine(outputPath, "src", "Services"),
                _fileSystem.Path.Combine(outputPath, "src", "Models"),
                _fileSystem.Path.Combine(outputPath, "tests"),
                _fileSystem.Path.Combine(outputPath, "docs")
            });

            // Generate configuration files
            await GenerateCRMConfigurationFiles(outputPath, options);
            result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, "appsettings.json"));
            result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, ".gitignore"));
            result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, "README.md"));

            // Generate source code files
            await GenerateCRMSourceFiles(outputPath, options);

            // Generate documentation
            await GenerateCRMDocumentation(outputPath, options);

            // Generate sample data if requested
            if (options.IncludeSampleData)
            {
                await GenerateCRMSampleData(outputPath);
                result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, "data", "sample-customers.json"));
                result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, "data", "sample-contacts.json"));
                result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, "data", "sample-opportunities.json"));
            }

            result.Success = true;
            result.Metadata["templateType"] = "CRM";
            result.Metadata["projectName"] = options.ProjectName;
            result.Metadata["generatedAt"] = DateTime.UtcNow;

            _logger.LogInformation("Successfully generated CRM template at {OutputPath}", outputPath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating CRM template");
            result.Errors.Add($"Error generating template: {ex.Message}");
        }

        return result;
    }

    public async Task<TemplateGenerationResult> GenerateEcommerceTemplateAsync(string outputPath, TemplateGenerationOptions options)
    {
        var result = new TemplateGenerationResult();

        try
        {
            // Validate output path
            if (!IsValidPath(outputPath))
            {
                result.Errors.Add($"Invalid output path: {outputPath}");
                return result;
            }

            // Check if directory exists
            if (_fileSystem.Directory.Exists(outputPath) && !options.OverwriteExisting)
            {
                result.Errors.Add($"Directory already exists: {outputPath}. Set OverwriteExisting to true to overwrite.");
                return result;
            }

            // Create directory structure
            CreateEcommerceDirectoryStructure(outputPath);

            // Generate configuration files
            await GenerateEcommerceConfigurationFiles(outputPath, options);

            // Generate payment provider services
            foreach (var provider in options.PaymentProviders)
            {
                await GeneratePaymentProviderService(outputPath, provider);
                result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, "src", "Services", "Payment", $"{provider}PaymentService.cs"));
            }

            // Generate shipping provider services
            foreach (var provider in options.ShippingProviders)
            {
                await GenerateShippingProviderService(outputPath, provider);
                result.GeneratedFiles.Add(_fileSystem.Path.Combine(outputPath, "src", "Services", "Shipping", $"{provider}ShippingService.cs"));
            }

            // Generate sample data if requested
            if (options.IncludeSampleData)
            {
                await GenerateEcommerceSampleData(outputPath);
            }

            result.Success = true;
            result.Metadata["templateType"] = "E-commerce";
            result.Metadata["projectName"] = options.ProjectName;
            result.Metadata["paymentProviders"] = options.PaymentProviders;
            result.Metadata["shippingProviders"] = options.ShippingProviders;

            _logger.LogInformation("Successfully generated E-commerce template at {OutputPath}", outputPath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating E-commerce template");
            result.Errors.Add($"Error generating template: {ex.Message}");
        }

        return result;
    }

    public async Task<TemplateGenerationResult> GenerateCustomTemplateAsync(string outputPath, string templateId, TemplateGenerationOptions options)
    {
        // This would be implemented to generate templates based on a template ID from the database
        throw new NotImplementedException("Custom template generation will be implemented in a future phase");
    }

    public async Task<TemplateGenerationResult> CustomizeTemplateAsync(string templatePath, string outputPath, TemplateCustomization customization)
    {
        var result = new TemplateGenerationResult();

        try
        {
            if (!_fileSystem.Directory.Exists(templatePath))
            {
                result.Errors.Add($"Template path does not exist: {templatePath}");
                return result;
            }

            // Create output directory
            _fileSystem.Directory.CreateDirectory(outputPath);

            // Process all files in template
            await ProcessTemplateFiles(templatePath, outputPath, customization, result);

            // Add additional files
            foreach (var (filename, content) in customization.AdditionalFiles)
            {
                var filePath = _fileSystem.Path.Combine(outputPath, filename);
                await _fileSystem.File.WriteAllTextAsync(filePath, content);
                result.GeneratedFiles.Add(filePath);
            }

            result.Success = true;
            _logger.LogInformation("Successfully customized template from {TemplatePath} to {OutputPath}", templatePath, outputPath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error customizing template");
            result.Errors.Add($"Error customizing template: {ex.Message}");
        }

        return result;
    }

    public async Task<TemplateGenerationResult> MergeTemplatesAsync(string[] templatePaths, string outputPath, TemplateMergeOptions options)
    {
        // This would be implemented to merge multiple templates
        throw new NotImplementedException("Template merging will be implemented in a future phase");
    }

    public async Task<TemplateGenerationResult> ApplyTemplateToProjectAsync(string projectPath, string templateId, TemplateApplicationOptions options)
    {
        // This would be implemented to apply a template to an existing project
        throw new NotImplementedException("Template application will be implemented in a future phase");
    }

    public async Task<TemplateGenerationResult> UpdateProjectFromTemplateAsync(string projectPath, string templateId, string fromVersion, string toVersion)
    {
        // This would be implemented to update a project based on template version changes
        throw new NotImplementedException("Template update will be implemented in a future phase");
    }

    private void CreateCRMDirectoryStructure(string outputPath)
    {
        var directories = new[]
        {
            "src",
            "src/Controllers",
            "src/Controllers/Api",
            "src/Services",
            "src/Services/Customer",
            "src/Services/Contact",
            "src/Services/Opportunity",
            "src/Models",
            "src/Models/Customer",
            "src/Models/Contact",
            "src/Models/Opportunity",
            "src/Data",
            "src/Data/Repositories",
            "tests",
            "tests/Unit",
            "tests/Integration",
            "docs",
            "docs/requirements",
            "docs/api",
            "data"
        };

        foreach (var dir in directories)
        {
            _fileSystem.Directory.CreateDirectory(_fileSystem.Path.Combine(outputPath, dir));
        }
    }

    private void CreateEcommerceDirectoryStructure(string outputPath)
    {
        var directories = new[]
        {
            "src",
            "src/Controllers",
            "src/Controllers/Api",
            "src/Services",
            "src/Services/Payment",
            "src/Services/Shipping",
            "src/Services/Inventory",
            "src/Services/Cart",
            "src/Models",
            "src/Models/Products",
            "src/Models/Orders",
            "src/Models/Cart",
            "src/Data",
            "tests",
            "docs",
            "data"
        };

        foreach (var dir in directories)
        {
            _fileSystem.Directory.CreateDirectory(_fileSystem.Path.Combine(outputPath, dir));
        }
    }

    private async Task GenerateCRMConfigurationFiles(string outputPath, TemplateGenerationOptions options)
    {
        // Generate appsettings.json
        var appSettings = new
        {
            ProjectName = options.ProjectName,
            MultiTenancy = options.MultiTenant,
            Authentication = new
            {
                Provider = options.AuthProvider,
                JwtSettings = options.AuthProvider == "JWT" ? new
                {
                    SecretKey = "YOUR_SECRET_KEY_HERE",
                    Issuer = options.ProjectName,
                    Audience = options.ProjectName,
                    ExpirationMinutes = 60
                } : null
            },
            Database = new
            {
                Provider = options.Database,
                ConnectionString = $"Server=localhost;Database={options.ProjectName}Db;Trusted_Connection=true;"
            },
            Logging = new
            {
                LogLevel = new
                {
                    Default = "Information",
                    Microsoft = "Warning",
                    System = "Warning"
                }
            }
        };

        var json = JsonSerializer.Serialize(appSettings, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(outputPath, "appsettings.json"), json);

        // Generate .gitignore
        var gitignore = @"
# Build results
bin/
obj/
out/

# User-specific files
*.user
*.userosscache
*.sln.docstates

# Visual Studio
.vs/
*.suo
*.ntvs*
*.njsproj
*.sln.ide

# .NET Core
project.lock.json
project.fragment.lock.json
artifacts/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
*.log
logs/

# OS files
.DS_Store
Thumbs.db
";
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(outputPath, ".gitignore"), gitignore);

        // Generate README.md
        var readme = $@"# {options.ProjectName}

A Customer Relationship Management (CRM) application built with modern technologies.

## Features

- Customer Management
- Contact Management
- Opportunity Tracking
- Activity Logging
- Reporting and Analytics
{(options.MultiTenant ? "- Multi-tenant Support" : "")}

## Technology Stack

- Backend: ASP.NET Core
- Database: {options.Database}
- Authentication: {options.AuthProvider}
- Frontend: React with TypeScript

## Getting Started

1. Clone the repository
2. Update the connection string in `appsettings.json`
3. Run database migrations
4. Start the application

## Documentation

See the `/docs` directory for detailed documentation.
";
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(outputPath, "README.md"), readme);
    }

    private async Task GenerateCRMSourceFiles(string outputPath, TemplateGenerationOptions options)
    {
        // Generate customer model
        var customerModel = @"using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace " + options.ProjectName + @".Models.Customer
{
    public class Customer
    {
        public Guid Id { get; set; }
        
        [Required]
        [MaxLength(200)]
        public string Name { get; set; } = string.Empty;
        
        [MaxLength(100)]
        public string? Industry { get; set; }
        
        [MaxLength(50)]
        public string? Size { get; set; }
        
        public decimal AnnualRevenue { get; set; }
        
        public DateTime CreatedAt { get; set; }
        
        public DateTime? UpdatedAt { get; set; }
        
        // Navigation properties
        public virtual ICollection<Contact> Contacts { get; set; } = new List<Contact>();
        public virtual ICollection<Opportunity> Opportunities { get; set; } = new List<Opportunity>();
    }
}";
        await _fileSystem.File.WriteAllTextAsync(
            _fileSystem.Path.Combine(outputPath, "src", "Models", "Customer", "Customer.cs"), 
            customerModel);

        // Generate customer service
        var customerService = @"using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using " + options.ProjectName + @".Models.Customer;

namespace " + options.ProjectName + @".Services.Customer
{
    public interface ICustomerService
    {
        Task<Customer> GetByIdAsync(Guid id);
        Task<IEnumerable<Customer>> GetAllAsync();
        Task<Customer> CreateAsync(Customer customer);
        Task<Customer> UpdateAsync(Customer customer);
        Task<bool> DeleteAsync(Guid id);
    }
    
    public class CustomerService : ICustomerService
    {
        // Implementation would go here
        public Task<Customer> GetByIdAsync(Guid id) => throw new NotImplementedException();
        public Task<IEnumerable<Customer>> GetAllAsync() => throw new NotImplementedException();
        public Task<Customer> CreateAsync(Customer customer) => throw new NotImplementedException();
        public Task<Customer> UpdateAsync(Customer customer) => throw new NotImplementedException();
        public Task<bool> DeleteAsync(Guid id) => throw new NotImplementedException();
    }
}";
        await _fileSystem.File.WriteAllTextAsync(
            _fileSystem.Path.Combine(outputPath, "src", "Services", "Customer", "CustomerService.cs"), 
            customerService);

        // Generate multi-tenancy middleware if enabled
        if (options.MultiTenant)
        {
            var tenantMiddleware = @"using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;

namespace " + options.ProjectName + @".Middleware
{
    public class TenantMiddleware
    {
        private readonly RequestDelegate _next;
        
        public TenantMiddleware(RequestDelegate next)
        {
            _next = next;
        }
        
        public async Task InvokeAsync(HttpContext context)
        {
            // Extract tenant from header, subdomain, or claim
            var tenantId = context.Request.Headers[""X-Tenant-Id""].ToString();
            
            if (!string.IsNullOrEmpty(tenantId))
            {
                context.Items[""TenantId""] = tenantId;
            }
            
            await _next(context);
        }
    }
}";
            await _fileSystem.File.WriteAllTextAsync(
                _fileSystem.Path.Combine(outputPath, "src", "Middleware", "TenantMiddleware.cs"), 
                tenantMiddleware);
        }
    }

    private async Task GenerateCRMDocumentation(string outputPath, TemplateGenerationOptions options)
    {
        var docsPath = _fileSystem.Path.Combine(outputPath, "docs", "requirements");

        // Generate BRD
        var brdContent = await _documentTemplateService.GenerateDocumentAsync("BRD", new Dictionary<string, object>
        {
            ["ProjectName"] = options.ProjectName,
            ["ProjectType"] = "CRM",
            ["MultiTenant"] = options.MultiTenant,
            ["Authentication"] = options.AuthProvider,
            ["Database"] = options.Database
        });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(docsPath, "BRD.md"), brdContent);

        // Generate PRD
        var prdContent = await _documentTemplateService.GenerateDocumentAsync("PRD", new Dictionary<string, object>
        {
            ["ProjectName"] = options.ProjectName,
            ["ProjectType"] = "CRM",
            ["Features"] = new[]
            {
                "Customer Management",
                "Contact Management",
                "Opportunity Tracking",
                "Activity Logging",
                "Reporting"
            }
        });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(docsPath, "PRD.md"), prdContent);

        // Generate FRD
        var frdContent = await _documentTemplateService.GenerateDocumentAsync("FRD", new Dictionary<string, object>
        {
            ["ProjectName"] = options.ProjectName,
            ["ProjectType"] = "CRM"
        });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(docsPath, "FRD.md"), frdContent);

        // Generate TRD
        var trdContent = await _documentTemplateService.GenerateDocumentAsync("TRD", new Dictionary<string, object>
        {
            ["ProjectName"] = options.ProjectName,
            ["ProjectType"] = "CRM",
            ["TechStack"] = new Dictionary<string, object>
            {
                ["Backend"] = "ASP.NET Core",
                ["Database"] = options.Database,
                ["Authentication"] = options.AuthProvider,
                ["Frontend"] = "React with TypeScript"
            }
        });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(docsPath, "TRD.md"), trdContent);
    }

    private async Task GenerateCRMSampleData(string outputPath)
    {
        var dataPath = _fileSystem.Path.Combine(outputPath, "data");
        _fileSystem.Directory.CreateDirectory(dataPath);

        // Sample customers
        var customers = new[]
        {
            new { Id = Guid.NewGuid(), Name = "Acme Corporation", Industry = "Technology", Size = "Enterprise", AnnualRevenue = 50000000 },
            new { Id = Guid.NewGuid(), Name = "Global Retail Inc", Industry = "Retail", Size = "Large", AnnualRevenue = 25000000 },
            new { Id = Guid.NewGuid(), Name = "StartUp Solutions", Industry = "Consulting", Size = "Small", AnnualRevenue = 1000000 }
        };
        
        var customersJson = JsonSerializer.Serialize(customers, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(dataPath, "sample-customers.json"), customersJson);

        // Sample contacts
        var contacts = new[]
        {
            new { Id = Guid.NewGuid(), CustomerId = customers[0].Id, FirstName = "John", LastName = "Doe", Email = "john.doe@acme.com", Phone = "+1-555-0100" },
            new { Id = Guid.NewGuid(), CustomerId = customers[0].Id, FirstName = "Jane", LastName = "Smith", Email = "jane.smith@acme.com", Phone = "+1-555-0101" },
            new { Id = Guid.NewGuid(), CustomerId = customers[1].Id, FirstName = "Bob", LastName = "Johnson", Email = "bob.johnson@globalretail.com", Phone = "+1-555-0200" }
        };
        
        var contactsJson = JsonSerializer.Serialize(contacts, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(dataPath, "sample-contacts.json"), contactsJson);

        // Sample opportunities
        var opportunities = new[]
        {
            new { Id = Guid.NewGuid(), CustomerId = customers[0].Id, Name = "Enterprise Software Deal", Value = 500000, Stage = "Negotiation", CloseDate = DateTime.UtcNow.AddMonths(2) },
            new { Id = Guid.NewGuid(), CustomerId = customers[1].Id, Name = "POS System Upgrade", Value = 150000, Stage = "Proposal", CloseDate = DateTime.UtcNow.AddMonths(1) },
            new { Id = Guid.NewGuid(), CustomerId = customers[2].Id, Name = "Consulting Services", Value = 50000, Stage = "Qualification", CloseDate = DateTime.UtcNow.AddMonths(3) }
        };
        
        var opportunitiesJson = JsonSerializer.Serialize(opportunities, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(dataPath, "sample-opportunities.json"), opportunitiesJson);
    }

    private async Task GenerateEcommerceConfigurationFiles(string outputPath, TemplateGenerationOptions options)
    {
        // Generate appsettings.json
        var appSettings = new
        {
            ProjectName = options.ProjectName,
            MultiTenancy = options.MultiTenant,
            Authentication = new
            {
                Provider = options.AuthProvider
            },
            Database = new
            {
                Provider = options.Database,
                ConnectionString = $"Server=localhost;Database={options.ProjectName}Db;Trusted_Connection=true;"
            },
            PaymentProviders = options.PaymentProviders.Select(p => new
            {
                Name = p,
                Enabled = true,
                Settings = new Dictionary<string, string>()
            }),
            ShippingProviders = options.ShippingProviders.Select(p => new
            {
                Name = p,
                Enabled = true,
                Settings = new Dictionary<string, string>()
            })
        };

        var json = JsonSerializer.Serialize(appSettings, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(outputPath, "appsettings.json"), json);
    }

    private async Task GeneratePaymentProviderService(string outputPath, string provider)
    {
        var serviceCode = $@"using System;
using System.Threading.Tasks;

namespace {outputPath.Split('/').Last()}.Services.Payment
{{
    public interface I{provider}PaymentService
    {{
        Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request);
        Task<RefundResult> ProcessRefundAsync(RefundRequest request);
        Task<bool> ValidateWebhookAsync(string payload, string signature);
    }}
    
    public class {provider}PaymentService : I{provider}PaymentService
    {{
        public Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
        {{
            // {provider} payment implementation
            throw new NotImplementedException();
        }}
        
        public Task<RefundResult> ProcessRefundAsync(RefundRequest request)
        {{
            // {provider} refund implementation
            throw new NotImplementedException();
        }}
        
        public Task<bool> ValidateWebhookAsync(string payload, string signature)
        {{
            // {provider} webhook validation
            throw new NotImplementedException();
        }}
    }}
}}";

        var paymentPath = _fileSystem.Path.Combine(outputPath, "src", "Services", "Payment");
        _fileSystem.Directory.CreateDirectory(paymentPath);
        await _fileSystem.File.WriteAllTextAsync(
            _fileSystem.Path.Combine(paymentPath, $"{provider}PaymentService.cs"), 
            serviceCode);
    }

    private async Task GenerateShippingProviderService(string outputPath, string provider)
    {
        var serviceCode = $@"using System;
using System.Threading.Tasks;

namespace {outputPath.Split('/').Last()}.Services.Shipping
{{
    public interface I{provider}ShippingService
    {{
        Task<ShippingRate[]> GetRatesAsync(ShippingRequest request);
        Task<TrackingInfo> GetTrackingAsync(string trackingNumber);
        Task<ShippingLabel> CreateLabelAsync(ShippingLabelRequest request);
    }}
    
    public class {provider}ShippingService : I{provider}ShippingService
    {{
        public Task<ShippingRate[]> GetRatesAsync(ShippingRequest request)
        {{
            // {provider} rate calculation
            throw new NotImplementedException();
        }}
        
        public Task<TrackingInfo> GetTrackingAsync(string trackingNumber)
        {{
            // {provider} tracking implementation
            throw new NotImplementedException();
        }}
        
        public Task<ShippingLabel> CreateLabelAsync(ShippingLabelRequest request)
        {{
            // {provider} label creation
            throw new NotImplementedException();
        }}
    }}
}}";

        var shippingPath = _fileSystem.Path.Combine(outputPath, "src", "Services", "Shipping");
        _fileSystem.Directory.CreateDirectory(shippingPath);
        await _fileSystem.File.WriteAllTextAsync(
            _fileSystem.Path.Combine(shippingPath, $"{provider}ShippingService.cs"), 
            serviceCode);
    }

    private async Task GenerateEcommerceSampleData(string outputPath)
    {
        var dataPath = _fileSystem.Path.Combine(outputPath, "data");
        _fileSystem.Directory.CreateDirectory(dataPath);

        // Sample products
        var products = new[]
        {
            new { Id = Guid.NewGuid(), Name = "Laptop Pro", Category = "Electronics", Price = 1299.99, Stock = 50 },
            new { Id = Guid.NewGuid(), Name = "Wireless Mouse", Category = "Accessories", Price = 29.99, Stock = 200 },
            new { Id = Guid.NewGuid(), Name = "USB-C Hub", Category = "Accessories", Price = 49.99, Stock = 150 }
        };
        
        var productsJson = JsonSerializer.Serialize(products, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(dataPath, "sample-products.json"), productsJson);

        // Sample categories
        var categories = new[]
        {
            new { Id = Guid.NewGuid(), Name = "Electronics", Description = "Electronic devices and gadgets" },
            new { Id = Guid.NewGuid(), Name = "Accessories", Description = "Computer and phone accessories" },
            new { Id = Guid.NewGuid(), Name = "Software", Description = "Digital software products" }
        };
        
        var categoriesJson = JsonSerializer.Serialize(categories, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(dataPath, "sample-categories.json"), categoriesJson);

        // Sample inventory
        var inventory = products.Select(p => new
        {
            ProductId = p.Id,
            AvailableStock = p.Stock,
            ReservedStock = 0,
            ReorderLevel = 10,
            ReorderQuantity = 50
        });
        
        var inventoryJson = JsonSerializer.Serialize(inventory, new JsonSerializerOptions { WriteIndented = true });
        await _fileSystem.File.WriteAllTextAsync(_fileSystem.Path.Combine(dataPath, "sample-inventory.json"), inventoryJson);
    }

    private async Task ProcessTemplateFiles(string sourcePath, string destinationPath, TemplateCustomization customization, TemplateGenerationResult result)
    {
        var files = _fileSystem.Directory.GetFiles(sourcePath, "*", SearchOption.AllDirectories);

        foreach (var file in files)
        {
            var relativePath = _fileSystem.Path.GetRelativePath(sourcePath, file);
            
            // Check if file should be excluded
            if (customization.ExcludeFiles.Any(pattern => IsMatchPattern(relativePath, pattern)))
            {
                continue;
            }

            var destFile = _fileSystem.Path.Combine(destinationPath, relativePath);
            var destDir = _fileSystem.Path.GetDirectoryName(destFile);
            
            if (!string.IsNullOrEmpty(destDir))
            {
                _fileSystem.Directory.CreateDirectory(destDir);
            }

            // Check if file is a template
            if (file.EndsWith(".template") || file.EndsWith(".scriban"))
            {
                // Process template
                var templateContent = await _fileSystem.File.ReadAllTextAsync(file);
                var processedContent = await ProcessTemplate(templateContent, customization.Variables);
                
                // Remove .template extension
                destFile = destFile.Replace(".template", "").Replace(".scriban", "");
                
                await _fileSystem.File.WriteAllTextAsync(destFile, processedContent);
                result.GeneratedFiles.Add(destFile);
            }
            else if (file.EndsWith(".merge") && customization.MergeMode)
            {
                // Merge with existing file
                var mergeFile = destFile.Replace(".merge", "");
                if (_fileSystem.File.Exists(mergeFile))
                {
                    // Merge logic would go here
                    result.ModifiedFiles.Add(mergeFile);
                }
            }
            else
            {
                // Copy as-is
                if (!customization.PreserveExisting || !_fileSystem.File.Exists(destFile))
                {
                    _fileSystem.File.Copy(file, destFile, true);
                    result.GeneratedFiles.Add(destFile);
                }
            }
        }
    }

    private async Task<string> ProcessTemplate(string templateContent, Dictionary<string, string> variables)
    {
        var template = Template.Parse(templateContent);
        if (template.HasErrors)
        {
            var errors = string.Join(", ", template.Messages);
            throw new InvalidOperationException($"Template parsing errors: {errors}");
        }

        var result = await template.RenderAsync(variables);
        return result;
    }

    private bool IsMatchPattern(string path, string pattern)
    {
        // Simple pattern matching (could be enhanced with proper glob support)
        if (pattern.StartsWith("*"))
        {
            return path.EndsWith(pattern.Substring(1));
        }
        else if (pattern.EndsWith("*"))
        {
            return path.StartsWith(pattern.Substring(0, pattern.Length - 1));
        }
        else
        {
            return path == pattern;
        }
    }

    private bool IsValidPath(string path)
    {
        try
        {
            var fullPath = _fileSystem.Path.GetFullPath(path);
            return true;
        }
        catch
        {
            return false;
        }
    }
}