# Iterative Requirements Elicitation Guide

## Overview

The Requirements Generation System now includes **Iterative Requirements Elicitation** capabilities in all prompt templates. This feature addresses the reality that no human can think of all requirements the first time through, making the requirements gathering process truly iterative and comprehensive.

## How It Works

### 1. Initial Document Generation
- LLM generates the initial requirements document based on available context
- Document includes all standard sections and requirements

### 2. Gap Analysis & Question Generation
- LLM performs comprehensive analysis to identify:
  - Missing concepts or requirements
  - Unclear or ambiguous specifications
  - Edge cases not considered
  - Integration points needing clarification
  - Compliance or regulatory gaps

### 3. Structured Client Questions
- Questions are organized by category (specific to each document type)
- Each question includes:
  - **Rationale**: Why this question is important
  - **Related Requirements**: Links to existing requirements
  - **Priority**: High/Medium/Low impact assessment
  - **Expected Impact**: How the answer will affect the document

### 4. Answer Integration with Traceability
- Client answers are captured with full traceability
- Changes are tracked and linked back to original questions
- Requirements are updated while maintaining traceability

## Document-Specific Question Categories

### Business Requirements Document (BRD)
- **Business Process**: Workflow clarifications, exception handling
- **Data**: Sources, quality, retention policies
- **Integration**: System interfaces, dependencies
- **Stakeholder**: Roles, authority, communication
- **Compliance**: Regulatory requirements, standards
- **Performance**: Volume, response time expectations

### Product Requirements Document (PRD)
- **User Experience**: Workflows, interface behavior
- **Feature Scope**: Boundaries, MVP decisions
- **Technical**: Platform support, performance
- **Integration**: Third-party services, APIs
- **Data**: Import/export, validation rules
- **Business Logic**: Calculations, workflows

### Functional Requirements Document (FRD)
- **Business Logic**: Calculations, rules, edge cases
- **User Interface**: Screen behavior, validation
- **Data Processing**: Transformation, validation
- **System Integration**: APIs, error handling
- **Workflow**: Process steps, notifications

### Non-Functional Requirements Document (NFRD)
- **Performance**: Response times, throughput
- **Security**: Compliance, encryption, access control
- **Usability**: Accessibility, browser support
- **Reliability**: Availability, disaster recovery
- **Scalability**: Growth projections, auto-scaling

### Data Requirements Document (DRD)
- **Data Structure**: Models, relationships
- **Data Quality**: Validation, cleansing rules
- **Data Governance**: Ownership, policies
- **Data Integration**: Sources, synchronization
- **Data Lifecycle**: Retention, archival

### Technical Requirements Document (TRD)
- **Architecture**: Patterns, components
- **Technology Stack**: Frameworks, tools
- **Infrastructure**: Servers, networking
- **Development**: Practices, standards
- **Deployment**: Strategies, automation

## Question Format

Each question follows a structured YAML format:

```yaml
id: {DOC_TYPE}-QUESTION-001
category: [Relevant Category]
question: [Specific, actionable question]
rationale: [Why this question is critical]
related_requirements: [Links to existing requirements]
priority: High|Medium|Low
expected_impact: [How answer affects implementation]
```

## Answer Integration Process

### 1. Capture Answers
```yaml
id: {DOC_TYPE}-ANSWER-001
question_id: {DOC_TYPE}-QUESTION-001
answer: [Client's detailed response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [Analysis of impact on existing requirements]
```

### 2. Update Requirements
- Modify existing requirements based on answers
- Create new requirements as needed
- Update acceptance criteria and validation rules
- Maintain traceability links

### 3. Document Changes
- Track what was modified and why
- Update version history
- Notify stakeholders of changes

## Best Practices

### For Question Generation
1. **Be Specific**: Ask precise questions that yield actionable answers
2. **Prioritize Impact**: Focus on high-impact clarifications first
3. **Consider Edge Cases**: Think about unusual scenarios
4. **Validate Assumptions**: Question what seems obvious
5. **Think Integration**: Consider system boundaries and interfaces
6. **Plan for Scale**: Ask about growth and volume expectations

### For Answer Integration
1. **Maintain Traceability**: Always link changes back to questions
2. **Update Systematically**: Don't just add - also modify existing content
3. **Consider Ripple Effects**: Changes in one area may affect others
4. **Validate Consistency**: Ensure new information doesn't conflict
5. **Document Rationale**: Explain why changes were made

## Usage Examples

### Example Question (BRD)
```yaml
id: BRD-QUESTION-001
category: Business Process
question: "What happens when a user tries to submit an order but their payment method fails? Should the system hold the inventory, send notifications, or allow retry attempts?"
rationale: "Payment failure scenarios are common but not addressed in current requirements. This affects inventory management, user experience, and system reliability."
related_requirements: [BRD-REQ-003, BRD-REQ-007]
priority: High
expected_impact: "Will require new business rules for payment failure handling, inventory reservation policies, and user notification workflows."
```

### Example Answer Integration
```yaml
id: BRD-ANSWER-001
question_id: BRD-QUESTION-001
answer: "Hold inventory for 15 minutes, send email notification, allow 3 retry attempts, then release inventory and notify user of cancellation."
provided_by: "Sarah Johnson, Product Manager"
date_received: 2025-01-27
impact_assessment: "Requires new requirements for inventory hold logic, retry mechanism, notification system, and timeout handling."
```

**Resulting Requirement Updates:**
- **BRD-REQ-003**: Updated to include 15-minute inventory hold
- **BRD-REQ-007**: Enhanced with retry logic and notification requirements
- **BRD-REQ-015**: New requirement for payment failure workflow

## Integration with Dual-LLM System

The iterative requirements elicitation works seamlessly with the dual-LLM system:

1. **Primary LLM** generates initial document with questions
2. **Reviewer LLM** can enhance questions and validate completeness
3. **Client provides answers** through structured process
4. **Primary LLM** integrates answers into updated requirements
5. **Reviewer LLM** validates integration and consistency

## Benefits

### For Clients
- **Comprehensive Coverage**: Ensures no critical requirements are missed
- **Structured Process**: Clear, organized approach to requirements refinement
- **Traceability**: Full visibility into how requirements evolved
- **Quality Assurance**: Systematic approach reduces implementation risks

### For Development Teams
- **Clarity**: Detailed requirements with fewer ambiguities
- **Completeness**: Edge cases and exceptions are addressed
- **Testability**: Requirements include validation criteria
- **Maintainability**: Changes are tracked and documented

### For Project Success
- **Risk Reduction**: Fewer surprises during implementation
- **Stakeholder Alignment**: Systematic stakeholder engagement
- **Change Management**: Controlled, traceable requirement evolution
- **Quality Improvement**: Iterative refinement leads to better outcomes

## Getting Started

1. **Generate Initial Document**: Use any prompt template as usual
2. **Review Generated Questions**: Examine the client clarification questions
3. **Prioritize Questions**: Focus on high-priority items first
4. **Engage Stakeholders**: Present questions in organized format
5. **Capture Answers**: Use structured answer format
6. **Integrate Changes**: Update requirements with full traceability
7. **Validate Results**: Ensure consistency and completeness

The iterative requirements elicitation system transforms requirements gathering from a one-time activity into a systematic, traceable, and comprehensive process that significantly improves project outcomes.
