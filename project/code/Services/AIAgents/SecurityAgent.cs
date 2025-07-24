using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

using System.Linq;
namespace ByteForgeFrontend.Services.AIAgents
{
    public class SecurityAgent : BaseAgent, ICodeGeneratingAgent
    {
        private readonly ILLMService _llmService;
        private readonly IDocumentGenerationService _documentService;
        private readonly ILogger<SecurityAgent> _agentLogger;

        public SecurityAgent(IServiceProvider serviceProvider, string name) 
            : base(serviceProvider, name)
        {
            _llmService = serviceProvider.GetService<ILLMService>();
            _documentService = serviceProvider.GetService<IDocumentGenerationService>();
            _agentLogger = serviceProvider.GetRequiredService<ILogger<SecurityAgent>>();
        }

        public async Task<AgentCodeGenerationResult> GenerateCodeAsync(AgentProjectContext context)
        {
            var stopwatch = Stopwatch.StartNew();
            var result = new AgentCodeGenerationResult();

            try
            {
                _agentLogger.LogInformation("Security agent starting code generation for project {ProjectId}", 
                    context.ProjectId);

                // Generate authentication code
                var authFiles = await GenerateAuthenticationAsync(context);
                result.GeneratedFiles.AddRange(authFiles.Keys);
                foreach (var file in authFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate authorization code
                var authzFiles = await GenerateAuthorizationAsync(context);
                result.GeneratedFiles.AddRange(authzFiles.Keys);
                foreach (var file in authzFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate security middleware
                var middlewareFiles = await GenerateSecurityMiddlewareAsync(context);
                result.GeneratedFiles.AddRange(middlewareFiles.Keys);
                foreach (var file in middlewareFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate audit logging
                var auditFiles = await GenerateAuditLoggingAsync(context);
                result.GeneratedFiles.AddRange(auditFiles.Keys);
                foreach (var file in auditFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                result.Success = true;
                _agentLogger.LogInformation("Security agent generated {FileCount} files", result.GeneratedFiles.Count);
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Error = ex.Message;
                _agentLogger.LogError(ex, "Security agent failed to generate code");
            }
            finally
            {
                stopwatch.Stop();
                result.Duration = stopwatch.Elapsed;
            }

            return result;
        }

        public async Task<bool> UseTemplateAsync(string templatePath, object model)
        {
            try
            {
                if (_documentService == null)
                {
                    _agentLogger.LogWarning("Document service not available for template usage");
                    return false;
                }

                var template = await _documentService.GetTemplateAsync(templatePath);
                var modelDict = model as Dictionary<string, object> ?? new Dictionary<string, object> { { "model", model } };
                var rendered = await _documentService.RenderTemplateAsync(template, modelDict);
                
                _agentLogger.LogDebug("Successfully used template {TemplatePath}", templatePath);
                return true;
            }
            catch (Exception ex)
            {
                _agentLogger.LogError(ex, "Failed to use template {TemplatePath}", templatePath);
                return false;
            }
        }

        protected override async Task<AgentResult> PerformWorkAsync(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                await Task.Delay(1000, cancellationToken);
            }

            return new AgentResult { Success = true };
        }

        private async Task<Dictionary<string, string>> GenerateAuthenticationAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                _agentLogger.LogWarning("LLM service not available, using mock generation");
                files["authentication/JwtService.cs"] = GenerateMockJwtService();
                files["authentication/AuthenticationController.cs"] = GenerateMockAuthController();
                return files;
            }

            var prompt = BuildAuthenticationPrompt(context);
            var request = new LLMGenerationRequest { Prompt = prompt };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".cs");
                foreach (var file in generatedFiles)
                {
                    files[$"authentication/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateAuthorizationAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                files["authorization/RoleAuthorizationHandler.cs"] = GenerateMockAuthorizationHandler();
                files["authorization/PermissionService.cs"] = GenerateMockPermissionService();
                return files;
            }

            var prompt = BuildAuthorizationPrompt(context);
            var request = new LLMGenerationRequest { Prompt = prompt };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".cs");
                foreach (var file in generatedFiles)
                {
                    files[$"authorization/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateSecurityMiddlewareAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();
            files["middleware/SecurityHeadersMiddleware.cs"] = GenerateMockSecurityMiddleware();
            return files;
        }

        private async Task<Dictionary<string, string>> GenerateAuditLoggingAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();
            files["audit/AuditService.cs"] = GenerateMockAuditService();
            return files;
        }

        private string BuildAuthenticationPrompt(AgentProjectContext context)
        {
            var requirements = context.Requirements;
            return $@"Generate authentication code for ASP.NET Core based on:

Security Requirements:
{requirements.SecurityRequirements}

Technical Requirements:
{requirements.TechnicalRequirements}

Include:
- JWT token generation and validation
- User authentication service
- Password hashing (BCrypt or similar)
- Refresh token support
- Multi-factor authentication support if mentioned in requirements
- Secure cookie handling

Use ASP.NET Core Identity where appropriate.";
        }

        private string BuildAuthorizationPrompt(AgentProjectContext context)
        {
            return $@"Generate authorization code based on:

Security Requirements:
{context.Requirements.SecurityRequirements}

Include:
- Role-based authorization
- Policy-based authorization
- Custom authorization handlers
- Permission management
- Resource-based authorization if needed";
        }

        private Dictionary<string, string> ParseGeneratedFiles(string llmResponse, string fileSuffix)
        {
            var files = new Dictionary<string, string>();
            var lines = llmResponse.Split('\n');
            string currentFile = null;
            var currentContent = new List<string>();

            foreach (var line in lines)
            {
                if (line.StartsWith("// File:") || line.StartsWith("# File:"))
                {
                    if (currentFile != null && currentContent.Any())
                    {
                        files[currentFile] = string.Join("\n", currentContent);
                    }
                    currentFile = line.Substring(line.IndexOf(':') + 1).Trim();
                    currentContent.Clear();
                }
                else if (currentFile != null)
                {
                    currentContent.Add(line);
                }
            }

            if (currentFile != null && currentContent.Any())
            {
                files[currentFile] = string.Join("\n", currentContent);
            }

            if (!files.Any() && !string.IsNullOrWhiteSpace(llmResponse))
            {
                files[$"Generated{fileSuffix}"] = llmResponse;
            }

            return files;
        }

        private string GenerateMockJwtService()
        {
            return @"using System;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;

namespace ByteForgeFrontend.Services.Authentication
{
    public interface IJwtService
    {
        string GenerateToken(ClaimsPrincipal principal);
        ClaimsPrincipal ValidateToken(string token);
    }

    public class JwtService : IJwtService
    {
        private readonly IConfiguration _configuration;
        private readonly string _secretKey;
        private readonly string _issuer;
        private readonly string _audience;

        public JwtService(IConfiguration configuration)
        {
            _configuration = configuration;
            _secretKey = _configuration[""Jwt:SecretKey""];
            _issuer = _configuration[""Jwt:Issuer""];
            _audience = _configuration[""Jwt:Audience""];
        }

        public string GenerateToken(ClaimsPrincipal principal)
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.ASCII.GetBytes(_secretKey);
            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(principal.Claims),
                Expires = DateTime.UtcNow.AddHours(24),
                Issuer = _issuer,
                Audience = _audience,
                SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), 
                    SecurityAlgorithms.HmacSha256Signature)
            };
            var token = tokenHandler.CreateToken(tokenDescriptor);
            return tokenHandler.WriteToken(token);
        }

        public ClaimsPrincipal ValidateToken(string token)
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.ASCII.GetBytes(_secretKey);
            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidateIssuer = true,
                ValidIssuer = _issuer,
                ValidateAudience = true,
                ValidAudience = _audience,
                ValidateLifetime = true,
                ClockSkew = TimeSpan.Zero
            };

            var principal = tokenHandler.ValidateToken(token, validationParameters, out _);
            return principal;
        }
    }
}";
        }

        private string GenerateMockAuthController()
        {
            return @"using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ByteForgeFrontend.Controllers
{
    [ApiController]
    [Route(""api/[controller]"")]
    public class AuthenticationController : ControllerBase
    {
        private readonly IJwtService _jwtService;

        public AuthenticationController(IJwtService jwtService)
        {
            _jwtService = jwtService;
        }

        [HttpPost(""login"")]
        [AllowAnonymous]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {
            // TODO: Validate credentials
            
            var claims = new[]
            {
                new Claim(ClaimTypes.Name, request.Username),
                new Claim(ClaimTypes.NameIdentifier, ""user-id""),
                new Claim(ClaimTypes.Role, ""User"")
            };

            var principal = new ClaimsPrincipal(new ClaimsIdentity(claims, ""jwt""));
            var token = _jwtService.GenerateToken(principal);

            return Ok(new { token });
        }

        [HttpPost(""logout"")]
        [Authorize]
        public IActionResult Logout()
        {
            // TODO: Implement token invalidation
            return Ok(new { message = ""Logged out successfully"" });
        }
    }

    public class LoginRequest
    {
        public string Username { get; set; }
        public string Password { get; set; }
    }
}";
        }

        private string GenerateMockAuthorizationHandler()
        {
            return @"using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;

namespace ByteForgeFrontend.Services.Authorization
{
    public class RoleRequirement : IAuthorizationRequirement
    {
        public string RequiredRole { get; }

        public RoleRequirement(string requiredRole)
        {
            RequiredRole = requiredRole;
        }
    }

    public class RoleAuthorizationHandler : AuthorizationHandler<RoleRequirement>
    {
        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            RoleRequirement requirement)
        {
            if (context.User.IsInRole(requirement.RequiredRole))
            {
                context.Succeed(requirement);
            }

            return Task.CompletedTask;
        }
    }
}";
        }

        private string GenerateMockPermissionService()
        {
            return @"using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Authorization
{
    public interface IPermissionService
    {
        Task<bool> HasPermissionAsync(string userId, string permission);
        Task<IEnumerable<string>> GetUserPermissionsAsync(string userId);
    }

    public class PermissionService : IPermissionService
    {
        public Task<bool> HasPermissionAsync(string userId, string permission)
        {
            // TODO: Implement permission checking logic
            return Task.FromResult(true);
        }

        public Task<IEnumerable<string>> GetUserPermissionsAsync(string userId)
        {
            // TODO: Fetch permissions from database
            var permissions = new List<string> { ""read"", ""write"" };
            return Task.FromResult<IEnumerable<string>>(permissions);
        }
    }
}";
        }

        private string GenerateMockSecurityMiddleware()
        {
            return @"using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;

namespace ByteForgeFrontend.Middleware
{
    public class SecurityHeadersMiddleware
    {
        private readonly RequestDelegate _next;

        public SecurityHeadersMiddleware(RequestDelegate next)
        {
            _next = next;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            context.Response.Headers.Add(""X-Content-Type-Options"", ""nosniff"");
            context.Response.Headers.Add(""X-Frame-Options"", ""DENY"");
            context.Response.Headers.Add(""X-XSS-Protection"", ""1; mode=block"");
            context.Response.Headers.Add(""Referrer-Policy"", ""strict-origin-when-cross-origin"");
            
            await _next(context);
        }
    }
}";
        }

        private string GenerateMockAuditService()
        {
            return @"using System;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.Audit
{
    public interface IAuditService
    {
        Task LogAsync(AuditEntry entry);
    }

    public class AuditService : IAuditService
    {
        public async Task LogAsync(AuditEntry entry)
        {
            // TODO: Implement audit logging to database
            await Task.CompletedTask;
        }
    }

    public class AuditEntry
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string UserId { get; set; }
        public string Action { get; set; }
        public string Resource { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public string IpAddress { get; set; }
        public string UserAgent { get; set; }
        public bool Success { get; set; }
        public string Details { get; set; }
    }
}";
        }
    }
}