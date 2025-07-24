# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ASP.NET Core 8 web application for automated lead processing using Elsa Workflows and Hangfire. The system generates fake leads from multiple sources, processes them through enrichment, vetting, scoring, and CRM integration workflows, and provides real-time dashboard updates via SignalR.

## Architecture

### Core Components
- **ASP.NET Core 8 Web App** with MVC and Web API
- **Entity Framework Core** with SQL Server for data persistence
- **ASP.NET Core Identity** for authentication and authorization
- **Elsa Workflows 3.4** for workflow orchestration
- **Hangfire** for background job scheduling
- **SignalR** for real-time dashboard updates
- **Next.js Frontend** for modern UI components
- **Azure deployment ready** with Key Vault integration

### Workflow Architecture: Hangfire vs Elsa

**Hangfire** - Background Job Scheduling:
- **Purpose**: Schedules and executes recurring background jobs
- **Use Cases**: Lead generation jobs that run on timers (every 5 seconds, 2 hours, etc.)
- **Examples**: `GoogleLeadJob`, `FacebookLeadJob`, `LinkedInLeadJob`, `YellowPagesLeadJob`
- **Features**: Job persistence, retry logic, dashboard monitoring, distributed processing
- **Location**: `/Jobs/` directory

**Elsa Workflows** - Business Process Orchestration:
- **Purpose**: Orchestrates complex, multi-step business processes with conditional logic
- **Use Cases**: Lead processing pipeline with enrichment, vetting, scoring, and CRM integration
- **Examples**: `ProcessSingleLeadWorkflow` that processes leads through multiple activities
- **Features**: Visual workflow designer, conditional branching, fault handling, activity composition
- **Location**: `/Workflows/` directory for definitions, `/Activities/` for custom activities

**Integration Pattern**:
1. **Hangfire jobs** generate or collect leads from external sources
2. **Hangfire jobs** trigger **Elsa workflows** to process individual leads
3. **Elsa workflows** execute the lead processing pipeline using custom activities
4. Both systems can publish events via **SignalR** for real-time dashboard updates

**Key Distinction**:
- **Hangfire**: "When should work happen?" (scheduling, timing, triggers)
- **Elsa**: "What work should happen?" (business logic, process flow, activities)

### Key Directories
- `/Models/` - Entity models (Lead, ApplicationUser)
- `/Data/` - Entity Framework DbContext
- `/Activities/` - Custom Elsa workflow activities
- `/Workflows/` - Elsa workflow definitions
- `/Jobs/` - Hangfire background jobs
- `/Services/` - Lead scraping and other services
- `/Controllers/` - MVC and API controllers
- `/Hubs/` - SignalR hubs for real-time communication
- `/FrontEnd/` - Next.js frontend application
- `/Views/` - MVC Razor views with SignalR integration

## Common Development Commands

### Database Operations
```bash
# Create and apply migrations
dotnet ef migrations add InitialCreate
dotnet ef database update

# Drop and recreate database (development only)
dotnet ef database drop
dotnet ef database update
```

### Build and Run
```bash
# Build the application
dotnet build

# Run in development mode
dotnet run

# Run with specific environment
dotnet run --environment Production
```

### Quick Start (Recommended)
```powershell
# Start both backend and frontend applications
.\start_bird.ps1

# This script will:
# - Kill processes on ports 5000, 7001, 3000
# - Start .NET backend in separate terminal
# - Start Next.js frontend in separate terminal
# - Open dashboard in browser automatically
```

### Utility Scripts
The project includes convenient scripts for common development tasks:

```bash
# Application Management
./scripts/restart-app.sh          # Stop and restart the application (Linux/macOS)
scripts\restart-app.bat           # Stop and restart the application (Windows)

# Testing
./scripts/run-tests.sh            # Comprehensive test runner with results
./scripts/run-tests.sh -v         # Verbose test output
./scripts/run-tests.sh -c         # Run tests with coverage
./scripts/quick-test.sh           # Fast test validation

# Build Management
./scripts/clean-build.sh          # Clean and rebuild solution
```

### Testing
```bash
# Using scripts (recommended)
./scripts/run-tests.sh            # Full test runner with detailed results
./scripts/run-tests.sh -c         # Run with code coverage
./scripts/quick-test.sh           # Quick validation

# Direct dotnet commands
dotnet test                       # Run all tests
dotnet test --collect:"XPlat Code Coverage"  # Run with coverage
dotnet test LeadProcessing.Tests/ # Run specific test project
dotnet test --verbosity normal   # Verbose output
dotnet test --filter "Category=Unit"  # Filter tests
```

## Configuration

### Connection Strings
- **Development**: Uses LocalDB (`(localdb)\\mssqllocaldb`)
- **Production**: Set via Azure Key Vault or environment variables

### Required Environment Variables for Production
- `ConnectionStrings__DefaultConnection` - SQL Server connection string
- `KeyVaultName` - Azure Key Vault name (optional)

## Workflow System

### Lead Processing Pipeline
1. **Lead Generation** - Fake leads generated every 5 seconds via Hangfire jobs
2. **Enrichment** - Adds missing lead information (simulated)
3. **Vetting** - Validates lead quality and format (real validation)
4. **Scoring** - Assigns quality scores based on criteria (real scoring)
5. **CRM Integration** - Upserts to Zoho CRM (simulated)

### Custom Elsa Activities
- `EnrichLeadActivity` - Enriches lead data with fake company/phone information
- `VetLeadActivity` - Validates leads (can fault workflows for invalid data)
- `ScoreLeadActivity` - Assigns quality scores based on email domain, completeness
- `ZohoUpsertActivity` - Simulates CRM integration with realistic outcomes

### Job Scheduling
- **GoogleLeadJob** - Runs every 5 seconds, generates single fake lead
- **FacebookLeadJob** - Runs every 2 hours (offset by 30 minutes)
- **YellowPagesLeadJob** - Runs every 3 hours
- **LinkedInLeadJob** - Runs every 6 hours

## API Endpoints

### Lead Management
- `GET /api/lead` - Get all leads
- `GET /api/lead/{id}` - Get specific lead
- `POST /api/lead` - Create new lead
- `PUT /api/lead/{id}` - Update lead
- `DELETE /api/lead/{id}` - Delete lead
- `POST /api/lead/{id}/process` - Trigger workflow for lead

### Monitoring
- `/hangfire` - Hangfire dashboard (requires authentication in production)
- `/health` - Health check endpoint
- `/Leads/Dashboard` - Real-time lead processing dashboard with SignalR

### SignalR Endpoints
- `/leadHub` - SignalR hub for real-time dashboard updates
- Events: `LeadCreated`, `LeadUpdated`, `DashboardUpdate`

## Testing Framework

### Test Structure
- **LeadProcessing.Tests** - MSTest project with comprehensive test coverage
- **Unit Tests** - Models, Activities, Services with mocked dependencies
- **Integration Tests** - Controller endpoints with in-memory database
- **Test Infrastructure** - Shared test utilities and data builders

### Test Categories
- **Models Tests** - Entity validation and behavior
- **Activity Tests** - Elsa workflow activities with various scenarios
- **Service Tests** - Lead scraping and business logic
- **Controller Tests** - API endpoints and HTTP responses
- **Job Tests** - Hangfire background job execution

### Test Data
- **Seed Data** - Automatically populated in development environment
- **Test Builders** - Fluent API for creating test entities
- **In-Memory Database** - Fast isolated testing with EF Core
- **Mock Services** - External dependencies mocked for unit tests

### Test Coverage Areas
- Happy path and error scenarios
- Edge cases and validation
- Workflow fault handling
- Database operations
- External service integration

## Azure Deployment

### Prerequisites
- Azure App Service
- Azure SQL Database
- Azure Key Vault (optional, for secrets)

### Deployment Steps
1. Configure connection strings in Azure App Service settings
2. Set up Azure Key Vault integration if needed
3. Deploy via GitHub Actions, Azure DevOps, or direct publish

## Real-Time Features

### Current Implementation Status
✅ **Completed Features:**
- Real-time dashboard with SignalR integration
- 5-second fake lead generation from Google source
- Live workflow progress tracking
- Automatic dashboard statistics updates
- Real-time notifications for lead creation/updates
- Complete workflow pipeline with fake data simulation

### Dashboard Features
- **Live Lead Counter** - Updates every 5 seconds as leads are generated
- **Real-Time Status Updates** - Shows lead progression through workflow steps
- **Live Recent Leads** - New leads appear instantly at top of list
- **Progress Bars** - Source distribution and pipeline completion rates
- **Toast Notifications** - Alerts for new leads and status changes
- **Auto-Refresh Statistics** - All metrics update without page reload

### Key URLs
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:3000 (Next.js - planned)
- **Real-Time Dashboard**: http://localhost:5000/Leads/Dashboard
- **Hangfire Jobs**: http://localhost:5000/hangfire

## Development Process
1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the todo.md file with a summary of the changes you made and any other relevant information.

### Critical Build Requirements
**MANDATORY**: Whenever ANY backend C# file is modified (including files in `/Models/`, `/Controllers/`, `/Services/`, `/Activities/`, `/Jobs/`, `/Hubs/`, `/Data/`, `/Workflows/`, or any `.cs` file), you MUST:

1. **Run `dotnet build`** immediately after making changes
2. **Fix any compilation errors** that occur during the build
3. **Verify the build succeeds** before considering the task complete
4. **Run tests** if build succeeds to ensure functionality is not broken

This applies to ALL C# file modifications, no matter how small. Do not skip this step or consider a task complete until the build passes successfully.