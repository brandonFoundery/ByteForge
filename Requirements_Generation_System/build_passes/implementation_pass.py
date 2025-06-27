"""
Implementation Pass - Claude Sonnet 4

This module implements Pass 3 of the AI-driven application builder.
Uses Claude Sonnet 4 to create detailed implementation specifications from the reviewed design.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional

import anthropic
from rich.console import Console

console = Console()


class ImplementationPass:
    """
    Pass 3: Implementation Phase using Claude Sonnet 4
    
    Creates detailed implementation specifications including:
    - Detailed code structure and organization
    - File-by-file implementation plans
    - Database migration scripts
    - API endpoint implementations
    - Component specifications
    - Testing strategies
    """

    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.base_path = base_path
        self.frontend_path = base_path / "FrontEnd"
        self.backend_path = base_path / "BackEnd"
        self.requirements_path = base_path / "Requirements"
        
        # Get implementation pass configuration
        self.pass_config = config.get('application_builder', {}).get('passes', {}).get('implementation', {})
        
        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)

    async def run(self, review_document: str) -> str:
        """
        Run the implementation pass
        
        Args:
            review_document: Review document from Pass 2 (Gemini 2.5)
            
        Returns:
            Implementation specification as markdown string
        """
        console.print("[cyan]⚙️ Running Implementation Pass with Claude Sonnet 4...[/cyan]")
        
        # Extract design and review information
        design_info = await self._extract_design_information(review_document)
        
        # Analyze existing codebase patterns
        codebase_patterns = await self._analyze_codebase_patterns()
        
        # Create implementation prompt
        implementation_prompt = self._create_implementation_prompt(
            design_info, codebase_patterns, review_document
        )
        
        # Call Claude Sonnet 4
        implementation_spec = await self._call_claude_sonnet_4(implementation_prompt)
        
        # Structure and validate the implementation specification
        structured_implementation = await self._structure_implementation_output(implementation_spec)
        
        console.print("[green]✅ Implementation Pass completed successfully[/green]")
        return structured_implementation

    async def _extract_design_information(self, review_document: str) -> Dict[str, Any]:
        """Extract key design information from the review document"""
        design_info = {
            'has_original_design': 'Original Design Document' in review_document,
            'has_review_feedback': 'Review Summary' in review_document or 'Recommendations' in review_document,
            'approval_status': 'unknown',
            'critical_issues': [],
            'recommendations': []
        }
        
        # Extract approval status
        if 'Ready for implementation' in review_document:
            design_info['approval_status'] = 'approved'
        elif 'Needs revision' in review_document:
            design_info['approval_status'] = 'needs_revision'
        elif 'Major concerns' in review_document:
            design_info['approval_status'] = 'major_concerns'
        
        # Look for critical issues and recommendations sections
        lines = review_document.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            if 'critical issues' in line_lower:
                current_section = 'critical_issues'
            elif 'recommendations' in line_lower:
                current_section = 'recommendations'
            elif line.startswith('#') or line.startswith('##'):
                current_section = None
            elif current_section and line.strip():
                if line.startswith('-') or line.startswith('*'):
                    design_info[current_section].append(line.strip())
        
        return design_info

    async def _analyze_codebase_patterns(self) -> str:
        """Analyze existing codebase patterns and conventions"""
        patterns = []
        
        # Analyze Frontend patterns
        frontend_patterns = self._analyze_frontend_patterns()
        patterns.append(f"## Frontend Patterns\n\n{frontend_patterns}")
        
        # Analyze Backend patterns
        backend_patterns = self._analyze_backend_patterns()
        patterns.append(f"## Backend Patterns\n\n{backend_patterns}")
        
        return "\n\n".join(patterns)

    def _analyze_frontend_patterns(self) -> str:
        """Analyze Next.js frontend patterns"""
        patterns = []
        
        patterns.append("### Component Structure")
        patterns.append("- Components in `/src/components` with TypeScript")
        patterns.append("- Layout components in `/src/components/layouts`")
        patterns.append("- Shared UI components with consistent naming")
        patterns.append("- Props interfaces defined with TypeScript")
        
        patterns.append("\n### State Management")
        patterns.append("- React Context for global state (Auth, Tenant)")
        patterns.append("- SWR for data fetching and caching")
        patterns.append("- Local state with useState/useReducer")
        
        patterns.append("\n### Styling Patterns")
        patterns.append("- Tailwind CSS for styling")
        patterns.append("- Responsive design with mobile-first approach")
        patterns.append("- Consistent color scheme and spacing")
        
        patterns.append("\n### API Integration")
        patterns.append("- Custom hooks for API calls")
        patterns.append("- Error handling with try-catch")
        patterns.append("- Loading states and error boundaries")
        
        return "\n".join(patterns)

    def _analyze_backend_patterns(self) -> str:
        """Analyze .NET Core backend patterns"""
        patterns = []
        
        patterns.append("### Clean Architecture Layers")
        patterns.append("- **Presentation**: Controllers, DTOs, Filters")
        patterns.append("- **Application**: Commands, Queries, Handlers (CQRS)")
        patterns.append("- **Domain**: Entities, Value Objects, Domain Services")
        patterns.append("- **Infrastructure**: Data Access, External Services")
        
        patterns.append("\n### CQRS Pattern")
        patterns.append("- Commands for write operations")
        patterns.append("- Queries for read operations")
        patterns.append("- MediatR for request/response handling")
        patterns.append("- Separate models for commands/queries")
        
        patterns.append("\n### Entity Framework Patterns")
        patterns.append("- DbContext with proper configuration")
        patterns.append("- Entity configurations in separate files")
        patterns.append("- Repository pattern (optional, EF Core is already UoW)")
        patterns.append("- Migrations for schema changes")
        
        patterns.append("\n### Multi-Tenancy")
        patterns.append("- Finbuckle.MultiTenant for tenant resolution")
        patterns.append("- Tenant-specific data isolation")
        patterns.append("- Tenant context in all operations")
        
        patterns.append("\n### API Patterns")
        patterns.append("- RESTful endpoints with proper HTTP verbs")
        patterns.append("- Consistent response formats")
        patterns.append("- Swagger/OpenAPI documentation")
        patterns.append("- Versioning strategy")
        
        return "\n".join(patterns)

    def _create_implementation_prompt(self, design_info: Dict[str, Any], codebase_patterns: str, review_document: str) -> str:
        """Create the implementation prompt for Claude Sonnet 4"""
        return f"""You are Claude Sonnet 4, an expert software developer specializing in creating detailed implementation specifications. Your task is to create comprehensive, actionable implementation plans based on the design review provided.

## Review Document Analysis
{review_document}

## Design Information Summary
- Approval Status: {design_info['approval_status']}
- Has Original Design: {design_info['has_original_design']}
- Has Review Feedback: {design_info['has_review_feedback']}
- Critical Issues Count: {len(design_info['critical_issues'])}
- Recommendations Count: {len(design_info['recommendations'])}

## Existing Codebase Patterns
{codebase_patterns}

## Your Implementation Task

Create a comprehensive implementation specification that includes:

### 1. Implementation Overview
- Feature summary and scope
- Implementation phases and timeline
- Dependencies and prerequisites
- Risk mitigation strategies

### 2. Database Implementation
- Entity definitions with properties and relationships
- Migration scripts (Entity Framework Core)
- Seed data requirements
- Indexing strategy

### 3. Backend Implementation
- **Domain Layer**: Entities, Value Objects, Domain Services
- **Application Layer**: Commands, Queries, Handlers, DTOs
- **Infrastructure Layer**: Repositories, External Services
- **Presentation Layer**: Controllers, Filters, Middleware

### 4. Frontend Implementation
- **Components**: React components with TypeScript interfaces
- **Pages**: Next.js pages and routing
- **State Management**: Context providers and custom hooks
- **API Integration**: Service functions and error handling

### 5. API Specifications
- Detailed endpoint definitions
- Request/response schemas
- Authentication/authorization requirements
- Error handling and status codes

### 6. File Structure
- Complete file organization
- Naming conventions
- Import/export patterns

### 7. Testing Strategy
- Unit test specifications
- Integration test plans
- End-to-end test scenarios

### 8. Implementation Steps
- Detailed step-by-step implementation guide
- Order of implementation (dependencies first)
- Validation checkpoints

## Implementation Guidelines

1. **Follow Existing Patterns**: Maintain consistency with the current codebase
2. **Clean Architecture**: Respect layer boundaries and dependencies
3. **SOLID Principles**: Ensure code follows SOLID design principles
4. **Multi-Tenancy**: Include tenant isolation in all data operations
5. **Security**: Implement proper authentication and authorization
6. **Performance**: Consider caching, indexing, and optimization
7. **Testability**: Design for easy unit and integration testing
8. **Maintainability**: Write clear, documented, and modular code

## Output Format

Structure your response as a comprehensive implementation specification in markdown format with:

- Clear section headers
- Code examples where appropriate
- Specific file names and locations
- Implementation order and dependencies
- Testing requirements
- Deployment considerations

Focus on providing actionable, specific guidance that a development team can follow to implement the feature successfully. Include enough detail that developers can start coding immediately without additional design decisions.

Address any critical issues or recommendations from the review, and ensure the implementation follows the established patterns and architecture of the existing system."""

    async def _call_claude_sonnet_4(self, prompt: str) -> str:
        """Call Claude Sonnet 4 API"""
        try:
            model_name = self.pass_config.get('model_name', 'claude-3-sonnet-20240229')
            temperature = self.pass_config.get('temperature', 0.2)
            max_tokens = self.pass_config.get('max_tokens', 4000)
            
            console.print(f"[dim]Calling Claude Sonnet 4 with {len(prompt)} characters...[/dim]")
            
            response = self.client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are Claude Sonnet 4, an expert software developer with deep knowledge of Clean Architecture, CQRS, Entity Framework Core, Next.js, and modern development practices. You excel at creating detailed, actionable implementation specifications.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            console.print(f"[red]Error calling Claude API: {e}[/red]")
            raise

    async def _structure_implementation_output(self, implementation_spec: str) -> str:
        """Structure and format the implementation output"""
        # Add metadata header
        structured_output = f"""---
title: "Implementation Specification"
feature: "AI-Generated Feature"
pass: "3-Implementation"
model: "Claude Sonnet 4"
generated_at: "{asyncio.get_event_loop().time()}"
implementation_status: "ready_for_build"
---

# Implementation Specification

## Specification Summary
This document contains the comprehensive implementation specification generated by Claude Sonnet 4 based on the design review from Pass 2. This specification provides detailed, actionable guidance for implementing the feature.

## Implementation Readiness
- **Status**: Ready for Build Phase (Pass 4)
- **Generated by**: Claude Sonnet 4 (Pass 3)
- **Based on**: Design Review from Gemini 2.5 (Pass 2)
- **Generation date**: {asyncio.get_event_loop().time()}

---

{implementation_spec}

---

## Next Steps
This implementation specification will be used in Pass 4 (Build Phase) where the actual code will be generated, compiled, and tested using the automated build system.

The build system will:
1. Generate code files based on these specifications
2. Create database migrations
3. Implement API endpoints
4. Build frontend components
5. Run automated tests
6. Create a pull request with the working implementation

---

*This specification was generated by the AI-Driven Application Builder - Implementation Pass (Claude Sonnet 4)*
"""
        
        return structured_output
