# Requirements Generation System - Usage Guide

## Overview

This comprehensive requirements generation system combines best practices from multiple approaches to create a complete, traceable set of software project documentation. The system uses Large Language Models (LLMs) to generate standardized documents with full bidirectional traceability.

## System Components

### 1. Core Document Templates Created

#### Phase 1: Business Requirements
- **01_BRD.md** - Business Requirements Document
- **02_PRD.md** - Product Requirements Document

#### Phase 2: Functional Specifications
- **04_FRD.md** - Functional Requirements Document
- **05_NFRD.md** - Non-Functional Requirements Document

#### Phase 3: Data & Technical Design
- **07_DRD.md** - Data Requirements Document
- **08_DB_Schema.md** - Database Schema Document
- **09_TRD.md** - Technical Requirements Document
- **10_API_OpenAPI.md** - OpenAPI Specification

#### Phase 4: Quality & Testing
- **20_Test_Plan.md** - Test Plan and Test Cases

#### Phase 5: Traceability
- **24_RTM.md** - Requirements Traceability Matrix

## How to Use This System

### Step 1: Prepare Your Inputs

For the FY.WB.Midway project, gather the following inputs from the Requirements directory:

1. **Business Context**:
   - Requirements/consolidated-requirements/master-prd.md
   - Requirements/Video Annotations/*.markdown
   - Requirements/cross-system-analysis/end-to-end-workflows.md

2. **Existing Requirements**:
   - Requirements/invoice-requirements/product-management/PRD.md
   - Requirements/logistics-requirements/product-management/PRD.md
   - Requirements/requirements/product-management/FRD.md

3. **Technical Context**:
   - Current architecture from CLAUDE.md
   - Existing database schemas from Requirements/*/database/DB-SCHEMA.sql

### Step 2: Document Generation Sequence

Follow this sequence for optimal results:

#### 1. Generate BRD (Business Requirements Document)
```markdown
Using the prompt in 01_BRD.md, provide:
- Business Context: From master-prd.md executive summary
- Stakeholder Inputs: From video annotations
- Strategic Objectives: From master-prd.md strategic objectives
- Constraints: Budget, timeline, compliance requirements

Output: Comprehensive BRD with traceable business requirements (BRD-001, BRD-002, etc.)
```

#### 2. Generate PRD (Product Requirements Document)
```markdown
Using the prompt in 02_PRD.md, provide:
- Business Requirements Document: Generated BRD
- User Research: From video annotations UI requirements
- Market Analysis: From master-prd.md market overview
- Technical Constraints: From CLAUDE.md

Output: PRD with features and user stories linked to BRD
```

#### 3. Generate FRD (Functional Requirements Document)
```markdown
Using the prompt in 04_FRD.md, provide:
- Product Requirements Document: Generated PRD
- Business Requirements Document: Generated BRD
- UI/UX Designs: From video annotations

Output: Detailed functional specifications linked to PRD user stories
```

#### 4. Generate NFRD (Non-Functional Requirements Document)
```markdown
Using the prompt in 05_NFRD.md, provide:
- PRD, FRD, BRD: Previously generated
- Compliance Requirements: PCI-DSS, GDPR from master-prd.md
- Performance Expectations: From master-prd.md performance requirements

Output: Measurable non-functional requirements
```

#### 5. Generate DRD (Data Requirements Document)
```markdown
Using the prompt in 07_DRD.md, provide:
- Functional Requirements Document: Generated FRD
- Existing Data Systems: From Requirements/*/database/DB-SCHEMA.sql
- Compliance Requirements: From NFRD

Output: Complete data model with entity definitions
```

#### 6. Generate DB Schema
```markdown
Using the prompt in 08_DB_Schema.md, provide:
- Data Requirements Document: Generated DRD
- Technical Requirements: PostgreSQL from CLAUDE.md
- Performance Requirements: From NFRD

Output: Complete database DDL scripts
```

#### 7. Generate TRD (Technical Requirements Document)
```markdown
Using the prompt in 09_TRD.md, provide:
- All previous documents (FRD, NFRD, DRD, PRD)
- Technology Constraints: From CLAUDE.md
- Team Capabilities: .NET, React expertise

Output: Complete technical architecture and design decisions
```

#### 8. Generate API Specification
```markdown
Using the prompt in 10_API_OpenAPI.md, provide:
- Functional Requirements: From FRD
- Data Requirements: From DRD
- Technical Architecture: From TRD
- Authentication Strategy: JWT from CLAUDE.md

Output: Complete OpenAPI 3.0 specification
```

#### 9. Generate Test Plan
```markdown
Using the prompt in 20_Test_Plan.md, provide:
- All requirements documents (FRD, NFRD, PRD)
- Technical Architecture: From TRD
- Risk Assessment: From master-prd.md

Output: Comprehensive test plan with test cases
```

#### 10. Generate RTM
```markdown
Using the prompt in 24_RTM.md, provide:
- All generated documents with their IDs
- Current implementation status
- Test execution results (if available)

Output: Complete requirements traceability matrix
```

### Step 3: Iterative Refinement

Each prompt template includes refinement prompts. After initial generation:

1. Use Refinement Round 1 to check completeness
2. Use Refinement Round 2 to enhance quality
3. Use Refinement Round 3 to optimize for your specific needs

### Step 4: Validation

Each template includes a validation checklist. Ensure all items are checked before proceeding to the next document.

## Traceability System

The system uses a hierarchical ID structure:

```
BRD-001 (Business Requirement)
  └─> PRD-001 (Product Feature)
      └─> FRD-001.1 (Functional Requirement)
          └─> TRD-001.1.1 (Technical Design)
              └─> TC-001.1.1.1 (Test Case)
```

### ID Prefixes:
- **BRD-XXX**: Business Requirements
- **PRD-XXX**: Product Features
- **PRD-US-XXX**: User Stories
- **FRD-XXX**: Functional Requirements
- **NFR-XXX**: Non-Functional Requirements
- **DRD-XXX**: Data Requirements
- **TRD-XXX**: Technical Requirements
- **TC-XXX**: Test Cases
- **DEF-XXX**: Defects

## Best Practices

### 1. Context is Key
Always provide complete upstream documents when generating downstream documents. The LLM performs better with full context.

### 2. Maintain Consistency
Use the same terminology throughout all documents. If you call it "customer" in the BRD, don't switch to "client" in the FRD.

### 3. Validate Traceability
After generating each document, verify that all IDs properly link to their sources.

### 4. Iterative Approach
Don't expect perfection on the first generation. Use the refinement prompts to improve quality.

### 5. Human Review
Always have subject matter experts review generated documents, especially for:
- Business accuracy
- Technical feasibility
- Compliance requirements
- Security considerations

## Common Issues and Solutions

### Issue: Inconsistent IDs
**Solution**: Create a master ID registry as you generate documents

### Issue: Missing Requirements
**Solution**: Use the RTM to identify gaps and regenerate affected documents

### Issue: Scope Creep
**Solution**: Always trace new requirements back to approved business requirements

### Issue: Technical Conflicts
**Solution**: Use the TRD as the single source of truth for technical decisions

## Integration with Development Workflow

### 1. Version Control
Store all generated documents in version control (Git) with clear commit messages.

### 2. Change Management
When requirements change:
1. Update the source document
2. Regenerate affected downstream documents
3. Update the RTM
4. Communicate changes to all stakeholders

### 3. Continuous Validation
Regularly generate the RTM to ensure:
- All requirements have test coverage
- No orphan requirements exist
- Implementation aligns with requirements

## Metrics and Reporting

Track these metrics:
- Requirements coverage (% with test cases)
- Requirements stability (change rate)
- Traceability completeness (% with full linkage)
- Document generation time
- Refinement iterations needed

## Next Steps for FY.WB.Midway

1. **Immediate Actions**:
   - Generate BRD using existing requirements
   - Create PRD from video annotations and master PRD
   - Build FRD from existing functional specs

2. **Validation Phase**:
   - Review with stakeholders
   - Validate technical feasibility
   - Confirm compliance coverage

3. **Implementation Support**:
   - Use generated specs for development
   - Maintain RTM throughout project
   - Update documents as requirements evolve

## Support and Troubleshooting

### LLM Prompt Tips
- Be specific about document versions
- Include all required context
- Use examples when available
- Iterate with refinement prompts

### Quality Assurance
- Cross-reference with existing documentation
- Validate with domain experts
- Test traceability links
- Verify compliance requirements

This system provides a comprehensive, traceable approach to requirements documentation that scales with project complexity while maintaining quality and consistency.