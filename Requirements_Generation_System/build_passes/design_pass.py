"""
Design Pass Implementation - OpenAI o3

This module implements Pass 1 of the AI-driven application builder.
Uses OpenAI o3 to analyze requirements and create high-level system design.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional

import openai
from rich.console import Console

console = Console()


class DesignPass:
    """
    Pass 1: Design Phase using OpenAI o3
    
    Analyzes requirements and creates high-level system design including:
    - System architecture
    - Component breakdown
    - Data models
    - API interfaces
    - Technology stack decisions
    """

    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.base_path = base_path
        self.requirements_path = base_path / "Requirements"
        
        # Get design pass configuration
        self.pass_config = config.get('application_builder', {}).get('passes', {}).get('design', {})
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.OpenAI(api_key=api_key)

    async def run(self, feature_spec: str) -> str:
        """
        Run the design pass
        
        Args:
            feature_spec: Feature specification from user input
            
        Returns:
            Design document as markdown string
        """
        console.print("[cyan]🎨 Running Design Pass with OpenAI o3...[/cyan]")
        
        # Gather context from existing requirements
        context = await self._gather_requirements_context()
        
        # Analyze existing codebase structure
        codebase_analysis = await self._analyze_codebase_structure()
        
        # Create design prompt
        design_prompt = self._create_design_prompt(feature_spec, context, codebase_analysis)
        
        # Call OpenAI o3
        design_document = await self._call_openai_o3(design_prompt)
        
        # Validate and structure the design
        structured_design = await self._structure_design_output(design_document)
        
        console.print("[green]✅ Design Pass completed successfully[/green]")
        return structured_design

    async def _gather_requirements_context(self) -> str:
        """Gather context from existing requirements documents"""
        context_parts = []
        
        # Read key requirements files
        key_files = [
            "consolidated-requirements/master-prd.md",
            "consolidated-requirements/master-technical-architecture.md",
            "cross-system-analysis/unified-api-strategy.md"
        ]
        
        for file_path in key_files:
            full_path = self.requirements_path / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    context_parts.append(f"## {file_path}\n\n{content[:2000]}...")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
        
        return "\n\n".join(context_parts)

    async def _analyze_codebase_structure(self) -> str:
        """Analyze the existing codebase structure"""
        analysis_parts = []
        
        # Analyze FrontEnd structure
        frontend_path = self.base_path / "FrontEnd"
        if frontend_path.exists():
            frontend_analysis = self._analyze_frontend_structure(frontend_path)
            analysis_parts.append(f"## Frontend Structure\n\n{frontend_analysis}")
        
        # Analyze BackEnd structure
        backend_path = self.base_path / "BackEnd"
        if backend_path.exists():
            backend_analysis = self._analyze_backend_structure(backend_path)
            analysis_parts.append(f"## Backend Structure\n\n{backend_analysis}")
        
        return "\n\n".join(analysis_parts)

    def _analyze_frontend_structure(self, frontend_path: Path) -> str:
        """Analyze the Next.js frontend structure"""
        analysis = []
        
        # Read package.json
        package_json = frontend_path / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                analysis.append("### Dependencies")
                analysis.append(f"- Framework: Next.js {package_data.get('dependencies', {}).get('next', 'unknown')}")
                analysis.append(f"- React: {package_data.get('dependencies', {}).get('react', 'unknown')}")
                analysis.append(f"- TypeScript: {package_data.get('devDependencies', {}).get('typescript', 'unknown')}")
                analysis.append(f"- Styling: Tailwind CSS")
                analysis.append(f"- State Management: React Context + SWR")
                
            except Exception as e:
                analysis.append(f"Could not read package.json: {e}")
        
        # Analyze src structure
        src_path = frontend_path / "src"
        if src_path.exists():
            analysis.append("\n### Source Structure")
            analysis.append("- `/src/components` - React components")
            analysis.append("- `/src/contexts` - React contexts (Auth, Tenant)")
            analysis.append("- `/src/pages` - Next.js pages (file-based routing)")
            analysis.append("- `/src/lib` - Utility libraries")
            analysis.append("- `/src/styles` - Global styles")
        
        return "\n".join(analysis)

    def _analyze_backend_structure(self, backend_path: Path) -> str:
        """Analyze the .NET Core backend structure"""
        analysis = []
        
        analysis.append("### Architecture")
        analysis.append("- Clean Architecture pattern")
        analysis.append("- .NET 8.0 Web API")
        analysis.append("- Entity Framework Core with SQL Server")
        analysis.append("- Multi-tenant with Finbuckle.MultiTenant")
        analysis.append("- CQRS with MediatR")
        analysis.append("- JWT Authentication")
        
        analysis.append("\n### Project Structure")
        analysis.append("- `FY.WB.Midway` - Presentation Layer (API Controllers)")
        analysis.append("- `FY.WB.Midway.Application` - Application Layer (CQRS, Business Logic)")
        analysis.append("- `FY.WB.Midway.Domain` - Domain Layer (Entities, Interfaces)")
        analysis.append("- `FY.WB.Midway.Infrastructure` - Infrastructure Layer (Data, External Services)")
        
        return "\n".join(analysis)

    def _create_design_prompt(self, feature_spec: str, context: str, codebase_analysis: str) -> str:
        """Create the design prompt for OpenAI o3"""
        return f"""You are an expert software architect tasked with designing a new feature for the LSOMigrator enterprise logistics and payment platform.

## Feature Specification
{feature_spec}

## Existing System Context
{context}

## Current Codebase Structure
{codebase_analysis}

## Your Task
Create a comprehensive system design for implementing this feature. Your design should include:

1. **System Architecture Overview**
   - How this feature fits into the existing architecture
   - Component interaction diagrams
   - Data flow patterns

2. **Frontend Design**
   - New React components needed
   - Page/route structure
   - State management approach
   - UI/UX considerations

3. **Backend Design**
   - New API endpoints required
   - Database schema changes
   - Business logic organization
   - Integration points

4. **Data Model**
   - New entities and relationships
   - Database migrations needed
   - Data validation rules

5. **API Interface Design**
   - RESTful endpoint specifications
   - Request/response schemas
   - Authentication/authorization requirements

6. **Technology Stack Decisions**
   - Any new dependencies needed
   - Justification for technology choices
   - Performance considerations

7. **Implementation Strategy**
   - Development phases
   - Risk assessment
   - Testing approach

Please provide a detailed, well-structured design document in markdown format that follows the existing system patterns and maintains consistency with the current architecture.

Focus on:
- Maintainability and scalability
- Security best practices
- Performance optimization
- Code reusability
- Clear separation of concerns

The design should be implementable by a development team familiar with the existing codebase."""

    async def _call_openai_o3(self, prompt: str) -> str:
        """Call OpenAI o3 API"""
        try:
            model_name = self.pass_config.get('model_name', 'o3-mini')
            temperature = self.pass_config.get('temperature', 0.2)
            max_tokens = self.pass_config.get('max_tokens', 4000)

            console.print(f"[dim]Calling OpenAI {model_name} with {len(prompt)} characters...[/dim]")

            # Build parameters based on model type
            params = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert software architect with deep knowledge of enterprise application design, Clean Architecture, and modern web development practices."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Add model-specific parameters
            if 'o3' in model_name.lower():
                # o3 models don't support temperature and use max_completion_tokens
                params['max_completion_tokens'] = max_tokens
            else:
                # Other models support temperature and use max_tokens
                params['temperature'] = temperature
                params['max_tokens'] = max_tokens

            response = self.client.chat.completions.create(**params)
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]Error calling OpenAI API: {e}[/red]")
            raise

    async def _structure_design_output(self, design_document: str) -> str:
        """Structure and validate the design output"""
        # Add metadata header
        structured_output = f"""---
title: "System Design Document"
feature: "AI-Generated Feature"
pass: "1-Design"
model: "OpenAI o3"
generated_at: "{asyncio.get_event_loop().time()}"
---

# System Design Document

{design_document}

---

*This document was generated by the AI-Driven Application Builder - Design Pass (OpenAI o3)*
"""
        
        return structured_output
