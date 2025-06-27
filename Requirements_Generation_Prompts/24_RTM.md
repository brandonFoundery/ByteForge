# Requirements Traceability Matrix (RTM) - Prompt Template

## Primary Prompt

```markdown
You are an expert Requirements Analyst and Quality Assurance Manager with extensive experience creating and maintaining Requirements Traceability Matrices. You excel at ensuring complete bidirectional traceability across all project artifacts, from business requirements through implementation and testing.

## Your Task

Generate a COMPREHENSIVE and DETAILED Requirements Traceability Matrix (RTM) for [PROJECT NAME] based on all provided requirements documents, design specifications, and test artifacts.

**🚨 CRITICAL INSTRUCTION: You MUST analyze the ACTUAL requirements provided in the context documents. Do NOT rely on template examples. Extract EVERY requirement ID (REQ-FUNC-001, REQ-FUNC-020, etc.) from the provided FRD, PRD, and other documents. Include ALL functional areas including CRM functionality, broker roles, pipeline management, kanban boards, and any other features mentioned in the requirements. Mark new requirements as "Not Implemented" in the Implementation Status column.**

**CRITICAL CONTENT REQUIREMENTS:**
- MINIMUM 3000 words of detailed content
- COMPLETE implementation of ALL sections shown in the template
- DETAILED traceability tables with ALL requirements from source documents
- COMPREHENSIVE coverage analysis with specific metrics
- EXTENSIVE impact analysis and dependency mapping
- THOROUGH gap analysis with specific action items
- DETAILED compliance tracking with evidence
- COMPLETE validation results with specific findings

**MANDATORY SECTIONS TO IMPLEMENT IN FULL:**
1. RTM Overview (500+ words)
2. Master Traceability Table (800+ words with ALL requirements)
3. Detailed Traceability by Module (600+ words)
4. Coverage Analysis (400+ words)
5. Impact Analysis (300+ words)
6. Orphan Analysis (200+ words)
7. Compliance Tracking (300+ words)
8. Traceability Metrics (200+ words)
9. Traceability Validation (200+ words)
10. RTM Maintenance (200+ words)

**CONTENT DEPTH REQUIREMENTS:**
- Include EVERY requirement ID from ALL source documents (especially REQ-FUNC-020, REQ-FUNC-021, REQ-FUNC-022 if present)
- Create detailed descriptions for each requirement
- Map ALL relationships and dependencies
- Include specific test case references
- Provide detailed status information (mark new CRM requirements as "Not Implemented")
- Calculate precise coverage percentages
- Identify specific gaps with action plans
- Include detailed compliance evidence
- Flag new requirements for implementation team attention

## Input Context Required

1. **Business Requirements Document**: [BRD with all business requirement IDs]
2. **Product Requirements Document**: [PRD with features and user stories]
3. **Functional Requirements Document**: [FRD with functional specifications]
4. **Non-Functional Requirements**: [NFRD with quality attributes]
5. **Technical Requirements Document**: [TRD with design decisions]
6. **Test Plan**: [Test cases and scenarios]
7. **Implementation Status**: [Development progress if available]

## Document Structure Requirements

Your RTM must include the following sections with YAML frontmatter:

```yaml
---
id: RTM
title: Requirements Traceability Matrix - [PROJECT NAME]
version: 1.0
status: Draft
created_by: [Your Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [BRD, PRD, FRD, NFRD, TRD]
downstream: [Test Reports, Implementation Tracking, Change Management]
tags: [traceability, requirements-management, verification, validation]
---
```

### 1. RTM Overview

#### 1.1 Purpose and Scope
```yaml
rtm_info:
  purpose: |
    - Ensure all requirements are implemented and tested
    - Track requirement changes and impacts
    - Provide coverage analysis
    - Support compliance and audit needs
  scope:
    included:
      - Business Requirements (BRD)
      - Product Features (PRD)
      - Functional Requirements (FRD)
      - Non-Functional Requirements (NFRD)
      - Design Components (TRD)
      - Test Cases (Test Plan)
      - Implementation Status
    excluded:
      - Detailed code references
      - Third-party requirements
  traceability_levels:
    - Business to Product
    - Product to Functional
    - Functional to Technical
    - Requirements to Tests
    - Tests to Defects
```

#### 1.2 Traceability Strategy
```yaml
strategy:
  forward_traceability:
    description: Requirements → Design → Code → Tests
    purpose: Ensure all requirements are implemented
    validation: No orphan requirements
    
  backward_traceability:
    description: Tests → Code → Design → Requirements
    purpose: Ensure all implementations trace to requirements
    validation: No gold plating
    
  bidirectional:
    description: Complete two-way linkage
    purpose: Impact analysis and change management
    validation: All links verified both directions
```

#### 1.3 Status Definitions
```yaml
status_definitions:
  requirement_status:
    - Proposed: Requirement identified but not approved
    - Approved: Requirement approved for implementation
    - In Progress: Implementation ongoing
    - Implemented: Code complete
    - Tested: Testing complete
    - Verified: Requirement verified and accepted
    - Deferred: Postponed to future release
    - Rejected: Not to be implemented
    
  test_status:
    - Not Started: Test not yet executed
    - In Progress: Test execution ongoing
    - Passed: Test passed successfully
    - Failed: Test failed, defect logged
    - Blocked: Cannot execute due to dependency
    - Skipped: Test skipped (document reason)
```

### 2. Master Traceability Table

```markdown
| Req ID | Requirement Description | Type | Priority | Source | Design Ref | Implementation | Test Cases | Test Status | Verification | Notes |
|--------|------------------------|------|----------|---------|------------|----------------|------------|-------------|--------------|-------|
| REQ-FUNC-001 | User authentication and login | Functional | Critical | FRD | TRD-001, TRD-SEC-001 | AuthService.java | TC-AUTH-001, TC-AUTH-002 | Passed | Verified | Core requirement |
| REQ-FUNC-020 | CRM broker dashboard functionality | Functional | High | FRD | TRD-CRM-001 | BrokerDashboard.tsx | TC-CRM-001, TC-CRM-002 | Not Implemented | Pending | New CRM feature |
| REQ-FUNC-021 | Kanban pipeline management | Functional | High | FRD | TRD-CRM-002 | KanbanBoard.tsx | TC-KANBAN-001 | Not Implemented | Pending | Pipeline visualization |
| REQ-FUNC-022 | Broker role management | Functional | Medium | FRD | TRD-RBAC-001 | RoleService.java | TC-RBAC-001, TC-RBAC-002 | Not Implemented | Pending | Role-based access |
| REQ-FUNC-003 | Dashboard metrics display | Functional | High | FRD | TRD-DASH-001 | DashboardService.java | TC-DASH-001 | Passed | Verified | |
| REQ-NFUNC-001 | Page load time <2 seconds | Non-Functional | High | NFRD | TRD-PERF-001 | Performance optimization | TC-PERF-001 | Failed | In Progress | Current: 2.5s |
| REQ-NFUNC-002 | OWASP Top 10 compliance | Non-Functional | Critical | NFRD | TRD-SEC-001, TRD-SEC-002 | Security framework | TC-SEC-001 through TC-SEC-010 | In Progress | Pending | 8/10 complete |

**IMPORTANT**: Use the ACTUAL requirement IDs from the provided documents, not these examples. These are just format examples. Mark new CRM requirements (REQ-FUNC-020, REQ-FUNC-021, REQ-FUNC-022) as "Not Implemented" to flag them for development.
```

### 3. Detailed Traceability by Module

#### 3.1 Authentication Module
```yaml
module: Authentication
coverage_summary:
  total_requirements: 15
  implemented: 12
  tested: 10
  verified: 8
  coverage_percentage: 80%

traceability_details:
  - requirement_id: BRD-001
    description: Secure user authentication
    child_requirements:
      - id: PRD-001
        type: Product Feature
        description: User login functionality
        functional_requirements:
          - id: FRD-AUTH-001
            description: Username/password validation
            design_components:
              - id: TRD-COMP-001
                component: AuthenticationService
                implementation_files:
                  - path: /src/services/AuthService.java
                    methods: [authenticate, validateCredentials]
                  - path: /src/controllers/LoginController.java
                    methods: [login, logout]
            test_coverage:
              - test_id: TC-AUTH-001
                description: Valid login test
                status: Passed
                execution_date: 2025-06-10
                defects: []
              - test_id: TC-AUTH-002
                description: Invalid password test
                status: Passed
                execution_date: 2025-06-10
                defects: []
            verification_status: Verified
            verification_method: User acceptance testing
            verification_date: 2025-06-11
```

### 4. Coverage Analysis

#### 4.1 Requirements Coverage
```yaml
coverage_analysis:
  by_requirement_type:
    - type: Business Requirements
      total: 50
      with_test_cases: 48
      coverage: 96%
      gaps:
        - BRD-045: Awaiting clarification
        - BRD-050: Deferred to Phase 2
        
    - type: Functional Requirements
      total: 200
      with_test_cases: 195
      coverage: 97.5%
      gaps:
        - FRD-187: Test case in development
        - FRD-193: Blocked by dependency
        - FRD-199: Environment not ready
        - FRD-200: Data not available
        - FRD-201: Deferred
        
    - type: Non-Functional Requirements
      total: 30
      with_test_cases: 25
      coverage: 83.3%
      gaps:
        - NFR-PERF-005: Performance environment needed
        - NFR-SEC-008: Security tool procurement
        - NFR-SCALE-003: Load testing deferred
        - NFR-COMP-002: Compliance audit pending
        - NFR-PORT-001: Platform testing deferred
```

#### 4.2 Test Coverage
```yaml
test_coverage:
  by_test_type:
    - type: Unit Tests
      requirements_covered: 150
      test_cases: 1200
      pass_rate: 98%
      code_coverage: 82%
      
    - type: Integration Tests
      requirements_covered: 180
      test_cases: 350
      pass_rate: 95%
      interface_coverage: 100%
      
    - type: System Tests
      requirements_covered: 200
      test_cases: 500
      pass_rate: 92%
      scenario_coverage: 95%
      
    - type: Acceptance Tests
      requirements_covered: 50
      test_cases: 100
      pass_rate: 88%
      user_story_coverage: 100%
```

### 5. Impact Analysis

#### 5.1 Change Impact Matrix
```yaml
change_impact:
  - change_id: CR-001
    description: Add social login support
    impacted_requirements:
      - BRD-001: Modify authentication approach
      - PRD-001: Add social login feature
      - FRD-AUTH-001: New validation logic
      - NFR-SEC-001: Additional security review
    impacted_components:
      - AuthenticationService: Major changes
      - LoginController: UI updates
      - UserDatabase: Schema changes
    impacted_tests:
      - TC-AUTH-*: All authentication tests
      - TC-SEC-001: Security test updates
    effort_estimate: 40 hours
    risk_level: Medium
```

#### 5.2 Dependency Analysis
```yaml
dependencies:
  critical_paths:
    - path: Payment Processing
      chain: BRD-002 → PRD-010 → FRD-PAY-* → TRD-COMP-005
      blockers:
        - Payment gateway integration pending
        - PCI compliance certification required
      mitigation: Use payment gateway sandbox
      
    - path: Reporting Module
      chain: BRD-015 → PRD-025 → FRD-RPT-* → TRD-COMP-008
      blockers:
        - Data warehouse setup incomplete
      mitigation: Use transactional DB temporarily
```

### 6. Orphan Analysis

#### 6.1 Orphan Requirements
```yaml
orphan_requirements:
  without_test_cases:
    - FRD-199: Email template management
      reason: Test environment constraint
      action: Create manual test procedure
      target_date: 2025-06-15
      
  without_implementation:
    - PRD-045: Advanced search filters
      reason: Technical complexity
      action: Spike investigation needed
      target_date: 2025-06-20
```

#### 6.2 Orphan Tests
```yaml
orphan_tests:
  without_requirements:
    - TC-MISC-001: Database connection pooling
      action: Link to NFR-PERF-003
      
    - TC-MISC-002: Cache invalidation
      action: Create NFR for caching strategy
```

### 7. Compliance Tracking

#### 7.1 Regulatory Compliance
```yaml
compliance_tracking:
  regulations:
    - regulation: PCI-DSS
      requirements:
        - NFR-SEC-010: Encryption at rest
          status: Implemented
          evidence: Security audit report
        - NFR-SEC-011: Access logging
          status: In Progress
          target: 2025-06-30
          
    - regulation: GDPR
      requirements:
        - NFR-COMP-001: Right to erasure
          status: Implemented
          evidence: TC-GDPR-001 passed
        - NFR-COMP-002: Data portability
          status: Planned
          target: 2025-07-15
```

### 8. Traceability Metrics

#### 8.1 Key Metrics
```yaml
metrics:
  completeness:
    - metric: Requirements with upstream trace
      value: 98%
      target: 100%
      gap: 5 requirements missing business context
      
    - metric: Requirements with test coverage
      value: 95%
      target: 100%
      gap: 12 requirements without tests
      
  quality:
    - metric: Test pass rate
      value: 92%
      target: 95%
      trend: Improving
      
    - metric: Requirement volatility
      value: 15%
      target: <20%
      trend: Stable
      
  progress:
    - metric: Requirements implemented
      value: 78%
      target: 100%
      projection: 2025-07-01
      
    - metric: Requirements verified
      value: 65%
      target: 100%
      projection: 2025-07-15
```

### 9. Traceability Validation

#### 9.1 Validation Rules
```yaml
validation_rules:
  mandatory_traces:
    - Every FRD must trace to at least one PRD
    - Every test case must trace to at least one requirement
    - Every high/critical requirement must have test coverage
    - Every NFR must have verification criteria
    
  consistency_checks:
    - Status progression must be logical
    - Child requirement priority ≤ parent priority
    - Test status must align with requirement status
    - Circular dependencies are forbidden
```

#### 9.2 Validation Results
```yaml
validation_results:
  errors:
    - FRD-155 has no upstream PRD reference
    - TC-MISC-003 has no requirement reference
    - BRD-030 priority conflicts with child PRD-040
    
  warnings:
    - FRD-122 has only manual test coverage
    - NFR-PERF-008 lacks specific metrics
    - TRD-015 not linked to any requirement
```

### 10. RTM Maintenance

#### 10.1 Update Procedures
```yaml
maintenance_procedures:
  update_triggers:
    - New requirement approved
    - Requirement change approved
    - Test case added/modified
    - Implementation completed
    - Test execution completed
    - Defect linked to requirement
    
  update_process:
    - Validate upstream/downstream links
    - Update status fields
    - Recalculate coverage metrics
    - Run validation rules
    - Generate change notifications
    
  review_schedule:
    - Daily: Status updates
    - Weekly: Coverage analysis
    - Sprint: Full validation
    - Release: Complete audit
```

## Traceability Instructions

1. **Complete Linkage**: Every artifact must have bidirectional links
2. **Unique IDs**: Maintain consistent ID scheme across documents
3. **Status Tracking**: Keep all status fields current
4. **Impact Analysis**: Update impacts for any changes
5. **Coverage Monitoring**: Track and address coverage gaps

## Quality Criteria

Your RTM must:
- Include all project artifacts
- Maintain bidirectional traceability
- Calculate accurate coverage metrics
- Identify all gaps and orphans
- Support impact analysis
- Enable compliance tracking
- Be easily maintainable
- Provide actionable insights

## Output Format

Provide the complete RTM in Markdown format with:
- Proper YAML frontmatter
- Comprehensive traceability tables
- Coverage analysis charts
- Gap identification
- Metrics dashboard
- Validation results
- Maintenance procedures

## Chain-of-Thought Instructions

When creating the RTM:
1. Collect all requirement IDs
2. Map parent-child relationships
3. Link to design and implementation
4. Connect test cases
5. Calculate coverage
6. Identify gaps
7. Analyze impacts
8. Validate consistency
```

## Iterative Refinement Prompts

### Refinement Round 1: Completeness
```markdown
Review the RTM and enhance it by:
1. Finding all missing links
2. Identifying orphan artifacts
3. Completing status updates
4. Adding missing test references
5. Validating ID consistency
```

### Refinement Round 2: Analysis
```markdown
Refine the RTM by:
1. Calculating detailed metrics
2. Performing gap analysis
3. Creating impact assessments
4. Identifying critical paths
5. Analyzing dependencies
```

### Refinement Round 3: Actionability
```markdown
Enhance the RTM by:
1. Prioritizing gaps for closure
2. Creating action items
3. Setting coverage targets
4. Defining improvement plans
5. Establishing review cycles

## Iterative Requirements Elicitation

After generating the initial Requirements Traceability Matrix, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the RTM requirements.

### 6. Client Clarification Questions

Think critically about requirement relationships, coverage analysis, impact assessment, change management, and verification that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: RTM-QUESTION-001
category: [Traceability Links|Coverage Analysis|Impact Assessment|Change Management|Verification|Gap Analysis|Other]
question: [Specific question for the client]
rationale: [Why this question is important for RTM success]
related_requirements: [RTM-XXX, BRD-REQ-XXX, or PRD-FEAT-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect the RTM requirements]
```

#### Question Categories:

**RTM-Specific Questions:**
- Clarifications on requirement relationships, traceability coverage, change impact, and verification status
- Edge cases and exception scenarios
- Integration and dependency requirements
- Performance and quality expectations
- Compliance and governance needs

### Instructions for Question Generation:

1. **Be Specific**: Ask precise questions that will yield actionable answers
2. **Prioritize Impact**: Focus on questions that will significantly affect RTM requirements
3. **Consider Edge Cases**: Think about unusual scenarios and exceptions
4. **Validate Assumptions**: Question any assumptions made in the initial requirements
5. **Ensure Completeness**: Look for gaps in requirement relationships, traceability coverage, change impact, and verification status
6. **Think Downstream**: Consider how answers will affect implementation
7. **Maintain Traceability**: Link questions to specific requirements when applicable

### Answer Integration Process:

When client answers are received, they should be integrated back into the Requirements Traceability Matrix using this process:

1. **Create Answer Records**:
```yaml
id: RTM-ANSWER-001
question_id: RTM-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing requirements]
```

2. **Update Affected Requirements**: Modify existing requirements based on answers
3. **Create New Requirements**: Add new requirements identified through answers
4. **Update Traceability**: Ensure all changes maintain proper traceability links
5. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive RTM requirements that address all critical aspects and reduce implementation risks.

```

## Validation Checklist

Before finalizing the RTM, ensure:

- [ ] All requirements are included
- [ ] Bidirectional links are complete
- [ ] Status fields are current
- [ ] Coverage metrics are accurate
- [ ] Gaps are identified and documented
- [ ] Validation errors are resolved
- [ ] Impact analysis is comprehensive
- [ ] Compliance tracking is complete
- [ ] Maintenance procedures are defined
- [ ] Metrics support decision-making

## Pro Tips for LLM Users

1. **Start Early**: Begin RTM with first requirement
2. **Automate Updates**: Use tools for maintenance
3. **Regular Reviews**: Don't let it get stale
4. **Focus on Value**: Track what matters
5. **Visual Dashboards**: Make metrics visible
6. **Change Control**: Update with every change
7. **Stakeholder Views**: Create role-based views

## Example Usage

```markdown
Generate an RTM using this template with the following context:
- BRD: "50 business requirements defined..."
- PRD: "120 user stories across 15 epics..."
- FRD: "200 functional requirements..."
- Test Plan: "500 test cases defined..."
- Current Status: "Development 60% complete..."
[Continue with all required inputs]