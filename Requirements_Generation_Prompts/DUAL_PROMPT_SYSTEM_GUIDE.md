# Dual-Prompt System Guide

## Overview

The Requirements Generation System now implements a **Dual-Prompt Architecture** with two separate LLMs working in tandem to ensure comprehensive requirements elicitation and validation.

## Architecture

### 🎯 **Primary LLM** (Generation + Initial Questions)
- **Default**: OpenAI o3-mini
- **Role**: Document generation and initial requirements gathering
- **Prompts**: Located in `/Requirements_Generation_Prompts/`
- **Focus**: Creating comprehensive initial documents with generation-focused questions

### 🔍 **Reviewer LLM** (Review + Validation Questions)  
- **Default**: Google Gemini 2.5 Pro
- **Role**: Document review and validation-focused questioning
- **Prompts**: Located in `/Requirements_Generation_Prompts/Review_Prompts/`
- **Focus**: Quality assurance, validation, and improvement-focused questions

## Workflow Process

### 1. **Primary Generation Phase**
```
Primary LLM → Uses Generation Prompts → Produces:
├── Initial Document (BRD, PRD, FRD, etc.)
└── Primary Questions (Generation-focused)
```

### 2. **Review & Validation Phase**
```
Reviewer LLM → Uses Review Prompts → Produces:
├── Enhanced Document (Improved version)
└── Reviewer Questions (Validation-focused)
```

### 3. **Question Integration Phase**
```
Combined Output:
├── Final Enhanced Document
├── Primary Questions (from generation)
├── Reviewer Questions (from validation)
└── Integrated Client Question Set
```

## Question Types & Focus

### Primary LLM Questions (Generation Focus)
- **Business Process**: Understanding workflows and procedures
- **Functional Scope**: Identifying missing features and capabilities
- **Data Requirements**: Understanding data sources and structures
- **Integration Needs**: Identifying system interfaces and dependencies
- **Stakeholder Roles**: Clarifying responsibilities and authority
- **Initial Compliance**: Basic regulatory and standard requirements

### Reviewer LLM Questions (Validation Focus)
- **Requirement Validation**: Verifying accuracy and completeness
- **Consistency Checks**: Identifying conflicts and alignment issues
- **Implementation Feasibility**: Assessing technical and business viability
- **Quality Assurance**: Ensuring measurability and testability
- **Risk Assessment**: Identifying potential risks and mitigation needs
- **Standards Compliance**: Verifying adherence to best practices

## Document-Specific Dual Prompts

### Business Requirements Document (BRD)
- **Primary**: `01_BRD.md` - Business analysis and requirements gathering
- **Reviewer**: `Review_01_BRD.md` - Business validation and feasibility review

### Product Requirements Document (PRD)
- **Primary**: `02_PRD.md` - Product feature definition and user stories
- **Reviewer**: `Review_02_PRD.md` - Product validation and market fit review

### Functional Requirements Document (FRD)
- **Primary**: `04_FRD.md` - Functional specification and system behavior
- **Reviewer**: `Review_04_FRD.md` - Functional validation and implementation review

### Non-Functional Requirements Document (NFRD)
- **Primary**: `05_NFRD.md` - Quality attributes and performance criteria
- **Reviewer**: `Review_05_NFRD.md` - Quality validation and operational review

### Data Requirements Document (DRD)
- **Primary**: `07_DRD.md` - Data modeling and governance requirements
- **Reviewer**: `Review_07_DRD.md` - Data validation and integrity review

### Database Schema Document
- **Primary**: `08_DB_Schema.md` - Database design and structure
- **Reviewer**: `Review_08_DB_Schema.md` - Schema validation and optimization review

### Technical Requirements Document (TRD)
- **Primary**: `09_TRD.md` - Technical architecture and infrastructure
- **Reviewer**: `Review_09_TRD.md` - Technical validation and feasibility review

### API Specification Document
- **Primary**: `10_API_OpenAPI.md` - API design and specification
- **Reviewer**: `Review_10_API_OpenAPI.md` - API validation and standards review

### UI/UX Specification Document
- **Primary**: `11_UIUX_Spec.md` - User interface and experience design
- **Reviewer**: `Review_11_UIUX_Spec.md` - UX validation and accessibility review

### Test Plan Document
- **Primary**: `20_Test_Plan.md` - Test strategy and planning
- **Reviewer**: `Review_20_Test_Plan.md` - Test validation and coverage review

### Requirements Traceability Matrix
- **Primary**: `24_RTM.md` - Traceability mapping and analysis
- **Reviewer**: `Review_24_RTM.md` - Traceability validation and gap review

## Question Format & Traceability

### Primary Questions Format
```yaml
id: {DOC_TYPE}-QUESTION-001
source: primary_llm
category: [Business Process|Functional Scope|Data|Integration|Stakeholder|Other]
question: [Generation-focused question]
rationale: [Why this question helps with initial requirements gathering]
related_requirements: [{DOC_TYPE}-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect initial requirements]
```

### Reviewer Questions Format
```yaml
id: {DOC_TYPE}-REVIEW-QUESTION-001
source: reviewer_llm
category: [Validation|Consistency|Implementation|Quality|Risk|Compliance|Other]
question: [Validation-focused question]
rationale: [Why this question is important for quality assurance]
related_requirements: [{DOC_TYPE}-XXX references if applicable]
priority: High|Medium|Low
review_focus: [What aspect needs validation]
expected_impact: [How the answer will improve requirement quality]
```

## Benefits of Dual-Prompt System

### 🎯 **Comprehensive Coverage**
- Primary LLM focuses on breadth and initial discovery
- Reviewer LLM focuses on depth and validation
- Combined approach ensures nothing is missed

### 🔍 **Quality Assurance**
- Two different perspectives on the same requirements
- Built-in validation and consistency checking
- Reduced risk of errors and omissions

### 🚀 **Implementation Readiness**
- Primary questions gather requirements
- Reviewer questions ensure implementability
- Combined output is development-ready

### 📊 **Risk Mitigation**
- Dual validation reduces project risks
- Early identification of potential issues
- Comprehensive stakeholder engagement

## Usage Examples

### Example: BRD Generation with Dual Questions

#### Primary LLM Output:
```yaml
# Primary Question Example
id: BRD-QUESTION-001
source: primary_llm
category: Business Process
question: "What are the key approval workflows for purchase orders over $10,000?"
rationale: "Understanding approval processes is critical for defining business rules"
priority: High
```

#### Reviewer LLM Output:
```yaml
# Reviewer Question Example  
id: BRD-REVIEW-QUESTION-001
source: reviewer_llm
category: Validation
question: "How will the approval workflow handle scenarios where approvers are unavailable (vacation, sick leave)?"
rationale: "Validates that the approval process is robust and handles edge cases"
priority: High
review_focus: "Business process resilience"
```

### Combined Client Presentation:
Both questions are presented together, providing comprehensive coverage from initial requirements gathering through validation and edge case consideration.

## Configuration

The dual-prompt system is configured in the orchestrator's review system:

```yaml
review_system:
  enabled: true
  primary_llm:
    provider: "openai"
    model: "o3-mini"
  reviewer_llm:
    provider: "gemini" 
    model: "gemini-2.5-pro-preview-06-05"
```

## Getting Started

1. **Generate Document**: Primary LLM creates initial document with primary questions
2. **Review Document**: Reviewer LLM enhances document and adds reviewer questions
3. **Present Questions**: Both question sets are presented to client
4. **Collect Answers**: Client responds to both primary and reviewer questions
5. **Integrate Changes**: Both sets of answers are integrated with full traceability

The dual-prompt system ensures that requirements are not only comprehensive but also validated, consistent, and ready for successful implementation.
