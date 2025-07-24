using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Text.Encodings.Web;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;
using Microsoft.AspNetCore.Authentication;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace ByteForgeFrontend.Services.Security.Authentication
{
    public class ApiKeyAuthenticationOptions : AuthenticationSchemeOptions
    {
        public const string DefaultScheme = "ApiKey";
        public string HeaderName { get; set; } = "X-API-Key";
        public string QueryParameterName { get; set; } = "api_key";
    }

    public class ApiKeyAuthenticationHandler : AuthenticationHandler<ApiKeyAuthenticationOptions>
    {
        private readonly IApiKeyManagementService _apiKeyService;

        public ApiKeyAuthenticationHandler(
            IOptionsMonitor<ApiKeyAuthenticationOptions> options,
            ILoggerFactory logger,
            UrlEncoder encoder,
            ISystemClock clock,
            IApiKeyManagementService apiKeyService)
            : base(options, logger, encoder, clock)
        {
            _apiKeyService = apiKeyService;
        }

        protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
        {
            try
            {
                var apiKey = ExtractApiKey();

                if (string.IsNullOrEmpty(apiKey))
                {
                    return AuthenticateResult.NoResult();
                }

                var validationResult = await _apiKeyService.ValidateApiKeyAsync(apiKey);

                if (!validationResult.IsValid)
                {
                    return AuthenticateResult.Fail($"Invalid API key: {validationResult.ErrorMessage}");
                }

                var claims = BuildClaims(validationResult);
                var identity = new ClaimsIdentity(claims, Scheme.Name);
                var principal = new ClaimsPrincipal(identity);
                var ticket = new AuthenticationTicket(principal, Scheme.Name);

                return AuthenticateResult.Success(ticket);
            }
            catch (Exception ex)
            {
                Logger.LogError(ex, "Error during API key authentication");
                return AuthenticateResult.Fail("An error occurred during authentication");
            }
        }

        protected override Task HandleChallengeAsync(AuthenticationProperties properties)
        {
            Response.Headers["WWW-Authenticate"] = $"ApiKey realm=\"{Options.ClaimsIssuer}\", charset=\"UTF-8\"";
            return base.HandleChallengeAsync(properties);
        }

        private string ExtractApiKey()
        {
            // Try to get API key from header
            if (Request.Headers.TryGetValue(Options.HeaderName, out var headerValue))
            {
                return headerValue.ToString();
            }

            // Try to get API key from query parameter
            if (Request.Query.TryGetValue(Options.QueryParameterName, out var queryValue))
            {
                return queryValue.ToString();
            }

            // Try to get API key from Authorization header (Bearer scheme)
            var authorization = Request.Headers["Authorization"].ToString();
            if (!string.IsNullOrEmpty(authorization) && authorization.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
            {
                return authorization.Substring("Bearer ".Length).Trim();
            }

            return null;
        }

        private List<Claim> BuildClaims(ApiKeyValidationResult validationResult)
        {
            var claims = new List<Claim>
            {
                new Claim("api_key", "true"),
                new Claim("tenant_id", validationResult.TenantId)
            };

            if (!string.IsNullOrEmpty(validationResult.UserId))
            {
                claims.Add(new Claim(ClaimTypes.NameIdentifier, validationResult.UserId));
                claims.Add(new Claim("user_api_key", "true"));
            }

            if (!string.IsNullOrEmpty(validationResult.ServiceName))
            {
                claims.Add(new Claim("service_name", validationResult.ServiceName));
                claims.Add(new Claim("service_api_key", "true"));
            }

            if (validationResult.AllowedEndpoints?.Count > 0)
            {
                foreach (var endpoint in validationResult.AllowedEndpoints)
                {
                    claims.Add(new Claim("allowed_endpoint", endpoint));
                }
            }

            return claims;
        }
    }

    public static class ApiKeyAuthenticationExtensions
    {
        public static AuthenticationBuilder AddApiKeyAuthentication(
            this AuthenticationBuilder builder,
            Action<ApiKeyAuthenticationOptions> configureOptions = null)
        {
            return builder.AddScheme<ApiKeyAuthenticationOptions, ApiKeyAuthenticationHandler>(
                ApiKeyAuthenticationOptions.DefaultScheme, 
                configureOptions);
        }

        public static AuthenticationBuilder AddApiKeyAuthentication(
            this AuthenticationBuilder builder,
            string authenticationScheme,
            Action<ApiKeyAuthenticationOptions> configureOptions = null)
        {
            return builder.AddScheme<ApiKeyAuthenticationOptions, ApiKeyAuthenticationHandler>(
                authenticationScheme, 
                configureOptions);
        }
    }
}