using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using ByteForgeFrontend.Models;
using ByteForgeFrontend.Services.Security.Authentication;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using Xunit;

namespace ByteForgeFrontend.Tests.Security.Authentication
{
    public class MultiTenantAuthenticationTests
    {
        private readonly Mock<UserManager<ApplicationUser>> _userManagerMock;
        private readonly Mock<IConfiguration> _configurationMock;
        private readonly MultiTenantAuthenticationService _authService;

        public MultiTenantAuthenticationTests()
        {
            var userStoreMock = new Mock<IUserStore<ApplicationUser>>();
            _userManagerMock = new Mock<UserManager<ApplicationUser>>(
                userStoreMock.Object, null, null, null, null, null, null, null, null);
            
            _configurationMock = new Mock<IConfiguration>();
            
            _authService = new MultiTenantAuthenticationService(
                _userManagerMock.Object,
                _configurationMock.Object);
        }

        [Fact]
        public async Task AuthenticateAsync_WithValidCredentials_ShouldReturnTokenWithTenantClaim()
        {
            // Arrange
            var email = "user@tenant1.com";
            var password = "ValidPassword123!";
            var tenantId = "tenant1";
            
            var user = new ApplicationUser
            {
                Id = "user123",
                Email = email,
                UserName = email,
                TenantId = tenantId
            };

            _userManagerMock.Setup(x => x.FindByEmailAsync(email))
                .ReturnsAsync(user);
            
            _userManagerMock.Setup(x => x.CheckPasswordAsync(user, password))
                .ReturnsAsync(true);
            
            _userManagerMock.Setup(x => x.GetRolesAsync(user))
                .ReturnsAsync(new List<string> { "User" });

            SetupJwtConfiguration();

            // Act
            var result = await _authService.AuthenticateAsync(email, password);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.NotEmpty(result.AccessToken);
            Assert.NotEmpty(result.RefreshToken);
            Assert.Equal(tenantId, result.TenantId);
            
            // Verify tenant claim is included
            var principal = _authService.ValidateToken(result.AccessToken);
            var tenantClaim = principal.FindFirst("tenant_id");
            Assert.NotNull(tenantClaim);
            Assert.Equal(tenantId, tenantClaim.Value);
        }

        [Fact]
        public async Task AuthenticateAsync_WithInvalidPassword_ShouldReturnFailure()
        {
            // Arrange
            var email = "user@tenant1.com";
            var password = "WrongPassword";
            
            var user = new ApplicationUser
            {
                Id = "user123",
                Email = email,
                UserName = email,
                TenantId = "tenant1"
            };

            _userManagerMock.Setup(x => x.FindByEmailAsync(email))
                .ReturnsAsync(user);
            
            _userManagerMock.Setup(x => x.CheckPasswordAsync(user, password))
                .ReturnsAsync(false);

            // Act
            var result = await _authService.AuthenticateAsync(email, password);

            // Assert
            Assert.NotNull(result);
            Assert.False(result.Success);
            Assert.Equal("Invalid email or password", result.ErrorMessage);
        }

        [Fact]
        public async Task AuthenticateAsync_WithCrossTenantAccess_ShouldCheckPermissions()
        {
            // Arrange
            var email = "admin@global.com";
            var password = "ValidPassword123!";
            var primaryTenantId = "global";
            var accessibleTenants = new[] { "tenant1", "tenant2", "tenant3" };
            
            var user = new ApplicationUser
            {
                Id = "admin123",
                Email = email,
                UserName = email,
                TenantId = primaryTenantId,
                AllowedTenants = string.Join(",", accessibleTenants)
            };

            _userManagerMock.Setup(x => x.FindByEmailAsync(email))
                .ReturnsAsync(user);
            
            _userManagerMock.Setup(x => x.CheckPasswordAsync(user, password))
                .ReturnsAsync(true);
            
            _userManagerMock.Setup(x => x.GetRolesAsync(user))
                .ReturnsAsync(new List<string> { "SuperAdmin" });

            SetupJwtConfiguration();

            // Act
            var result = await _authService.AuthenticateAsync(email, password, "tenant2");

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.Equal("tenant2", result.TenantId);
            
            // Verify claims include both primary and requested tenant
            var principal = _authService.ValidateToken(result.AccessToken);
            var requestedTenantClaim = principal.FindFirst("tenant_id");
            var primaryTenantClaim = principal.FindFirst("primary_tenant_id");
            var allowedTenantsClaim = principal.FindFirst("allowed_tenants");
            
            Assert.NotNull(requestedTenantClaim);
            Assert.Equal("tenant2", requestedTenantClaim.Value);
            Assert.NotNull(primaryTenantClaim);
            Assert.Equal(primaryTenantId, primaryTenantClaim.Value);
            Assert.NotNull(allowedTenantsClaim);
            Assert.Contains("tenant2", allowedTenantsClaim.Value);
        }

        [Fact]
        public async Task AuthenticateAsync_WithUnauthorizedTenantAccess_ShouldReturnFailure()
        {
            // Arrange
            var email = "user@tenant1.com";
            var password = "ValidPassword123!";
            var userTenantId = "tenant1";
            var requestedTenantId = "tenant2";
            
            var user = new ApplicationUser
            {
                Id = "user123",
                Email = email,
                UserName = email,
                TenantId = userTenantId,
                AllowedTenants = userTenantId // Only allowed in their own tenant
            };

            _userManagerMock.Setup(x => x.FindByEmailAsync(email))
                .ReturnsAsync(user);
            
            _userManagerMock.Setup(x => x.CheckPasswordAsync(user, password))
                .ReturnsAsync(true);

            // Act
            var result = await _authService.AuthenticateAsync(email, password, requestedTenantId);

            // Assert
            Assert.NotNull(result);
            Assert.False(result.Success);
            Assert.Equal("Access denied to the requested tenant", result.ErrorMessage);
        }

        [Fact]
        public async Task ValidateToken_WithExpiredToken_ShouldReturnNull()
        {
            // Arrange
            var expiredToken = "expired.jwt.token"; // This would be a real expired token in production

            // Act
            var principal = _authService.ValidateToken(expiredToken);

            // Assert
            Assert.Null(principal);
        }

        [Fact]
        public async Task RefreshTokenAsync_WithValidRefreshToken_ShouldReturnNewTokens()
        {
            // Arrange
            var userId = "user123";
            var refreshToken = "valid-refresh-token";
            var tenantId = "tenant1";
            
            var user = new ApplicationUser
            {
                Id = userId,
                Email = "user@tenant1.com",
                UserName = "user@tenant1.com",
                TenantId = tenantId,
                RefreshToken = refreshToken,
                RefreshTokenExpiryTime = DateTime.UtcNow.AddDays(7)
            };

            _userManagerMock.Setup(x => x.FindByIdAsync(userId))
                .ReturnsAsync(user);
            
            _userManagerMock.Setup(x => x.GetRolesAsync(user))
                .ReturnsAsync(new List<string> { "User" });
            
            _userManagerMock.Setup(x => x.UpdateAsync(It.IsAny<ApplicationUser>()))
                .ReturnsAsync(IdentityResult.Success);

            SetupJwtConfiguration();

            // Act
            var result = await _authService.RefreshTokenAsync(userId, refreshToken);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Success);
            Assert.NotEmpty(result.AccessToken);
            Assert.NotEmpty(result.RefreshToken);
            Assert.NotEqual(refreshToken, result.RefreshToken); // Should be a new refresh token
        }

        [Fact]
        public async Task GetTenantPermissionsAsync_ShouldReturnTenantSpecificPermissions()
        {
            // Arrange
            var userId = "user123";
            var tenantId = "tenant1";
            
            var user = new ApplicationUser
            {
                Id = userId,
                TenantId = tenantId
            };

            _userManagerMock.Setup(x => x.FindByIdAsync(userId))
                .ReturnsAsync(user);
            
            _userManagerMock.Setup(x => x.GetRolesAsync(user))
                .ReturnsAsync(new List<string> { "TenantAdmin" });

            // Act
            var permissions = await _authService.GetTenantPermissionsAsync(userId, tenantId);

            // Assert
            Assert.NotNull(permissions);
            Assert.Contains("tenant.manage", permissions);
            Assert.Contains("tenant.users.read", permissions);
            Assert.Contains("tenant.users.write", permissions);
            Assert.Contains("tenant.settings.read", permissions);
            Assert.Contains("tenant.settings.write", permissions);
        }

        private void SetupJwtConfiguration()
        {
            var jwtSection = new Mock<IConfigurationSection>();
            jwtSection.Setup(x => x["SecretKey"]).Returns("super-secret-key-for-testing-that-is-at-least-32-characters");
            jwtSection.Setup(x => x["Issuer"]).Returns("ByteForgeFrontend");
            jwtSection.Setup(x => x["Audience"]).Returns("ByteForgeFrontend");
            
            _configurationMock.Setup(x => x.GetSection("JwtSettings"))
                .Returns(jwtSection.Object);
        }
    }
}