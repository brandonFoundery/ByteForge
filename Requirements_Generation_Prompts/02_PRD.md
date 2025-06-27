# Product Requirements Document (PRD) - Prompt Template

## Primary Prompt

```markdown
You are an expert Product Manager and technical writer with extensive experience translating business requirements into comprehensive Product Requirements Documents (PRDs). You excel at defining product features, user stories, and acceptance criteria that deliver business value while maintaining technical feasibility.

## Your Task

Generate a complete Product Requirements Document (PRD) for [PROJECT NAME] based on the provided Business Requirements Document (BRD) and additional product context.

## Input Context Required

1. **Business Requirements Document**: [Provide the complete BRD with requirement IDs]
2. **User Research**: [Provide user interviews, surveys, personas if available]
3. **Market Analysis**: [Competitive analysis, market trends]
4. **Technical Constraints**: [Platform limitations, integration requirements]
5. **Product Vision**: [Long-term product strategy and roadmap]

## Document Structure Requirements

Your PRD must include the following sections with YAML frontmatter:

```yaml
---
id: PRD
title: Product Requirements Document - [PROJECT NAME]
version: 1.0
status: Draft
created_by: [Your Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [BRD, User Research, Market Analysis]
downstream: [FRD, NFRD, DRD, TRD]
tags: [product-requirements, features, user-stories, acceptance-criteria]
---
```

### 1. Executive Summary
- Product vision statement
- Key value propositions
- Target market and users
- Success metrics
- Alignment with business requirements (reference BRD)

### 2. Product Overview
#### 2.1 Product Description
- What the product is and does
- Core functionality overview
- Key differentiators

#### 2.2 Product Goals and Objectives
For each goal:

```yaml
id: PRD-GOAL-001
title: [Goal Title]
description: [Detailed goal description]
success_metrics: [How we measure achievement]
business_requirement: [BRD-REQ-XXX reference]
target_date: [Achievement timeline]
priority: Critical|High|Medium|Low
```

#### 2.3 Product Scope
- In-scope features and capabilities
- Out-of-scope items (explicitly excluded)
- Future considerations (post-MVP)

### 3. User Personas and Use Cases
For each persona:

```yaml
id: PRD-PERSONA-001
name: [Persona Name]
role: [User Role/Title]
description: [Detailed persona description]
goals: 
  - [What they want to achieve]
  - [Their primary objectives]
pain_points:
  - [Current frustrations]
  - [Problems to solve]
use_cases: [PRD-UC-XXX references]
feature_priorities: [Which features matter most]
```

For each use case:

```yaml
id: PRD-UC-001
title: [Use Case Title]
persona: [PRD-PERSONA-XXX reference]
description: [Detailed use case narrative]
preconditions: [What must be true before]
main_flow:
  1. [Step 1]
  2. [Step 2]
  3. [Continue steps]
alternative_flows:
  - condition: [When this happens]
    steps: [Alternative steps]
postconditions: [State after completion]
related_features: [PRD-FEAT-XXX references]
```

### 4. Product Features and Requirements
For each feature:

```yaml
id: PRD-FEAT-001
title: [Feature Name]
epic: [High-level grouping]
description: [Comprehensive feature description]
business_requirement: [BRD-REQ-XXX reference]
user_value: [Why users need this]
business_value: [Why business needs this]
priority: P0|P1|P2|P3
effort: XS|S|M|L|XL
status: Proposed|Approved|In Development|Released
acceptance_criteria:
  - [Specific, measurable criterion 1]
  - [Specific, measurable criterion 2]
  - [Continue with all criteria]
user_stories: [List of PRD-US-XXX references]
dependencies: [Other features this depends on]
assumptions: [Assumptions made]
constraints: [Technical or business constraints]
mockups: [Link to design mockups if available]
```

### 5. User Stories
For each user story:

```yaml
id: PRD-US-001
title: [User Story Title]
feature: [PRD-FEAT-XXX reference]
persona: [PRD-PERSONA-XXX reference]
story: "As a [persona], I want to [action] so that [benefit]"
acceptance_criteria:
  - GIVEN [context]
    WHEN [action]
    THEN [outcome]
  - [Additional criteria in Given/When/Then format]
priority: Critical|High|Medium|Low
effort_points: [1-13 Fibonacci]
dependencies: [Other user stories or features]
notes: [Implementation notes or considerations]
```

### 6. Functional Requirements
Detailed functional specifications for each feature:

```yaml
id: PRD-FR-001
title: [Functional Requirement]
feature: [PRD-FEAT-XXX reference]
description: [Detailed functional behavior]
input: [Required inputs]
processing: [How it works]
output: [Expected outputs]
validation_rules: [Input validation requirements]
error_handling: [Error scenarios and handling]
performance: [Performance requirements]
```

### 7. Non-Functional Requirements
For each NFR:

```yaml
id: PRD-NFR-001
category: Performance|Security|Usability|Reliability|Scalability
title: [NFR Title]
description: [Detailed requirement]
acceptance_criteria: [Measurable criteria]
verification_method: [How to verify]
related_features: [PRD-FEAT-XXX references]
priority: Critical|High|Medium|Low
```

### 8. User Interface Requirements
#### 8.1 Design Principles
- Visual design guidelines
- Interaction patterns
- Accessibility requirements (WCAG compliance)

#### 8.2 Key Screens and Flows
For each major screen/flow:

```yaml
id: PRD-UI-001
name: [Screen/Flow Name]
description: [What this screen does]
user_stories: [PRD-US-XXX references]
elements:
  - [UI element 1]
  - [UI element 2]
interactions: [Key interactions]
mockup_link: [Link to design]
accessibility: [Specific accessibility requirements]
```

### 9. Integration Requirements
For each integration:

```yaml
id: PRD-INT-001
system: [External System Name]
type: API|Database|File|Event
description: [Integration description]
data_flow: Inbound|Outbound|Bidirectional
frequency: Real-time|Batch|On-demand
related_features: [PRD-FEAT-XXX references]
requirements:
  - [Specific requirement 1]
  - [Specific requirement 2]
```

### 10. Data Requirements
High-level data needs:

```yaml
id: PRD-DATA-001
entity: [Data Entity Name]
description: [What this data represents]
attributes: [Key attributes needed]
volume: [Expected data volume]
retention: [How long to keep]
privacy: Public|Internal|Confidential|Restricted
related_features: [PRD-FEAT-XXX references]
```

### 11. Analytics and Reporting
For each analytics requirement:

```yaml
id: PRD-ANALYTICS-001
title: [Metric/Report Name]
description: [What to measure/report]
purpose: [Why this matters]
data_source: [Where data comes from]
frequency: Real-time|Daily|Weekly|Monthly
audience: [Who uses this]
related_features: [PRD-FEAT-XXX references]
```

### 12. Success Metrics and KPIs
Define product success:

```yaml
id: PRD-KPI-001
metric: [KPI Name]
description: [What this measures]
baseline: [Current state]
target: [Goal state]
measurement: [How to measure]
timeline: [When to achieve]
related_goals: [PRD-GOAL-XXX references]
```

### 13. Release Strategy
- MVP definition and scope
- Phased release plan
- Feature rollout priorities
- Beta testing approach
- Launch criteria

### 14. Risks and Mitigation
For each risk:

```yaml
id: PRD-RISK-001
title: [Risk Title]
description: [Risk description]
probability: High|Medium|Low
impact: High|Medium|Low
mitigation: [Mitigation strategy]
contingency: [Backup plan]
owner: [Who manages this risk]
```

### 15. Glossary
Product-specific terms and definitions.

## Traceability Instructions

1. **Link to BRD**: Every feature must trace to at least one BRD requirement
2. **Feature IDs**: Use hierarchical numbering (PRD-FEAT-001, PRD-US-001.1, etc.)
3. **Cross-references**: Link related features and dependencies
4. **Downstream placeholders**: Note where FRD will provide details
5. **Maintain consistency**: Use consistent terminology from BRD

## Quality Criteria

Your PRD must:
- Clearly define the "what" without prescribing the "how"
- Include user-centric language and focus
- Provide measurable acceptance criteria
- Maintain traceability to business requirements
- Be feasible within stated constraints
- Include clear prioritization
- Support agile development practices

## Output Format

Provide the complete PRD in Markdown format with:
- Proper YAML frontmatter
- Structured sections with clear hierarchy
- YAML blocks for all traceable items
- User story format for all stories
- Clear, concise product language
- Visual diagrams where helpful (Mermaid format)

## Chain-of-Thought Instructions

When generating the PRD:
1. First, analyze the BRD to understand business requirements
2. Map each BRD requirement to potential product features
3. Group related features into logical epics
4. Define user stories that fulfill each feature
5. Ensure complete coverage of business requirements
6. Validate feasibility within constraints
7. Prioritize based on business value and effort

## Iterative Requirements Elicitation

After generating the initial PRD, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the product requirements.

### 16. Client Clarification Questions

Think critically about product features, user experiences, technical considerations, and business logic that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: PRD-QUESTION-001
category: [User Experience|Feature Scope|Technical|Integration|Data|Performance|Security|Business Logic|Other]
question: [Specific question for the client]
rationale: [Why this question is important for product success]
related_requirements: [PRD-FEAT-XXX, PRD-US-XXX, or BRD-REQ-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect product features or user experience]
```

#### Question Categories:

**User Experience Questions:**
- User workflow clarifications
- Interface behavior expectations
- Accessibility requirements
- Mobile vs desktop priorities
- User onboarding needs

**Feature Scope Questions:**
- Feature boundary definitions
- MVP vs future release decisions
- Feature interaction scenarios
- Edge case handling
- Feature configuration options

**Technical Questions:**
- Platform and browser support
- Performance expectations
- Offline functionality needs
- Real-time vs batch processing
- API design preferences

**Integration Questions:**
- Third-party service requirements
- Data synchronization needs
- Authentication methods
- Single sign-on requirements
- External system dependencies

**Data Questions:**
- Data import/export needs
- Data validation rules
- Data archival policies
- Reporting requirements
- Analytics tracking needs

**Performance Questions:**
- Response time expectations
- Concurrent user loads
- Data volume handling
- Search performance needs
- File upload/download limits

**Security Questions:**
- User permission models
- Data encryption requirements
- Audit logging needs
- Compliance requirements
- Password policy preferences

**Business Logic Questions:**
- Calculation methods
- Approval workflows
- Notification preferences
- Business rule exceptions
- Customization requirements

### Instructions for Question Generation:

1. **Focus on User Value**: Ask questions that will improve user experience and product value
2. **Consider Technical Feasibility**: Include questions about technical constraints and possibilities
3. **Think User Journeys**: Consider complete user workflows and potential friction points
4. **Validate Assumptions**: Question any assumptions made about user behavior or business processes
5. **Consider Scalability**: Think about how features will work at scale
6. **Plan for Edge Cases**: Ask about unusual scenarios and exception handling
7. **Maintain Product Vision**: Ensure questions align with overall product strategy
8. **Link to Business Value**: Connect questions to business requirements and ROI

### Answer Integration Process:

When client answers are received, they should be integrated back into the PRD using this process:

1. **Create Answer Records**:
```yaml
id: PRD-ANSWER-001
question_id: PRD-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing features or requirements]
```

2. **Update Affected Features**: Modify existing features based on answers
3. **Create New Features/Stories**: Add new features or user stories identified through answers
4. **Refine Acceptance Criteria**: Update acceptance criteria based on clarifications
5. **Update Priorities**: Adjust feature priorities based on new information
6. **Update Traceability**: Ensure all changes maintain proper traceability links
7. **Document Changes**: Track what was modified and why

This iterative approach ensures the product delivers maximum user value while meeting all business requirements and technical constraints.
```

## Iterative Refinement Prompts

### Refinement Round 1: User-Centric Validation
```markdown
Review the PRD and enhance it by:
1. Ensuring all user personas are well-defined and realistic
2. Validating that every feature provides clear user value
3. Strengthening user stories with more specific acceptance criteria
4. Adding any missing edge cases or alternative flows
5. Confirming accessibility requirements are comprehensive
```

### Refinement Round 2: Technical Feasibility
```markdown
Refine the PRD by:
1. Reviewing technical constraints and dependencies
2. Identifying potential technical risks or challenges
3. Ensuring NFRs are realistic and measurable
4. Validating integration requirements are complete
5. Confirming data requirements are well-defined
```

### Refinement Round 3: Business Alignment
```markdown
Enhance the PRD by:
1. Verifying complete traceability to BRD requirements
2. Strengthening business value justifications
3. Refining prioritization based on ROI
4. Ensuring success metrics align with business KPIs
5. Validating the MVP scope delivers core value
```

## Validation Checklist

Before finalizing the PRD, ensure:

- [ ] All BRD requirements are addressed by product features
- [ ] Every feature has clear user stories with acceptance criteria
- [ ] User personas are comprehensive and drive feature design
- [ ] Priorities are justified by user and business value
- [ ] NFRs cover all quality aspects (performance, security, etc.)
- [ ] Integration points are clearly defined
- [ ] Success metrics are measurable and achievable
- [ ] Technical constraints are acknowledged and addressed
- [ ] The MVP delivers a coherent, valuable product
- [ ] All items have unique IDs and proper traceability

## Pro Tips for LLM Users

1. **BRD First**: Always provide the complete BRD for context
2. **User Research**: Include real user feedback when available
3. **Competitive Context**: Reference competitor features for differentiation
4. **Prioritize Ruthlessly**: Not everything can be P0
5. **Think MVP**: Define the minimum lovable product
6. **Story Format**: Use consistent user story format throughout
7. **Visual Aids**: Include mockup references where possible

## Example Usage

```markdown
Generate a PRD using this template with the following context:
- BRD: [Paste complete BRD with requirement IDs]
- User Research: "Interviews with 20 logistics managers revealed..."
- Market Analysis: "Competitors offer basic tracking but lack..."
- Technical Constraints: "Must integrate with existing SAP system..."
[Continue with all required inputs]