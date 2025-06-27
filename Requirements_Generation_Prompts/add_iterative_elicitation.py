#!/usr/bin/env python3
"""
Script to add iterative requirements elicitation sections to all prompt templates
"""

import os
import re
from pathlib import Path

# Document type configurations
DOC_CONFIGS = {
    "07_DRD.md": {
        "doc_type": "DRD",
        "doc_full_name": "Data Requirements Document",
        "section_number": "8",
        "focus_areas": "data structures, relationships, quality, governance, integration, and lifecycle management",
        "categories": "Data Structure|Data Quality|Data Governance|Data Integration|Data Security|Data Lifecycle|Data Migration|Other",
        "related_refs": "DRD-XXX, FRD-XXX, or PRD-FEAT-XXX",
        "specific_areas": "data models, data flows, data quality rules, and governance policies"
    },
    "08_DB_Schema.md": {
        "doc_type": "DB",
        "doc_full_name": "Database Schema Document",
        "section_number": "7",
        "focus_areas": "database design, table structures, relationships, indexes, constraints, and data integrity",
        "categories": "Table Design|Relationships|Indexes|Constraints|Data Types|Performance|Security|Migration|Other",
        "related_refs": "DB-XXX, DRD-XXX, or FRD-XXX",
        "specific_areas": "database schema, table relationships, indexing strategies, and data integrity rules"
    },
    "09_TRD.md": {
        "doc_type": "TRD",
        "doc_full_name": "Technical Requirements Document",
        "section_number": "9",
        "focus_areas": "technical architecture, technology stack, infrastructure, development practices, and deployment strategies",
        "categories": "Architecture|Technology Stack|Infrastructure|Integration|Development|Deployment|DevOps|Other",
        "related_refs": "TRD-XXX, NFRD-XXX, or FRD-XXX",
        "specific_areas": "technical architecture, technology choices, infrastructure needs, and development practices"
    },
    "10_API_OpenAPI.md": {
        "doc_type": "API",
        "doc_full_name": "API OpenAPI Specification Document",
        "section_number": "10",
        "focus_areas": "API endpoints, data models, authentication, error handling, performance, and integration patterns",
        "categories": "Endpoints|Data Models|Authentication|Error Handling|Performance|Versioning|Security|Integration|Other",
        "related_refs": "API-XXX, TRD-XXX, or FRD-XXX",
        "specific_areas": "API design, data schemas, integration patterns, and service contracts"
    },
    "11_UIUX_Spec.md": {
        "doc_type": "UX",
        "doc_full_name": "UI/UX Specification Document",
        "section_number": "11",
        "focus_areas": "user interface design, user experience, accessibility, responsive design, and interaction patterns",
        "categories": "Interface Design|User Experience|Accessibility|Responsive Design|Interaction|Navigation|Visual Design|Other",
        "related_refs": "UX-XXX, PRD-FEAT-XXX, or FRD-XXX",
        "specific_areas": "interface specifications, user workflows, accessibility requirements, and design systems"
    },
    "20_Test_Plan.md": {
        "doc_type": "TEST",
        "doc_full_name": "Test Plan Document",
        "section_number": "9",
        "focus_areas": "test strategies, test cases, test environments, test data, automation, and quality assurance",
        "categories": "Test Strategy|Test Cases|Test Environment|Test Data|Automation|Performance Testing|Security Testing|Other",
        "related_refs": "TEST-XXX, FRD-XXX, or NFRD-XXX",
        "specific_areas": "testing approaches, test coverage, test environments, and quality metrics"
    },
    "24_RTM.md": {
        "doc_type": "RTM",
        "doc_full_name": "Requirements Traceability Matrix",
        "section_number": "6",
        "focus_areas": "requirement relationships, coverage analysis, impact assessment, change management, and verification",
        "categories": "Traceability Links|Coverage Analysis|Impact Assessment|Change Management|Verification|Gap Analysis|Other",
        "related_refs": "RTM-XXX, BRD-REQ-XXX, or PRD-FEAT-XXX",
        "specific_areas": "requirement relationships, traceability coverage, change impact, and verification status"
    }
}

def create_iterative_section(config):
    """Create the iterative requirements elicitation section for a document type"""
    
    template = f"""
## Iterative Requirements Elicitation

After generating the initial {config['doc_full_name']}, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the {config['doc_type']} requirements.

### {config['section_number']}. Client Clarification Questions

Think critically about {config['focus_areas']} that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: {config['doc_type']}-QUESTION-001
category: [{config['categories']}]
question: [Specific question for the client]
rationale: [Why this question is important for {config['doc_type']} success]
related_requirements: [{config['related_refs']} references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect the {config['doc_type']} requirements]
```

#### Question Categories:

**{config['doc_type']}-Specific Questions:**
- Clarifications on {config['specific_areas']}
- Edge cases and exception scenarios
- Integration and dependency requirements
- Performance and quality expectations
- Compliance and governance needs

### Instructions for Question Generation:

1. **Be Specific**: Ask precise questions that will yield actionable answers
2. **Prioritize Impact**: Focus on questions that will significantly affect {config['doc_type']} requirements
3. **Consider Edge Cases**: Think about unusual scenarios and exceptions
4. **Validate Assumptions**: Question any assumptions made in the initial requirements
5. **Ensure Completeness**: Look for gaps in {config['specific_areas']}
6. **Think Downstream**: Consider how answers will affect implementation
7. **Maintain Traceability**: Link questions to specific requirements when applicable

### Answer Integration Process:

When client answers are received, they should be integrated back into the {config['doc_full_name']} using this process:

1. **Create Answer Records**:
```yaml
id: {config['doc_type']}-ANSWER-001
question_id: {config['doc_type']}-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing requirements]
```

2. **Update Affected Requirements**: Modify existing requirements based on answers
3. **Create New Requirements**: Add new requirements identified through answers
4. **Update Traceability**: Ensure all changes maintain proper traceability links
5. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive {config['doc_type']} requirements that address all critical aspects and reduce implementation risks.
"""
    
    return template

def add_iterative_section_to_file(file_path, config):
    """Add the iterative section to a specific prompt file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if iterative section already exists
        if "## Iterative Requirements Elicitation" in content:
            print(f"✓ {file_path.name} already has iterative section")
            return True
        
        # Find the insertion point (before the closing ```)
        # Look for the last ``` that closes the main prompt
        pattern = r'```\s*$'
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        if not matches:
            print(f"✗ Could not find insertion point in {file_path.name}")
            return False
        
        # Insert before the last ```
        insertion_point = matches[-1].start()
        
        # Create the iterative section
        iterative_section = create_iterative_section(config)
        
        # Insert the section
        new_content = (
            content[:insertion_point] + 
            iterative_section + 
            "\n" + 
            content[insertion_point:]
        )
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Added iterative section to {file_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {file_path.name}: {e}")
        return False

def main():
    """Main function to process all prompt files"""
    
    print("🔄 Adding Iterative Requirements Elicitation to Prompt Templates")
    print("=" * 70)
    
    current_dir = Path(__file__).parent
    success_count = 0
    total_count = 0
    
    for filename, config in DOC_CONFIGS.items():
        file_path = current_dir / filename
        total_count += 1
        
        if not file_path.exists():
            print(f"⚠️  {filename} not found, skipping")
            continue
        
        if add_iterative_section_to_file(file_path, config):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Summary: {success_count}/{total_count} files processed successfully")
    
    if success_count == total_count:
        print("🎉 All prompt templates updated with iterative requirements elicitation!")
    else:
        print("⚠️  Some files may need manual review")

if __name__ == "__main__":
    main()
