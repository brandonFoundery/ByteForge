"""
Review Pass Implementation - Gemini 2.5

This module implements Pass 2 of the AI-driven application builder.
Uses Gemini 2.5 to review and validate the design from Pass 1.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional

import google.generativeai as genai
from rich.console import Console

console = Console()


class ReviewPass:
    """
    Pass 2: Review Phase using Gemini 2.5
    
    Reviews and validates the design from Pass 1 including:
    - Design completeness and consistency
    - Alignment with requirements
    - Potential issues and improvements
    - Scalability and maintainability assessment
    - Risk analysis and mitigation strategies
    """

    def __init__(self, config: Dict[str, Any], base_path: Path):
        self.config = config
        self.base_path = base_path
        self.requirements_path = base_path / "Requirements"
        
        # Get review pass configuration
        self.pass_config = config.get('application_builder', {}).get('passes', {}).get('review', {})
        
        # Initialize Gemini client
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Initialize the model
        model_name = self.pass_config.get('model_name', 'gemini-2.5-pro-preview-06-05')
        self.model = genai.GenerativeModel(model_name)

    async def run(self, design_document: str) -> str:
        """
        Run the review pass
        
        Args:
            design_document: Design document from Pass 1 (OpenAI o3)
            
        Returns:
            Review report and validated design as markdown string
        """
        console.print("[cyan]🔍 Running Review Pass with Gemini 2.5...[/cyan]")
        
        # Parse the design document
        design_analysis = await self._analyze_design_document(design_document)
        
        # Gather additional context for validation
        validation_context = await self._gather_validation_context()
        
        # Create review prompt
        review_prompt = self._create_review_prompt(design_document, design_analysis, validation_context)
        
        # Call Gemini 2.5
        review_report = await self._call_gemini_25(review_prompt)
        
        # Structure the review output
        structured_review = await self._structure_review_output(review_report, design_document)
        
        console.print("[green]✅ Review Pass completed successfully[/green]")
        return structured_review

    async def _analyze_design_document(self, design_document: str) -> Dict[str, Any]:
        """Analyze the design document structure and content"""
        analysis = {
            'sections_found': [],
            'missing_sections': [],
            'word_count': len(design_document.split()),
            'has_architecture_diagram': 'architecture' in design_document.lower() or 'diagram' in design_document.lower(),
            'has_api_specs': 'api' in design_document.lower() or 'endpoint' in design_document.lower(),
            'has_data_model': 'database' in design_document.lower() or 'entity' in design_document.lower(),
            'has_security_considerations': 'security' in design_document.lower() or 'authentication' in design_document.lower()
        }
        
        # Check for expected sections
        expected_sections = [
            'system architecture',
            'frontend design',
            'backend design',
            'data model',
            'api interface',
            'technology stack',
            'implementation strategy'
        ]
        
        for section in expected_sections:
            if section.lower() in design_document.lower():
                analysis['sections_found'].append(section)
            else:
                analysis['missing_sections'].append(section)
        
        return analysis

    async def _gather_validation_context(self) -> str:
        """Gather additional context for design validation"""
        context_parts = []
        
        # Read architectural guidelines and best practices
        guidelines_files = [
            "consolidated-requirements/master-technical-architecture.md",
            "cross-system-analysis/unified-api-strategy.md",
            "consolidated-requirements/master-security-requirements.md"
        ]
        
        for file_path in guidelines_files:
            full_path = self.requirements_path / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    context_parts.append(f"## {file_path}\n\n{content[:1500]}...")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
        
        # Add technology stack constraints
        tech_constraints = self._get_technology_constraints()
        context_parts.append(f"## Technology Stack Constraints\n\n{tech_constraints}")
        
        return "\n\n".join(context_parts)

    def _get_technology_constraints(self) -> str:
        """Get technology stack constraints and preferences"""
        return """
### Required Technologies
- Frontend: Next.js 14+ with TypeScript
- Backend: .NET 8.0 Web API with Clean Architecture
- Database: SQL Server with Entity Framework Core
- Authentication: JWT with multi-tenant support
- State Management: React Context + SWR for data fetching
- Styling: Tailwind CSS
- API Pattern: CQRS with MediatR

### Architectural Constraints
- Must follow Clean Architecture principles
- Multi-tenant architecture required (Finbuckle.MultiTenant)
- All APIs must be RESTful and follow OpenAPI standards
- Database must support multi-tenancy with tenant isolation
- Frontend must be responsive and accessible (WCAG 2.1 AA)
- All components must be testable and follow SOLID principles

### Performance Requirements
- API response times < 200ms for standard operations
- Frontend initial load < 3 seconds
- Database queries must be optimized with proper indexing
- Support for horizontal scaling

### Security Requirements
- All data must be encrypted in transit and at rest
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
"""

    def _create_review_prompt(self, design_document: str, design_analysis: Dict[str, Any], validation_context: str) -> str:
        """Create the review prompt for Gemini 2.5"""
        return f"""You are a senior software architect and technical reviewer with expertise in enterprise application design, security, and scalability. Your task is to thoroughly review the system design document provided and provide comprehensive feedback.

## Design Document to Review
{design_document}

## Design Analysis Summary
- Sections found: {', '.join(design_analysis['sections_found'])}
- Missing sections: {', '.join(design_analysis['missing_sections']) if design_analysis['missing_sections'] else 'None'}
- Word count: {design_analysis['word_count']}
- Has architecture diagram: {design_analysis['has_architecture_diagram']}
- Has API specifications: {design_analysis['has_api_specs']}
- Has data model: {design_analysis['has_data_model']}
- Has security considerations: {design_analysis['has_security_considerations']}

## Validation Context and Constraints
{validation_context}

## Your Review Task

Please provide a comprehensive review that includes:

### 1. Design Completeness Assessment
- Evaluate if all necessary components are covered
- Identify any missing critical elements
- Assess the level of detail provided

### 2. Technical Architecture Review
- Validate the proposed architecture against Clean Architecture principles
- Review component separation and dependencies
- Assess scalability and maintainability
- Evaluate technology stack choices

### 3. Security Analysis
- Review security considerations and implementations
- Identify potential security vulnerabilities
- Validate authentication and authorization approaches
- Assess data protection measures

### 4. Performance Considerations
- Evaluate performance implications of the design
- Identify potential bottlenecks
- Review caching strategies
- Assess database design efficiency

### 5. Integration Assessment
- Review how the new feature integrates with existing systems
- Validate API design and contracts
- Assess data flow and communication patterns
- Identify potential integration challenges

### 6. Risk Analysis
- Identify technical risks and challenges
- Assess implementation complexity
- Evaluate potential failure points
- Suggest risk mitigation strategies

### 7. Improvement Recommendations
- Suggest specific improvements to the design
- Recommend alternative approaches where applicable
- Provide optimization suggestions
- Highlight best practices to follow

### 8. Implementation Readiness
- Assess if the design is ready for implementation
- Identify areas that need more detail
- Suggest implementation phases or priorities
- Evaluate testing strategies

## Review Format

Please structure your review as follows:

1. **Executive Summary** - Overall assessment and key findings
2. **Detailed Review** - Section-by-section analysis
3. **Critical Issues** - Must-fix issues before implementation
4. **Recommendations** - Specific improvement suggestions
5. **Risk Assessment** - Identified risks and mitigation strategies
6. **Approval Status** - Ready for implementation / Needs revision / Major concerns

## Review Criteria

Rate each aspect on a scale of 1-5 (1=Poor, 5=Excellent):
- Completeness
- Technical soundness
- Security considerations
- Performance design
- Maintainability
- Integration approach

Provide specific, actionable feedback that will help improve the design and ensure successful implementation. Focus on practical concerns and real-world implementation challenges.

Be thorough but constructive in your review. The goal is to validate and improve the design, not to criticize unnecessarily."""

    async def _call_gemini_25(self, prompt: str) -> str:
        """Call Gemini 2.5 API"""
        try:
            temperature = self.pass_config.get('temperature', 0.1)
            max_tokens = self.pass_config.get('max_tokens', 3000)
            
            console.print(f"[dim]Calling Gemini 2.5 with {len(prompt)} characters...[/dim]")
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                candidate_count=1
            )
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config
            )
            
            if response.candidates and response.candidates[0].content:
                return response.candidates[0].content.parts[0].text
            else:
                raise RuntimeError("No valid response from Gemini API")
            
        except Exception as e:
            console.print(f"[red]Error calling Gemini API: {e}[/red]")
            raise

    async def _structure_review_output(self, review_report: str, original_design: str) -> str:
        """Structure and format the review output"""
        # Add metadata header
        structured_output = f"""---
title: "Design Review Report"
feature: "AI-Generated Feature"
pass: "2-Review"
model: "Gemini 2.5"
generated_at: "{asyncio.get_event_loop().time()}"
review_status: "completed"
---

# Design Review Report

## Review Summary
This document contains the comprehensive review of the system design document generated in Pass 1. The review was conducted by Gemini 2.5 to validate design completeness, technical soundness, and implementation readiness.

## Original Design Document
The following design was reviewed:
- **Generated by**: OpenAI o3 (Pass 1)
- **Word count**: {len(original_design.split())} words
- **Review date**: {asyncio.get_event_loop().time()}

---

{review_report}

---

## Next Steps
Based on this review, the design will proceed to Pass 3 (Implementation Specification) where Claude Sonnet 4 will create detailed implementation plans incorporating the feedback and recommendations from this review.

## Appendix: Original Design Document
<details>
<summary>Click to view the original design document that was reviewed</summary>

{original_design}

</details>

---

*This review was generated by the AI-Driven Application Builder - Review Pass (Gemini 2.5)*
"""
        
        return structured_output
