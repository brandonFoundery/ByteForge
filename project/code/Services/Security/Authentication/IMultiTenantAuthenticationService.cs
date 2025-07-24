using System.Security.Claims;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace ByteForgeFrontend.Services.Security.Authentication
{
    public interface IMultiTenantAuthenticationService
    {
        Task<AuthenticationResult> AuthenticateAsync(string email, string password, string requestedTenantId = null);
        Task<AuthenticationResult> RefreshTokenAsync(string userId, string refreshToken);
        ClaimsPrincipal ValidateToken(string token);
        Task<IEnumerable<string>> GetTenantPermissionsAsync(string userId, string tenantId);
        Task<bool> ValidateTenantAccessAsync(string userId, string tenantId);
        Task RevokeAllTokensAsync(string userId, string tenantId);
    }

    public class AuthenticationResult
    {
        public bool Success { get; set; }
        public string AccessToken { get; set; }
        public string RefreshToken { get; set; }
        public string TenantId { get; set; }
        public string UserId { get; set; }
        public List<string> Roles { get; set; } = new List<string>();
        public string ErrorMessage { get; set; }
    }
}