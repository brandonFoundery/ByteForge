using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using ByteForgeFrontend.Services;
using System;

namespace ByteForgeFrontend.Services.Infrastructure.LLM;

/// <summary>
/// Extension methods for registering LLM services in the dependency injection container
/// </summary>
public static class LLMServiceCollectionExtensions
{
    /// <summary>
    /// Adds LLM services to the service collection
    /// </summary>
    /// <param name="services">The service collection</param>
    /// <param name="configuration">The configuration</param>
    /// <returns>The service collection for chaining</returns>
    public static IServiceCollection AddLLMServices(this IServiceCollection services, IConfiguration configuration)
    {
        if (services == null)
            throw new ArgumentNullException(nameof(services));
        
        if (configuration == null)
            throw new ArgumentNullException(nameof(configuration));

        // Register core LLM services
        services.AddSingleton<ILLMConfigurationService, LLMConfigurationService>();
        services.AddScoped<ILLMProviderFactory, LLMProviderFactory>();
        services.AddScoped<ILLMService, LLMService>();

        // Configure HttpClient factory for LLM providers
        services.AddHttpClient();

        // Configure named HttpClients for each LLM provider with appropriate settings
        ConfigureLLMHttpClients(services);

        return services;
    }

    /// <summary>
    /// Adds LLM services with custom configuration
    /// </summary>
    /// <param name="services">The service collection</param>
    /// <param name="configureOptions">Action to configure LLM options</param>
    /// <returns>The service collection for chaining</returns>
    public static IServiceCollection AddLLMServices(this IServiceCollection services, Action<LLMServicesConfiguration> configureOptions)
    {
        if (services == null)
            throw new ArgumentNullException(nameof(services));
        
        if (configureOptions == null)
            throw new ArgumentNullException(nameof(configureOptions));

        // Configure LLM options
        var llmConfiguration = new LLMServicesConfiguration();
        configureOptions(llmConfiguration);
        
        services.AddSingleton(llmConfiguration);
        services.AddSingleton<ILLMConfigurationService>(provider => 
            new LLMConfigurationService(provider.GetRequiredService<IConfiguration>()));

        // Register core services
        services.AddScoped<ILLMProviderFactory, LLMProviderFactory>();
        services.AddScoped<ILLMService, LLMService>();
        
        // Configure HttpClient factory
        services.AddHttpClient();
        ConfigureLLMHttpClients(services);

        return services;
    }

    /// <summary>
    /// Configures named HttpClients for each LLM provider
    /// </summary>
    /// <param name="services">The service collection</param>
    private static void ConfigureLLMHttpClients(IServiceCollection services)
    {
        // OpenAI HttpClient configuration
        services.AddHttpClient("LLM_openai", client =>
        {
            client.BaseAddress = new Uri("https://api.openai.com/");
            client.Timeout = TimeSpan.FromSeconds(120);
            client.DefaultRequestHeaders.Add("User-Agent", "ByteForge/1.0");
        });

        // Anthropic HttpClient configuration
        services.AddHttpClient("LLM_anthropic", client =>
        {
            client.BaseAddress = new Uri("https://api.anthropic.com/");
            client.Timeout = TimeSpan.FromSeconds(120);
            client.DefaultRequestHeaders.Add("User-Agent", "ByteForge/1.0");
        });

        // Google Gemini HttpClient configuration
        services.AddHttpClient("LLM_googlegemini", client =>
        {
            client.BaseAddress = new Uri("https://generativelanguage.googleapis.com/");
            client.Timeout = TimeSpan.FromSeconds(120);
            client.DefaultRequestHeaders.Add("User-Agent", "ByteForge/1.0");
        });

        // Grok HttpClient configuration
        services.AddHttpClient("LLM_grok", client =>
        {
            client.BaseAddress = new Uri("https://api.x.ai/");
            client.Timeout = TimeSpan.FromSeconds(120);
            client.DefaultRequestHeaders.Add("User-Agent", "ByteForge/1.0");
        });
    }

    /// <summary>
    /// Adds only mock LLM services for testing purposes
    /// </summary>
    /// <param name="services">The service collection</param>
    /// <returns>The service collection for chaining</returns>
    public static IServiceCollection AddMockLLMServices(this IServiceCollection services)
    {
        if (services == null)
            throw new ArgumentNullException(nameof(services));

        // Configure mock LLM configuration
        var mockConfig = new LLMServicesConfiguration
        {
            UseMockResponses = true,
            DefaultProvider = "mock"
        };

        services.AddSingleton(mockConfig);
        services.AddSingleton<ILLMConfigurationService>(provider =>
            new LLMConfigurationService(provider.GetRequiredService<IConfiguration>()));

        services.AddScoped<ILLMProviderFactory, LLMProviderFactory>();
        services.AddScoped<ILLMService, LLMService>();

        return services;
    }
}