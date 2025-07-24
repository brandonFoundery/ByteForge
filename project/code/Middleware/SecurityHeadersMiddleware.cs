using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

using System.Collections.Generic;
namespace ByteForgeFrontend.Middleware
{
    public class SecurityHeadersMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly IConfiguration _configuration;
        private readonly ILogger<SecurityHeadersMiddleware> _logger;

        public SecurityHeadersMiddleware(
            RequestDelegate next, 
            IConfiguration configuration,
            ILogger<SecurityHeadersMiddleware> logger = null)
        {
            _next = next;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            // Add security headers before processing the request
            AddSecurityHeaders(context);
            
            // Call the next middleware in the pipeline
            await _next(context);
        }

        private void AddSecurityHeaders(HttpContext context)
        {
            var headers = context.Response.Headers;
            
            // Prevent MIME type sniffing
            headers.Add("X-Content-Type-Options", "nosniff");
            
            // Prevent clickjacking attacks
            headers.Add("X-Frame-Options", "DENY");
            
            // Enable XSS protection in older browsers
            headers.Add("X-XSS-Protection", "1; mode=block");
            
            // Control referrer information
            headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");
            
            // Enforce HTTPS
            if (IsHttpsEnabled())
            {
                headers.Add("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
            }
            
            // Content Security Policy
            var cspPolicy = BuildContentSecurityPolicy();
            if (!string.IsNullOrEmpty(cspPolicy))
            {
                headers.Add("Content-Security-Policy", cspPolicy);
            }
            
            // Feature Policy / Permissions Policy
            headers.Add("Permissions-Policy", "geolocation=(), microphone=(), camera=()");
            
            // Remove server header for security
            headers.Remove("Server");
            headers.Remove("X-Powered-By");
            
            _logger?.LogDebug("Security headers added to response");
        }

        private bool IsHttpsEnabled()
        {
            return _configuration.GetValue<bool>("Security:EnforceHttps", true);
        }

        private string BuildContentSecurityPolicy()
        {
            var cspConfig = _configuration.GetSection("Security:ContentSecurityPolicy");
            
            if (!cspConfig.Exists())
            {
                // Default restrictive CSP
                return "default-src 'self'; " +
                       "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; " +
                       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
                       "font-src 'self' https://fonts.gstatic.com; " +
                       "img-src 'self' data: https:; " +
                       "connect-src 'self' wss: https:; " +
                       "frame-ancestors 'none'; " +
                       "base-uri 'self'; " +
                       "form-action 'self';";
            }

            // Build CSP from configuration
            var policies = new List<string>();
            
            foreach (var directive in cspConfig.GetChildren())
            {
                var value = directive.Value;
                if (!string.IsNullOrEmpty(value))
                {
                    policies.Add($"{directive.Key} {value}");
                }
            }
            
            return string.Join("; ", policies);
        }
    }

    public static class SecurityHeadersMiddlewareExtensions
    {
        public static IApplicationBuilder UseSecurityHeaders(this IApplicationBuilder builder)
        {
            return builder.UseMiddleware<SecurityHeadersMiddleware>();
        }
    }
}