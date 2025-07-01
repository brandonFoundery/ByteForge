#!/usr/bin/env python3
"""
Enhance Claude Code Instructions

This script enhances the generated Claude Code instruction files with detailed,
specific content based on the design documents and requirements. It creates
comprehensive, actionable instructions for each agent/phase combination.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from rich.console import Console

console = Console()


class ClaudeInstructionEnhancer:
    """Enhances Claude Code instruction files with detailed content"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.instructions_path = base_path / "generated_documents" / "design" / "claude_instructions"
        self.design_path = base_path / "generated_documents" / "design"
        
        # Load design documents for context
        self.design_docs = self._load_design_documents()

    def _load_design_documents(self) -> Dict[str, str]:
        """Load all design documents for context"""
        design_docs = {}
        
        design_files = [
            "backend-agent-design.md",
            "frontend-agent-design.md", 
            "security-agent-design.md",
            "infrastructure-agent-design.md",
            "integration-agent-design.md"
        ]
        
        for file_name in design_files:
            file_path = self.design_path / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    design_docs[file_name] = f.read()
                console.print(f"[dim]📖 Loaded design document: {file_name}[/dim]")
        
        return design_docs

    def enhance_all_instructions(self) -> bool:
        """Enhance all instruction files with detailed content"""
        try:
            console.print("[bold blue]🔧 Enhancing Claude Code Instructions[/bold blue]")
            console.print("[dim]Adding detailed, specific content to each instruction file[/dim]\n")
            
            # Define the instruction enhancements
            enhancements = {
                "backend-phase1-mvp-core-features.md": self._get_backend_phase1_content(),
                "frontend-phase1-mvp-core-features.md": self._get_frontend_phase1_content(),
                "security-phase1-mvp-core-features.md": self._get_security_phase1_content(),
                "infrastructure-phase1-mvp-core-features.md": self._get_infrastructure_phase1_content(),
                "integration-phase1-mvp-core-features.md": self._get_integration_phase1_content(),
            }
            
            # Apply enhancements
            for filename, content in enhancements.items():
                self._enhance_instruction_file(filename, content)
            
            console.print("\n[bold green]✅ All instruction files enhanced successfully![/bold green]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ Failed to enhance instructions: {e}[/bold red]")
            return False

    def _enhance_instruction_file(self, filename: str, enhanced_content: str):
        """Replace an instruction file with enhanced content"""
        file_path = self.instructions_path / filename
        
        # Backup original
        backup_path = file_path.with_suffix('.md.backup')
        if file_path.exists():
            import shutil
            shutil.copy2(file_path, backup_path)
        
        # Write enhanced content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        console.print(f"[green]✨ Enhanced: {filename}[/green]")

    def _get_backend_phase1_content(self) -> str:
        """Get enhanced content for backend phase 1"""
        return '''# Backend Agent - Phase 1: MVP Core Features

## Agent Information
- **Agent ID**: backend-phase1
- **Phase**: MVP Core Features
- **Estimated Duration**: 60 minutes
- **Dependencies**: None (Foundation agent - MUST complete first)
- **Can Run Parallel With**: None

## Mission Statement
Implement the foundational backend infrastructure for FY.WB.Midway, including core data models, basic CRUD operations, authentication infrastructure, and essential API endpoints. This is the foundation that all other agents depend on.

## Context Documents Required
You have access to the following context documents in the repository:

### Primary Requirements
- `generated_documents/prd.md` - Product Requirements Document
- `generated_documents/FRD.md` - Functional Requirements Document  
- `generated_documents/NFRD.md` - Non-Functional Requirements Document
- `generated_documents/brd.md` - Business Requirements Document
- `generated_documents/DRD.md` - Data Requirements Document

### Technical Specifications
- `generated_documents/dev_plan.md` - Development Plan
- `generated_documents/db_schema.md` - Database Schema
- `generated_documents/api_spec.md` - API Specification
- `generated_documents/trd.md` - Technical Requirements Document

### Design Documents
- `generated_documents/design/backend-agent-design.md` - Your specific design document
- `CLAUDE.md` - Project structure and development guidelines

## Specific Deliverables

### 1. Core Data Models (Priority: CRITICAL)
Create the following entity classes in `BackEnd.Domain/Entities/`:

#### Required Entities
- **Client.cs** - Customer/client management
- **Load.cs** - Load/shipment tracking  
- **Invoice.cs** - Invoice processing and management
- **Carrier.cs** - Carrier/transportation provider management
- **User.cs** - User authentication and management
- **AuditLog.cs** - System audit trail

#### Entity Requirements
- Implement proper inheritance from base entity classes
- Include all required properties per database schema
- Add proper navigation properties for relationships
- Include data annotations for validation
- Follow Clean Architecture patterns

### 2. Database Context and Configuration
Create/update the following in `BackEnd.Infrastructure/Persistence/`:

#### Required Files
- **ApplicationDbContext.cs** - Main EF Core context
- **Configurations/ClientConfiguration.cs** - Client entity configuration
- **Configurations/LoadConfiguration.cs** - Load entity configuration
- **Configurations/InvoiceConfiguration.cs** - Invoice entity configuration
- **Configurations/CarrierConfiguration.cs** - Carrier entity configuration
- **Configurations/UserConfiguration.cs** - User entity configuration

#### Database Migration
- Create initial migration with all core entities
- Ensure proper foreign key relationships
- Include seed data for development

### 3. Repository Pattern Implementation
Create repositories in `BackEnd.Infrastructure/Persistence/`:

#### Required Repositories
- **IClientRepository.cs** and **ClientRepository.cs**
- **ILoadRepository.cs** and **LoadRepository.cs**
- **IInvoiceRepository.cs** and **InvoiceRepository.cs**
- **ICarrierRepository.cs** and **CarrierRepository.cs**
- **IUserRepository.cs** and **UserRepository.cs**

### 4. CQRS Implementation
Create commands and queries in `BackEnd.Application/`:

#### Client Operations
- **Commands/CreateClientCommand.cs**
- **Commands/UpdateClientCommand.cs**
- **Commands/DeleteClientCommand.cs**
- **Queries/GetClientQuery.cs**
- **Queries/GetClientsQuery.cs**

#### Load Operations
- **Commands/CreateLoadCommand.cs**
- **Commands/UpdateLoadCommand.cs**
- **Queries/GetLoadQuery.cs**
- **Queries/GetLoadsQuery.cs**

#### Similar patterns for Invoice, Carrier, and User entities

### 5. API Controllers
Create controllers in `BackEnd/Controllers/`:

#### Required Controllers
- **ClientsController.cs** - Client management endpoints
- **LoadsController.cs** - Load management endpoints
- **InvoicesController.cs** - Invoice management endpoints
- **CarriersController.cs** - Carrier management endpoints
- **AuthController.cs** - Authentication endpoints

#### Controller Requirements
- Follow RESTful conventions
- Implement proper HTTP status codes
- Include input validation
- Add proper error handling
- Use MediatR for CQRS pattern

### 6. Authentication Infrastructure
Implement JWT-based authentication:

#### Required Components
- **Services/JwtService.cs** - JWT token generation and validation
- **Middleware/AuthenticationMiddleware.cs** - Custom auth middleware
- **Models/LoginRequest.cs** and **LoginResponse.cs**
- **Models/RegisterRequest.cs**

#### Authentication Features
- User registration and login
- JWT token generation
- Token validation middleware
- Password hashing and validation
- Basic role-based authorization

## Build, Test, and Fix Process

### 1. Build Process
```bash
cd BackEnd
dotnet restore
dotnet build
```

### 2. Database Setup
```bash
cd BackEnd
dotnet ef migrations add InitialCreate
dotnet ef database update
```

### 3. Testing Requirements
- Create unit tests for all repositories
- Create integration tests for API endpoints
- Test authentication flow end-to-end
- Verify database operations work correctly

### 4. Bug Fix Process
If build or tests fail:
1. Analyze error messages carefully
2. Check for missing dependencies or references
3. Verify entity configurations are correct
4. Ensure proper dependency injection setup
5. Fix issues and re-run tests
6. Document any significant fixes

## Completion Criteria

### Code Deliverables ✓
- [ ] All entity classes created with proper relationships
- [ ] Database context and configurations implemented
- [ ] Repository pattern fully implemented
- [ ] CQRS commands and queries created
- [ ] API controllers with all CRUD endpoints
- [ ] Authentication infrastructure complete

### Build Success ✓
- [ ] Solution builds without errors
- [ ] All NuGet packages restore successfully
- [ ] Database migration creates successfully
- [ ] No compilation warnings for new code

### Test Results ✓
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Authentication flow works end-to-end
- [ ] Database operations function correctly
- [ ] API endpoints return expected responses

### Documentation ✓
- [ ] Update README.md with setup instructions
- [ ] Document API endpoints in api_spec.md
- [ ] Add inline code documentation
- [ ] Update database schema documentation

## Completion Report Template

When you complete this phase, provide a structured report:

```markdown
# Backend Phase 1 Completion Report

## Summary
[Brief summary of work completed]

## Deliverables Completed
- [x] Core data models: Client, Load, Invoice, Carrier, User, AuditLog
- [x] Database context and entity configurations
- [x] Repository pattern implementation
- [x] CQRS commands and queries
- [x] API controllers with CRUD operations
- [x] JWT authentication infrastructure

## Build Results
- Build Status: SUCCESS/FAILED
- Test Results: X/Y tests passed
- Migration Status: SUCCESS/FAILED

## API Endpoints Available
- GET/POST/PUT/DELETE /api/clients
- GET/POST/PUT/DELETE /api/loads
- GET/POST/PUT/DELETE /api/invoices
- GET/POST/PUT/DELETE /api/carriers
- POST /api/auth/login
- POST /api/auth/register

## Known Issues
[List any known issues or limitations]

## Next Steps for Dependent Agents
- Frontend can now integrate with these API endpoints
- Security agent can extend the authentication system
- Infrastructure agent can containerize this backend

## Files Created/Modified
[List of all files created or modified]

## Database Schema
[Confirm database schema matches requirements]
```

## Error Handling and Recovery

### Common Issues and Solutions
1. **Entity Framework Issues**: Check connection strings and entity configurations
2. **Dependency Injection**: Ensure all services are registered in Program.cs
3. **Authentication Issues**: Verify JWT configuration and middleware order
4. **Database Migration Issues**: Check for conflicting migrations or schema issues

### Recovery Process
If critical errors occur:
1. Document the error in detail
2. Attempt automated fixes for common issues
3. If unable to resolve, mark as failed with detailed error log
4. Provide recommendations for manual intervention

## Success Metrics
- All API endpoints functional and tested
- Authentication system working
- Database operations successful
- Clean build with no errors
- Comprehensive test coverage
- Ready for frontend integration

**IMPORTANT**: This is the foundation phase. All other agents depend on your successful completion. Take time to ensure quality and completeness before marking as complete.

**COMPLETION SIGNAL**: When finished, respond with "BACKEND-PHASE1-COMPLETE" followed by your completion report.
'''

    def _get_frontend_phase1_content(self) -> str:
        """Get enhanced content for frontend phase 1"""
        return '''# Frontend Agent - Phase 1: MVP Core Features

## Agent Information
- **Agent ID**: frontend-phase1
- **Phase**: MVP Core Features
- **Estimated Duration**: 45 minutes
- **Dependencies**: backend-phase1 (MUST be completed first)
- **Can Run Parallel With**: security-phase1, infrastructure-phase1

## Mission Statement
Implement the core frontend user interface for FY.WB.Midway using Next.js and React, including dashboard layout, basic forms, authentication UI, and integration with the backend APIs created by the backend-phase1 agent.

## Context Documents Required
You have access to the following context documents in the repository:

### Primary Requirements
- `generated_documents/prd.md` - Product Requirements Document
- `generated_documents/FRD.md` - Functional Requirements Document
- `generated_documents/uiux_spec.md` - UI/UX Specifications

### Technical Specifications
- `generated_documents/dev_plan.md` - Development Plan
- `generated_documents/api_spec.md` - API Specification (for backend integration)

### Design Documents
- `generated_documents/design/frontend-agent-design.md` - Your specific design document
- `generated_documents/design/backend-agent-design.md` - Backend API reference
- `CLAUDE.md` - Project structure and development guidelines

### Backend Context (Dependencies)
- Backend APIs from backend-phase1 agent:
  - `/api/clients` - Client management
  - `/api/loads` - Load management
  - `/api/invoices` - Invoice management
  - `/api/carriers` - Carrier management
  - `/api/auth/login` - Authentication
  - `/api/auth/register` - User registration

## Specific Deliverables

### 1. Core Layout and Navigation (Priority: CRITICAL)
Create the main application structure in `FrontEnd/src/`:

#### Required Components
- **components/Layout/MainLayout.tsx** - Main application layout
- **components/Layout/Sidebar.tsx** - Navigation sidebar
- **components/Layout/Header.tsx** - Top navigation header
- **components/Layout/Footer.tsx** - Application footer

#### Layout Requirements
- Responsive design using Tailwind CSS
- Clean, professional appearance
- Navigation menu with main sections:
  - Dashboard
  - Load Management
  - Client Management
  - Carrier Management
  - Invoice Processing
  - Reports (placeholder)

### 2. Authentication System (Priority: CRITICAL)
Create authentication components in `FrontEnd/src/components/Auth/`:

#### Required Components
- **LoginForm.tsx** - User login form
- **RegisterForm.tsx** - User registration form
- **AuthProvider.tsx** - Authentication context provider
- **ProtectedRoute.tsx** - Route protection component

#### Authentication Features
- Login form with email/password
- Registration form with validation
- JWT token management
- Automatic token refresh
- Protected route handling
- Logout functionality

### 3. Dashboard Components (Priority: HIGH)
Create dashboard in `FrontEnd/src/components/Dashboard/`:

#### Required Components
- **DashboardLayout.tsx** - Main dashboard container
- **DashboardStats.tsx** - Key metrics display
- **RecentActivity.tsx** - Recent activity feed
- **QuickActions.tsx** - Quick action buttons

#### Dashboard Features
- Overview of key metrics (loads, clients, invoices)
- Recent activity timeline
- Quick access to common actions
- Responsive grid layout

### 4. Load Management (Priority: HIGH)
Create load management in `FrontEnd/src/components/LoadManagement/`:

#### Required Components
- **LoadList.tsx** - List of all loads
- **LoadForm.tsx** - Create/edit load form
- **LoadDetail.tsx** - Detailed load view
- **LoadCard.tsx** - Individual load card component

#### Load Management Features
- Display list of loads with filtering
- Create new load form
- Edit existing loads
- View load details
- Load status tracking

### 5. Client Management (Priority: HIGH)
Create client management in `FrontEnd/src/components/ClientManagement/`:

#### Required Components
- **ClientList.tsx** - List of all clients
- **ClientForm.tsx** - Create/edit client form
- **ClientDetail.tsx** - Detailed client view
- **ClientCard.tsx** - Individual client card component

### 6. API Integration Layer (Priority: CRITICAL)
Create API services in `FrontEnd/src/services/`:

#### Required Services
- **api.ts** - Base API configuration with axios
- **authService.ts** - Authentication API calls
- **clientService.ts** - Client CRUD operations
- **loadService.ts** - Load CRUD operations
- **carrierService.ts** - Carrier CRUD operations
- **invoiceService.ts** - Invoice CRUD operations

#### API Integration Features
- Axios configuration with base URL
- JWT token interceptors
- Error handling and retry logic
- Type-safe API calls with TypeScript
- Loading states and error states

## Build, Test, and Fix Process

### 1. Build Process
```bash
cd FrontEnd
npm install
npm run build
npm run dev
```

### 2. Testing Requirements
- Test all components render without errors
- Test authentication flow works with backend
- Test API integration with backend endpoints
- Test responsive design on different screen sizes
- Test form validation and error handling

### 3. Integration Testing
- Verify login/logout works with backend JWT
- Test CRUD operations for all entities
- Verify protected routes work correctly
- Test error handling for API failures

## Completion Criteria

### Code Deliverables ✓
- [ ] Main layout and navigation components
- [ ] Authentication system with login/register
- [ ] Dashboard with key metrics
- [ ] Load management CRUD interface
- [ ] Client management CRUD interface
- [ ] API integration layer complete

### Build Success ✓
- [ ] Application builds without errors
- [ ] All dependencies install successfully
- [ ] Development server starts without issues
- [ ] No TypeScript compilation errors

### Test Results ✓
- [ ] All components render correctly
- [ ] Authentication flow works end-to-end
- [ ] API integration functions properly
- [ ] Forms validate and submit correctly
- [ ] Responsive design works on mobile/desktop

## Completion Report Template

```markdown
# Frontend Phase 1 Completion Report

## Summary
[Brief summary of work completed]

## Deliverables Completed
- [x] Main layout and navigation system
- [x] Authentication UI (login/register)
- [x] Dashboard with metrics display
- [x] Load management interface
- [x] Client management interface
- [x] API integration layer

## Build Results
- Build Status: SUCCESS/FAILED
- Development Server: RUNNING/FAILED
- TypeScript Compilation: SUCCESS/FAILED

## Features Implemented
- User authentication with JWT
- CRUD operations for all main entities
- Responsive design with Tailwind CSS
- Protected routing
- Error handling and loading states

## API Integration Status
- Authentication endpoints: WORKING/FAILED
- Client endpoints: WORKING/FAILED
- Load endpoints: WORKING/FAILED
- Carrier endpoints: WORKING/FAILED
- Invoice endpoints: WORKING/FAILED

## Known Issues
[List any known issues or limitations]

## Next Steps for Integration Agent
- Frontend is ready for end-to-end integration testing
- All API endpoints are integrated and functional
- Authentication flow is complete
```

**IMPORTANT**: Ensure backend-phase1 is completed before starting. Your work depends on the API endpoints created by the backend agent.

**COMPLETION SIGNAL**: When finished, respond with "FRONTEND-PHASE1-COMPLETE" followed by your completion report.
'''

    def _get_security_phase1_content(self) -> str:
        """Get enhanced content for security phase 1"""
        return '''# Security Agent - Phase 1: MVP Core Features

## Agent Information
- **Agent ID**: security-phase1
- **Phase**: MVP Core Features
- **Estimated Duration**: 30 minutes
- **Dependencies**: backend-phase1 (MUST be completed first)
- **Can Run Parallel With**: frontend-phase1, infrastructure-phase1

## Mission Statement
Enhance and secure the authentication infrastructure created by the backend-phase1 agent, implementing comprehensive JWT security, role-based access control, audit logging, and security middleware for the FY.WB.Midway application.

## Context Documents Required
You have access to the following context documents in the repository:

### Primary Requirements
- `generated_documents/NFRD.md` - Non-Functional Requirements (Security focus)
- `generated_documents/trd_security.md` - Security Technical Requirements

### Technical Specifications
- `generated_documents/dev_plan.md` - Development Plan
- `generated_documents/api_spec.md` - API Specification

### Design Documents
- `generated_documents/design/security-agent-design.md` - Your specific design document
- `generated_documents/design/backend-agent-design.md` - Backend foundation reference
- `CLAUDE.md` - Project structure and development guidelines

### Backend Context (Dependencies)
- Authentication infrastructure from backend-phase1:
  - Basic JWT service
  - User entity and authentication
  - Auth controller endpoints
  - Authentication middleware

## Specific Deliverables

### 1. Enhanced JWT Security (Priority: CRITICAL)
Enhance the JWT service in `BackEnd/Services/`:

#### Enhanced JwtService.cs
- **Token Expiration Management**: Configurable access and refresh tokens
- **Token Revocation**: Blacklist mechanism for revoked tokens
- **Secure Token Generation**: Strong random secrets and proper algorithms
- **Token Validation**: Comprehensive validation with proper error handling
- **Refresh Token Logic**: Secure refresh token rotation

#### Required Features
- Access tokens (15-30 minutes expiry)
- Refresh tokens (7-30 days expiry)
- Token blacklisting for logout
- Secure token storage recommendations
- Token validation middleware enhancements

### 2. Role-Based Access Control (Priority: HIGH)
Implement RBAC system in `BackEnd.Domain/`:

#### Required Entities
- **Entities/Role.cs** - User roles definition
- **Entities/Permission.cs** - Granular permissions
- **Entities/UserRole.cs** - User-role relationships

#### Required Services
- **Services/AuthorizationService.cs** - Permission checking logic
- **Services/RoleService.cs** - Role management operations

#### RBAC Features
- Predefined roles: Admin, Manager, User, ReadOnly
- Granular permissions for each entity type
- Dynamic permission checking
- Role hierarchy support

### 3. Security Middleware Enhancement (Priority: HIGH)
Enhance security middleware in `BackEnd/Middleware/`:

#### Enhanced AuthenticationMiddleware.cs
- **JWT Validation**: Comprehensive token validation
- **Rate Limiting**: Request rate limiting per user/IP
- **Security Headers**: Add security headers to responses
- **Request Logging**: Log all authentication attempts

#### Additional Middleware
- **AuthorizationMiddleware.cs** - Permission-based authorization
- **SecurityHeadersMiddleware.cs** - Security headers (CORS, CSP, etc.)
- **AuditMiddleware.cs** - Request/response auditing

### 4. Comprehensive Audit Logging (Priority: HIGH)
Implement audit system in `BackEnd/Services/`:

#### Enhanced AuditService.cs
- **User Actions**: Log all user actions with context
- **Data Changes**: Track entity modifications
- **Authentication Events**: Log login/logout/failures
- **Security Events**: Log security violations and attempts

#### Audit Features
- Structured logging with correlation IDs
- Audit trail for compliance
- Security event monitoring
- Performance impact minimization

## Build, Test, and Fix Process

### 1. Build Process
```bash
cd BackEnd
dotnet restore
dotnet build
```

### 2. Security Testing
```bash
# Run security-specific tests
dotnet test --filter Category=Security

# Run integration tests
dotnet test --filter Category=Integration
```

### 3. Security Validation
- Test JWT token generation and validation
- Verify role-based access control works
- Test audit logging captures events
- Validate security middleware functions
- Check password security implementation

## Completion Criteria

### Code Deliverables ✓
- [ ] Enhanced JWT service with refresh tokens
- [ ] Role-based access control system
- [ ] Comprehensive security middleware
- [ ] Audit logging system
- [ ] Password security enhancements
- [ ] API security attributes and validation
- [ ] Security configuration management
- [ ] Security test suite

### Build Success ✓
- [ ] Solution builds without security errors
- [ ] All security dependencies resolve
- [ ] No security-related compilation warnings
- [ ] Security middleware integrates properly

### Test Results ✓
- [ ] All security unit tests pass
- [ ] JWT functionality tests pass
- [ ] RBAC authorization tests pass
- [ ] Audit logging tests pass
- [ ] Security middleware tests pass
- [ ] Integration tests with authentication pass

## Completion Report Template

```markdown
# Security Phase 1 Completion Report

## Summary
[Brief summary of security enhancements completed]

## Deliverables Completed
- [x] Enhanced JWT service with refresh token support
- [x] Role-based access control (Admin, Manager, User, ReadOnly)
- [x] Comprehensive security middleware stack
- [x] Audit logging for all user actions
- [x] Password security with strong hashing
- [x] API endpoint security attributes
- [x] Security configuration management
- [x] Security test suite

## Security Features Implemented
- JWT access/refresh token system
- Role-based authorization
- Request rate limiting
- Comprehensive audit trail
- Password complexity enforcement
- Account lockout protection
- Security headers middleware

## Test Results
- Security Unit Tests: X/Y passed
- Integration Tests: X/Y passed
- JWT Functionality: PASS/FAIL
- RBAC Authorization: PASS/FAIL
- Audit Logging: PASS/FAIL

## Security Roles Defined
- Admin: Full system access
- Manager: Business operations access
- User: Standard user operations
- ReadOnly: View-only access

## Known Security Issues
[List any known security limitations or issues]

## Next Steps for Integration
- Security system ready for frontend integration
- RBAC roles available for UI permission handling
- Audit system ready for compliance reporting
```

**IMPORTANT**: Security is critical for the entire application. Ensure all security features are thoroughly tested before marking as complete.

**COMPLETION SIGNAL**: When finished, respond with "SECURITY-PHASE1-COMPLETE" followed by your completion report.
'''

    def _get_infrastructure_phase1_content(self) -> str:
        """Get enhanced content for infrastructure phase 1"""
        return '''# Infrastructure Agent - Phase 1: MVP Core Features

## Agent Information
- **Agent ID**: infrastructure-phase1
- **Phase**: MVP Core Features
- **Estimated Duration**: 35 minutes
- **Dependencies**: backend-phase1 (MUST be completed first)
- **Can Run Parallel With**: frontend-phase1, security-phase1

## Mission Statement
Implement the foundational infrastructure for FY.WB.Midway, including Docker containerization, basic Azure resource definitions, CI/CD pipeline setup, and development environment configuration to support the backend and frontend applications.

## Context Documents Required
You have access to the following context documents in the repository:

### Primary Requirements
- `generated_documents/NFRD.md` - Non-Functional Requirements (Infrastructure focus)
- `generated_documents/trd_infrastructure.md` - Infrastructure Technical Requirements

### Technical Specifications
- `generated_documents/dev_plan.md` - Development Plan
- `generated_documents/trd.md` - Technical Requirements Document

### Design Documents
- `generated_documents/design/infrastructure-agent-design.md` - Your specific design document
- `generated_documents/design/backend-agent-design.md` - Backend application reference
- `CLAUDE.md` - Project structure and development guidelines

### Backend Context (Dependencies)
- Backend application from backend-phase1:
  - ASP.NET Core API structure
  - Database requirements
  - Configuration needs
  - Port and service requirements

## Specific Deliverables

### 1. Docker Configuration (Priority: CRITICAL)
Create containerization setup in project root:

#### Required Docker Files
- **Dockerfile.backend** - Backend API containerization
- **Dockerfile.frontend** - Frontend Next.js containerization
- **docker-compose.yml** - Multi-container orchestration
- **docker-compose.override.yml** - Development overrides
- **.dockerignore** - Docker ignore patterns

#### Docker Features
- Multi-stage builds for optimization
- Development and production configurations
- Proper port mapping and networking
- Volume mounts for development
- Environment variable configuration

### 2. Azure Infrastructure as Code (Priority: HIGH)
Create Azure resource definitions in `Infrastructure/`:

#### Required Bicep Files
- **main.bicep** - Main infrastructure template
- **modules/app-service.bicep** - App Service configuration
- **modules/sql-database.bicep** - Azure SQL Database
- **modules/storage.bicep** - Storage account configuration
- **modules/key-vault.bicep** - Key Vault for secrets

#### Azure Resources
- App Service Plan (Basic tier for MVP)
- App Service for backend API
- Static Web App for frontend
- Azure SQL Database (Basic tier)
- Storage Account for file uploads
- Key Vault for secrets management
- Application Insights for monitoring

### 3. CI/CD Pipeline (Priority: HIGH)
Create GitHub Actions workflows in `.github/workflows/`:

#### Required Workflow Files
- **ci-backend.yml** - Backend build and test
- **ci-frontend.yml** - Frontend build and test
- **cd-staging.yml** - Staging deployment
- **cd-production.yml** - Production deployment

#### CI/CD Features
- Automated testing on pull requests
- Build validation for both frontend and backend
- Automated deployment to staging
- Manual approval for production deployment
- Environment-specific configurations

### 4. Environment Configuration (Priority: HIGH)
Create environment setup in `Infrastructure/environments/`:

#### Required Environment Files
- **development.json** - Development environment config
- **staging.json** - Staging environment config
- **production.json** - Production environment config
- **local.json** - Local development overrides

#### Configuration Management
- Environment-specific database connections
- API endpoints and service URLs
- Feature flags for different environments
- Logging and monitoring configurations

## Build, Test, and Fix Process

### 1. Docker Build Process
```bash
# Build backend container
docker build -f Dockerfile.backend -t fy-wb-midway-backend .

# Build frontend container
docker build -f Dockerfile.frontend -t fy-wb-midway-frontend ./FrontEnd

# Test multi-container setup
docker-compose up -d
```

### 2. Infrastructure Validation
```bash
# Validate Bicep templates
az bicep build --file Infrastructure/main.bicep

# Test deployment (dry run)
az deployment group create --resource-group test-rg --template-file Infrastructure/main.bicep --what-if
```

### 3. CI/CD Testing
- Test GitHub Actions workflows locally
- Validate build processes for both applications
- Test deployment scripts
- Verify environment configurations

## Completion Criteria

### Code Deliverables ✓
- [ ] Docker configuration for backend and frontend
- [ ] Azure infrastructure as code (Bicep)
- [ ] CI/CD pipeline configuration
- [ ] Environment-specific configurations
- [ ] Database deployment scripts
- [ ] Monitoring and logging setup
- [ ] Security configuration
- [ ] Development utility scripts

### Build Success ✓
- [ ] Docker containers build successfully
- [ ] Bicep templates validate without errors
- [ ] CI/CD pipelines execute successfully
- [ ] Multi-container setup works locally
- [ ] Database deployment scripts work

### Test Results ✓
- [ ] Docker containers run without errors
- [ ] Infrastructure templates deploy successfully
- [ ] CI/CD workflows complete successfully
- [ ] Environment configurations load properly
- [ ] Monitoring and logging function correctly

## Completion Report Template

```markdown
# Infrastructure Phase 1 Completion Report

## Summary
[Brief summary of infrastructure work completed]

## Deliverables Completed
- [x] Docker containerization for backend and frontend
- [x] Azure infrastructure as code (Bicep templates)
- [x] CI/CD pipeline with GitHub Actions
- [x] Environment-specific configurations
- [x] Database deployment automation
- [x] Monitoring and logging setup
- [x] Security configuration
- [x] Development utility scripts

## Infrastructure Components
- Docker multi-container setup
- Azure App Service and SQL Database
- GitHub Actions CI/CD pipeline
- Application Insights monitoring
- Key Vault for secrets management

## Build Results
- Docker Backend Build: SUCCESS/FAILED
- Docker Frontend Build: SUCCESS/FAILED
- Bicep Template Validation: SUCCESS/FAILED
- CI/CD Pipeline Test: SUCCESS/FAILED

## Azure Resources Defined
- App Service Plan (Basic B1)
- App Service for backend API
- Static Web App for frontend
- Azure SQL Database (Basic)
- Storage Account
- Key Vault
- Application Insights

## Environment Configurations
- Development: Local Docker setup
- Staging: Azure staging environment
- Production: Azure production environment

## Known Issues
[List any known infrastructure limitations or issues]

## Next Steps for Other Agents
- Docker containers ready for application deployment
- Azure infrastructure ready for staging deployment
- CI/CD pipeline ready for automated deployments
- Monitoring ready for application insights
```

**IMPORTANT**: Your infrastructure work enables deployment and scaling of the entire application. Ensure all components are tested and documented before marking as complete.

**COMPLETION SIGNAL**: When finished, respond with "INFRASTRUCTURE-PHASE1-COMPLETE" followed by your completion report.
'''

    def _get_integration_phase1_content(self) -> str:
        """Get enhanced content for integration phase 1"""
        return '''# Integration Agent - Phase 1: MVP Core Features

## Agent Information
- **Agent ID**: integration-phase1
- **Phase**: MVP Core Features
- **Estimated Duration**: 30 minutes
- **Dependencies**: backend-phase1, frontend-phase1, security-phase1 (ALL must be completed first)
- **Can Run Parallel With**: None (Final integration step)

## Mission Statement
Integrate all components created by the backend, frontend, and security agents into a cohesive, working application. Perform end-to-end testing, fix integration issues, and ensure the complete MVP system functions correctly.

## Context Documents Required
You have access to the following context documents in the repository:

### Primary Requirements
- `generated_documents/prd.md` - Product Requirements Document
- `generated_documents/FRD.md` - Functional Requirements Document
- `generated_documents/NFRD.md` - Non-Functional Requirements Document

### Technical Specifications
- `generated_documents/dev_plan.md` - Development Plan
- `generated_documents/api_spec.md` - API Specification
- `generated_documents/test_plan.md` - Test Plan

### Design Documents
- `generated_documents/design/integration-agent-design.md` - Your specific design document
- `generated_documents/design/backend-agent-design.md` - Backend reference
- `generated_documents/design/frontend-agent-design.md` - Frontend reference
- `generated_documents/design/security-agent-design.md` - Security reference
- `CLAUDE.md` - Project structure and development guidelines

### Component Context (Dependencies)
- **Backend APIs** from backend-phase1:
  - Authentication endpoints
  - Client, Load, Invoice, Carrier CRUD APIs
  - Database operations
- **Frontend UI** from frontend-phase1:
  - Authentication forms
  - Dashboard and management interfaces
  - API integration layer
- **Security System** from security-phase1:
  - JWT token management
  - Role-based access control
  - Audit logging

## Specific Deliverables

### 1. End-to-End Integration Testing (Priority: CRITICAL)
Create comprehensive integration tests in `Tests/Integration/`:

#### Required Test Files
- **AuthenticationIntegrationTests.cs** - Full auth flow testing
- **ClientManagementIntegrationTests.cs** - Client CRUD end-to-end
- **LoadManagementIntegrationTests.cs** - Load CRUD end-to-end
- **SecurityIntegrationTests.cs** - Security and authorization testing
- **UIIntegrationTests.cs** - Frontend-backend integration

#### Integration Test Coverage
- User registration and login flow
- JWT token generation and validation
- CRUD operations for all entities
- Role-based access control
- Error handling and validation
- API response formatting
- Frontend-backend data flow

### 2. API Integration Fixes (Priority: HIGH)
Resolve integration issues between frontend and backend:

#### Common Integration Issues
- **CORS Configuration**: Ensure frontend can call backend APIs
- **API Response Formats**: Standardize response structures
- **Error Handling**: Consistent error responses and frontend handling
- **Authentication Flow**: JWT token passing and validation
- **Data Validation**: Ensure frontend and backend validation match

#### Required Fixes
- Update CORS policies in backend
- Standardize API response formats
- Fix authentication token handling
- Resolve data validation mismatches
- Update error handling consistency

### 3. Database Integration (Priority: HIGH)
Ensure database operations work correctly:

#### Database Integration Tasks
- **Connection String Configuration**: Verify database connectivity
- **Migration Execution**: Ensure all migrations run successfully
- **Seed Data**: Create initial data for testing
- **Transaction Handling**: Verify CRUD operations work correctly
- **Performance Testing**: Basic performance validation

### 4. Security Integration (Priority: HIGH)
Integrate security components across the application:

#### Security Integration Tasks
- **JWT Flow Integration**: End-to-end token validation
- **Role-Based UI**: Frontend respects user roles
- **API Authorization**: Backend enforces permissions
- **Audit Logging**: Verify logging captures all actions
- **Password Security**: Ensure secure password handling

### 5. Error Handling and Logging (Priority: MEDIUM)
Implement comprehensive error handling:

#### Error Handling Features
- **Global Error Handling**: Catch and handle all errors gracefully
- **User-Friendly Messages**: Convert technical errors to user messages
- **Logging Integration**: Ensure all errors are logged
- **Error Recovery**: Implement retry mechanisms where appropriate

### 6. Performance Optimization (Priority: MEDIUM)
Basic performance optimizations:

#### Performance Tasks
- **API Response Times**: Optimize slow endpoints
- **Frontend Loading**: Implement loading states
- **Database Queries**: Optimize N+1 queries
- **Caching**: Implement basic caching where beneficial

## Build, Test, and Fix Process

### 1. Full System Build
```bash
# Build backend
cd BackEnd
dotnet restore
dotnet build

# Build frontend
cd ../FrontEnd
npm install
npm run build

# Start both applications
cd ../BackEnd
dotnet run &
cd ../FrontEnd
npm run dev
```

### 2. Integration Testing
```bash
# Run all integration tests
cd BackEnd
dotnet test --filter Category=Integration

# Run end-to-end tests
npm run test:e2e
```

### 3. Manual Testing Checklist
- [ ] User can register and login
- [ ] Dashboard displays correctly
- [ ] Can create, read, update, delete clients
- [ ] Can create, read, update, delete loads
- [ ] Can create, read, update, delete carriers
- [ ] Can create, read, update, delete invoices
- [ ] Role-based access works correctly
- [ ] Error messages display appropriately
- [ ] Logout works correctly

### 4. Bug Fix Process
If integration issues occur:
1. Identify the failing component (frontend, backend, security)
2. Check API calls and responses in browser dev tools
3. Verify database operations and data consistency
4. Test authentication and authorization flows
5. Fix issues and re-test end-to-end
6. Document fixes and update tests

## Completion Criteria

### Code Deliverables ✓
- [ ] Comprehensive integration test suite
- [ ] API integration fixes implemented
- [ ] Database integration verified
- [ ] Security integration complete
- [ ] Error handling implemented
- [ ] Performance optimizations applied

### Build Success ✓
- [ ] Both frontend and backend build successfully
- [ ] Applications start without errors
- [ ] Database migrations run successfully
- [ ] No critical compilation warnings

### Test Results ✓
- [ ] All integration tests pass
- [ ] End-to-end manual testing successful
- [ ] Authentication flow works completely
- [ ] All CRUD operations functional
- [ ] Security and authorization working
- [ ] Error handling tested and working

### Documentation ✓
- [ ] Integration test documentation
- [ ] Known issues documented
- [ ] Deployment instructions updated
- [ ] User guide created

## Completion Report Template

```markdown
# Integration Phase 1 Completion Report

## Summary
[Brief summary of integration work completed]

## Deliverables Completed
- [x] End-to-end integration testing suite
- [x] API integration fixes and optimizations
- [x] Database integration verification
- [x] Security system integration
- [x] Error handling and logging
- [x] Performance optimizations

## Integration Test Results
- Authentication Flow: PASS/FAIL
- Client Management: PASS/FAIL
- Load Management: PASS/FAIL
- Carrier Management: PASS/FAIL
- Invoice Management: PASS/FAIL
- Security Authorization: PASS/FAIL
- Error Handling: PASS/FAIL

## System Status
- Backend API: RUNNING/FAILED
- Frontend Application: RUNNING/FAILED
- Database: CONNECTED/FAILED
- Authentication: WORKING/FAILED
- All CRUD Operations: WORKING/FAILED

## Performance Metrics
- Average API Response Time: X ms
- Frontend Load Time: X seconds
- Database Query Performance: ACCEPTABLE/NEEDS_WORK

## Known Issues
[List any remaining issues or limitations]

## Deployment Readiness
- Local Development: READY/NOT_READY
- Staging Deployment: READY/NOT_READY
- Production Deployment: READY/NOT_READY

## Next Steps
- System ready for infrastructure deployment
- All core MVP features functional
- Ready for user acceptance testing
```

**IMPORTANT**: This is the final integration step for Phase 1. Ensure all components work together seamlessly before marking as complete. The success of the entire MVP depends on your integration work.

**COMPLETION SIGNAL**: When finished, respond with "INTEGRATION-PHASE1-COMPLETE" followed by your completion report.
'''


def main():
    """Main function to enhance Claude instructions"""
    base_path = Path(__file__).parent.parent
    enhancer = ClaudeInstructionEnhancer(base_path)

    success = enhancer.enhance_all_instructions()
    if success:
        console.print("\n[bold green]🎉 Claude Code instruction enhancement complete![/bold green]")
        console.print("[green]All instruction files now contain detailed, specific content.[/green]")
        console.print("[green]Ready for Claude Code execution with comprehensive instructions.[/green]")
    else:
        console.print("\n[bold red]❌ Failed to enhance instruction files.[/bold red]")


if __name__ == "__main__":
    main()
