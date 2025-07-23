---
agent_type: Backend Agent  
branch_pattern: feature/backend-*  
technology_stack: ASP.NET Core, Entity Framework Core, CQRS, MediatR  
dependencies: [Frontend Agent, Authentication Agent, Notification Agent]  
generated_at: '2025-07-23T14:16:38'  
id: BACKEND_AGENT_DESIGN  
version: '1.0'  
---

# Backend Agent Design Document

## 1. Agent Overview

### 1.1 Role and Responsibilities
The Backend Agent is responsible for implementing server-side business logic, managing APIs, and handling data access layers. It ensures that the application is scalable, secure, and efficient in processing requests and managing data.

### 1.2 Scope of Work
- Develop RESTful APIs for client-side consumption.
- Implement business logic using CQRS and MediatR patterns.
- Manage data persistence and retrieval using Entity Framework Core.
- Ensure integration with other agents and external services.

### 1.3 Technology Stack
- **ASP.NET Core**: For building the web API.
- **Entity Framework Core**: For data access and ORM.
- **CQRS**: For separating read and write operations.
- **MediatR**: For handling commands and queries.

## 2. Feature Assignments from Development Plan
- **Phase 1**: Implement basic CRUD operations for core entities.
- **Phase 2**: Develop complex business logic and validation rules.
- **Phase 3**: Integrate with external services and other agents.
- **Phase 4**: Optimize performance and scalability.

## 3. Branch Strategy and Workflow

### 3.1 Branch Naming Convention
Branches will follow the pattern `feature/backend-*`, where `*` is a descriptive name of the feature being developed.

### 3.2 Development Workflow
1. **Feature Branch Creation**: Create a new branch from `develop` for each feature.
2. **Development**: Implement the feature, ensuring all unit tests pass.
3. **Code Review**: Submit a pull request for peer review.
4. **Merge**: Once approved, merge the feature branch back into `develop`.

## 4. Technical Architecture
- **API Layer**: ASP.NET Core controllers to handle HTTP requests.
- **Business Logic Layer**: Implemented using CQRS and MediatR to handle commands and queries.
- **Data Access Layer**: Entity Framework Core for database interactions.
- **Integration Layer**: Interfaces and services for communication with other agents and external APIs.

## 5. Dependencies and Integration Points
- **Frontend Agent**: Consumes APIs exposed by the Backend Agent.
- **Authentication Agent**: Provides authentication and authorization services.
- **Notification Agent**: Sends notifications based on backend events.
- **External Services**: Payment gateways, third-party APIs, etc.

## 6. Implementation Plan by Phase

### Phase 1: Basic CRUD Operations
- Timeline: 2 weeks
- Tasks: Define entities, set up database schema, implement CRUD APIs.

### Phase 2: Business Logic and Validation
- Timeline: 3 weeks
- Tasks: Implement CQRS patterns, develop validation logic, integrate MediatR.

### Phase 3: Integration
- Timeline: 2 weeks
- Tasks: Implement integration with other agents and external services.

### Phase 4: Optimization
- Timeline: 2 weeks
- Tasks: Performance tuning, load testing, and scalability improvements.

## 7. Claude Code Instructions

### 7.1 Context Files Required
- `entities/`: Directory containing entity definitions.
- `controllers/`: Directory for API controllers.
- `services/`: Directory for business logic services.

### 7.2 Implementation Prompts
- `--add-dir entities/ -p "Define core entities for the application"`
- `--add-dir controllers/ -p "Implement CRUD operations for each entity"`
- `--add-dir services/ -p "Develop business logic using CQRS and MediatR"`

### 7.3 Validation Criteria
- Ensure all APIs return correct HTTP status codes.
- Validate data integrity and business rules.
- Confirm successful integration with dependent agents.

## 8. Success Metrics and Testing
- **API Performance**: Response time under 200ms for 95% of requests.
- **Data Integrity**: 100% accuracy in CRUD operations.
- **Integration Tests**: Pass all tests with dependent agents.
- **Load Testing**: Support 1000 concurrent users with acceptable performance.

This document provides a comprehensive guide for implementing the Backend Agent using Claude Code, ensuring all features are developed efficiently and integrated seamlessly with the overall system architecture.