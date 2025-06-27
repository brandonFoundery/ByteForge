# Iterative Requirements Elicitation Template

This template can be adapted for each document type by replacing the placeholders:

- `{DOC_TYPE}` - Document type (NFRD, DRD, TRD, etc.)
- `{DOC_FULL_NAME}` - Full document name (Non-Functional Requirements Document, etc.)
- `{QUESTION_CATEGORIES}` - Specific question categories for this document type
- `{RELATED_REFS}` - Related requirement reference patterns

## Template Section:

```markdown
## Iterative Requirements Elicitation

After generating the initial {DOC_FULL_NAME}, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the {DOC_TYPE} requirements.

### X. Client Clarification Questions

Think critically about {SPECIFIC_FOCUS_AREAS} that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: {DOC_TYPE}-QUESTION-001
category: [{QUESTION_CATEGORIES}]
question: [Specific question for the client]
rationale: [Why this question is important for {DOC_TYPE} success]
related_requirements: [{RELATED_REFS} references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect the {DOC_TYPE} requirements]
```

#### Question Categories:

{CATEGORY_SPECIFIC_CONTENT}

### Instructions for Question Generation:

1. **Be Specific**: Ask precise questions that will yield actionable answers
2. **Prioritize Impact**: Focus on questions that will significantly affect {DOC_TYPE} requirements
3. **Consider Edge Cases**: Think about unusual scenarios and exceptions
4. **Validate Assumptions**: Question any assumptions made in the initial requirements
5. **Ensure Completeness**: Look for gaps in {SPECIFIC_AREAS}
6. **Think Downstream**: Consider how answers will affect implementation
7. **Maintain Traceability**: Link questions to specific requirements when applicable

### Answer Integration Process:

When client answers are received, they should be integrated back into the {DOC_FULL_NAME} using this process:

1. **Create Answer Records**:
```yaml
id: {DOC_TYPE}-ANSWER-001
question_id: {DOC_TYPE}-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing requirements]
```

2. **Update Affected Requirements**: Modify existing requirements based on answers
3. **Create New Requirements**: Add new requirements identified through answers
4. **Update Traceability**: Ensure all changes maintain proper traceability links
5. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive {DOC_TYPE} requirements that address all critical aspects and reduce implementation risks.
```

## Document-Specific Adaptations:

### NFRD (Non-Functional Requirements Document)
- Focus: Performance, Security, Usability, Reliability, Scalability
- Categories: Performance|Security|Usability|Reliability|Scalability|Compliance|Maintainability|Other
- Specific Areas: performance criteria, security requirements, usability standards

### DRD (Data Requirements Document)
- Focus: Data structures, relationships, quality, governance
- Categories: Data Structure|Data Quality|Data Governance|Data Integration|Data Security|Data Lifecycle|Other
- Specific Areas: data models, data flows, data quality rules

### TRD (Technical Requirements Document)
- Focus: Architecture, technology stack, infrastructure
- Categories: Architecture|Technology Stack|Infrastructure|Integration|Development|Deployment|Other
- Specific Areas: technical architecture, technology choices, infrastructure needs

### API Specification
- Focus: Endpoints, data formats, authentication, error handling
- Categories: Endpoints|Data Models|Authentication|Error Handling|Performance|Versioning|Other
- Specific Areas: API design, data schemas, integration patterns

### UI/UX Specification
- Focus: User interface design, user experience, accessibility
- Categories: Interface Design|User Experience|Accessibility|Responsive Design|Interaction|Navigation|Other
- Specific Areas: interface specifications, user workflows, accessibility requirements

### Test Plan
- Focus: Test strategies, test cases, test environments
- Categories: Test Strategy|Test Cases|Test Environment|Test Data|Automation|Performance Testing|Other
- Specific Areas: testing approaches, test coverage, test environments

### RTM (Requirements Traceability Matrix)
- Focus: Requirement relationships, coverage, impact analysis
- Categories: Traceability Links|Coverage Analysis|Impact Assessment|Change Management|Verification|Other
- Specific Areas: requirement relationships, traceability coverage, change impact
```
