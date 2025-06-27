#!/usr/bin/env python3
"""
Script to generate reviewer prompt templates for all document types
"""

import os
from pathlib import Path

# Document type configurations for reviewer prompts
REVIEWER_CONFIGS = {
    "Review_02_PRD.md": {
        "doc_type": "PRD",
        "doc_full_name": "Product Requirements Document",
        "expert_role": "Senior Product Manager and Requirements Reviewer",
        "expertise": "validating and improving product requirements documentation, ensuring user value delivery and technical feasibility",
        "review_categories": "User Experience|Feature Validation|Technical Feasibility|Business Value|Market Fit|Usability|Other",
        "question_prefix": "PRD-REVIEW-QUESTION",
        "focus_areas": [
            "User story completeness and clarity",
            "Feature scope and boundary definitions", 
            "Acceptance criteria specificity",
            "User experience consistency",
            "Technical feasibility assessment",
            "Business value validation"
        ],
        "validation_aspects": [
            "User journey completeness",
            "Feature interaction scenarios", 
            "MVP vs future release clarity",
            "User acceptance criteria testability",
            "Market requirements alignment",
            "Competitive analysis completeness"
        ]
    },
    "Review_04_FRD.md": {
        "doc_type": "FRD", 
        "doc_full_name": "Functional Requirements Document",
        "expert_role": "Senior Systems Analyst and Functional Requirements Reviewer",
        "expertise": "validating and improving functional specifications, ensuring system behavior clarity and implementation feasibility",
        "review_categories": "Functional Logic|System Behavior|Data Flow|Integration|Error Handling|Performance|Other",
        "question_prefix": "FRD-REVIEW-QUESTION",
        "focus_areas": [
            "System behavior specifications",
            "Business logic completeness",
            "Data flow accuracy",
            "Integration point definitions",
            "Error handling scenarios",
            "Functional workflow clarity"
        ],
        "validation_aspects": [
            "Business rule completeness",
            "System response specifications",
            "Data validation logic",
            "Integration error handling",
            "Workflow exception scenarios",
            "Performance impact assessment"
        ]
    },
    "Review_05_NFRD.md": {
        "doc_type": "NFRD",
        "doc_full_name": "Non-Functional Requirements Document", 
        "expert_role": "Senior Architect and Quality Assurance Reviewer",
        "expertise": "validating and improving non-functional requirements, ensuring system quality attributes and operational excellence",
        "review_categories": "Performance Validation|Security Assessment|Scalability Review|Reliability Check|Compliance Verification|Operational Readiness|Other",
        "question_prefix": "NFRD-REVIEW-QUESTION",
        "focus_areas": [
            "Performance criteria measurability",
            "Security requirement completeness",
            "Scalability target realism", 
            "Reliability specification clarity",
            "Compliance requirement accuracy",
            "Operational monitoring capabilities"
        ],
        "validation_aspects": [
            "Performance target achievability",
            "Security control effectiveness",
            "Scalability architecture alignment",
            "Disaster recovery feasibility",
            "Compliance audit readiness",
            "Monitoring and alerting completeness"
        ]
    },
    "Review_07_DRD.md": {
        "doc_type": "DRD",
        "doc_full_name": "Data Requirements Document",
        "expert_role": "Senior Data Architect and Data Requirements Reviewer",
        "expertise": "validating and improving data requirements, ensuring data integrity, governance, and lifecycle management",
        "review_categories": "Data Model Validation|Data Quality Assessment|Governance Review|Integration Verification|Security Check|Lifecycle Management|Other",
        "question_prefix": "DRD-REVIEW-QUESTION",
        "focus_areas": [
            "Data model accuracy and completeness",
            "Data quality rule effectiveness",
            "Data governance policy alignment",
            "Data integration feasibility",
            "Data security requirement adequacy",
            "Data lifecycle management clarity"
        ],
        "validation_aspects": [
            "Entity relationship accuracy",
            "Data validation rule completeness",
            "Master data management strategy",
            "Data migration requirements",
            "Privacy and retention compliance",
            "Data lineage traceability"
        ]
    },
    "Review_08_DB_Schema.md": {
        "doc_type": "DB",
        "doc_full_name": "Database Schema Document",
        "expert_role": "Senior Database Architect and Schema Reviewer",
        "expertise": "validating and improving database schemas, ensuring data integrity, performance, and scalability",
        "review_categories": "Schema Validation|Performance Review|Integrity Check|Scalability Assessment|Security Review|Migration Planning|Other",
        "question_prefix": "DB-REVIEW-QUESTION",
        "focus_areas": [
            "Table structure optimization",
            "Relationship integrity validation",
            "Index strategy effectiveness",
            "Constraint completeness",
            "Performance optimization opportunities",
            "Security implementation adequacy"
        ],
        "validation_aspects": [
            "Normalization level appropriateness",
            "Foreign key relationship accuracy",
            "Index performance impact",
            "Data type optimization",
            "Constraint enforcement effectiveness",
            "Migration strategy feasibility"
        ]
    },
    "Review_09_TRD.md": {
        "doc_type": "TRD",
        "doc_full_name": "Technical Requirements Document",
        "expert_role": "Senior Technical Architect and Requirements Reviewer",
        "expertise": "validating and improving technical requirements, ensuring architectural soundness and implementation feasibility",
        "review_categories": "Architecture Review|Technology Validation|Infrastructure Assessment|Integration Verification|Performance Check|Security Review|Other",
        "question_prefix": "TRD-REVIEW-QUESTION",
        "focus_areas": [
            "Technical architecture soundness",
            "Technology stack appropriateness",
            "Infrastructure requirement adequacy",
            "Integration strategy feasibility",
            "Development practice alignment",
            "Deployment strategy effectiveness"
        ],
        "validation_aspects": [
            "Architectural pattern consistency",
            "Technology choice justification",
            "Scalability architecture alignment",
            "Security architecture completeness",
            "DevOps pipeline integration",
            "Monitoring and observability coverage"
        ]
    },
    "Review_10_API_OpenAPI.md": {
        "doc_type": "API",
        "doc_full_name": "API OpenAPI Specification Document",
        "expert_role": "Senior API Architect and Specification Reviewer",
        "expertise": "validating and improving API specifications, ensuring design consistency, security, and developer experience",
        "review_categories": "API Design Review|Security Validation|Performance Assessment|Documentation Check|Versioning Strategy|Integration Testing|Other",
        "question_prefix": "API-REVIEW-QUESTION",
        "focus_areas": [
            "API design consistency and standards",
            "Security implementation completeness",
            "Performance optimization opportunities",
            "Documentation clarity and completeness",
            "Error handling strategy effectiveness",
            "Versioning and backward compatibility"
        ],
        "validation_aspects": [
            "RESTful design principle adherence",
            "Authentication and authorization completeness",
            "Rate limiting and throttling strategies",
            "Error response standardization",
            "API contract testing coverage",
            "Developer experience optimization"
        ]
    },
    "Review_11_UIUX_Spec.md": {
        "doc_type": "UX",
        "doc_full_name": "UI/UX Specification Document",
        "expert_role": "Senior UX Architect and Design Reviewer",
        "expertise": "validating and improving UI/UX specifications, ensuring user experience excellence and accessibility compliance",
        "review_categories": "User Experience Review|Accessibility Validation|Design Consistency|Interaction Assessment|Performance Check|Responsive Design|Other",
        "question_prefix": "UX-REVIEW-QUESTION",
        "focus_areas": [
            "User journey completeness and optimization",
            "Accessibility compliance verification",
            "Design system consistency",
            "Interaction pattern effectiveness",
            "Responsive design implementation",
            "Performance impact assessment"
        ],
        "validation_aspects": [
            "User workflow efficiency",
            "WCAG compliance verification",
            "Cross-platform consistency",
            "Interaction feedback adequacy",
            "Mobile-first design principles",
            "Loading and performance optimization"
        ]
    },
    "Review_20_Test_Plan.md": {
        "doc_type": "TEST",
        "doc_full_name": "Test Plan Document",
        "expert_role": "Senior QA Architect and Test Strategy Reviewer",
        "expertise": "validating and improving test plans, ensuring comprehensive coverage and quality assurance effectiveness",
        "review_categories": "Test Coverage Review|Strategy Validation|Environment Assessment|Automation Check|Performance Testing|Security Testing|Other",
        "question_prefix": "TEST-REVIEW-QUESTION",
        "focus_areas": [
            "Test coverage completeness",
            "Test strategy effectiveness",
            "Test environment adequacy",
            "Automation strategy optimization",
            "Performance testing coverage",
            "Security testing integration"
        ],
        "validation_aspects": [
            "Requirement traceability coverage",
            "Test case design effectiveness",
            "Test data management strategy",
            "Defect management process",
            "Regression testing strategy",
            "Quality metrics definition"
        ]
    },
    "Review_24_RTM.md": {
        "doc_type": "RTM",
        "doc_full_name": "Requirements Traceability Matrix",
        "expert_role": "Senior Requirements Manager and Traceability Reviewer",
        "expertise": "validating and improving requirements traceability, ensuring comprehensive coverage and change impact analysis",
        "review_categories": "Traceability Validation|Coverage Assessment|Gap Analysis|Impact Review|Change Management|Verification Status|Other",
        "question_prefix": "RTM-REVIEW-QUESTION",
        "focus_areas": [
            "Traceability link completeness",
            "Coverage gap identification",
            "Impact analysis accuracy",
            "Change management effectiveness",
            "Verification status tracking",
            "Requirement relationship validation"
        ],
        "validation_aspects": [
            "Bidirectional traceability verification",
            "Orphaned requirement identification",
            "Test coverage mapping accuracy",
            "Change impact assessment completeness",
            "Requirement status consistency",
            "Stakeholder approval tracking"
        ]
    }
}

def create_reviewer_prompt_template(config):
    """Create a reviewer prompt template for a specific document type"""
    
    focus_areas_list = "\n".join([f"- {area}" for area in config["focus_areas"]])
    validation_aspects_list = "\n".join([f"- {aspect}" for aspect in config["validation_aspects"]])
    
    template = f"""# {config['doc_full_name']} ({config['doc_type']}) - Reviewer Prompt Template

## Reviewer Prompt

```markdown
You are an expert {config['expert_role']} with extensive experience in {config['expertise']}. You excel at identifying gaps, inconsistencies, and areas for improvement while ensuring alignment with business objectives and implementation feasibility.

## Your Task

Review the provided {config['doc_full_name']} ({config['doc_type']}) for [PROJECT NAME] and provide an enhanced version along with additional clarification questions that will help validate and improve the requirements.

## Review Context

You will be provided with:
1. **Original {config['doc_type']}**: The document generated by the primary LLM
2. **Source Context**: The original context used for generation
3. **Primary Questions**: Questions already generated by the primary LLM

## Review Instructions

### 1. Document Quality Assessment

Evaluate the {config['doc_type']} for:

**Completeness:**
{focus_areas_list}

**Consistency:**
- Do requirements align with stated objectives?
- Are there conflicting requirements or priorities?
- Is terminology used consistently throughout?
- Do traceability IDs follow proper hierarchy?

**Clarity:**
- Are requirements written in clear, unambiguous language?
- Are specifications detailed enough for implementation?
- Are assumptions explicitly documented?
- Are constraints and limitations clearly identified?

**Feasibility:**
- Are requirements realistic and achievable?
- Are technical constraints properly considered?
- Are resource and timeline expectations reasonable?
- Are risk factors adequately addressed?

### 2. Enhancement Guidelines

Improve the document by:

**Adding Missing Details:**
- Enhance vague or incomplete requirements
- Add specific technical details and constraints
- Include missing implementation considerations
- Clarify complex specifications

**Improving Structure:**
- Ensure logical flow and organization
- Strengthen traceability relationships
- Improve section coherence
- Enhance readability and navigation

**Strengthening Content:**
- Make requirements more specific and measurable
- Add relevant technical context
- Include implementation considerations
- Strengthen acceptance criteria definitions

### 3. Preservation Requirements

**CRITICAL - You MUST preserve:**
- All traceability IDs exactly as they appear ({config['doc_type']}-XXX-001, etc.)
- Document structure and section organization
- All references to upstream/downstream documents
- Original requirement intent and scope
- Professional technical writing tone

**DO NOT:**
- Change or renumber existing traceability IDs
- Remove or significantly shorten content sections
- Alter the fundamental document structure
- Change the technical scope or objectives

## Reviewer Question Generation

After reviewing the document, generate additional clarification questions that focus on **validation, verification, and improvement** of the {config['doc_type']} requirements.

### Reviewer Question Categories

**Validation Questions:**
{validation_aspects_list}

**Consistency Questions:**
- Identify potential requirement conflicts
- Check alignment between objectives and specifications
- Verify priority consistency across requirements
- Validate technical coherence

**Implementation Questions:**
- Assess feasibility of technical requirements
- Identify potential implementation risks
- Check resource and timeline realism
- Validate technical architecture alignment

**Quality Questions:**
- Verify requirement measurability and testability
- Check completeness of acceptance criteria
- Validate technical specifications
- Assess quality assurance strategies

### Reviewer Question Format

```yaml
id: {config['question_prefix']}-001
source: reviewer_llm
category: [{config['review_categories']}]
question: [Specific validation or improvement question]
rationale: [Why this question is important for {config['doc_type']} quality]
related_requirements: [{config['doc_type']}-XXX references if applicable]
priority: High|Medium|Low
review_focus: [What aspect of the requirement needs validation]
expected_impact: [How the answer will improve requirement quality]
```

### Instructions for Reviewer Question Generation:

1. **Focus on Validation**: Ask questions that verify the accuracy and completeness of requirements
2. **Check Feasibility**: Question whether requirements are realistic and achievable
3. **Identify Risks**: Ask about potential technical risks and mitigation strategies
4. **Verify Alignment**: Ensure requirements support stated objectives
5. **Test Measurability**: Confirm that acceptance criteria are specific and measurable
6. **Validate Architecture**: Verify technical architecture and design decisions
7. **Check Standards**: Ensure compliance with relevant standards and best practices
8. **Assess Dependencies**: Identify and validate technical dependencies and constraints

## Output Format

Provide your review in this format:

### Enhanced {config['doc_type']} Document
[Provide the improved version of the {config['doc_type']} with all enhancements while preserving structure and IDs]

### Review Summary
- **Strengths Identified**: [Key strengths of the original document]
- **Areas Enhanced**: [Summary of improvements made]
- **Critical Gaps Addressed**: [Important missing elements that were added]
- **Consistency Issues Resolved**: [Any conflicts or inconsistencies fixed]

### Reviewer Clarification Questions

Generate 8-15 additional questions organized by category that focus on validation and improvement:

#### Validation Questions
[Questions to verify requirement accuracy and completeness]

#### Consistency Questions  
[Questions to check for conflicts and alignment issues]

#### Implementation Questions
[Questions about feasibility and implementation considerations]

#### Quality Questions
[Questions to improve requirement quality and measurability]

### Integration Notes
- **Primary Questions Complement**: [How your questions complement the primary LLM questions]
- **Validation Focus**: [Specific areas where validation is most critical]
- **Implementation Readiness**: [Assessment of how ready requirements are for implementation]

This dual-question approach ensures comprehensive requirements validation from both generation and review perspectives.
```"""
    
    return template

def main():
    """Generate all reviewer prompt templates"""
    
    print("🔄 Generating Reviewer Prompt Templates")
    print("=" * 50)
    
    current_dir = Path(__file__).parent
    success_count = 0
    total_count = len(REVIEWER_CONFIGS)
    
    for filename, config in REVIEWER_CONFIGS.items():
        file_path = current_dir / filename
        
        try:
            template_content = create_reviewer_prompt_template(config)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print(f"✓ Created {filename}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Error creating {filename}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Summary: {success_count}/{total_count} reviewer prompts created successfully")
    
    if success_count == total_count:
        print("🎉 All reviewer prompt templates generated!")
    else:
        print("⚠️  Some files may need manual review")

if __name__ == "__main__":
    main()
