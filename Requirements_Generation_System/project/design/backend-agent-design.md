---
agent_type: Backend Agent  
branch_pattern: feature/backend-*  
technology_stack: ASP.NET Core, Entity Framework Core, CQRS, MediatR  
dependencies: [Frontend Agent, Authentication Agent, Notification Agent]  
generated_at: '2025-06-30T21:21:20'  
id: BACKEND_AGENT_DESIGN  
version: '1.0'  
---

# Backend Agent Design Document

## 1. Agent Overview

### 1.1 Role and Responsibilities
The Backend Agent is responsible for implementing server-side business logic, managing APIs, and handling data access layers. It ensures robust and scalable backend services that support the enterprise application.

### 1.2 Scope of Work
- Develop RESTful APIs for client applications.
- Implement business logic using CQRS and MediatR patterns.
- Manage data access using Entity Framework Core.
- Ensure secure and efficient data transactions.
- Collaborate with other agents for seamless integration.

### 1.3 Technology Stack
- **ASP.NET Core**: For building cross-platform web applications.
- **Entity Framework Core**: For ORM and database interactions.
- **CQRS**: For separating read and write operations.
- **MediatR**: For handling in-process messaging.

## 2. Feature Assignments from Development Plan
- **Phase 1**: Implement basic CRUD operations for core entities.
- **Phase 2**: Develop advanced business logic and validation rules.
- **Phase 3**: Integrate with external services and other agents.
- **Phase 4**: Optimize performance and scalability.

## 3. Branch Strategy and Workflow

### 3.1 Branch Naming Convention
Branches will follow the pattern `feature/backend-*` to ensure consistency and traceability.

### 3.2 Development Workflow
1. **Feature Branch Creation**: Create a branch from `develop` for each feature.
2. **Development**: Implement features and commit changes.
3. **Code Review**: Submit pull requests for peer review.
4. **Testing**: Conduct unit and integration tests.
5. **Merge**: Merge approved changes into `develop`.

## 4. Technical Architecture
- **API Layer**: Exposes endpoints for client applications.
- **Business Logic Layer**: Implements CQRS and MediatR for command and query separation.
- **Data Access Layer**: Utilizes Entity Framework Core for database operations.
- **Integration Layer**: Manages communication with other agents and external services.

## 5. Dependencies and Integration Points
- **Frontend Agent**: Provides data and services for UI components.
- **Authentication Agent**: Manages user authentication and authorization.
- **Notification Agent**: Sends notifications based on backend events.
- **External Services**: Integrates with third-party APIs for extended functionality.

## 6. Implementation Plan by Phase

### Phase 1: Basic CRUD Operations
- **Timeline**: 2 weeks
- **Tasks**: Define entities, implement CRUD APIs, set up database schema.

### Phase 2: Business Logic and Validation
- **Timeline**: 3 weeks
- **Tasks**: Implement CQRS patterns, add validation rules, refine business logic.

### Phase 3: Integration
- **Timeline**: 2 weeks
- **Tasks**: Integrate with other agents, configure external service connections.

### Phase 4: Optimization
- **Timeline**: 2 weeks
- **Tasks**: Conduct performance testing, optimize queries, enhance scalability.

## 7. Claude Code Instructions

### 7.1 Context Files Required
- `entities/*.cs`: Entity definitions.
- `commands/*.cs`: Command handlers.
- `queries/*.cs`: Query handlers.
- `controllers/*.cs`: API controllers.

### 7.2 Implementation Prompts
- Use `--add-dir src/BackendAgent` to specify the source directory.
- Use `-p "Implement CRUD operations for [EntityName]"` for specific tasks.
- Use `-p "Integrate with [AgentName] for [Feature]"` for integration tasks.

### 7.3 Validation Criteria
- Ensure all APIs return correct HTTP status codes.
- Validate data integrity and consistency.
- Confirm successful integration with dependent agents.

## 8. Success Metrics and Testing
- **API Response Time**: Average response time should be under 200ms.
- **Data Accuracy**: Ensure 100% accuracy in data transactions.
- **Integration Tests**: Pass all integration tests with other agents.
- **Load Testing**: Support up to 10,000 concurrent users without degradation.

This design document provides a comprehensive guide for implementing the Backend Agent using Claude Code. It outlines the necessary steps, dependencies, and success criteria to ensure a robust and efficient backend system.