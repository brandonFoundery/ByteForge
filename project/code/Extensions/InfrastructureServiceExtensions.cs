using Microsoft.Extensions.FileProviders;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.DocumentGenerators;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.Traceability;
using ByteForgeFrontend.Services.Infrastructure.Templates;
using ByteForgeFrontend.Services;
using ByteForgeFrontend.Services.Monitoring;
using System.IO.Abstractions;

using System;
namespace ByteForgeFrontend.Extensions;

public static class InfrastructureServiceExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
    {
        // LLM Services - using dedicated extension method
        services.AddLLMServices(configuration);

        // Document Generation Services
        var templatesPath = Path.Combine(Directory.GetCurrentDirectory(), "Templates");
        if (!Directory.Exists(templatesPath))
        {
            Directory.CreateDirectory(templatesPath);
        }
        services.AddSingleton<IFileProvider>(new PhysicalFileProvider(templatesPath));
        services.AddScoped<IDocumentTemplateService, DocumentTemplateService>();
        services.AddScoped<IDocumentValidationService, DocumentValidationService>();
        services.AddScoped<IDocumentGenerationService, DocumentGenerationService>();

        // Project Management Services
        services.AddScoped<IProjectService, ProjectService>();
        services.AddScoped<IProjectTemplateService, ProjectTemplateService>();

        // Requirements Generation Services
        services.AddScoped<IRequirementsOrchestrationService, RequirementsOrchestrationService>();
        services.AddScoped<IRequirementTraceabilityService, RequirementTraceabilityService>();
        
        // Document Generators
        services.AddScoped<IDocumentGenerator<BRDGenerationRequest, BRDGenerationResponse>, BRDGenerator>();
        services.AddScoped<IDocumentGenerator<PRDGenerationRequest, PRDGenerationResponse>, PRDGenerator>();
        services.AddScoped<IDocumentGenerator<FRDGenerationRequest, FRDGenerationResponse>, FRDGenerator>();
        services.AddScoped<IDocumentGenerator<TRDGenerationRequest, TRDGenerationResponse>, TRDGenerator>();
        
        // Workflow Monitoring Service
        services.AddScoped<IWorkflowMonitoringService, WorkflowMonitoringService>();
        
        // Monitoring Service
        services.AddSingleton<IMonitoringService, MonitoringService>();
        
        // Template Services
        services.AddScoped<ITemplateManagementService, TemplateManagementService>();
        services.AddScoped<ITemplateValidationService, TemplateValidationService>();
        services.AddSingleton<System.IO.Abstractions.IFileSystem, System.IO.Abstractions.FileSystem>();
        services.AddScoped<ITemplateGenerator, TemplateGenerator>();

        return services;
    }
}