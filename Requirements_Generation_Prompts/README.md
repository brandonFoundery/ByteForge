# Requirements Generation Prompt Library

This library contains comprehensive prompt templates for generating standardized, traceable requirements documentation for enterprise software projects. Each prompt incorporates best practices from industry standards and is designed to work with Large Language Models (LLMs).

## Document Generation Sequence

### Phase 1: Business Requirements
1. **01_BRD.md** - Business Requirements Document
2. **02_PRD.md** - Product Requirements Document
3. **03_Market_Analysis.md** - Market Analysis Document (Optional)

### Phase 2: Functional Specifications  
4. **04_FRD.md** - Functional Requirements Document
5. **05_NFRD.md** - Non-Functional Requirements Document
6. **06_Use_Cases.md** - Use Case Specifications

### Phase 3: Data & Technical Design
7. **07_DRD.md** - Data Requirements Document
8. **08_DB_Schema.md** - Database Schema Document
9. **09_TRD.md** - Technical Requirements Document
10. **10_API_OpenAPI.md** - OpenAPI Specification
11. **11_API_AsyncAPI.md** - AsyncAPI Specification

### Phase 4: UX/UI Design
12. **12_UXSMD.md** - UX Site Map Document
13. **13_UXDMD.md** - UX Data Map Document
14. **14_UI_Components.md** - UI Component Specifications
15. **15_Design_System.md** - Design System Documentation

### Phase 5: Implementation Guides
16. **16_Server_Guide.md** - Backend Implementation Guide
17. **17_React_Store.md** - Frontend State Management
18. **18_React_Root.md** - Frontend Architecture
19. **19_Component_Library.md** - Component Library Documentation

### Phase 6: Quality & Operations
20. **20_Test_Plan.md** - Test Plan and Test Cases
21. **21_Analytics_Spec.md** - Analytics Requirements
22. **22_Onboarding_Guide.md** - Team Onboarding Guide
23. **23_Deployment_Guide.md** - Deployment & Operations Guide

### Phase 7: Traceability & Control
24. **24_RTM.md** - Requirements Traceability Matrix
25. **25_Change_Management.md** - Change Management Documentation
26. **26_Risk_Assessment.md** - Risk Assessment Matrix

## Traceability System

Each document uses a hierarchical ID structure to maintain full traceability:

```
BRD-001 → PRD-001 → FRD-001.1 → TRD-001.1.1 → TC-001.1.1.1
```

## Prompt Engineering Principles

Each prompt template includes:
- **Role Definition**: Clear persona for the LLM
- **Context Requirements**: Required input documents
- **Traceability Instructions**: ID assignment and linking
- **Output Format**: Structured with YAML frontmatter
- **Validation Criteria**: Quality checks
- **Iterative Refinement**: Guidance for improvements

## YAML Frontmatter Standard

All documents include standardized YAML frontmatter:

```yaml
---
id: [DOCUMENT-ID]
title: [Document Title]
version: 1.0
status: Draft|Review|Approved|Released
created_by: [Author Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [List of upstream document IDs]
downstream: [List of downstream document IDs]
tags: [relevant, keywords, for, search]
---
```

## Usage Instructions

1. **Sequential Generation**: Follow the document sequence for best results
2. **Context Provision**: Always provide required upstream documents
3. **Iterative Refinement**: Use the refinement prompts for quality improvement
4. **Traceability Maintenance**: Ensure all IDs are properly linked
5. **Version Control**: Track all document versions and changes

## Best Practices

1. **Start with Business Context**: Always begin with BRD/PRD
2. **Maintain Consistency**: Use standardized terminology across documents
3. **Validate Traceability**: Regularly check ID linkages
4. **Review Iteratively**: Multiple refinement passes improve quality
5. **Document Dependencies**: Clearly state all prerequisites

## Quality Checklist

- [ ] All required fields populated
- [ ] Traceability IDs properly assigned
- [ ] Upstream references validated
- [ ] Downstream placeholders created
- [ ] YAML frontmatter complete
- [ ] Content meets acceptance criteria
- [ ] Technical accuracy verified
- [ ] Business alignment confirmed