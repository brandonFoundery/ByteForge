# Business Requirements Document (BRD) - Prompt Template

## Primary Prompt

```markdown
You are an expert Business Analyst and technical writer with extensive experience in creating comprehensive Business Requirements Documents (BRDs) for enterprise software projects. You excel at translating business needs into clear, actionable requirements that align with strategic objectives.

## Your Task

Generate a complete Business Requirements Document (BRD) for [PROJECT NAME] based on the provided business context and stakeholder inputs.

## Input Context Required

1. **Business Context**: [Provide company background, industry, current challenges]
2. **Stakeholder Inputs**: [Provide interview summaries, workshop notes, survey results]
3. **Strategic Objectives**: [List company strategic goals and KPIs]
4. **Market Analysis**: [Provide competitive landscape, market trends if available]
5. **Constraints**: [Budget, timeline, regulatory requirements]

## Document Structure Requirements

Your BRD must include the following sections with YAML frontmatter:

```yaml
---
id: BRD
title: Business Requirements Document - [PROJECT NAME]
version: 1.0
status: Draft
created_by: [Your Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [Business Strategy Documents, Stakeholder Interviews]
downstream: [PRD, FRD, NFRD]
tags: [business-requirements, strategic-alignment, stakeholder-needs]
---
```

### 1. Executive Summary
- Business problem statement
- Proposed solution overview
- Expected business value
- Key success metrics

### 2. Business Context
- Current state analysis
- Problem definition and root causes
- Business impact of current problems
- Opportunity analysis

### 3. Project Objectives and Goals
Each objective must be SMART (Specific, Measurable, Achievable, Relevant, Time-bound):

```yaml
id: BRD-OBJ-001
title: [Objective Title]
description: [Detailed objective description]
success_criteria: [How we measure success]
target_date: [When to achieve]
business_value: [Expected value/impact]
priority: High|Medium|Low
status: Draft
```

### 4. Stakeholder Analysis
For each stakeholder group:

```yaml
id: BRD-STK-001
name: [Stakeholder Group]
role: [Their role in the project]
interests: [What they care about]
influence: High|Medium|Low
requirements_source: [Which requirements they drive]
communication_needs: [How to engage them]
```

### 5. Business Requirements
For each requirement:

```yaml
id: BRD-REQ-001
title: [Requirement Title]
description: [Detailed requirement description - what business capability is needed]
rationale: [Why this is needed]
success_criteria: [How to verify this requirement is met]
priority: Must Have|Should Have|Could Have|Won't Have
source: [Stakeholder or document reference]
verification_method: [How to verify: Demo|Test|Inspection|Analysis]
status: Draft|Approved|Deferred|Rejected
acceptance_criteria:
  - [Specific criterion 1]
  - [Specific criterion 2]
  - [Specific criterion 3]
dependencies: [List any dependent requirements]
assumptions: [List assumptions made]
constraints: [List applicable constraints]
```

### 6. Business Process Requirements
Document current and future state processes:

```yaml
id: BRD-PROC-001
process_name: [Process Name]
current_state: [Description of current process]
future_state: [Description of desired process]
improvement_metrics: [How we measure improvement]
affected_stakeholders: [BRD-STK-XXX references]
related_requirements: [BRD-REQ-XXX references]
```

### 7. Business Rules
For each business rule:

```yaml
id: BRD-RULE-001
rule_name: [Business Rule Name]
description: [Detailed rule description]
conditions: [When the rule applies]
actions: [What happens when rule is triggered]
exceptions: [Any exceptions to the rule]
source: [Regulatory/Policy source]
related_requirements: [BRD-REQ-XXX references]
```

### 8. Assumptions and Dependencies
- Project assumptions with risk levels
- External dependencies
- Internal dependencies
- Critical success factors

### 9. Constraints and Risks
For each constraint/risk:

```yaml
id: BRD-RISK-001
type: Risk|Constraint
title: [Risk/Constraint Title]
description: [Detailed description]
probability: High|Medium|Low
impact: High|Medium|Low
mitigation: [Mitigation strategy]
owner: [Who owns this risk]
status: Active|Mitigated|Accepted
```

### 10. Success Metrics and KPIs
Define measurable success criteria:

```yaml
id: BRD-KPI-001
metric_name: [KPI Name]
description: [What this measures]
current_value: [Baseline]
target_value: [Goal]
measurement_method: [How to measure]
frequency: [How often to measure]
owner: [Who tracks this]
related_objectives: [BRD-OBJ-XXX references]
```

### 11. Cost-Benefit Analysis
- Implementation costs (one-time and ongoing)
- Expected benefits (quantified where possible)
- ROI calculation
- Payback period

### 12. Glossary
Define all business terms, acronyms, and domain-specific language.

## Traceability Instructions

1. **Requirement IDs**: Use sequential numbering (BRD-REQ-001, BRD-REQ-002, etc.)
2. **Cross-references**: Link related requirements using their IDs
3. **Downstream placeholders**: Create "TBD" entries for PRD linkages
4. **Upstream references**: Cite specific stakeholder inputs or documents
5. **Maintain consistency**: Use the same business terminology throughout

## Quality Criteria

Your BRD must:
- Be written in clear, non-technical business language
- Focus on WHAT is needed, not HOW to implement
- Include measurable success criteria for all requirements
- Provide clear prioritization using MoSCoW method
- Include comprehensive stakeholder perspectives
- Be internally consistent and free of contradictions
- Support downstream technical documentation

## Output Format

Provide the complete BRD in Markdown format with:
- Proper YAML frontmatter
- Hierarchical section numbering
- YAML blocks for all traceable items
- Clear, professional business writing
- Tables and diagrams where helpful (in Markdown/Mermaid format)

## Iterative Requirements Elicitation

After generating the initial BRD, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the requirements.

### 13. Client Clarification Questions

Think critically about concepts, data, requirements, and business processes that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: BRD-QUESTION-001
category: [Business Process|Data|Integration|Stakeholder|Compliance|Performance|Security|Other]
question: [Specific question for the client]
rationale: [Why this question is important]
related_requirements: [BRD-REQ-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect the requirements]
```

#### Question Categories:

**Business Process Questions:**
- Process flow clarifications
- Exception handling scenarios
- Approval workflows
- Business rule edge cases

**Data Questions:**
- Data sources and ownership
- Data quality requirements
- Data retention policies
- Master data management

**Integration Questions:**
- System interfaces and dependencies
- Data exchange requirements
- Third-party service dependencies
- Legacy system constraints

**Stakeholder Questions:**
- Role clarifications
- Decision-making authority
- Communication preferences
- Training requirements

**Compliance Questions:**
- Regulatory requirements
- Audit trail needs
- Data privacy requirements
- Industry standards

**Performance Questions:**
- Volume expectations
- Response time requirements
- Availability needs
- Scalability requirements

**Security Questions:**
- Access control requirements
- Data protection needs
- Authentication methods
- Authorization levels

### Instructions for Question Generation:

1. **Be Specific**: Ask precise questions that will yield actionable answers
2. **Prioritize Impact**: Focus on questions that will significantly affect requirements
3. **Consider Edge Cases**: Think about unusual scenarios and exceptions
4. **Validate Assumptions**: Question any assumptions made in the initial requirements
5. **Ensure Completeness**: Look for gaps in business processes, data flows, and stakeholder needs
6. **Think Downstream**: Consider how answers will affect technical implementation
7. **Maintain Traceability**: Link questions to specific requirements when applicable

### Answer Integration Process:

When client answers are received, they should be integrated back into the BRD using this process:

1. **Create Answer Records**:
```yaml
id: BRD-ANSWER-001
question_id: BRD-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing requirements]
```

2. **Update Affected Requirements**: Modify existing requirements based on answers
3. **Create New Requirements**: Add new requirements identified through answers
4. **Update Traceability**: Ensure all changes maintain proper traceability links
5. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive requirements capture and reduces the risk of missing critical business needs.
```

## Iterative Refinement Prompts

### Refinement Round 1: Completeness Check
```markdown
Review the generated BRD and enhance it by:
1. Ensuring all stakeholder groups are represented
2. Verifying each requirement has clear acceptance criteria
3. Adding any missing business rules or constraints
4. Strengthening the cost-benefit analysis with specific metrics
5. Ensuring all requirements are traceable to business objectives
```

### Refinement Round 2: Clarity and Consistency
```markdown
Refine the BRD by:
1. Simplifying any complex business language
2. Ensuring consistent terminology throughout
3. Clarifying any ambiguous requirements
4. Adding examples where helpful
5. Verifying all cross-references are correct
```

### Refinement Round 3: Prioritization and Risk
```markdown
Enhance the BRD by:
1. Reviewing and validating all priority assignments
2. Ensuring risks are comprehensive and well-mitigated
3. Identifying any gaps in the requirements
4. Validating dependencies between requirements
5. Confirming alignment with strategic objectives
```

## Validation Checklist

Before finalizing the BRD, ensure:

- [ ] All sections are complete with no TBD items (except downstream references)
- [ ] Every requirement has a unique ID and is traceable
- [ ] Acceptance criteria are specific and measurable
- [ ] Stakeholder needs are comprehensively addressed
- [ ] Business value is clearly articulated for each requirement
- [ ] Priorities are justified and aligned with business goals
- [ ] Risks and mitigations are realistic and actionable
- [ ] The document is readable by non-technical stakeholders
- [ ] Cost-benefit analysis supports the business case
- [ ] Success metrics are measurable and achievable

## Pro Tips for LLM Users

1. **Provide Rich Context**: The more stakeholder input you provide, the better the output
2. **Iterate Multiple Times**: Use refinement prompts to improve quality
3. **Validate with Stakeholders**: Always review generated content with actual stakeholders
4. **Maintain Living Document**: Update the BRD as understanding evolves
5. **Focus on Business Value**: Every requirement should tie to measurable business value

## Example Usage

```markdown
Generate a BRD using this template with the following context:
- Business Context: "We are a mid-size logistics company struggling with manual payment processing..."
- Stakeholder Inputs: "CFO wants 50% reduction in payment processing time..."
- Strategic Objectives: "Digital transformation initiative targeting 30% operational efficiency..."
[Continue with all required inputs]