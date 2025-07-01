#!/usr/bin/env python3
"""
Enhanced Claude Code Instruction Template Generator

This module creates optimized, structured instruction templates for Claude Code
that eliminate shell escaping issues and provide better context management.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from rich.console import Console

console = Console()


class InstructionTemplate:
    """Enhanced instruction template with structured sections"""
    
    def __init__(self, agent_id: str, phase_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.phase_id = phase_id
        self.config = config
        self.timestamp = datetime.now().isoformat()
        
    def generate_instruction(self) -> str:
        """Generate a comprehensive, structured instruction for Claude Code"""
        
        agent_config = self._get_agent_config()
        phase_config = self._get_phase_config()
        
        instruction = f"""# {agent_config['name']} - {phase_config['name']}

## Execution Metadata
- **Agent ID**: {self.agent_id}
- **Phase ID**: {self.phase_id}
- **Generated**: {self.timestamp}
- **Estimated Duration**: {agent_config.get('estimated_duration', 30)} minutes
- **Priority**: {agent_config.get('priority', 1)}

## Mission Statement

You are the **{agent_config['name']}** responsible for implementing {phase_config['description']}.

Your primary objective is to {agent_config['description']} following Clean Architecture principles and modern development best practices.

## Context and Prerequisites

### Required Documents
Read and understand these context documents before starting:

1. **Project Overview**
   - `CLAUDE.md` - Project structure and development guidelines
   - `generated_documents/prd.md` - Product Requirements Document
   - `generated_documents/frd.md` - Functional Requirements Document

2. **Technical Specifications**
   - `generated_documents/api_spec.md` - API Specification
   - `generated_documents/db_schema.md` - Database Schema
   - `generated_documents/dev_plan.md` - Development Plan

3. **Design Documents**
   - `generated_documents/design/{self.agent_id}-agent-design.md` - Your specific design document

### Dependencies
{self._generate_dependencies_section()}

## Specific Deliverables

{self._generate_deliverables_section()}

## Implementation Guidelines

### Code Quality Standards
- Follow existing code patterns and conventions
- Use TypeScript for frontend, C# for backend
- Implement proper error handling and logging
- Add comprehensive documentation
- Ensure all code is testable

### Security Requirements
- Implement proper authentication and authorization
- Validate all inputs
- Use secure coding practices
- Follow OWASP guidelines

### Performance Requirements
- Optimize for scalability
- Implement efficient data access patterns
- Use caching where appropriate
- Monitor performance metrics

## Build and Test Process

{self._generate_build_process()}

## Completion Criteria

You must complete ALL of the following before marking this task as done:

### ✅ Code Deliverables
- [ ] All required files created or modified
- [ ] Code follows project standards and patterns
- [ ] All imports and dependencies properly configured
- [ ] Documentation updated (README, API docs, etc.)

### ✅ Build Success
- [ ] Code compiles without errors
- [ ] All dependencies resolve correctly
- [ ] No linting errors or warnings
- [ ] Build process completes successfully

### ✅ Testing
- [ ] All existing tests continue to pass
- [ ] New functionality has appropriate tests
- [ ] Integration tests pass
- [ ] Manual testing completed

### ✅ Integration
- [ ] Changes integrate properly with existing code
- [ ] API contracts maintained
- [ ] Database migrations applied (if needed)
- [ ] Dependencies updated correctly

## Success Verification

Run these commands to verify successful completion:

```bash
{self._generate_verification_commands()}
```

## Error Recovery

If you encounter issues:

1. **Build Errors**: Check dependencies, imports, and configuration
2. **Test Failures**: Review test requirements and data setup
3. **Integration Issues**: Verify API contracts and data models
4. **Dependency Problems**: Check package versions and compatibility

## Completion Report

When finished, provide a structured report with:

```markdown
# {agent_config['name']} {phase_config['name']} - Completion Report

## Summary
[Brief summary of what was implemented]

## Deliverables Completed
{self._generate_completion_checklist()}

## Files Created/Modified
[List all files you created or modified]

## Build and Test Results
- Build Status: [SUCCESS/FAILED]
- Test Results: [X/Y tests passed]
- Integration Status: [SUCCESS/FAILED]

## Known Issues or Limitations
[List any known issues]

## Next Steps
[What dependent agents can now proceed]
```

## Important Notes

- **Quality over Speed**: Focus on creating maintainable, well-structured code
- **Follow Patterns**: Use existing project patterns and conventions
- **Test Everything**: Ensure all functionality works as expected
- **Document Changes**: Update relevant documentation
- **Commit Properly**: Use clear, descriptive commit messages

---

**Start by reading all context documents, then proceed with implementation following the exact deliverables listed above.**
"""
        
        return instruction

    def _get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration from config"""
        agents_config = self.config.get('claude_code_execution', {}).get('agents', {})
        return agents_config.get(self.agent_id, {
            'name': f'{self.agent_id.title()} Agent',
            'description': f'{self.agent_id} implementation',
            'priority': 1,
            'estimated_duration': 30
        })

    def _get_phase_config(self) -> Dict[str, Any]:
        """Get phase configuration from config"""
        phases_config = self.config.get('claude_code_execution', {}).get('phases', {})
        return phases_config.get(self.phase_id, {
            'name': f'{self.phase_id.title()}',
            'description': f'{self.phase_id} implementation',
            'priority': 1,
            'estimated_duration': 60
        })

    def _generate_dependencies_section(self) -> str:
        """Generate dependencies section"""
        phases_config = self.config.get('claude_code_execution', {}).get('phases', {})
        phase_config = phases_config.get(self.phase_id, {})
        dependencies = phase_config.get('dependencies', {}).get(self.agent_id, [])
        
        if not dependencies:
            return "**Prerequisites**: None - this agent can run independently."
        
        deps_text = "**Prerequisites**: The following agents must complete successfully before you start:\n\n"
        for dep in dependencies:
            deps_text += f"- {dep}\n"
        
        deps_text += "\nVerify that all prerequisite agents have completed before starting your implementation."
        return deps_text

    def _generate_deliverables_section(self) -> str:
        """Generate specific deliverables based on agent and phase"""
        deliverables = {
            ('backend', 'phase1'): [
                "Core domain entities with proper inheritance from FullAuditedMultiTenantEntity",
                "Database context configuration with multi-tenancy support",
                "Basic CRUD operations using CQRS pattern with MediatR",
                "Authentication and authorization infrastructure",
                "Core API controllers following Clean Architecture patterns",
                "Database migrations for core entities",
                "Basic validation using FluentValidation",
                "Error handling middleware",
                "Logging infrastructure setup"
            ],
            ('frontend', 'phase1'): [
                "Main dashboard layout with responsive design",
                "Authentication components (login, register)",
                "Core navigation and routing setup",
                "Basic form components with validation",
                "Data fetching setup with SWR or React Query",
                "Multi-layout system (Admin, Client, Public)",
                "Core UI components library",
                "State management setup (Context API)",
                "Error boundary components"
            ],
            ('security', 'phase1'): [
                "JWT authentication implementation",
                "Role-based authorization system",
                "Security middleware configuration",
                "Input validation and sanitization",
                "CORS configuration",
                "Security headers implementation",
                "Audit logging system",
                "Password security implementation",
                "Session management"
            ],
            ('infrastructure', 'phase1'): [
                "Docker containerization setup",
                "Development environment configuration",
                "CI/CD pipeline basic setup",
                "Environment configuration management",
                "Health check endpoints",
                "Logging infrastructure",
                "Monitoring setup",
                "Database connection configuration",
                "Deployment scripts"
            ],
            ('integration', 'phase1'): [
                "API integration patterns",
                "External service connectors",
                "Data synchronization mechanisms",
                "Error handling for external calls",
                "Retry and circuit breaker patterns",
                "API versioning strategy",
                "Integration testing framework",
                "Mock external services for testing",
                "API documentation generation"
            ]
        }
        
        key = (self.agent_id, self.phase_id)
        specific_deliverables = deliverables.get(key, [f"{self.agent_id} {self.phase_id} implementation"])
        
        deliverables_text = f"Complete the following specific deliverables for {self.agent_id} {self.phase_id}:\n\n"
        for i, deliverable in enumerate(specific_deliverables, 1):
            deliverables_text += f"{i}. **{deliverable}**\n"
        
        return deliverables_text

    def _generate_build_process(self) -> str:
        """Generate build process instructions"""
        if self.agent_id == 'backend':
            return """### Backend Build Process
```bash
cd BackEnd
dotnet restore
dotnet build
dotnet test
dotnet run --project FY.WB.Midway
```

### Database Operations
```bash
# Add migration (if needed)
dotnet ef migrations add NewMigration --project FY.WB.Midway.Infrastructure --startup-project FY.WB.Midway

# Update database
dotnet ef database update --project FY.WB.Midway.Infrastructure --startup-project FY.WB.Midway
```"""
        
        elif self.agent_id == 'frontend':
            return """### Frontend Build Process
```bash
cd FrontEnd
npm install
npm run lint
npm run build
npm test
npm run dev  # for development server
```

### TypeScript Check
```bash
npm run type-check
```"""
        
        else:
            return f"""### {self.agent_id.title()} Build Process
Follow the standard build process for your technology stack.
Ensure all dependencies are installed and configured properly.
Run all tests to verify functionality."""

    def _generate_verification_commands(self) -> str:
        """Generate verification commands"""
        if self.agent_id == 'backend':
            return """# Backend verification
cd BackEnd
dotnet build
dotnet test
dotnet run --no-build --project FY.WB.Midway &
curl -f http://localhost:5002/health || echo "Health check failed"
"""
        elif self.agent_id == 'frontend':
            return """# Frontend verification
cd FrontEnd
npm run lint
npm run type-check
npm run build
npm test -- --watchAll=false
"""
        else:
            return f"# {self.agent_id.title()} verification\n# Add specific verification commands for {self.agent_id}"

    def _generate_completion_checklist(self) -> str:
        """Generate completion checklist"""
        deliverables = self._generate_deliverables_section()
        lines = deliverables.split('\n')
        checklist = []
        
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                item = line.split('**')[1] if '**' in line else line.strip()
                checklist.append(f"- [x] {item}")
        
        return '\n'.join(checklist)


def generate_enhanced_instruction(agent_id: str, phase_id: str, base_path: Path) -> str:
    """Generate enhanced instruction for Claude Code"""
    
    # Load configuration
    config_path = base_path / "Requirements_Generation_System" / "config.yaml"
    config = {}
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not load config: {e}[/yellow]")
    
    # Generate instruction
    template = InstructionTemplate(agent_id, phase_id, config)
    return template.generate_instruction()


def main():
    """Test the instruction template generator"""
    base_path = Path("project")
    
    # Generate sample instruction
    instruction = generate_enhanced_instruction("backend", "phase1", base_path)
    
    # Save to file
    output_path = base_path / "generated_documents" / "design" / "claude_instructions"
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "backend-phase1-sample.md", 'w', encoding='utf-8') as f:
        f.write(instruction)
    
    console.print("[green]✅ Sample instruction generated successfully![/green]")


if __name__ == "__main__":
    main()