# Functional Requirements Document (FRD) - Prompt Template

## Primary Prompt

```markdown
You are an expert Systems Analyst and Business Analyst with extensive experience translating product requirements into detailed Functional Requirements Documents (FRDs). You excel at decomposing user stories into precise, testable functional specifications that development teams can implement.

## Your Task

Generate a complete Functional Requirements Document (FRD) for [PROJECT NAME] based on the provided Product Requirements Document (PRD) and technical context.

## Input Context Required

1. **Product Requirements Document**: [Provide complete PRD with all feature and user story IDs]
2. **Business Requirements Document**: [Provide BRD for business context]
3. **Technical Architecture**: [High-level architecture decisions if available]
4. **System Interfaces**: [Existing systems to integrate with]
5. **UI/UX Designs**: [Wireframes, mockups if available]

## Document Structure Requirements

Your FRD must include the following sections with YAML frontmatter:

```yaml
---
id: FRD
title: Functional Requirements Document - [PROJECT NAME]
version: 1.0
status: Draft
created_by: [Your Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [PRD, BRD, UI/UX Designs]
downstream: [TRD, DRD, Test Plans, Development Tasks]
tags: [functional-requirements, system-behavior, specifications]
---
```

### 1. Introduction
#### 1.1 Purpose
- Document purpose and intended audience
- Relationship to PRD and other documents

#### 1.2 Scope
- System boundaries and interfaces
- Functional areas covered
- Exclusions and limitations

#### 1.3 Document Conventions
- Terminology and notation used
- Requirement priority definitions
- Status definitions

### 2. System Overview
#### 2.1 System Context
- High-level system architecture
- Major components and their relationships
- External interfaces and integrations

#### 2.2 User Roles and Permissions
For each system role:

```yaml
id: FRD-ROLE-001
name: [Role Name]
description: [Role description and responsibilities]
permissions:
  - module: [System Module]
    actions: [Create, Read, Update, Delete, Execute]
  - module: [Another Module]
    actions: [Specific permissions]
parent_role: [FRD-ROLE-XXX if inherits permissions]
related_personas: [PRD-PERSONA-XXX references]
```

#### 2.3 System States and Modes
Define system operating states:

```yaml
id: FRD-STATE-001
name: [State Name]
description: [When system is in this state]
entry_conditions: [How system enters this state]
exit_conditions: [How system leaves this state]
available_functions: [What users can do in this state]
restrictions: [What is not available]
```

### 3. Functional Requirements by Module

For each functional module/area:

#### 3.X [Module Name]

##### Module Overview
- Purpose and responsibilities
- Key entities and relationships
- Integration points

##### Functional Requirements
For each functional requirement:

```yaml
id: FRD-001
title: [Functional Requirement Title]
module: [Module Name]
description: |
  The system SHALL [specific, testable requirement statement]
source_requirements:
  - PRD-FEAT-XXX
  - PRD-US-XXX
priority: Critical|High|Medium|Low
preconditions:
  - [Condition that must be true before]
  - [Another precondition]
postconditions:
  - [State after successful execution]
  - [Another postcondition]
main_flow:
  1. [User/System action]
  2. System validates [what]
  3. System performs [action]
  4. System displays [result]
  5. [Continue steps as needed]
alternative_flows:
  - id: AF-001
    condition: [When this occurs]
    steps:
      1. [Alternative step 1]
      2. [Alternative step 2]
exception_flows:
  - id: EF-001
    condition: [Error condition]
    steps:
      1. System displays [error message]
      2. System logs [error details]
      3. System returns to [state]
business_rules:
  - [BR-001: Specific business rule]
  - [BR-002: Another rule]
data_requirements:
  inputs:
    - field: [Field Name]
      type: [Data Type]
      validation: [Validation Rules]
      required: true|false
  outputs:
    - field: [Field Name]
      type: [Data Type]
      format: [Display Format]
ui_requirements:
  screen: [Screen/Page Name]
  elements:
    - [Required UI element]
    - [Another UI element]
performance:
  response_time: [Expected response time]
  concurrent_users: [Number supported]
  data_volume: [Expected volume]
security:
  - [Security requirement]
  - [Access control requirement]
audit:
  - [What to log]
  - [Audit trail requirements]
test_scenarios:
  - [High-level test scenario]
  - [Another test scenario]
```

##### Business Rules
For complex business rules referenced above:

```yaml
id: BR-001
title: [Business Rule Name]
description: [Detailed rule description]
formula: [If mathematical/logical formula]
conditions:
  - IF [condition1] AND [condition2]
  - THEN [action/result]
  - ELSE [alternative action]
exceptions: [Any exceptions to the rule]
examples:
  - scenario: [Example scenario]
    result: [Expected result]
related_requirements: [FRD-XXX references]
```

### 4. System-Wide Functional Requirements

#### 4.1 Authentication and Authorization

```yaml
id: FRD-AUTH-001
title: User Authentication
description: |
  The system SHALL authenticate users using [method]
requirements:
  - Support multi-factor authentication
  - Session timeout after [X] minutes of inactivity
  - Password complexity rules: [specify]
  - Account lockout after [N] failed attempts
  - Single Sign-On integration with [systems]
```

#### 4.2 Data Management

```yaml
id: FRD-DATA-001
title: Data Validation Framework
description: |
  The system SHALL validate all user inputs according to defined rules
requirements:
  - Client-side validation for immediate feedback
  - Server-side validation for security
  - Consistent error message format
  - Field-level validation rules
  - Cross-field validation support
```

#### 4.3 Audit and Logging

```yaml
id: FRD-AUDIT-001
title: Comprehensive Audit Trail
description: |
  The system SHALL maintain audit trails for all data modifications
requirements:
  - Capture: who, what, when, where, old value, new value
  - Immutable audit records
  - Configurable retention periods
  - Audit report generation
  - Compliance with [regulations]
```

#### 4.4 Notification System

```yaml
id: FRD-NOTIF-001
title: Multi-Channel Notifications
description: |
  The system SHALL send notifications through configured channels
requirements:
  - Email notifications with templates
  - In-app notifications
  - SMS notifications (optional)
  - User preference management
  - Delivery tracking and retry logic
```

### 5. Interface Requirements

#### 5.1 User Interface Requirements
General UI principles and requirements:

```yaml
id: FRD-UI-001
category: General UI Requirements
requirements:
  - Responsive design for desktop/tablet/mobile
  - WCAG 2.1 AA accessibility compliance
  - Consistent navigation patterns
  - Keyboard navigation support
  - Screen reader compatibility
  - Multi-language support (i18n)
  - Theme customization support
```

#### 5.2 External System Interfaces
For each external interface:

```yaml
id: FRD-EXT-001
system: [External System Name]
type: REST API|SOAP|File|Database|Message Queue
direction: Inbound|Outbound|Bidirectional
description: [Interface purpose and data exchanged]
requirements:
  - Protocol: [HTTPS, SFTP, etc.]
  - Authentication: [Method used]
  - Data format: [JSON, XML, CSV, etc.]
  - Frequency: [Real-time, Batch, On-demand]
  - Error handling: [Retry logic, notifications]
  - Data mapping: [Field mappings if applicable]
related_functions: [FRD-XXX references]
```

### 6. Data Requirements (High-Level)
Summary of data entities and relationships:

```yaml
id: FRD-ENTITY-001
entity: [Entity Name]
description: [What this entity represents]
key_attributes:
  - name: [Attribute]
    type: [Data type]
    required: true|false
    unique: true|false
relationships:
  - entity: [Related Entity]
    type: one-to-one|one-to-many|many-to-many
    description: [Relationship description]
operations:
  - Create: [Who can create]
  - Read: [Who can read]
  - Update: [Who can update]
  - Delete: [Who can delete]
retention: [How long to keep data]
related_functions: [FRD-XXX references]
```

### 7. Performance Requirements
Specific performance criteria:

```yaml
id: FRD-PERF-001
title: System Response Times
requirements:
  - Page load: <2 seconds for 95% of requests
  - API response: <200ms for simple queries
  - Complex reports: <30 seconds generation time
  - File upload: 10MB/second minimum
  - Concurrent users: Support 1000 simultaneous
measurement: [How to measure]
degradation: [Acceptable degradation under load]
```

### 8. Migration Requirements
If replacing existing system:

```yaml
id: FRD-MIG-001
title: Data Migration Requirements
description: Migration from [legacy system]
requirements:
  - Data mapping specifications
  - Data cleansing rules
  - Migration validation criteria
  - Rollback procedures
  - Parallel run requirements
  - Cutover planning
```

## Traceability Instructions

1. **Link to PRD**: Every functional requirement must trace to PRD features/user stories
2. **Requirement IDs**: Use consistent numbering (FRD-001, FRD-002, etc.)
3. **Module Organization**: Group requirements by functional module
4. **Cross-references**: Link related requirements and dependencies
5. **Test Scenarios**: Include high-level test scenarios for each requirement
6. **Downstream References**: Note where TRD will provide implementation details

## Quality Criteria

Your FRD must:
- Use "SHALL" for mandatory requirements
- Be unambiguous and testable
- Include all positive and negative scenarios
- Define clear acceptance criteria
- Specify all business rules explicitly
- Include error handling for all functions
- Define all user interactions step-by-step
- Be implementation-agnostic (no technology specifics)

## Output Format

Provide the complete FRD in Markdown format with:
- Proper YAML frontmatter
- Hierarchical section organization
- YAML blocks for all requirements
- Step-by-step flows for all functions
- Clear, technical writing
- Diagrams where helpful (Mermaid format)

## Chain-of-Thought Instructions

When generating functional requirements:
1. Start with the PRD user story
2. Identify all user actions needed
3. Define system responses for each action
4. Add validation and business rules
5. Include error scenarios
6. Consider edge cases
7. Ensure testability

## Iterative Requirements Elicitation

After generating the initial FRD, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the functional specifications.

### 9. Client Clarification Questions

Think critically about system behaviors, business logic, data processing, user interactions, and technical specifications that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: FRD-QUESTION-001
category: [Business Logic|User Interface|Data Processing|System Integration|Validation Rules|Error Handling|Performance|Security|Workflow|Other]
question: [Specific question for the client]
rationale: [Why this question is critical for functional specification]
related_requirements: [FRD-XXX, PRD-FEAT-XXX, or PRD-US-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect system functionality or implementation]
```

#### Question Categories:

**Business Logic Questions:**
- Calculation methods and formulas
- Business rule edge cases and exceptions
- Approval workflow details
- State transition conditions
- Complex decision trees

**User Interface Questions:**
- Screen behavior and interactions
- Field validation feedback
- Navigation patterns
- Error message content and placement
- Accessibility requirements

**Data Processing Questions:**
- Data transformation rules
- Batch processing requirements
- Real-time processing needs
- Data validation logic
- Import/export specifications

**System Integration Questions:**
- API behavior and error handling
- Data synchronization requirements
- External system dependencies
- Message format specifications
- Timeout and retry logic

**Validation Rules Questions:**
- Field-level validation criteria
- Cross-field validation logic
- Business rule validation
- Data format requirements
- Constraint specifications

**Error Handling Questions:**
- Error message specifications
- Recovery procedures
- Logging requirements
- User notification methods
- System behavior during failures

**Performance Questions:**
- Response time expectations
- Concurrent user scenarios
- Data volume handling
- Search and filtering performance
- Report generation requirements

**Security Questions:**
- Access control specifications
- Data encryption requirements
- Audit trail details
- Session management
- Permission inheritance

**Workflow Questions:**
- Process step definitions
- Parallel vs sequential processing
- Escalation procedures
- Notification triggers
- Status tracking requirements

### Instructions for Question Generation:

1. **Focus on Precision**: Ask questions that will eliminate ambiguity in functional specifications
2. **Consider Implementation**: Think about what developers need to know to build the system
3. **Think User Scenarios**: Consider all possible user interactions and system responses
4. **Validate Business Rules**: Question complex business logic and edge cases
5. **Consider Data Flow**: Think about how data moves through the system
6. **Plan for Errors**: Ask about all possible error conditions and recovery
7. **Ensure Testability**: Questions should lead to testable requirements
8. **Think Integration**: Consider how different system components interact

### Answer Integration Process:

When client answers are received, they should be integrated back into the FRD using this process:

1. **Create Answer Records**:
```yaml
id: FRD-ANSWER-001
question_id: FRD-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing functional requirements]
```

2. **Update Affected Requirements**: Modify existing functional requirements based on answers
3. **Create New Requirements**: Add new functional requirements identified through answers
4. **Refine Business Rules**: Update or create business rules based on clarifications
5. **Update Flows**: Modify main, alternative, and exception flows as needed
6. **Update Validation Rules**: Add or modify data validation requirements
7. **Update Traceability**: Ensure all changes maintain proper traceability links
8. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive functional specifications that developers can implement with confidence and testers can validate effectively.
```

## Iterative Refinement Prompts

### Refinement Round 1: Completeness Check
```markdown
Review the FRD and enhance it by:
1. Ensuring every PRD user story is fully decomposed
2. Adding missing alternative and exception flows
3. Detailing all validation rules and error messages
4. Identifying missing business rules
5. Ensuring all user roles have defined permissions
```

### Refinement Round 2: Testability Enhancement
```markdown
Refine the FRD by:
1. Making all requirements explicitly testable
2. Adding specific acceptance criteria where missing
3. Including boundary conditions and edge cases
4. Defining expected error messages exactly
5. Ensuring performance criteria are measurable
```

### Refinement Round 3: Technical Clarity
```markdown
Enhance the FRD by:
1. Removing any ambiguous language ("should", "might", "usually")
2. Clarifying all technical interfaces
3. Detailing data validation rules precisely
4. Ensuring security requirements are comprehensive
5. Validating all cross-references are correct
```

## Validation Checklist

Before finalizing the FRD, ensure:

- [ ] All PRD features and user stories are addressed
- [ ] Every requirement has a unique ID and traceability
- [ ] All requirements use "SHALL" language
- [ ] Main, alternative, and exception flows are complete
- [ ] Business rules are explicitly defined
- [ ] Error handling is specified for all scenarios
- [ ] Performance requirements are measurable
- [ ] Security requirements are comprehensive
- [ ] UI requirements support accessibility
- [ ] All external interfaces are defined
- [ ] Test scenarios cover all requirements

## Pro Tips for LLM Users

1. **PRD is Key**: Provide the complete PRD for full context
2. **Be Specific**: Vague requirements lead to implementation issues
3. **Think Like a Tester**: If you can't test it, rewrite it
4. **Error Cases Matter**: Spend time on exception flows
5. **Business Rules**: Extract and document all rules explicitly
6. **Avoid Implementation**: Don't specify how, just what
7. **User Perspective**: Write from the user's point of view

## Example Usage

```markdown
Generate an FRD using this template with the following context:
- PRD: [Paste complete PRD with all IDs]
- BRD: [Reference key business requirements]
- Technical Context: "System will integrate with SAP and Salesforce..."
- UI Designs: "Material Design components with custom theme..."
[Continue with all required inputs]