# AI Agent Design Documents

This directory contains detailed design documents for each AI agent that will implement features according to the ByteForge development plan.

## Agent Overview

Each agent is responsible for a specific domain of the application and will use Claude Code to implement their assigned features:

### 1. Frontend Agent (`frontend-agent-design.md`)
- **Responsibility**: Next.js/React/Tailwind UI implementation
- **Scope**: All user interfaces across all phases
- **Branch Pattern**: `feature/frontend-*`

### 2. Backend Agent (`backend-agent-design.md`)
- **Responsibility**: ASP.NET Core API, CQRS, business logic
- **Scope**: All backend services and APIs
- **Branch Pattern**: `feature/backend-*`

### 3. Infrastructure Agent (`infrastructure-agent-design.md`)
- **Responsibility**: Azure resources, CI/CD, database schema
- **Scope**: Platform setup, deployment, infrastructure
- **Branch Pattern**: `feature/infrastructure-*`

### 4. Security Agent (`security-agent-design.md`)
- **Responsibility**: Authentication, authorization, audit trails
- **Scope**: Security features and compliance
- **Branch Pattern**: `feature/security-*`

### 5. Integration Agent (`integration-agent-design.md`)
- **Responsibility**: Third-party integrations (Stripe, external APIs)
- **Scope**: Payment processing, external service integrations
- **Branch Pattern**: `feature/integration-*`

## Usage with Claude Code

Each design document is structured to be used as context for Claude Code:

```bash
claude --add-dir ./generated_documents/design \
      --add-dir ./generated_documents \
      --add-dir ./[ProjectDirectory] \
      -p "Implement the [Agent] features for Phase [N]"
```

The design documents provide comprehensive context including:
- Requirements from FRD, NFRD, TRD documents
- API specifications and database schema
- UI/UX specifications and component designs
- Test plans and validation criteria

## Generated At
2025-06-27 17:38:24

## Model Provider
OPENAI
