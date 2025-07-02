# Generate ASP.NET Core Backend Code for LSOMigrator

You are an expert .NET developer. Create a complete ASP.NET Core 8.0 Web API project using Clean Architecture for the LSOMigrator application. Generate actual code files - don't just describe what to do.

## Required Project Structure

Create the following directory structure and files:

```
LSOMigrator.Backend/
├── LSOMigrator.Domain/
│   ├── Entities/
│   │   ├── MigrationJob.cs
│   │   ├── FieldMapping.cs
│   │   ├── ContractData.cs
│   │   └── ProcessHistoryEntry.cs
│   └── LSOMigrator.Domain.csproj
├── LSOMigrator.Application/
│   ├── Commands/
│   │   └── CreateMigrationJobCommand.cs
│   ├── Queries/
│   │   └── GetMigrationJobQuery.cs
│   ├── DTOs/
│   │   └── MigrationJobDto.cs
│   └── LSOMigrator.Application.csproj
├── LSOMigrator.Infrastructure/
│   ├── Data/
│   │   ├── LSOMigratorDbContext.cs
│   │   └── Configurations/
│   │       └── MigrationJobConfiguration.cs
│   └── LSOMigrator.Infrastructure.csproj
├── LSOMigrator.API/
│   ├── Controllers/
│   │   ├── HealthController.cs
│   │   └── MigrationController.cs
│   ├── Program.cs
│   ├── appsettings.json
│   └── LSOMigrator.API.csproj
└── LSOMigrator.Backend.sln
```

## Step-by-Step Implementation

### 1. Create Solution File
Generate `LSOMigrator.Backend.sln` with all project references.

### 2. Create Domain Layer
- **MigrationJob.cs**: Entity with Id, Name, Status, CreatedDate, SourcePath, TargetPath
- **FieldMapping.cs**: Entity with Id, SourceField, TargetField, MappingRule, MigrationJobId
- **ContractData.cs**: Entity with Id, JsonData, ProcessedDate, MigrationJobId
- **ProcessHistoryEntry.cs**: Audit entity with Id, Action, Timestamp, UserId, Details

### 3. Create Application Layer
- **CreateMigrationJobCommand.cs**: MediatR command with validation
- **GetMigrationJobQuery.cs**: MediatR query to retrieve jobs
- **MigrationJobDto.cs**: Data transfer object for API responses

### 4. Create Infrastructure Layer
- **LSOMigratorDbContext.cs**: DbContext with entities and audit fields
- **MigrationJobConfiguration.cs**: Entity Framework configuration

### 5. Create API Layer
- **Program.cs**: Configure services, middleware, and dependency injection
- **HealthController.cs**: Simple health check endpoint
- **MigrationController.cs**: CRUD operations for migration jobs
- **appsettings.json**: Configuration for connection strings and JWT

## Technical Requirements

- Use .NET 8.0
- Entity Framework Core with SQL Server
- MediatR for CQRS pattern
- AutoMapper for object mapping
- FluentValidation for input validation
- Swagger for API documentation
- JWT Bearer authentication

## Critical: Generate Actual Code Files

For each file mentioned above, create the complete C# code implementation. Include:
- Proper using statements
- Correct namespaces
- Complete class implementations
- Proper dependency injection setup
- Entity Framework configurations
- MediatR command/query handlers

Start by creating the solution file, then work through each layer systematically. Generate working, compilable C# code for each file.