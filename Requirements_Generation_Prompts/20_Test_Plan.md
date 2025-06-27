# Test Plan and Test Cases Document - Prompt Template

## Primary Prompt

```markdown
You are an expert QA Lead and Test Architect with extensive experience creating comprehensive test strategies for enterprise software systems. You excel at designing test plans that ensure complete requirement coverage while optimizing testing efficiency and effectiveness.

## Your Task

Generate a COMPREHENSIVE and DETAILED Test Plan and Test Cases Document for [PROJECT NAME] based on the provided requirements documents and system architecture.

**🚨 CRITICAL INSTRUCTION: You MUST analyze the ACTUAL requirements provided in the FRD and other context documents. Do NOT rely on template examples. Extract EVERY requirement ID (REQ-FUNC-001, REQ-FUNC-020, etc.) and create test cases for ALL functional areas including CRM functionality, broker roles, pipeline management, kanban boards, and any other features mentioned in the requirements. Mark test cases for new requirements as "Not Implemented" or "Pending Implementation" to flag them for the testing team.**

**CRITICAL CONTENT REQUIREMENTS:**
- MINIMUM 3500 words of detailed testing content
- COMPLETE implementation of ALL sections shown in the template
- DETAILED test cases for ALL functional requirements
- COMPREHENSIVE test strategy with specific methodologies
- EXTENSIVE test environment specifications
- THOROUGH risk analysis with mitigation strategies
- DETAILED automation framework specifications
- COMPLETE defect management procedures

**MANDATORY SECTIONS TO IMPLEMENT IN FULL:**
1. Test Plan Overview (500+ words)
2. Test Scope and Approach (400+ words)
3. Test Environment (400+ words)
4. Test Cases (1000+ words with detailed test cases)
5. Test Execution (300+ words)
6. Defect Management (300+ words)
7. Risk Management (300+ words)
8. Test Automation (300+ words)

**CONTENT DEPTH REQUIREMENTS:**
- Include detailed test cases for EVERY functional area
- Provide comprehensive test data specifications
- Include specific environment configurations
- Provide detailed automation strategies
- Include precise metrics and success criteria
- Provide comprehensive risk assessments
- Include detailed execution schedules

## Input Context Required

1. **Functional Requirements Document**: [Complete FRD with all functional specifications]
2. **Non-Functional Requirements Document**: [Complete NFRD with quality attributes]
3. **Technical Requirements Document**: [TRD for architecture understanding]
4. **Product Requirements Document**: [PRD for user stories and acceptance criteria]
5. **Risk Assessment**: [Known risks and critical areas]
6. **Testing Constraints**: [Timeline, resources, environments available]

## Document Structure Requirements

Your Test Plan must include the following sections with YAML frontmatter:

```yaml
---
id: TEST-PLAN
title: Test Plan and Test Cases - [PROJECT NAME]
version: 1.0
status: Draft
created_by: [Your Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [FRD, NFRD, PRD, TRD]
downstream: [Test Reports, Defect Reports, RTM]
tags: [test-plan, test-cases, quality-assurance, verification]
---
```

### 1. Test Plan Overview

#### 1.1 Introduction
```yaml
test_plan_info:
  purpose: Comprehensive testing strategy for [PROJECT NAME]
  scope: [What is included/excluded from testing]
  approach: Risk-based testing with requirement coverage
  deliverables:
    - Test Plan Document
    - Test Case Repository
    - Test Execution Reports
    - Defect Reports
    - Test Summary Report
```

#### 1.2 Test Objectives
```yaml
objectives:
  primary:
    - Verify all functional requirements are correctly implemented
    - Validate non-functional requirements are met
    - Ensure system reliability and stability
    - Identify defects before production release
  quality_goals:
    - Requirement coverage: 100%
    - Code coverage: >80%
    - Critical defect escape rate: 0%
    - Test automation: >70%
```

#### 1.3 Test Strategy
```yaml
test_strategy:
  levels:
    - level: Unit Testing
      responsible: Development Team
      coverage_target: 80%
      automation: 100%
      
    - level: Integration Testing
      responsible: QA Team
      coverage_target: 100% of interfaces
      automation: 80%
      
    - level: System Testing
      responsible: QA Team
      coverage_target: 100% of requirements
      automation: 70%
      
    - level: Acceptance Testing
      responsible: Business Users + QA
      coverage_target: 100% of user stories
      automation: 30%
      
  types:
    - Functional Testing
    - Performance Testing
    - Security Testing
    - Usability Testing
    - Compatibility Testing
    - Regression Testing
```

### 2. Test Scope and Approach

#### 2.1 In Scope
```yaml
in_scope:
  functional_areas:
    - area: User Management
      priority: Critical
      test_types: [Functional, Security, Performance]
      
    - area: Order Processing
      priority: Critical
      test_types: [Functional, Performance, Integration]
      
    - area: Payment Processing
      priority: Critical
      test_types: [Functional, Security, Integration]
      
    - area: Reporting
      priority: High
      test_types: [Functional, Performance]
      
  non_functional_areas:
    - Performance under load
    - Security vulnerabilities
    - Browser compatibility
    - Mobile responsiveness
    - API contract validation
```

#### 2.2 Out of Scope
```yaml
out_of_scope:
  - Legacy system testing (except integration points)
  - Third-party service internal testing
  - Hardware compatibility testing
  - Localization testing (Phase 2)
```

#### 2.3 Test Approach
```yaml
approach:
  methodology: Agile Testing
  test_design_techniques:
    - Equivalence Partitioning
    - Boundary Value Analysis
    - Decision Table Testing
    - State Transition Testing
    - Use Case Testing
  prioritization: Risk-based
  execution_approach: Exploratory + Scripted
```

### 3. Test Environment

#### 3.1 Environment Requirements
```yaml
environments:
  - name: Development
    purpose: Developer testing
    configuration:
      - OS: Ubuntu 20.04
      - Database: PostgreSQL 15 (Docker)
      - Services: All microservices (Docker Compose)
    data: Synthetic test data
    access: Development team only
    
  - name: QA
    purpose: Functional and integration testing
    configuration:
      - OS: Ubuntu 20.04
      - Database: PostgreSQL 15 (Dedicated)
      - Services: Full deployment (Kubernetes)
    data: Production-like test data
    access: QA team
    
  - name: Staging
    purpose: UAT and performance testing
    configuration:
      - OS: Production-identical
      - Database: Production-identical
      - Services: Production-identical
    data: Anonymized production data
    access: QA + Business users
    
  - name: Performance
    purpose: Load and stress testing
    configuration:
      - Scaled infrastructure
      - Load balancers
      - CDN integration
    data: Volume test data
    tools: JMeter, Gatling
```

#### 3.2 Test Data Requirements
```yaml
test_data:
  categories:
    - type: Master Data
      examples: [Users, Products, Customers]
      volume: 10,000 records each
      source: Data generation scripts
      
    - type: Transactional Data
      examples: [Orders, Payments, Invoices]
      volume: 100,000 records
      source: Production sampling + generation
      
    - type: Edge Cases
      examples: [Max length strings, boundary values]
      volume: Comprehensive set
      source: Manual creation
      
  management:
    - Version controlled test data
    - Automated data refresh
    - Data masking for PII
    - Backup and restore procedures
```

### 4. Test Cases

#### 4.1 Test Case Template
```yaml
test_case_template:
  id: TC-[Module]-[Number]
  title: [Test Case Title]
  priority: Critical|High|Medium|Low
  type: Functional|Performance|Security|Usability
  requirement_ref: [FRD-XXX, PRD-US-XXX]
  preconditions:
    - [Precondition 1]
    - [Precondition 2]
  test_data:
    - [Test data requirement 1]
    - [Test data requirement 2]
  steps:
    - step: 1
      action: [User action]
      expected: [Expected result]
    - step: 2
      action: [User action]
      expected: [Expected result]
  postconditions:
    - [System state after test]
  automation_status: Manual|Automated|Planned
  automation_script: [Script reference if automated]
```

#### 4.2 Sample Test Cases

##### Authentication Module
```yaml
test_case:
  id: TC-AUTH-001
  title: Successful User Login with Valid Credentials
  priority: Critical
  type: Functional
  requirement_ref: [FRD-AUTH-001, PRD-US-001]
  preconditions:
    - User account exists with status 'ACTIVE'
    - User is not currently logged in
    - Login page is accessible
  test_data:
    - username: testuser@example.com
    - password: ValidPass123!
  steps:
    - step: 1
      action: Navigate to login page
      expected: Login form is displayed with username and password fields
    - step: 2
      action: Enter valid username 'testuser@example.com'
      expected: Username is accepted, no error shown
    - step: 3
      action: Enter valid password 'ValidPass123!'
      expected: Password is masked, no error shown
    - step: 4
      action: Click 'Login' button
      expected: |
        - Loading indicator appears
        - User is redirected to dashboard
        - User name appears in header
        - Session cookie is set
  postconditions:
    - User session is active
    - User can access authorized resources
    - Login attempt is logged in audit trail
  automation_status: Automated
  automation_script: /tests/auth/test_login.py::test_successful_login
```

```yaml
test_case:
  id: TC-AUTH-002
  title: Failed Login with Invalid Password
  priority: High
  type: Functional
  requirement_ref: [FRD-AUTH-001]
  preconditions:
    - User account exists
    - User is not locked out
  test_data:
    - username: testuser@example.com
    - password: WrongPassword123
  steps:
    - step: 1
      action: Navigate to login page
      expected: Login form is displayed
    - step: 2
      action: Enter valid username
      expected: Username is accepted
    - step: 3
      action: Enter invalid password
      expected: Password is masked
    - step: 4
      action: Click 'Login' button
      expected: |
        - Error message: "Invalid username or password"
        - User remains on login page
        - Password field is cleared
        - Failed attempt counter increments
  postconditions:
    - User is not logged in
    - Failed attempt is logged
    - Account lockout counter is incremented
  automation_status: Automated
```

##### Performance Test Cases
```yaml
test_case:
  id: TC-PERF-001
  title: API Response Time Under Normal Load
  priority: High
  type: Performance
  requirement_ref: [NFR-PERF-001.2]
  preconditions:
    - System is deployed in performance environment
    - No other load tests running
    - Monitoring tools are active
  test_data:
    - Concurrent users: 100
    - Request rate: 1000 req/min
    - Test duration: 30 minutes
  steps:
    - step: 1
      action: Configure JMeter with 100 concurrent threads
      expected: JMeter test plan configured
    - step: 2
      action: Start test execution
      expected: Load is generated steadily
    - step: 3
      action: Monitor response times
      expected: |
        - 95th percentile < 200ms
        - 99th percentile < 500ms
        - No errors returned
    - step: 4
      action: Analyze results
      expected: All SLAs are met
  postconditions:
    - Test results are saved
    - System remains stable
    - No memory leaks detected
  automation_status: Automated
  automation_script: /performance/jmeter/normal_load.jmx
```

### 5. Test Execution

#### 5.1 Test Execution Strategy
```yaml
execution_strategy:
  phases:
    - phase: Sprint Testing
      duration: Continuous during sprint
      activities:
        - New feature testing
        - Integration testing
        - Automated regression
      exit_criteria:
        - All stories tested
        - No critical defects
        
    - phase: Release Testing
      duration: 2 weeks before release
      activities:
        - Full regression testing
        - Performance testing
        - Security testing
        - UAT
      exit_criteria:
        - 100% test execution
        - No critical/high defects
        - Performance SLAs met
        - UAT sign-off
```

#### 5.2 Test Execution Tracking
```yaml
tracking:
  metrics:
    - Test cases planned vs executed
    - Pass/fail rates by module
    - Defect discovery rate
    - Test execution velocity
    - Automation percentage
  tools:
    - Test Management: TestRail/Zephyr
    - Defect Tracking: JIRA
    - Automation: Selenium, Pytest
    - Performance: JMeter, Gatling
  reporting:
    - Daily execution status
    - Weekly test summary
    - Release readiness report
```

### 6. Defect Management

#### 6.1 Defect Lifecycle
```yaml
defect_lifecycle:
  states:
    - New: Just discovered
    - Assigned: Assigned to developer
    - In Progress: Being fixed
    - Ready for Test: Fix complete
    - Verified: Fix confirmed
    - Closed: Defect resolved
    - Reopened: Fix failed verification
  
  severity_levels:
    - Critical: System crash, data loss
    - High: Major function broken
    - Medium: Function impaired
    - Low: Minor issue
    
  priority_matrix:
    - P1: Critical severity, fix immediately
    - P2: High severity or critical business impact
    - P3: Medium severity, fix in current release
    - P4: Low severity, fix if time permits
```

#### 6.2 Defect Metrics
```yaml
defect_metrics:
  tracking:
    - Defect density by module
    - Defect discovery rate
    - Defect fix rate
    - Reopen rate
    - Escape rate to production
  goals:
    - Critical defect fix: 24 hours
    - High defect fix: 48 hours
    - Zero critical escapes
    - Reopen rate < 10%
```

### 7. Risk Management

#### 7.1 Testing Risks
```yaml
risks:
  - risk_id: RISK-001
    description: Insufficient test environment availability
    probability: Medium
    impact: High
    mitigation:
      - Containerized environments
      - Environment scheduling
      - Cloud-based alternatives
      
  - risk_id: RISK-002
    description: Test data quality issues
    probability: High
    impact: Medium
    mitigation:
      - Automated data generation
      - Production data sampling
      - Data validation scripts
      
  - risk_id: RISK-003
    description: Late requirement changes
    probability: High
    impact: High
    mitigation:
      - Agile testing approach
      - Automated regression suite
      - Risk-based test prioritization
```

### 8. Test Automation

#### 8.1 Automation Strategy
```yaml
automation_strategy:
  framework: Selenium + Pytest + BDD
  tools:
    ui_testing: Selenium WebDriver
    api_testing: REST Assured / Postman
    unit_testing: JUnit / Jest
    performance: JMeter / Gatling
    mobile: Appium
    
  scope:
    - Regression test suite
    - Smoke tests
    - API contract tests
    - Critical user journeys
    
  maintenance:
    - Page Object Model pattern
    - Reusable components
    - Version control integration
    - CI/CD pipeline integration
```

#### 8.2 Automation Coverage
```yaml
automation_coverage:
  current_state:
    unit_tests: 75%
    integration_tests: 60%
    ui_tests: 40%
    api_tests: 80%
    
  target_state:
    unit_tests: 85%
    integration_tests: 80%
    ui_tests: 70%
    api_tests: 95%
    
  roi_calculation:
    manual_execution_time: 400 hours/release
    automated_execution_time: 40 hours/release
    development_effort: 200 hours
    break_even: 6 months
```

### 9. Entry and Exit Criteria

#### 9.1 Entry Criteria
```yaml
entry_criteria:
  for_testing:
    - Code complete for features
    - Unit tests passing
    - Code deployed to test environment
    - Test data available
    - Test cases reviewed and approved
    
  for_uat:
    - System testing complete
    - No critical/high defects open
    - Performance criteria met
    - Security scan passed
    - Documentation complete
```

#### 9.2 Exit Criteria
```yaml
exit_criteria:
  for_test_phase:
    - All planned tests executed
    - >95% test cases passed
    - No critical defects open
    - <5 high defects open
    - Performance SLAs met
    
  for_release:
    - UAT sign-off received
    - All P1/P2 defects fixed
    - Regression suite passed
    - Security clearance obtained
    - Rollback plan tested
```

### 10. Test Deliverables

```yaml
deliverables:
  documents:
    - Test Plan (this document)
    - Test Case Repository
    - Test Execution Reports
    - Defect Reports
    - Test Summary Report
    - Automation Scripts
    - Performance Test Results
    
  schedule:
    - Test Plan: Sprint 0
    - Test Cases: Ongoing
    - Execution Reports: Daily during testing
    - Summary Report: End of release
```

## Traceability Instructions

1. **Requirement Coverage**: Every requirement must have at least one test case
2. **Test Case IDs**: Use hierarchical numbering linking to requirements
3. **Defect Linking**: Link defects to failed test cases
4. **Automation Mapping**: Track which tests are automated
5. **Risk Coverage**: Ensure high-risk areas have thorough testing

## Quality Criteria

Your Test Plan must:
- Cover all functional and non-functional requirements
- Include positive and negative test scenarios
- Define clear pass/fail criteria
- Address all identified risks
- Be executable within constraints
- Support automation goals
- Enable efficient defect tracking
- Provide measurable quality metrics

## Output Format

Provide the complete Test Plan in Markdown format with:
- Proper YAML frontmatter
- Structured test cases
- Clear execution strategy
- Comprehensive coverage mapping
- Risk mitigation plans
- Automation roadmap
- Measurable exit criteria

## Chain-of-Thought Instructions

When creating the test plan:
1. Analyze all requirements for testability
2. Identify critical user journeys
3. Design test cases for coverage
4. Plan for negative scenarios
5. Consider non-functional testing
6. Define automation strategy
7. Plan test execution phases
8. Set measurable criteria
```

## Iterative Refinement Prompts

### Refinement Round 1: Coverage Analysis
```markdown
Review the test plan and enhance it by:
1. Mapping every requirement to test cases
2. Identifying gaps in test coverage
3. Adding edge case scenarios
4. Ensuring error paths are tested
5. Validating non-functional coverage
```

### Refinement Round 2: Risk-Based Enhancement
```markdown
Refine the test plan by:
1. Prioritizing tests by risk
2. Adding tests for high-risk areas
3. Planning mitigation for test risks
4. Focusing on critical paths
5. Enhancing security test cases
```

### Refinement Round 3: Execution Optimization
```markdown
Enhance the test plan by:
1. Optimizing test execution order
2. Identifying automation candidates
3. Streamlining test data needs
4. Improving defect workflows
5. Clarifying exit criteria

## Iterative Requirements Elicitation

After generating the initial Test Plan Document, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the TEST requirements.

### 9. Client Clarification Questions

Think critically about test strategies, test cases, test environments, test data, automation, and quality assurance that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: TEST-QUESTION-001
category: [Test Strategy|Test Cases|Test Environment|Test Data|Automation|Performance Testing|Security Testing|Other]
question: [Specific question for the client]
rationale: [Why this question is important for TEST success]
related_requirements: [TEST-XXX, FRD-XXX, or NFRD-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect the TEST requirements]
```

#### Question Categories:

**TEST-Specific Questions:**
- Clarifications on testing approaches, test coverage, test environments, and quality metrics
- Edge cases and exception scenarios
- Integration and dependency requirements
- Performance and quality expectations
- Compliance and governance needs

### Instructions for Question Generation:

1. **Be Specific**: Ask precise questions that will yield actionable answers
2. **Prioritize Impact**: Focus on questions that will significantly affect TEST requirements
3. **Consider Edge Cases**: Think about unusual scenarios and exceptions
4. **Validate Assumptions**: Question any assumptions made in the initial requirements
5. **Ensure Completeness**: Look for gaps in testing approaches, test coverage, test environments, and quality metrics
6. **Think Downstream**: Consider how answers will affect implementation
7. **Maintain Traceability**: Link questions to specific requirements when applicable

### Answer Integration Process:

When client answers are received, they should be integrated back into the Test Plan Document using this process:

1. **Create Answer Records**:
```yaml
id: TEST-ANSWER-001
question_id: TEST-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing requirements]
```

2. **Update Affected Requirements**: Modify existing requirements based on answers
3. **Create New Requirements**: Add new requirements identified through answers
4. **Update Traceability**: Ensure all changes maintain proper traceability links
5. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive TEST requirements that address all critical aspects and reduce implementation risks.

```

## Validation Checklist

Before finalizing the Test Plan, ensure:

- [ ] All requirements have test coverage
- [ ] Test cases are clear and reproducible
- [ ] Entry/exit criteria are measurable
- [ ] Test environments are defined
- [ ] Automation strategy is realistic
- [ ] Risk mitigation is planned
- [ ] Defect process is clear
- [ ] Resources are identified
- [ ] Timeline is achievable
- [ ] Traceability is complete

## Pro Tips for LLM Users

1. **Requirements First**: Thoroughly analyze FRD/NFRD before test design
2. **User Journeys**: Focus on critical business paths
3. **Negative Testing**: Don't forget error scenarios
4. **Maintainability**: Design reusable test cases
5. **Automation ROI**: Automate repetitive tests first
6. **Risk Focus**: Prioritize high-risk areas
7. **Clear Criteria**: Make pass/fail unambiguous

## Example Usage

```markdown
Generate a Test Plan using this template with the following context:
- FRD: [Complete functional requirements]
- NFRD: "Performance: <200ms response, Security: OWASP Top 10..."
- PRD: [User stories with acceptance criteria]
- Timeline: "6-week release cycle, 2-week testing window..."
- Team: "5 QA engineers, 3 with automation experience..."
[Continue with all required inputs]