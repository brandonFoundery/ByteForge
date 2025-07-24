using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;
using ByteForgeFrontend.Models;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;

namespace ByteForgeFrontend.Services.Security.Authentication
{
    public class MultiTenantAuthenticationService : IMultiTenantAuthenticationService
    {
        private readonly UserManager<ApplicationUser> _userManager;
        private readonly IConfiguration _configuration;
        private readonly ILogger<MultiTenantAuthenticationService> _logger;

        public MultiTenantAuthenticationService(
            UserManager<ApplicationUser> userManager,
            IConfiguration configuration,
            ILogger<MultiTenantAuthenticationService> logger = null)
        {
            _userManager = userManager;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task<AuthenticationResult> AuthenticateAsync(string email, string password, string requestedTenantId = null)
        {
            try
            {
                var user = await _userManager.FindByEmailAsync(email);
                if (user == null)
                {
                    return new AuthenticationResult
                    {
                        Success = false,
                        ErrorMessage = "Invalid email or password"
                    };
                }

                var passwordValid = await _userManager.CheckPasswordAsync(user, password);
                if (!passwordValid)
                {
                    return new AuthenticationResult
                    {
                        Success = false,
                        ErrorMessage = "Invalid email or password"
                    };
                }

                // Determine which tenant to authenticate for
                var tenantId = requestedTenantId ?? user.TenantId;

                // Validate tenant access if different from user's primary tenant
                if (!string.IsNullOrEmpty(requestedTenantId) && requestedTenantId != user.TenantId)
                {
                    if (!await ValidateTenantAccessAsync(user.Id, requestedTenantId))
                    {
                        return new AuthenticationResult
                        {
                            Success = false,
                            ErrorMessage = "Access denied to the requested tenant"
                        };
                    }
                }

                // Get user roles
                var roles = await _userManager.GetRolesAsync(user);

                // Generate tokens
                var (accessToken, refreshToken) = await GenerateTokensAsync(user, tenantId, roles);

                // Update refresh token in database
                user.RefreshToken = refreshToken;
                user.RefreshTokenExpiryTime = DateTime.UtcNow.AddDays(7);
                await _userManager.UpdateAsync(user);

                return new AuthenticationResult
                {
                    Success = true,
                    AccessToken = accessToken,
                    RefreshToken = refreshToken,
                    TenantId = tenantId,
                    UserId = user.Id,
                    Roles = roles.ToList()
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error during authentication for {Email}", email);
                return new AuthenticationResult
                {
                    Success = false,
                    ErrorMessage = "An error occurred during authentication"
                };
            }
        }

        public async Task<AuthenticationResult> RefreshTokenAsync(string userId, string refreshToken)
        {
            try
            {
                var user = await _userManager.FindByIdAsync(userId);
                if (user == null || user.RefreshToken != refreshToken || user.RefreshTokenExpiryTime <= DateTime.UtcNow)
                {
                    return new AuthenticationResult
                    {
                        Success = false,
                        ErrorMessage = "Invalid or expired refresh token"
                    };
                }

                var roles = await _userManager.GetRolesAsync(user);
                var (accessToken, newRefreshToken) = await GenerateTokensAsync(user, user.TenantId, roles);

                // Update refresh token
                user.RefreshToken = newRefreshToken;
                user.RefreshTokenExpiryTime = DateTime.UtcNow.AddDays(7);
                await _userManager.UpdateAsync(user);

                return new AuthenticationResult
                {
                    Success = true,
                    AccessToken = accessToken,
                    RefreshToken = newRefreshToken,
                    TenantId = user.TenantId,
                    UserId = user.Id,
                    Roles = roles.ToList()
                };
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error during token refresh for user {UserId}", userId);
                return new AuthenticationResult
                {
                    Success = false,
                    ErrorMessage = "An error occurred during token refresh"
                };
            }
        }

        public ClaimsPrincipal ValidateToken(string token)
        {
            try
            {
                var jwtSettings = _configuration.GetSection("JwtSettings");
                var secretKey = jwtSettings["SecretKey"];
                var issuer = jwtSettings["Issuer"];
                var audience = jwtSettings["Audience"];

                var tokenHandler = new JwtSecurityTokenHandler();
                var validationParameters = new TokenValidationParameters
                {
                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
                    ValidateIssuer = true,
                    ValidIssuer = issuer,
                    ValidateAudience = true,
                    ValidAudience = audience,
                    ValidateLifetime = true,
                    ClockSkew = TimeSpan.Zero
                };

                var principal = tokenHandler.ValidateToken(token, validationParameters, out SecurityToken validatedToken);
                return principal;
            }
            catch (Exception ex)
            {
                _logger?.LogWarning(ex, "Token validation failed");
                return null;
            }
        }

        public async Task<IEnumerable<string>> GetTenantPermissionsAsync(string userId, string tenantId)
        {
            var permissions = new List<string>();
            
            var user = await _userManager.FindByIdAsync(userId);
            if (user == null || !await ValidateTenantAccessAsync(userId, tenantId))
            {
                return permissions;
            }

            var roles = await _userManager.GetRolesAsync(user);
            
            // Map roles to permissions based on tenant
            foreach (var role in roles)
            {
                switch (role)
                {
                    case "TenantAdmin":
                        permissions.AddRange(new[]
                        {
                            "tenant.manage",
                            "tenant.users.read",
                            "tenant.users.write",
                            "tenant.settings.read",
                            "tenant.settings.write",
                            "tenant.billing.read",
                            "tenant.billing.write"
                        });
                        break;
                    case "ProjectManager":
                        permissions.AddRange(new[]
                        {
                            "projects.create",
                            "projects.read",
                            "projects.update",
                            "projects.delete",
                            "documents.generate",
                            "agents.execute"
                        });
                        break;
                    case "Developer":
                        permissions.AddRange(new[]
                        {
                            "projects.read",
                            "documents.read",
                            "agents.view"
                        });
                        break;
                    case "User":
                        permissions.AddRange(new[]
                        {
                            "projects.read",
                            "documents.read"
                        });
                        break;
                    case "SuperAdmin":
                        // Cross-tenant admin permissions
                        permissions.AddRange(new[]
                        {
                            "system.manage",
                            "tenants.manage",
                            "tenants.access.all"
                        });
                        break;
                }
            }

            return permissions.Distinct();
        }

        public async Task<bool> ValidateTenantAccessAsync(string userId, string tenantId)
        {
            var user = await _userManager.FindByIdAsync(userId);
            if (user == null)
            {
                return false;
            }

            // Check if it's the user's primary tenant
            if (user.TenantId == tenantId)
            {
                return true;
            }

            // Check if user has access to multiple tenants
            if (!string.IsNullOrEmpty(user.AllowedTenants))
            {
                var allowedTenants = user.AllowedTenants.Split(',', StringSplitOptions.RemoveEmptyEntries);
                return allowedTenants.Contains(tenantId);
            }

            return false;
        }

        public async Task RevokeAllTokensAsync(string userId, string tenantId)
        {
            var user = await _userManager.FindByIdAsync(userId);
            if (user != null && user.TenantId == tenantId)
            {
                user.RefreshToken = null;
                user.RefreshTokenExpiryTime = DateTime.UtcNow;
                await _userManager.UpdateAsync(user);
                
                // In a production system, you would also:
                // 1. Add the user's current JWT to a blacklist
                // 2. Notify other services to invalidate cached tokens
                // 3. Log the security event
            }
        }

        private async Task<(string accessToken, string refreshToken)> GenerateTokensAsync(
            ApplicationUser user, 
            string tenantId, 
            IList<string> roles)
        {
            var jwtSettings = _configuration.GetSection("JwtSettings");
            var secretKey = jwtSettings["SecretKey"];
            var issuer = jwtSettings["Issuer"];
            var audience = jwtSettings["Audience"];

            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.NameIdentifier, user.Id),
                new Claim(ClaimTypes.Email, user.Email!),
                new Claim(ClaimTypes.Name, user.UserName!),
                new Claim("tenant_id", tenantId),
                new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
                new Claim(JwtRegisteredClaimNames.Iat, 
                    new DateTimeOffset(DateTime.UtcNow).ToUnixTimeSeconds().ToString(), 
                    ClaimValueTypes.Integer64)
            };

            // Add primary tenant if different from requested tenant
            if (user.TenantId != tenantId)
            {
                claims.Add(new Claim("primary_tenant_id", user.TenantId));
            }

            // Add allowed tenants
            if (!string.IsNullOrEmpty(user.AllowedTenants))
            {
                claims.Add(new Claim("allowed_tenants", user.AllowedTenants));
            }

            // Add roles
            foreach (var role in roles)
            {
                claims.Add(new Claim(ClaimTypes.Role, role));
            }

            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var token = new JwtSecurityToken(
                issuer: issuer,
                audience: audience,
                claims: claims,
                expires: DateTime.UtcNow.AddHours(1),
                signingCredentials: creds);

            var accessToken = new JwtSecurityTokenHandler().WriteToken(token);
            var refreshToken = GenerateRefreshToken();

            return (accessToken, refreshToken);
        }

        private string GenerateRefreshToken()
        {
            var randomNumber = new byte[32];
            using var rng = System.Security.Cryptography.RandomNumberGenerator.Create();
            rng.GetBytes(randomNumber);
            return Convert.ToBase64String(randomNumber);
        }
    }
}