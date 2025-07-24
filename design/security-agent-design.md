---
agent_type: Security Agent
branch_pattern: feature/security-*
technology_stack: ASP.NET Core Identity, JWT, Azure AD, Azure Key Vault
dependencies: [Core Agent, Database Agent]
generated_at: '2025-07-23T18:05:35'
id: SECURITY_AGENT_DESIGN
version: '1.0'
---

# Security Agent Design Document

## 1. Agent Overview

### 1.1 Role and Responsibilities
The Security Agent is a specialized AI agent responsible for implementing security-related features in the enterprise software application. Its primary responsibilities include:
- Handling user authentication using modern standards like JWT and integration with Azure AD.
- Managing authorization, including role-based access control (RBAC) and policy enforcement.
- Implementing audit trails to log security events, user actions, and system changes for compliance purposes.
- Ensuring data protection through secure storage of secrets using Azure Key Vault.
- Enforcing compliance with standards such as GDPR, HIPAA, or custom enterprise policies by integrating security checks into the application lifecycle.

The agent ensures that all security implementations are robust, scalable, and integrated seamlessly with other parts of the system, reducing vulnerabilities and maintaining trust.

### 1.2 Scope of Work
The scope includes developing backend services, middleware, and APIs for security features. It covers:
- Authentication endpoints (login, logout, token refresh).
- Authorization guards and policies.
- Audit logging mechanisms integrated with database storage.
- Secret management for API keys, connection strings, and certificates.
- Integration with external identity providers like Azure AD.
- Exclusion: Frontend UI components (handled by UI Agent) and non-security database schemas (handled by Database Agent).

The agent will work on features assigned from the development plan, focusing on the `feature/security-*` branch pattern.

### 1.3 Technology Stack
- **ASP.NET Core Identity**: For user management, roles, and claims-based authentication.
- **JWT (JSON Web Tokens)**: For stateless authentication and token-based authorization.
- **Azure AD**: For enterprise-grade identity and access management, including single sign-on (SSO).
- **Azure Key Vault**: For secure storage and retrieval of secrets, keys, and certificates.
- Supporting technologies: Entity Framework Core for audit data persistence, Serilog or NLog for logging, and xUnit for unit testing.

## 2. Feature Assignments from Development Plan
Based on the development plan (extracted from dev_plan.md), the following security-related features are assigned to this agent, organized by phase. These features align with the agent's description for authentication, authorization, audit trails, and compliance.

### Phase 1: Foundation (Weeks 1-2)
- Implement basic user authentication using ASP.NET Core Identity and JWT.
- Integrate Azure AD for external authentication.
- Set up Azure Key Vault for secret management.

### Phase 2: Core Security (Weeks 3-4)
- Develop role-based authorization (RBAC) with claims and policies.
- Implement audit trail logging for user actions and security events.

### Phase 3: Advanced Features and Compliance (Weeks 5-6)
- Add multi-factor authentication (MFA) support via Azure AD.
- Implement compliance checks (e.g., data encryption enforcement, access revocation).
- Integrate audit trails with reporting endpoints for compliance audits.

### Phase 4: Optimization and Testing (Weeks 7-8)
- Optimize token validation and refresh mechanisms.
- Implement security monitoring and alerting for anomalies.

## 3. Branch Strategy and Workflow

### 3.1 Branch Naming Convention
All work for this agent must follow the `feature/security-*` pattern. Examples:
- `feature/security-authentication-setup`: For initial authentication implementation.
- `feature/security-audit-trails`: For audit logging features.
- `feature/security-compliance-checks`: For compliance-related enhancements.
Branches should be short-lived, merged into `develop` after peer review and testing.

### 3.2 Development Workflow
1. **Branch Creation**: Create a new branch from `develop` using the naming convention.
2. **Implementation**: Use Claude Code to generate code based on prompts in Section 7. Commit changes with descriptive messages (e.g., "Implement JWT authentication endpoint").
3. **Testing**: Run unit tests, integration tests, and security scans (e.g., OWASP ZAP).
4. **Pull Request (PR)**: Submit PR to `develop` with details on features implemented, tests passed, and any dependencies.
5. **Merge and Cleanup**: After approval, merge and delete the branch. Resolve conflicts with dependent agents (e.g., Core Agent).
6. **Iteration**: If issues arise, create bugfix branches like `bugfix/security-token-validation`.

## 4. Technical Architecture
The Security Agent's architecture is built on ASP.NET Core, emphasizing modularity and security best practices.

- **Layers**:
  - **API Layer**: Exposes endpoints like `/api/auth/login`, `/api/auth/refresh-token` using controllers secured with `[Authorize]` attributes.
  - **Service Layer**: Contains business logic, e.g., `AuthenticationService` for token generation/validation, `AuditService` for logging events.
  - **Data Access Layer**: Uses Entity Framework Core to interact with audit databases; integrates with ASP.NET Core Identity's `UserManager` and `RoleManager`.
  - **Middleware**: Custom middleware for JWT validation, Azure AD token handling, and audit logging on requests.

- **Key Components**:
  - **Authentication Flow**: User logs in via Azure AD or local credentials → Generate JWT with claims → Store in client → Validate on API calls.
  - **Authorization**: Policies defined in `Startup.cs` (e.g., `RequireRole("Admin")`), checked via `IAuthorizationService`.
  - **Audit Trails**: Intercept requests/responses with middleware, log to database with details (user ID, action, timestamp, IP).
  - **Secret Management**: Use `AzureKeyVaultClient` to fetch secrets during app startup, injected via dependency injection.

- **Diagrams** (Conceptual):
  - Authentication Sequence: Client → API → Azure AD → JWT Issuance → Client Storage.
  - Audit Flow: Request → Middleware → Log to DB → Response.

- **Scalability and Security**: Stateless JWT for horizontal scaling; rate limiting to prevent brute-force attacks; encryption at rest using Azure services.

## 5. Dependencies and Integration Points
- **Internal Dependencies**:
  - **Core Agent**: Relies on core application services for startup configuration and shared utilities (e.g., app settings).
  - **Database Agent**: Depends on database schemas for user storage and audit logs; integrates via shared EF Core contexts.

- **External Dependencies**:
  - Azure AD for identity federation.
  - Azure Key Vault for secret retrieval.
  - External libraries: Microsoft.AspNetCore.Identity, System.IdentityModel.Tokens.Jwt, Azure.Identity.

- **Integration Points**:
  - API hooks: Security services injected into other agents' controllers (e.g., via NuGet packages).
  - Event-driven: Publish security events (e.g., login failures) to a message bus for other agents to consume.
  - Configuration: Shared `appsettings.json` for Azure endpoints.

## 6. Implementation Plan by Phase
The implementation is divided into phases aligned with the development plan, with estimated timelines assuming a 2-week sprint per phase.

### Phase 1: Foundation (Weeks 1-2)
- Set up ASP.NET Core Identity in the project.
- Implement JWT authentication and Azure AD integration.
- Configure Azure Key Vault.
- Timeline: Complete by end of Week 2; milestones: Working login endpoint.

### Phase 2: Core Security (Weeks 3-4)
- Add RBAC policies and claims.
- Develop audit logging service and middleware.
- Timeline: Complete by end of Week 4; milestones: Authorized API calls and logged events.

### Phase 3: Advanced Features and Compliance (Weeks 5-6)
- Integrate MFA and compliance enforcement.
- Build audit reporting APIs.
- Timeline: Complete by end of Week 6; milestones: MFA-enabled auth and compliance reports.

### Phase 4: Optimization and Testing (Weeks 7-8)
- Optimize performance (e.g., caching tokens).
- Implement monitoring and full testing suite.
- Timeline: Complete by end of Week 8; milestones: 100% test coverage, security audit passed.

## 7. Claude Code Instructions

### 7.1 Context Files Required
- Project structure: `--add-dir src` (includes all source code directories).
- Configuration files: `appsettings.json`, `Startup.cs`, `Program.cs`.
- Dependency files: `*.csproj` for package references.
- Existing security files: If any, add `--add-dir src/Security` for partial implementations.

### 7.2 Implementation Prompts
Use Claude Code with specific prompts for each feature. Examples:

- For authentication setup: `claude code --add-dir src -p 'Implement ASP.NET Core Identity with JWT authentication in Startup.cs. Include Azure AD configuration and token generation in AuthenticationService.cs. Ensure compatibility with Database Agent schemas.'`
- For authorization: `claude code --add-dir src -p 'Add role-based authorization policies in Startup.cs. Create AuthorizationService.cs with methods to check claims and roles using ASP.NET Core Identity.'`
- For audit trails: `claude code --add-dir src -p 'Implement AuditMiddleware.cs to log requests to the database. Integrate with Entity Framework Core from Database Agent. Log user ID, action, timestamp, and IP.'`
- For Key Vault: `claude code --add-dir src -p 'Configure Azure Key Vault in Program.cs to load secrets like connection strings and API keys. Use Azure.Identity for authentication.'`
- For compliance: `claude code --add-dir src -p 'Add compliance checks in services, such as encryption enforcement and access revocation logic, integrated with Azure AD.'`

### 7.3 Validation Criteria
- Code compiles without errors.
- Unit tests pass (e.g., `dotnet test`).
- Security scans (e.g., no hard-coded secrets, proper token validation).
- Integration tests: Successful login with JWT, authorization denials for invalid roles, audit logs persisted.
- Review: Code adheres to SOLID principles, follows naming conventions, and includes comments.

## 8. Success Metrics and Testing
- **Success Metrics**:
  - 95% code coverage for security features.
  - Zero high-severity vulnerabilities in scans (e.g., using SonarQube or OWASP tools).
  - Performance: Authentication latency < 500ms; audit logging adds < 10% overhead.
  - Compliance: All features pass simulated audits (e.g., log completeness for 100% of actions).

- **Testing Criteria**:
  - **Unit Tests**: Test individual methods (e.g., token validation, policy checks) using xUnit and Moq.
  - **Integration Tests**: End-to-end flows (e.g., login → authorized API call → audit log) with TestServer.
  - **Security Tests**: Penetration testing for common attacks (e.g., SQL injection, token forgery) using tools like Burp Suite.
  - **Load Tests**: Simulate 1000 concurrent logins to ensure scalability.
  - **Manual Validation**: Verify Azure AD SSO, Key Vault secret retrieval, and compliance reports in a staging environment.