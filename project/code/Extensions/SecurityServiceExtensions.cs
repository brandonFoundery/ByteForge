using System;
using System.Text;
using System.Threading.Tasks;
using System.Threading.RateLimiting;
using System.Security.Claims;
using ByteForgeFrontend.Services.Security.Authentication;
using ByteForgeFrontend.Services.Security.Audit;
using ByteForgeFrontend.Services.Security.Compliance;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Tokens;

namespace ByteForgeFrontend.Extensions
{
    public static class SecurityServiceExtensions
    {
        public static IServiceCollection AddSecurityServices(
            this IServiceCollection services, 
            IConfiguration configuration)
        {
            return AddByteForgeSecurity(services, configuration);
        }
        
        public static IServiceCollection AddByteForgeSecurity(
            this IServiceCollection services, 
            IConfiguration configuration)
        {
            // Add security services
            services.AddScoped<IMultiTenantAuthenticationService, MultiTenantAuthenticationService>();
            services.AddScoped<IApiKeyManagementService, ApiKeyManagementService>();
            services.AddScoped<IAuditLoggingService, AuditLoggingService>();
            services.AddScoped<IComplianceService, ComplianceService>();

            // Configure JWT authentication
            ConfigureJwtAuthentication(services, configuration);

            // Configure API key authentication
            ConfigureApiKeyAuthentication(services, configuration);

            // Configure authorization policies
            ConfigureAuthorizationPolicies(services, configuration);

            // Configure Identity options
            ConfigureIdentityOptions(services, configuration);

            // Add CORS if needed
            ConfigureCors(services, configuration);

            return services;
        }

        private static void ConfigureJwtAuthentication(IServiceCollection services, IConfiguration configuration)
        {
            var jwtSettings = configuration.GetSection("JwtSettings");
            var secretKey = jwtSettings["SecretKey"];
            var issuer = jwtSettings["Issuer"];
            var audience = jwtSettings["Audience"];

            services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
            })
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
                    ValidateIssuer = true,
                    ValidIssuer = issuer,
                    ValidateAudience = true,
                    ValidAudience = audience,
                    ValidateLifetime = true,
                    ClockSkew = TimeSpan.Zero,
                    RequireExpirationTime = true
                };

                options.Events = new JwtBearerEvents
                {
                    OnTokenValidated = async context =>
                    {
                        // Additional token validation logic
                        var tenantId = context.Principal?.FindFirst("tenant_id")?.Value;
                        if (string.IsNullOrEmpty(tenantId))
                        {
                            context.Fail("Missing tenant information");
                        }
                    },
                    OnAuthenticationFailed = context =>
                    {
                        if (context.Exception.GetType() == typeof(SecurityTokenExpiredException))
                        {
                            context.Response.Headers.Add("Token-Expired", "true");
                        }
                        return Task.CompletedTask;
                    }
                };
            });
        }

        private static void ConfigureApiKeyAuthentication(IServiceCollection services, IConfiguration configuration)
        {
            services.AddAuthentication()
                .AddApiKeyAuthentication(ApiKeyAuthenticationOptions.DefaultScheme, options =>
                {
                    options.HeaderName = configuration["Security:ApiKey:HeaderName"] ?? "X-API-Key";
                    options.QueryParameterName = configuration["Security:ApiKey:QueryParameterName"] ?? "api_key";
                });
        }

        private static void ConfigureAuthorizationPolicies(IServiceCollection services, IConfiguration configuration)
        {
            services.AddAuthorization(options =>
            {
                // Tenant-based policies
                options.AddPolicy("RequireTenant", policy =>
                    policy.RequireClaim("tenant_id"));

                options.AddPolicy("RequireTenantAdmin", policy =>
                    policy.RequireClaim("tenant_id")
                          .RequireRole("TenantAdmin"));

                // Project-based policies
                options.AddPolicy("ProjectAccess", policy =>
                    policy.RequireClaim("tenant_id")
                          .RequireRole("User", "Developer", "ProjectManager", "TenantAdmin"));

                options.AddPolicy("ProjectManagement", policy =>
                    policy.RequireClaim("tenant_id")
                          .RequireRole("ProjectManager", "TenantAdmin"));

                // Document generation policies
                options.AddPolicy("DocumentGeneration", policy =>
                    policy.RequireClaim("tenant_id")
                          .RequireRole("ProjectManager", "TenantAdmin"));

                // Agent execution policies
                options.AddPolicy("AgentExecution", policy =>
                    policy.RequireClaim("tenant_id")
                          .RequireRole("ProjectManager", "TenantAdmin"));

                // API key policies
                options.AddPolicy("ApiKeyAccess", policy =>
                    policy.RequireAssertion(context =>
                        context.User.HasClaim("api_key", "true") ||
                        context.User.HasClaim(c => c.Type == ClaimTypes.NameIdentifier)));

                options.AddPolicy("ServiceApiKey", policy =>
                    policy.RequireClaim("service_api_key", "true"));

                // System admin policies
                options.AddPolicy("SystemAdmin", policy =>
                    policy.RequireRole("SuperAdmin"));

                // Compliance policies
                options.AddPolicy("ComplianceAccess", policy =>
                    policy.RequireClaim("tenant_id")
                          .RequireRole("TenantAdmin", "ComplianceOfficer"));
            });
        }

        private static void ConfigureIdentityOptions(IServiceCollection services, IConfiguration configuration)
        {
            services.Configure<IdentityOptions>(options =>
            {
                // Password settings
                options.Password.RequireDigit = true;
                options.Password.RequireLowercase = true;
                options.Password.RequireUppercase = true;
                options.Password.RequireNonAlphanumeric = true;
                options.Password.RequiredLength = configuration.GetValue<int>("Security:Password:MinLength", 12);
                options.Password.RequiredUniqueChars = 4;

                // Lockout settings
                options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(30);
                options.Lockout.MaxFailedAccessAttempts = configuration.GetValue<int>("Security:Lockout:MaxAttempts", 5);
                options.Lockout.AllowedForNewUsers = true;

                // User settings
                options.User.RequireUniqueEmail = true;
                options.User.AllowedUserNameCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._@+";

                // Sign-in settings
                options.SignIn.RequireConfirmedEmail = configuration.GetValue<bool>("Security:RequireConfirmedEmail", false);
                options.SignIn.RequireConfirmedPhoneNumber = false;
            });
        }

        private static void ConfigureCors(IServiceCollection services, IConfiguration configuration)
        {
            var corsConfig = configuration.GetSection("Security:Cors");
            if (!corsConfig.Exists()) return;

            services.AddCors(options =>
            {
                options.AddPolicy("ByteForgeCors", builder =>
                {
                    var allowedOrigins = corsConfig.GetSection("AllowedOrigins").Get<string[]>();
                    if (allowedOrigins?.Length > 0)
                    {
                        builder.WithOrigins(allowedOrigins);
                    }
                    else
                    {
                        builder.AllowAnyOrigin();
                    }

                    if (corsConfig.GetValue<bool>("AllowCredentials", false))
                    {
                        builder.AllowCredentials();
                    }

                    var allowedHeaders = corsConfig.GetSection("AllowedHeaders").Get<string[]>();
                    if (allowedHeaders?.Length > 0)
                    {
                        builder.WithHeaders(allowedHeaders);
                    }
                    else
                    {
                        builder.AllowAnyHeader();
                    }

                    var allowedMethods = corsConfig.GetSection("AllowedMethods").Get<string[]>();
                    if (allowedMethods?.Length > 0)
                    {
                        builder.WithMethods(allowedMethods);
                    }
                    else
                    {
                        builder.AllowAnyMethod();
                    }

                    var exposedHeaders = corsConfig.GetSection("ExposedHeaders").Get<string[]>();
                    if (exposedHeaders?.Length > 0)
                    {
                        builder.WithExposedHeaders(exposedHeaders);
                    }
                });
            });
        }

        public static IServiceCollection AddRateLimiting(
            this IServiceCollection services,
            IConfiguration configuration)
        {
            // Configure rate limiting (requires Microsoft.AspNetCore.RateLimiting package)
            services.AddRateLimiter(options =>
            {
                options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

                // Global rate limit
                options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(httpContext =>
                    RateLimitPartition.GetFixedWindowLimiter(
                        partitionKey: httpContext.User?.Identity?.Name ?? httpContext.Request.Headers.Host.ToString(),
                        factory: partition => new FixedWindowRateLimiterOptions
                        {
                            AutoReplenishment = true,
                            PermitLimit = configuration.GetValue<int>("Security:RateLimit:Global:PermitLimit", 100),
                            Window = TimeSpan.FromMinutes(configuration.GetValue<int>("Security:RateLimit:Global:WindowMinutes", 1))
                        }));

                // API key specific rate limiting
                options.AddPolicy("ApiKeyLimit", httpContext =>
                    RateLimitPartition.GetFixedWindowLimiter(
                        partitionKey: httpContext.Request.Headers["X-API-Key"].ToString(),
                        factory: partition => new FixedWindowRateLimiterOptions
                        {
                            AutoReplenishment = true,
                            PermitLimit = configuration.GetValue<int>("Security:RateLimit:ApiKey:PermitLimit", 1000),
                            Window = TimeSpan.FromMinutes(configuration.GetValue<int>("Security:RateLimit:ApiKey:WindowMinutes", 60))
                        }));
            });

            return services;
        }
    }
}