---
agent_type: Backend Agent
branch_pattern: feature/backend-*
technology_stack: ASP.NET Core, Entity Framework Core, CQRS, MediatR
dependencies: [Database Agent, Authentication Agent]
generated_at: '2025-07-23T18:03:29'
id: BACKEND_AGENT_DESIGN
version: '1.0'
---

# Backend Agent Design Document

## 1. Agent Overview

### 1.1 Role and Responsibilities
The Backend Agent is responsible for implementing the server-side business logic, APIs, and data access layers of the enterprise software application. This includes handling HTTP requests, processing business rules via CQRS patterns, orchestrating data operations with Entity Framework Core, and mediating commands/queries using MediatR. The agent ensures secure, scalable, and maintainable backend services that integrate with databases, authentication systems, and other agents. Key responsibilities include:
- Developing RESTful APIs for core features.
- Implementing command and query handlers for business operations.
- Managing data persistence and retrieval.
- Ensuring compliance with security standards (e.g., input validation, error handling).
- Collaborating with other agents for end-to-end feature delivery.

### 1.2 Scope of Work
The scope encompasses all backend-related tasks, including API endpoint creation, business logic implementation, data modeling integration, and integration with external services. Out of scope: Frontend UI development, database schema design (handled by Database Agent), and deployment infrastructure (handled by DevOps Agent). The agent focuses on features assigned in the development plan, ensuring they align with the overall system architecture.

### 1.3 Technology Stack
- **ASP.NET Core**: For building web APIs and middleware.
- **Entity Framework Core**: For ORM-based data access and migrations.
- **CQRS (Command Query Responsibility Segregation)**: To separate read and write operations for better scalability and maintainability.
- **MediatR**: For implementing the mediator pattern to handle commands and queries decoupled from controllers.
- Additional libraries: AutoMapper for DTO-entity mapping, FluentValidation for input validation, and Serilog for logging.

## 2. Feature Assignments from Development Plan
Based on the dev_plan.md, the Backend Agent is assigned features related to server-side logic and APIs. These are organized by phase for phased implementation. (Assumed project: Building an e-commerce platform with user management, product catalog, and order processing.)

- **Phase 1: Foundation and User Management**
  - Implement User Registration API (POST /api/users/register) with CQRS command for creating users.
  - Implement User Login API (POST /api/users/login) integrating with Authentication Agent.
  - Develop Query Handlers for retrieving user profiles (GET /api/users/{id}).

- **Phase 2: Product Catalog and Inventory**
  - Create Product CRUD APIs (GET/POST/PUT/DELETE /api/products) using MediatR for commands and queries.
  - Implement Inventory Check Query (GET /api/inventory/{productId}) with EF Core data access.
  - Add business logic for stock validation in command handlers.

- **Phase 3: Order Processing and Integration**
  - Develop Order Creation API (POST /api/orders) with CQRS command handling payment integration.
  - Implement Order Query APIs (GET /api/orders/{id}, GET /api/orders) for listing and details.
  - Integrate with Database Agent for transactional data persistence.

- **Phase 4: Advanced Features and Optimization**
  - Add API for Reporting (GET /api/reports/sales) using aggregated queries.
  - Implement caching mechanisms in query handlers (e.g., using MemoryCache).
  - Refactor for performance optimizations and error handling.

## 3. Branch Strategy and Workflow

### 3.1 Branch Naming Convention
All work must follow the pattern `feature/backend-*`, where `*` is a descriptive slug (e.g., `feature/backend-user-registration`). Bug fixes use `fix/backend-*`, and hotfixes use `hotfix/backend-*`. Branches are created from the `develop` branch and merged via pull requests to `develop` after review.

### 3.2 Development Workflow
1. **Branch Creation**: Create a new branch from `develop` using the naming convention.
2. **Implementation**: Develop features using Claude Code, committing incrementally with descriptive messages (e.g., "Implement UserRegistrationCommandHandler").
3. **Testing**: Run unit tests locally and ensure integration tests pass.
4. **Pull Request**: Submit a PR to `develop` with a description linking to the feature in the dev plan. Include code reviews from other agents.
5. **Merge and Cleanup**: After approval, merge and delete the branch. Use rebase for clean history.
6. **Release**: Features are bundled into releases from `develop` to `main`.

## 4. Technical Architecture
The Backend Agent follows a layered architecture with CQRS and MediatR at its core:

- **Presentation Layer**: ASP.NET Core controllers handle HTTP requests, mapping to MediatR requests (e.g., `await _mediator.Send(new CreateUserCommand())`).
- **Application Layer**: Contains CQRS components:
  - **Commands**: Mutable operations (e.g., `CreateProductCommand`) handled by `IRequestHandler<CreateProductCommand>`.
  - **Queries**: Read-only operations (e.g., `GetProductQuery`) handled by `IRequestHandler<GetProductQuery, ProductDto>`.
  - MediatR pipelines for behaviors like validation, logging, and caching.
- **Domain Layer**: Core entities (e.g., User, Product) with business rules. Uses Domain-Driven Design (DDD) aggregates.
- **Infrastructure Layer**: EF Core DbContext for data access (e.g., `AppDbContext` with repositories). Includes services for email, external APIs.
- **Cross-Cutting Concerns**: 
  - Dependency Injection via ASP.NET Core's IServiceCollection.
  - Error handling with global exception middleware.
  - Security: JWT authentication integrated with Authentication Agent.
- **Project Structure**:
  ```
  src/
  ├── Api/ (Controllers)
  ├── Application/ (Commands, Queries, Handlers, DTOs)
  ├── Domain/ (Entities, Value Objects)
  ├── Infrastructure/ (DbContext, Repositories, Services)
  └── Program.cs (Startup)
  ```

## 5. Dependencies and Integration Points
- **Internal Dependencies**:
  - **Database Agent**: Provides database schemas and migrations; Backend Agent uses EF Core to interact with the DbContext.
  - **Authentication Agent**: Supplies auth tokens and user claims; integrated via middleware in ASP.NET Core.
- **External Integration Points**:
  - Database (e.g., SQL Server via connection string).
  - External services (e.g., payment gateway APIs called from command handlers).
  - Message queues (e.g., RabbitMQ for async events, if needed in later phases).
- **Integration Strategy**: Use interfaces for loose coupling (e.g., `IAuthService` from Authentication Agent). Mock dependencies in unit tests.

## 6. Implementation Plan by Phase
The implementation is divided into phases aligned with the development plan. Timelines assume a 4-week sprint cycle per phase, starting from document generation date.

- **Phase 1: Foundation and User Management (Weeks 1-4)**
  - Week 1: Set up project structure, configure MediatR and EF Core.
  - Week 2: Implement user registration and login APIs with handlers.
  - Week 3: Add query handlers and integrate with Authentication Agent.
  - Week 4: Unit testing and PR submission.

- **Phase 2: Product Catalog and Inventory (Weeks 5-8)**
  - Week 5: Define product entities and CRUD commands.
  - Week 6: Implement query handlers and inventory logic.
  - Week 7: Integrate with Database Agent for data persistence.
  - Week 8: Performance testing and refinements.

- **Phase 3: Order Processing and Integration (Weeks 9-12)**
  - Week 9: Develop order creation command with transaction support.
  - Week 10: Implement order queries and reporting.
  - Week 11: Handle integrations (e.g., payment events).
  - Week 12: End-to-end testing.

- **Phase 4: Advanced Features and Optimization (Weeks 13-16)**
  - Week 13: Add caching and advanced queries.
  - Week 14: Implement reporting APIs.
  - Week 15: Optimize and refactor code.
  - Week 16: Final reviews and merge to main.

## 7. Claude Code Instructions

### 7.1 Context Files Required
- dev_plan.md (for feature details).
- Existing codebase directories: src/Api, src/Application, src/Domain, src/Infrastructure.
- Configuration files: appsettings.json, Program.cs.
- Use --add-dir to include: --add-dir src (for project structure).

### 7.2 Implementation Prompts
Use Claude Code with specific prompts for each task. Example prompts:

- For implementing a command handler:  
  `claude-code -p "Implement the CreateUserCommand and its Handler in the Application layer using MediatR. Ensure it maps to User entity and saves via EF Core. Follow CQRS pattern." --add-dir src/Application --add-dir src/Domain`

- For API controller:  
  `claude-code -p "Create UsersController with POST /register endpoint that sends CreateUserCommand via MediatR. Include validation and error handling." --add-dir src/Api --add-dir src/Application`

- For query implementation:  
  `claude-code -p "Develop GetProductQuery and Handler to retrieve product details from DbContext. Return ProductDto." --add-dir src/Application --add-dir src/Infrastructure`

- Phase-specific:  
  `claude-code -p "Based on Phase 1 of dev_plan.md, implement user management features in backend. Ensure integration with Authentication Agent." --add-dir . --add-file dev_plan.md`

### 7.3 Validation Criteria
- Code compiles without errors.
- Unit tests pass (e.g., using xUnit for handlers).
- API endpoints respond correctly (tested with Postman or Swagger).
- Adherence to CQRS: No direct DB access in controllers.
- Logging and validation present in handlers.
- Branch commits follow conventions and include tests.

## 8. Success Metrics and Testing
- **Success Metrics**:
  - 100% code coverage for handlers and controllers.
  - API response times under 200ms for queries.
  - Zero critical security vulnerabilities (scanned with tools like SonarQube).
  - All assigned features implemented and integrated per phase.

- **Testing Criteria**:
  - **Unit Tests**: Test individual handlers (e.g., mock DbContext for EF Core tests).
  - **Integration Tests**: Use TestServer for API endpoints, verifying DB interactions.
  - **End-to-End Tests**: Simulate full flows (e.g., register user then query profile).
  - **Tools**: xUnit, Moq for mocking, FluentAssertions for assertions.
  - **Validation**: Run tests in CI pipeline; ensure no regressions on merge.