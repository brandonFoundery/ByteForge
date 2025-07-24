# ByteForgeFrontend Security System

## Overview

The ByteForgeFrontend security system provides comprehensive security features including multi-tenant authentication, API key management, audit logging, and compliance reporting. This system follows security best practices and supports GDPR and SOC2 compliance requirements.

## Components

### 1. Multi-Tenant Authentication

**Service**: `MultiTenantAuthenticationService`

Features:
- JWT-based authentication with tenant isolation
- Support for cross-tenant access with proper permissions
- Refresh token rotation
- Role-based access control per tenant

Usage:
```csharp
// Authenticate user
var result = await _authService.AuthenticateAsync(email, password, requestedTenantId);

// Validate JWT token
var principal = _authService.ValidateToken(accessToken);

// Get tenant-specific permissions
var permissions = await _authService.GetTenantPermissionsAsync(userId, tenantId);
```

### 2. API Key Management

**Service**: `ApiKeyManagementService`

Features:
- Secure API key generation and storage (AES encryption)
- Support for different key types (LLM Provider, User Access, Service-to-Service)
- Rate limiting per API key
- Key rotation and expiration
- Audit trail for all key operations

Usage:
```csharp
// Create API key
var result = await _apiKeyService.CreateApiKeyAsync(
    tenantId, 
    "OpenAI Integration", 
    "sk-...", 
    ApiKeyType.LLMProvider,
    metadata: new Dictionary<string, string> { ["provider"] = "openai" });

// Validate API key
var validation = await _apiKeyService.ValidateApiKeyAsync(apiKey);

// Rotate API key
var rotateResult = await _apiKeyService.RotateApiKeyAsync(keyId, tenantId);
```

### 3. Audit Logging

**Service**: `AuditLoggingService`

Features:
- Comprehensive logging of all security-relevant events
- Support for different log types (User Actions, API Calls, Security Events)
- Automatic capture of IP address and user agent
- Data retention policies
- Compliance report generation

Usage:
```csharp
// Log user action
await _auditService.LogUserActionAsync(
    userId, tenantId, "CreateProject", "Project", projectId,
    new Dictionary<string, object> { ["projectName"] = name });

// Log security event
await _auditService.LogSecurityEventAsync(
    userId, tenantId, SecurityEventType.FailedLogin,
    new Dictionary<string, object> { ["reason"] = "Invalid password" },
    SecuritySeverity.Medium);

// Get audit statistics
var stats = await _auditService.GetAuditStatisticsAsync(
    tenantId, startDate, endDate);
```

### 4. Compliance Management

**Service**: `ComplianceService`

Features:
- GDPR compliance validation and reporting
- SOC2 control assessment
- Data portability (GDPR Article 20)
- Right to erasure (GDPR Article 17)
- Compliance dashboards and reports
- Scheduled compliance reviews

Usage:
```csharp
// Validate GDPR compliance
var gdprResult = await _complianceService.ValidateGDPRComplianceAsync(tenantId, userId);

// Handle data portability request
var exportResult = await _complianceService.HandleDataPortabilityRequestAsync(tenantId, userId);

// Generate compliance report
var report = await _complianceService.ExportComplianceReportAsync(
    tenantId, ComplianceReportType.Annual, year);
```

## Security Features

### Authentication & Authorization

1. **JWT Tokens**
   - 1-hour access token lifetime
   - 7-day refresh token lifetime
   - Tenant isolation via claims
   - Role-based access control

2. **API Key Authentication**
   - Custom authentication handler
   - Support for header and query parameter
   - Automatic rate limiting
   - Endpoint restrictions

3. **Multi-Factor Authentication**
   - TOTP support (Time-based One-Time Password)
   - Backup codes
   - Per-tenant enforcement

### Data Protection

1. **Encryption**
   - AES-256 encryption for API keys
   - TLS 1.2+ for data in transit
   - Database encryption at rest

2. **Security Headers**
   - Content Security Policy (CSP)
   - X-Frame-Options
   - X-Content-Type-Options
   - Strict-Transport-Security
   - Custom security headers middleware

3. **Rate Limiting**
   - Global rate limits
   - Per-API key limits
   - Configurable windows and thresholds

### Compliance Features

1. **GDPR Compliance**
   - Consent management
   - Data portability exports
   - Right to erasure implementation
   - Privacy policy versioning
   - Audit trail of data processing

2. **SOC2 Compliance**
   - Security control validation
   - Access control policies
   - Audit logging
   - Encryption verification
   - Session management

## Configuration

### appsettings.json

```json
{
  "JwtSettings": {
    "SecretKey": "your-secret-key-at-least-32-characters",
    "Issuer": "ByteForgeFrontend",
    "Audience": "ByteForgeFrontend"
  },
  "Security": {
    "EnforceHttps": true,
    "Password": {
      "MinLength": 12
    },
    "Lockout": {
      "MaxAttempts": 5
    },
    "RateLimit": {
      "Global": {
        "PermitLimit": 100,
        "WindowMinutes": 1
      },
      "ApiKey": {
        "PermitLimit": 1000,
        "WindowMinutes": 60
      }
    },
    "ContentSecurityPolicy": {
      "default-src": "'self'",
      "script-src": "'self' 'unsafe-inline'",
      "style-src": "'self' 'unsafe-inline'",
      "img-src": "'self' data: https:",
      "connect-src": "'self' wss: https:"
    }
  },
  "Encryption": {
    "Key": "base64-encoded-32-byte-key",
    "IV": "base64-encoded-16-byte-iv"
  },
  "AuditLog": {
    "RetentionDays": 2555,
    "EnableDetailedLogging": true
  }
}
```

### Startup Configuration

```csharp
public void ConfigureServices(IServiceCollection services)
{
    // Add security services
    services.AddByteForgeSecurity(Configuration);
    
    // Add rate limiting
    services.AddRateLimiting(Configuration);
    
    // Configure authentication
    services.AddAuthentication()
        .AddJwtBearer()
        .AddApiKeyAuthentication();
}

public void Configure(IApplicationBuilder app)
{
    // Security headers middleware (first)
    app.UseSecurityHeaders();
    
    // Rate limiting
    app.UseRateLimiter();
    
    // Authentication & Authorization
    app.UseAuthentication();
    app.UseAuthorization();
}
```

## Authorization Policies

### Built-in Policies

1. **RequireTenant**: User must belong to a tenant
2. **RequireTenantAdmin**: User must be a tenant administrator
3. **ProjectAccess**: User can access projects
4. **ProjectManagement**: User can manage projects
5. **DocumentGeneration**: User can generate documents
6. **AgentExecution**: User can execute AI agents
7. **ApiKeyAccess**: Request must use valid API key
8. **ServiceApiKey**: Request must use service-to-service key
9. **SystemAdmin**: User must be a super administrator
10. **ComplianceAccess**: User can access compliance features

### Usage in Controllers

```csharp
[Authorize(Policy = "RequireTenant")]
[ApiController]
[Route("api/[controller]")]
public class ProjectsController : ControllerBase
{
    [HttpPost]
    [Authorize(Policy = "ProjectManagement")]
    public async Task<IActionResult> CreateProject([FromBody] CreateProjectRequest request)
    {
        // Implementation
    }

    [HttpGet("{id}")]
    [Authorize(Policy = "ProjectAccess")]
    public async Task<IActionResult> GetProject(string id)
    {
        // Implementation
    }
}
```

## Testing

The security system includes comprehensive unit tests:

1. **MultiTenantAuthenticationTests**
   - Authentication with valid/invalid credentials
   - Cross-tenant access validation
   - Token validation and refresh
   - Permission verification

2. **ApiKeyManagementTests**
   - Key creation and encryption
   - Key validation and rate limiting
   - Key rotation and expiration
   - Audit trail verification

3. **AuditLoggingTests**
   - Event logging for all types
   - Compliance report generation
   - Data retention enforcement
   - Statistics and analytics

4. **ComplianceTests**
   - GDPR compliance validation
   - SOC2 control assessment
   - Data portability and erasure
   - Compliance dashboard generation

## Best Practices

1. **API Keys**
   - Rotate keys regularly
   - Use appropriate key types
   - Set expiration dates
   - Monitor usage patterns

2. **Audit Logging**
   - Log all security-relevant events
   - Include sufficient context
   - Review logs regularly
   - Set appropriate retention periods

3. **Compliance**
   - Regular compliance reviews
   - Keep consent records updated
   - Implement data minimization
   - Document all processing activities

4. **Security Headers**
   - Use restrictive CSP policies
   - Enable HSTS on production
   - Remove server identification headers
   - Test with security scanners

## Monitoring

### Key Metrics

1. **Authentication**
   - Failed login attempts
   - Token refresh rates
   - Cross-tenant access attempts

2. **API Keys**
   - Key usage by type
   - Rate limit violations
   - Expired key access attempts

3. **Compliance**
   - GDPR consent rates
   - Data request volumes
   - Security control gaps

### Alerts

Configure alerts for:
- Multiple failed login attempts
- Unauthorized cross-tenant access
- API key rate limit exceeded
- Compliance violations detected
- Suspicious activity patterns

## Migration Guide

For existing applications:

1. **Database Migration**
   - Add security-related tables
   - Update user model for multi-tenancy
   - Create initial security configuration

2. **Authentication Migration**
   - Replace existing authentication
   - Map existing roles to new system
   - Generate API keys for integrations

3. **Compliance Setup**
   - Enable audit logging
   - Configure retention policies
   - Set up initial compliance reviews

## Support

For security-related issues:
1. Check audit logs for detailed information
2. Review compliance dashboards
3. Verify configuration settings
4. Contact security team for assistance