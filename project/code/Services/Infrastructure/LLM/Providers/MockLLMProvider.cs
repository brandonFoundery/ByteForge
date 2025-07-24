using Microsoft.Extensions.Logging;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.LLM.Providers;

public class MockLLMProvider : ILLMProvider
{
    private readonly ILogger<MockLLMProvider> _logger;

    public MockLLMProvider(ILogger<MockLLMProvider> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public string Name => "Mock";
    public bool IsAvailable => true;

    public async Task<LLMGenerationResponse> GenerateAsync(LLMGenerationRequest request, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Mock LLM Provider generating response for prompt: {Prompt}", 
            request.Prompt?.Substring(0, Math.Min(request.Prompt.Length, 50)));

        // Simulate some processing time
        await Task.Delay(100, cancellationToken);

        // Generate mock response based on request
        var content = GenerateMockContent(request);

        return new LLMGenerationResponse
        {
            Success = true,
            Content = content,
            Provider = Name,
            Model = "mock-model-v1",
            TokensUsed = EstimateTokens(content),
            ResponseTime = TimeSpan.FromMilliseconds(100),
            Metadata = new Dictionary<string, object>
            {
                ["isMock"] = true,
                ["generatedAt"] = DateTime.UtcNow
            }
        };
    }

    public Task<bool> ValidateConnectionAsync()
    {
        return Task.FromResult(true);
    }
    
    private string GenerateMockContent(LLMGenerationRequest request)
    {
        // Check if this is a document generation request
        if (request.Prompt.Contains("Business Requirements Document", StringComparison.OrdinalIgnoreCase))
        {
            return GenerateMockBRD(request);
        }
        else if (request.Prompt.Contains("Product Requirements Document", StringComparison.OrdinalIgnoreCase))
        {
            return GenerateMockPRD(request);
        }
        else if (request.Prompt.Contains("Functional Requirements Document", StringComparison.OrdinalIgnoreCase))
        {
            return GenerateMockFRD(request);
        }
        else if (request.Prompt.Contains("Technical Requirements Document", StringComparison.OrdinalIgnoreCase))
        {
            return GenerateMockTRD(request);
        }

        // Default mock response
        return $"This is a mock response generated for testing purposes.\n\nOriginal prompt: {request.Prompt}\n\nMock generated content would appear here.";
    }

    private string GenerateMockBRD(LLMGenerationRequest request)
    {
        return @"## Executive Summary
This Business Requirements Document outlines the key business needs and objectives for the project.

## Business Objectives
- Improve operational efficiency
- Enhance customer satisfaction
- Increase revenue by 20%

## Stakeholders
- Product Owner: Jane Doe
- Development Team Lead: John Smith
- Business Analyst: Sarah Johnson

## Business Requirements
- BR-001: The system shall provide user authentication
- BR-002: The system shall support multiple user roles
- BR-003: The system shall generate automated reports

## Success Criteria
- All requirements implemented and tested
- User acceptance testing passed
- Performance benchmarks met";
    }

    private string GenerateMockPRD(LLMGenerationRequest request)
    {
        return @"## Product Overview
This product will revolutionize how users interact with our platform.

## Features
- User Management System
- Reporting Dashboard
- API Integration
- Mobile Application

## User Stories
- As a user, I want to log in securely
- As an admin, I want to manage user permissions
- As a user, I want to view my dashboard

## Technical Requirements
- Cloud-based architecture
- RESTful API design
- Responsive web interface

## Acceptance Criteria
- All features functional
- Performance under 2 second response time
- 99.9% uptime";
    }

    private string GenerateMockFRD(LLMGenerationRequest request)
    {
        return @"## System Overview
The system provides comprehensive functionality for managing business operations.

## Functional Requirements
- FR-001: User authentication using JWT tokens
- FR-002: Role-based access control
- FR-003: Data export functionality
- FR-004: Real-time notifications

## Use Cases
- UC-001: User Login
  - Actor: Registered User
  - Flow: Enter credentials → Validate → Grant access
- UC-002: Generate Report
  - Actor: Admin User
  - Flow: Select parameters → Generate → Download

## Data Requirements
- User profiles with encrypted passwords
- Audit logs for all transactions
- Configurable system settings

## Interface Requirements
- RESTful API for external integrations
- WebSocket support for real-time updates
- Mobile-responsive UI";
    }

    private string GenerateMockTRD(LLMGenerationRequest request)
    {
        return @"## Architecture Overview
Microservices architecture deployed on cloud infrastructure.

## Technology Stack
- Backend: .NET 8 with ASP.NET Core
- Frontend: React 18 with TypeScript
- Database: SQL Server 2022
- Cache: Redis
- Container: Docker
- Orchestration: Kubernetes

## Database Design
- Normalized relational schema
- Indexing strategy for performance
- Backup and recovery procedures

## API Design
- RESTful endpoints following OpenAPI 3.0
- JWT authentication
- Rate limiting and throttling

## Security Requirements
- TLS 1.3 for all communications
- Data encryption at rest
- Regular security audits
- OWASP compliance

## Performance Requirements
- Response time < 200ms for 95% of requests
- Support 10,000 concurrent users
- 99.9% uptime SLA";
    }

    private int EstimateTokens(string content)
    {
        // Rough estimation: 1 token ≈ 4 characters
        return content.Length / 4;
    }
}