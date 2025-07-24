using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Models;
using ByteForgeFrontend.Services;
using ByteForgeFrontend.Extensions;
using ByteForgeFrontend.Hubs;
using Elsa.Extensions;
using Elsa.EntityFrameworkCore.Extensions;
using Hangfire;
using Hangfire.SqlServer;
using Hangfire.Storage.SQLite;
using Azure.Identity;

using Azure.Core;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
var builder = WebApplication.CreateBuilder(args);

// Add Azure Key Vault if running in Azure
if (builder.Environment.IsProduction())
{
    builder.Configuration.AddAzureKeyVault(
        new Uri($"https://{builder.Configuration["KeyVaultName"]}.vault.azure.net/"),
        new DefaultAzureCredential());
}

// Add services to the container
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") ?? 
    throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");

builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlite(connectionString));

builder.Services.AddDatabaseDeveloperPageExceptionFilter();

// Add Identity services
builder.Services.AddDefaultIdentity<ApplicationUser>(options => 
{
    options.SignIn.RequireConfirmedAccount = false;
    options.Password.RequireDigit = true;
    options.Password.RequiredLength = 8;
})
.AddEntityFrameworkStores<ApplicationDbContext>();

// Add JWT Authentication
var jwtSettings = builder.Configuration.GetSection("JwtSettings");
var secretKey = jwtSettings["SecretKey"] ?? "your-super-secret-key-that-should-be-at-least-32-characters-long";
var issuer = jwtSettings["Issuer"] ?? "ByteForgeFrontend";
var audience = jwtSettings["Audience"] ?? "ByteForgeFrontend";

builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = IdentityConstants.ApplicationScheme;
    options.DefaultChallengeScheme = IdentityConstants.ApplicationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = issuer,
        ValidAudience = audience,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
        ClockSkew = TimeSpan.Zero
    };

    // Configure SignalR to use JWT tokens
    options.Events = new JwtBearerEvents
    {
        OnMessageReceived = context =>
        {
            var accessToken = context.Request.Query["access_token"];
            var path = context.HttpContext.Request.Path;
            
            if (!string.IsNullOrEmpty(accessToken) && 
                (path.StartsWithSegments("/notificationHub") || path.StartsWithSegments("/projectHub")))
            {
                context.Token = accessToken;
            }
            
            return Task.CompletedTask;
        }
    };
});

// Add Elsa services
builder.Services.AddElsa(elsa =>
{
    // Elsa configuration for ByteForge workflows
});

// Add Hangfire services
builder.Services.AddHangfire(config => config
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UseSQLiteStorage(connectionString));

builder.Services.AddHangfireServer();

// Add ByteForge services will be configured via extension method

// Add ByteForge Infrastructure Services
builder.Services.AddInfrastructureServices(builder.Configuration);

// Add AI Agent Services
builder.Services.AddAIAgentServices();

// Add Security Services
builder.Services.AddSecurityServices(builder.Configuration);

// Add HttpClient services for external integrations
builder.Services.AddHttpClient("ByteForge", client =>
{
    client.DefaultRequestHeaders.Add("User-Agent", "ByteForgeFrontend/1.0");
});

// ByteForge services are registered via extension method

// Add CORS services
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowNextJS", policy =>
    {
        policy.WithOrigins("http://localhost:3000", "https://localhost:3000", "http://localhost:3020", "https://localhost:3020")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

// Add SignalR services
builder.Services.AddSignalR();

// ByteForge notification services will be added via extension method

// Add workflow monitoring service
builder.Services.AddScoped<IWorkflowMonitoringService, WorkflowMonitoringService>();

// Add settings service
builder.Services.AddScoped<ISettingsService, SettingsService>();

// Add initialization services
builder.Services.AddTransient<DatabaseInitializationService>();
builder.Services.AddScoped<IJobSchedulingService, JobSchedulingService>();

// Add MVC services
builder.Services.AddControllersWithViews();

// Add health checks
builder.Services.AddHealthChecks()
    .AddDbContextCheck<ApplicationDbContext>();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseMigrationsEndPoint();
}
else
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

// Use CORS
app.UseCors("AllowNextJS");

app.UseRouting();

app.UseAuthentication();
app.UseAuthorization();

// Configure Hangfire Dashboard
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new[] { new HangfireAuthorizationFilter() }
});

// Add health check endpoint
app.MapHealthChecks("/health");

// MVC routing for dashboard integration
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

// API controllers are accessible via [Route] attributes
app.MapControllers();

// Map SignalR Hub
app.MapHub<NotificationHub>("/notificationHub");
// Initialize database and schedule jobs properly
try
{
    app.Logger.LogInformation("Starting database initialization...");
    
    // Step 1: Initialize database (EF + Hangfire schema)
    using (var scope = app.Services.CreateScope())
    {
        var dbInitializer = scope.ServiceProvider.GetRequiredService<DatabaseInitializationService>();
        await dbInitializer.InitializeAsync();
    }
    
    // Step 2: Initialize job schedules and schedule recurring jobs after database is ready
    app.Logger.LogInformation("Initializing job schedules and scheduling recurring jobs...");
    using (var scope = app.Services.CreateScope())
    {
        var jobScheduler = scope.ServiceProvider.GetRequiredService<IJobSchedulingService>();
        await jobScheduler.InitializeDefaultJobSchedulesAsync();
        jobScheduler.ScheduleRecurringJobs();
    }
    
    app.Logger.LogInformation("Application startup completed successfully");
}
catch (Exception ex)
{
    app.Logger.LogError(ex, "Application startup failed during database initialization");
    throw;
}

app.Run();

// Make Program class accessible for testing
public partial class Program { }