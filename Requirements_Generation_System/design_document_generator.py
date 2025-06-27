"""
Design Document Generator for AI Agents

This module generates detailed design documents for each AI agent that will implement
features according to the development plan. Each design document contains branch
information, work scope, and detailed design specifications for Claude Code implementation.
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import anthropic
import openai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class GenerationResult:
    """Result of design document generation"""
    success: bool
    total_execution_time: float
    generated_documents: List[str]
    error_summary: Optional[str] = None


class DesignDocumentGenerator:
    """Generates AI agent design documents using direct API calls"""
    
    def __init__(self, project_name: str, base_path: Path, model_provider: str = "openai"):
        self.project_name = project_name
        self.base_path = base_path
        self.model_provider = model_provider
        self.output_path = base_path / "generated_documents" / "design"
        self.requirements_path = base_path / "generated_documents"
        
        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize API client based on provider
        self._init_api_client()
        
        # Agent definitions
        self.agents = {
            "frontend": {
                "name": "Frontend Agent",
                "branch_pattern": "feature/frontend-*",
                "technology_stack": "Next.js, React, TypeScript, Tailwind CSS",
                "description": "Responsible for all user interface components and user experience flows"
            },
            "backend": {
                "name": "Backend Agent", 
                "branch_pattern": "feature/backend-*",
                "technology_stack": "ASP.NET Core, Entity Framework Core, CQRS, MediatR",
                "description": "Responsible for server-side business logic, APIs, and data access layers"
            },
            "infrastructure": {
                "name": "Infrastructure Agent",
                "branch_pattern": "feature/infrastructure-*", 
                "technology_stack": "Azure, Terraform, Azure DevOps, Docker, Kubernetes",
                "description": "Responsible for cloud infrastructure, CI/CD pipelines, and deployment automation"
            },
            "security": {
                "name": "Security Agent",
                "branch_pattern": "feature/security-*",
                "technology_stack": "ASP.NET Core Identity, JWT, Azure AD, Azure Key Vault", 
                "description": "Responsible for authentication, authorization, audit trails, and compliance"
            },
            "integration": {
                "name": "Integration Agent",
                "branch_pattern": "feature/integration-*",
                "technology_stack": "Stripe API, Azure Service Bus, REST APIs, Webhooks",
                "description": "Responsible for third-party integrations, payment gateway, and external APIs"
            }
        }
    
    def _init_api_client(self):
        """Initialize the appropriate API client"""
        if self.model_provider == "openai":
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.model_provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    async def generate_all_agent_designs(self) -> GenerationResult:
        """Generate design documents for all AI agents"""
        start_time = time.time()
        generated_documents = []
        errors = []
        
        console.print(f"[cyan]Generating design documents for {len(self.agents)} AI agents...[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            for agent_id, agent_info in self.agents.items():
                task = progress.add_task(f"Generating {agent_info['name']} design...", total=None)
                
                try:
                    # Generate design document for this agent
                    document_content = await self._generate_agent_design(agent_id, agent_info)
                    
                    # Save the document
                    filename = f"{agent_id}-agent-design.md"
                    filepath = self.output_path / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(document_content)
                    
                    generated_documents.append(filename)
                    console.print(f"[green]✅ Generated: {filename}[/green]")
                    
                except Exception as e:
                    error_msg = f"Failed to generate {agent_info['name']} design: {str(e)}"
                    errors.append(error_msg)
                    console.print(f"[red]❌ {error_msg}[/red]")
                
                progress.remove_task(task)
        
        # Generate README.md for the design directory
        try:
            readme_content = self._generate_design_readme()
            readme_path = self.output_path / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            generated_documents.append("README.md")
            console.print(f"[green]✅ Generated: README.md[/green]")
        except Exception as e:
            errors.append(f"Failed to generate README.md: {str(e)}")
        
        total_time = time.time() - start_time
        success = len(errors) == 0
        error_summary = "; ".join(errors) if errors else None
        
        return GenerationResult(
            success=success,
            total_execution_time=total_time,
            generated_documents=generated_documents,
            error_summary=error_summary
        )
    
    async def _generate_agent_design(self, agent_id: str, agent_info: Dict) -> str:
        """Generate design document for a specific agent using API calls"""
        
        # Load context from requirements documents
        context = await self._load_requirements_context()
        dev_plan = await self._load_dev_plan()
        
        # Create the prompt for design document generation
        prompt = self._create_design_prompt(agent_id, agent_info, context, dev_plan)
        
        # Generate content using the selected API
        if self.model_provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert software architect creating detailed design documents for AI agents that will implement enterprise software features."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            content = response.choices[0].message.content
        
        elif self.model_provider == "anthropic":
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.content[0].text
        
        return content
    
    async def _load_requirements_context(self) -> str:
        """Load relevant requirements documents as context"""
        context_files = [
            "FRD.md", "NFRD.md", "TRD.md", "api_spec.md", 
            "db_schema.md", "test_plan.md"
        ]
        
        context = []
        for filename in context_files:
            filepath = self.requirements_path / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context.append(f"## {filename}\n\n{content}\n\n")
        
        return "\n".join(context)
    
    async def _load_dev_plan(self) -> str:
        """Load the development plan document"""
        dev_plan_path = self.requirements_path / "dev_plan.md"
        if dev_plan_path.exists():
            with open(dev_plan_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _create_design_prompt(self, agent_id: str, agent_info: Dict, context: str, dev_plan: str) -> str:
        """Create the prompt for generating agent design document"""
        
        return f"""Create a comprehensive design document for the {agent_info['name']} that will implement features using Claude Code.

AGENT SPECIFICATIONS:
- Name: {agent_info['name']}
- Branch Pattern: {agent_info['branch_pattern']}
- Technology Stack: {agent_info['technology_stack']}
- Description: {agent_info['description']}

REQUIREMENTS CONTEXT:
{context}

DEVELOPMENT PLAN:
{dev_plan}

Generate a detailed design document with the following structure:

---
agent_type: {agent_info['name']}
branch_pattern: {agent_info['branch_pattern']}
technology_stack: {agent_info['technology_stack']}
dependencies: [list of other agents this depends on]
generated_at: '{time.strftime("%Y-%m-%dT%H:%M:%S.%f")}'
id: {agent_id.upper()}_AGENT_DESIGN
version: '1.0'
---

# {agent_info['name']} Design Document

## 1. Agent Overview
### 1.1 Role and Responsibilities
### 1.2 Scope of Work
### 1.3 Technology Stack

## 2. Feature Assignments from Development Plan
[Extract relevant features from the dev_plan.md and organize by phase]

## 3. Branch Strategy and Workflow
### 3.1 Branch Naming Convention
### 3.2 Development Workflow

## 4. Technical Architecture
[Detailed technical architecture specific to this agent]

## 5. Dependencies and Integration Points
[Dependencies on other agents and external services]

## 6. Implementation Plan by Phase
[Phase-by-phase implementation plan with timelines]

## 7. Claude Code Instructions
### 7.1 Context Files Required
### 7.2 Implementation Prompts
### 7.3 Validation Criteria

## 8. Success Metrics and Testing
[Specific metrics and testing criteria for this agent]

Make the document comprehensive, actionable, and ready for Claude Code implementation. Include specific prompts that can be used with Claude Code's --add-dir and -p flags.
"""
    
    def _generate_design_readme(self) -> str:
        """Generate README.md for the design directory"""
        return f"""# AI Agent Design Documents

This directory contains detailed design documents for each AI agent that will implement features according to the {self.project_name} development plan.

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
claude --add-dir ./generated_documents/design \\
      --add-dir ./generated_documents \\
      --add-dir ./[ProjectDirectory] \\
      -p "Implement the [Agent] features for Phase [N]"
```

The design documents provide comprehensive context including:
- Requirements from FRD, NFRD, TRD documents
- API specifications and database schema
- UI/UX specifications and component designs
- Test plans and validation criteria

## Generated At
{time.strftime("%Y-%m-%d %H:%M:%S")}

## Model Provider
{self.model_provider.upper()}
"""


async def main():
    """Test the design document generator"""
    base_path = Path("d:/Repository/@Clients/FY.WB.Midway")
    generator = DesignDocumentGenerator("FY.WB.Midway", base_path, "openai")
    
    result = await generator.generate_all_agent_designs()
    
    if result.success:
        console.print(f"[green]✅ Successfully generated {len(result.generated_documents)} design documents[/green]")
    else:
        console.print(f"[red]❌ Generation failed: {result.error_summary}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
