using Microsoft.AspNetCore.Identity;
using System.Collections.Generic;
using ByteForgeFrontend.Models.Security;

using System;
namespace ByteForgeFrontend.Models;

public class ApplicationUser : IdentityUser
{
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;
    public string? RefreshToken { get; set; }
    public DateTime RefreshTokenExpiryTime { get; set; }
    
    // Multi-tenant support
    public string TenantId { get; set; }
    public string AllowedTenants { get; set; } // Comma-separated list for cross-tenant access
    
    // GDPR compliance
    public bool DataProcessingConsent { get; set; }
    public DateTime? DataProcessingConsentDate { get; set; }
    public bool MarketingConsent { get; set; }
    public DateTime? MarketingConsentDate { get; set; }
    public DateTime? LastPrivacyPolicyAcceptance { get; set; }
    
    // Two-factor authentication
    public bool TwoFactorRequired { get; set; }
    public string TwoFactorSecret { get; set; }
    
    // Navigation properties
    public virtual ICollection<ApiKey> ApiKeys { get; set; } = new List<ApiKey>();
}