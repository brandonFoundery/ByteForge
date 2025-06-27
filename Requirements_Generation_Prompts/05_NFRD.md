# Non-Functional Requirements Document (NFRD) - Prompt Template

## Primary Prompt

```markdown
You are an expert Systems Architect and Quality Analyst with extensive experience defining Non-Functional Requirements (NFRs) for enterprise systems. You excel at translating quality attributes, performance expectations, and operational constraints into measurable, testable specifications.

## Your Task

Generate a complete Non-Functional Requirements Document (NFRD) for [PROJECT NAME] based on the provided context and quality expectations.

## Input Context Required

1. **Product Requirements Document**: [Provide PRD for product vision and goals]
2. **Functional Requirements Document**: [Provide FRD for functional context]
3. **Business Requirements Document**: [Provide BRD for business constraints]
4. **Technical Constraints**: [Infrastructure, platform limitations]
5. **Compliance Requirements**: [Industry standards, regulations]
6. **Service Level Agreements**: [If available]

## Document Structure Requirements

Your NFRD must include the following sections with YAML frontmatter:

```yaml
---
id: NFRD
title: Non-Functional Requirements Document - [PROJECT NAME]
version: 1.0
status: Draft
created_by: [Your Name]
created_on: YYYY-MM-DD
last_updated: YYYY-MM-DD
upstream: [PRD, FRD, BRD, Compliance Docs]
downstream: [TRD, Test Plans, SLA Documents]
tags: [non-functional-requirements, quality-attributes, performance, security]
---
```

### 1. Introduction
#### 1.1 Purpose
- Document objectives and scope
- Relationship to functional requirements
- Target audience

#### 1.2 NFR Categories
- Performance
- Security
- Usability
- Reliability
- Scalability
- Maintainability
- Portability
- Compliance

#### 1.3 Measurement Approach
- How NFRs will be validated
- Testing methodologies
- Monitoring strategies

### 2. Performance Requirements

#### 2.1 Response Time Requirements
```yaml
id: NFR-PERF-001
category: Performance
title: System Response Time
description: Maximum acceptable response times for system operations
priority: Critical
requirements:
  - id: NFR-PERF-001.1
    operation: Page Load Time
    target: ≤ 2 seconds
    percentile: 95th percentile
    conditions: Normal load conditions
    measurement_method: Synthetic monitoring
    degradation_threshold: 3 seconds
    source_requirement: [PRD-GOAL-XXX]
    
  - id: NFR-PERF-001.2
    operation: API Response Time
    target: ≤ 200ms
    percentile: 99th percentile
    conditions: For simple queries
    measurement_method: APM tools
    degradation_threshold: 500ms
    
  - id: NFR-PERF-001.3
    operation: Complex Report Generation
    target: ≤ 30 seconds
    percentile: 90th percentile
    conditions: Reports up to 10,000 records
    measurement_method: Application logging
```

#### 2.2 Throughput Requirements
```yaml
id: NFR-PERF-002
category: Performance
title: System Throughput
description: Transaction processing capacity requirements
priority: High
requirements:
  - id: NFR-PERF-002.1
    metric: Concurrent Users
    target: 10,000 simultaneous users
    sustained_period: 8 hours
    peak_multiplier: 2x (20,000 users)
    
  - id: NFR-PERF-002.2
    metric: Transactions Per Second
    target: 1,000 TPS
    transaction_type: Order processing
    sustained_period: Continuous
    peak_target: 5,000 TPS
    
  - id: NFR-PERF-002.3
    metric: Data Processing Rate
    target: 100,000 records/minute
    operation: Batch processing
    parallel_streams: 10
```

#### 2.3 Resource Utilization
```yaml
id: NFR-PERF-003
category: Performance
title: Resource Efficiency
description: System resource utilization limits
requirements:
  - CPU Utilization: ≤ 70% average, ≤ 90% peak
  - Memory Usage: ≤ 80% of allocated
  - Database Connections: ≤ 80% of pool
  - Network Bandwidth: ≤ 60% of available
monitoring: Real-time dashboards with alerts
```

### 3. Security Requirements

#### 3.1 Authentication and Authorization
```yaml
id: NFR-SEC-001
category: Security
title: Authentication Requirements
description: User authentication and session management
priority: Critical
requirements:
  - id: NFR-SEC-001.1
    requirement: Multi-Factor Authentication
    description: MFA required for all administrative access
    implementation: TOTP, SMS, or biometric
    compliance: NIST 800-63B
    
  - id: NFR-SEC-001.2
    requirement: Password Policy
    description: Enforce strong password requirements
    rules:
      - Minimum 12 characters
      - Mix of uppercase, lowercase, numbers, symbols
      - No dictionary words
      - No reuse of last 12 passwords
      - Expiry: 90 days for privileged accounts
    
  - id: NFR-SEC-001.3
    requirement: Session Management
    description: Secure session handling
    specifications:
      - Session timeout: 30 minutes idle
      - Absolute timeout: 8 hours
      - Secure session tokens (cryptographically random)
      - Session invalidation on logout
```

#### 3.2 Data Security
```yaml
id: NFR-SEC-002
category: Security
title: Data Protection Requirements
description: Data encryption and protection standards
priority: Critical
requirements:
  - id: NFR-SEC-002.1
    requirement: Encryption at Rest
    standard: AES-256
    scope: All sensitive data
    key_management: HSM-based key storage
    
  - id: NFR-SEC-002.2
    requirement: Encryption in Transit
    standard: TLS 1.3 minimum
    certificate: EV SSL certificates
    cipher_suites: AEAD ciphers only
    
  - id: NFR-SEC-002.3
    requirement: Data Masking
    scope: PII in non-production environments
    method: Format-preserving encryption
    exceptions: None
```

#### 3.3 Security Monitoring
```yaml
id: NFR-SEC-003
category: Security
title: Security Monitoring and Audit
description: Security event monitoring and response
requirements:
  - SIEM integration for all security events
  - Real-time threat detection
  - Automated incident response for common threats
  - Security audit logs retained for 2 years
  - Quarterly penetration testing
  - Annual security audits
```

### 4. Usability Requirements

#### 4.1 User Experience Standards
```yaml
id: NFR-USE-001
category: Usability
title: User Interface Standards
description: UI/UX requirements for optimal user experience
priority: High
requirements:
  - id: NFR-USE-001.1
    requirement: Responsive Design
    description: Support multiple device types
    breakpoints:
      - Mobile: 320px - 768px
      - Tablet: 768px - 1024px
      - Desktop: 1024px+
    testing: Cross-browser compatibility
    
  - id: NFR-USE-001.2
    requirement: Page Load Perception
    description: Optimize perceived performance
    techniques:
      - Progressive rendering
      - Lazy loading for images
      - Skeleton screens
      - Optimistic UI updates
```

#### 4.2 Accessibility Requirements
```yaml
id: NFR-USE-002
category: Usability
title: Accessibility Standards
description: Ensure system accessibility for all users
priority: High
compliance: WCAG 2.1 Level AA
requirements:
  - Keyboard navigation for all functions
  - Screen reader compatibility
  - Color contrast ratio ≥ 4.5:1
  - Alternative text for all images
  - Captions for video content
  - Form labels and error messages
  - Focus indicators
testing_tools:
  - WAVE
  - axe DevTools
  - NVDA/JAWS testing
```

#### 4.3 User Efficiency
```yaml
id: NFR-USE-003
category: Usability
title: User Productivity Requirements
description: Enable efficient user task completion
requirements:
  - Maximum 3 clicks to any function
  - Keyboard shortcuts for frequent actions
  - Bulk operations support
  - Auto-save for data entry
  - Smart defaults and suggestions
  - Context-sensitive help
metrics:
  - Task completion time
  - Error rate
  - User satisfaction score
```

### 5. Reliability Requirements

#### 5.1 Availability Requirements
```yaml
id: NFR-REL-001
category: Reliability
title: System Availability
description: Uptime and availability targets
priority: Critical
requirements:
  - id: NFR-REL-001.1
    metric: Overall Availability
    target: 99.9% (three nines)
    measurement_period: Monthly
    allowed_downtime: 43.2 minutes/month
    exclusions: Scheduled maintenance windows
    
  - id: NFR-REL-001.2
    metric: Core Service Availability
    services: [Authentication, Payment Processing]
    target: 99.99% (four nines)
    measurement_period: Monthly
    allowed_downtime: 4.32 minutes/month
```

#### 5.2 Fault Tolerance
```yaml
id: NFR-REL-002
category: Reliability
title: Fault Tolerance and Recovery
description: System resilience requirements
requirements:
  - id: NFR-REL-002.1
    requirement: Automatic Failover
    description: Seamless failover for critical components
    failover_time: ≤ 30 seconds
    data_loss: Zero (RPO = 0)
    
  - id: NFR-REL-002.2
    requirement: Graceful Degradation
    description: Maintain core functions during partial failures
    degraded_features: [Reports, Analytics, Batch Jobs]
    protected_features: [Auth, Transactions, Data Access]
```

#### 5.3 Backup and Recovery
```yaml
id: NFR-REL-003
category: Reliability
title: Backup and Disaster Recovery
description: Data protection and recovery capabilities
requirements:
  - RPO (Recovery Point Objective): 15 minutes
  - RTO (Recovery Time Objective): 2 hours
  - Backup frequency: Continuous replication
  - Backup retention: 30 days online, 1 year archive
  - DR testing: Quarterly
  - Geo-redundancy: Minimum 100 miles separation
```

### 6. Scalability Requirements

#### 6.1 Vertical Scalability
```yaml
id: NFR-SCALE-001
category: Scalability
title: Vertical Scaling Capabilities
description: System ability to scale up
requirements:
  - CPU scaling: Up to 64 cores
  - Memory scaling: Up to 512GB RAM
  - Storage scaling: Expandable to 100TB
  - Performance linearity: 80% efficiency
```

#### 6.2 Horizontal Scalability
```yaml
id: NFR-SCALE-002
category: Scalability
title: Horizontal Scaling Capabilities
description: System ability to scale out
requirements:
  - Auto-scaling triggers:
    - CPU > 70%
    - Memory > 80%
    - Request queue > 100
  - Scale-out time: ≤ 5 minutes
  - Scale-in time: ≤ 10 minutes
  - Maximum instances: 100
  - Load distribution: Round-robin with health checks
```

#### 6.3 Data Scalability
```yaml
id: NFR-SCALE-003
category: Scalability
title: Data Growth Management
description: Database and storage scalability
requirements:
  - Database sharding capability
  - Partition strategy by date/tenant
  - Archive strategy for old data
  - Query performance maintained up to 10TB
  - Index optimization automation
```

### 7. Maintainability Requirements

#### 7.1 Code Maintainability
```yaml
id: NFR-MAINT-001
category: Maintainability
title: Code Quality Standards
description: Software maintainability requirements
requirements:
  - Code coverage: ≥ 80%
  - Cyclomatic complexity: ≤ 10
  - Technical debt ratio: < 5%
  - Documentation coverage: 100% public APIs
  - Code review: 100% of changes
tools:
  - Static analysis: SonarQube
  - Code formatting: Prettier/ESLint
  - Documentation: JSDoc/Swagger
```

#### 7.2 System Monitoring
```yaml
id: NFR-MAINT-002
category: Maintainability
title: Observability Requirements
description: System monitoring and diagnostics
requirements:
  - Application Performance Monitoring (APM)
  - Distributed tracing for all requests
  - Centralized logging with correlation IDs
  - Real-time metrics dashboards
  - Alerting with escalation
  - Synthetic monitoring for key flows
```

#### 7.3 Deployment Requirements
```yaml
id: NFR-MAINT-003
category: Maintainability
title: Deployment and Updates
description: System deployment capabilities
requirements:
  - Zero-downtime deployments
  - Blue-green deployment support
  - Rollback capability: ≤ 5 minutes
  - Automated deployment pipeline
  - Feature flags for gradual rollout
  - Database migration automation
```

### 8. Portability Requirements

```yaml
id: NFR-PORT-001
category: Portability
title: Platform Independence
description: System portability across platforms
requirements:
  - Cloud provider agnostic design
  - Container-based deployment (Docker)
  - Kubernetes orchestration support
  - Database abstraction layer
  - External service abstraction
  - Configuration externalization
supported_platforms:
  - AWS, Azure, GCP
  - On-premise deployment option
  - Hybrid cloud support
```

### 9. Compliance Requirements

```yaml
id: NFR-COMP-001
category: Compliance
title: Regulatory Compliance
description: Legal and regulatory requirements
priority: Critical
regulations:
  - id: NFR-COMP-001.1
    regulation: GDPR
    requirements:
      - Right to be forgotten
      - Data portability
      - Consent management
      - Privacy by design
      
  - id: NFR-COMP-001.2
    regulation: PCI-DSS Level 1
    requirements:
      - Secure network architecture
      - Cardholder data protection
      - Vulnerability management
      - Access control measures
      
  - id: NFR-COMP-001.3
    regulation: SOX
    requirements:
      - Financial data integrity
      - Audit trail completeness
      - Change management controls
      - Segregation of duties
```

### 10. Capacity Requirements

```yaml
id: NFR-CAP-001
category: Capacity
title: System Capacity Planning
description: Expected system load and growth
current_state:
  users: 10,000
  transactions_daily: 1,000,000
  data_volume: 1TB
growth_projection:
  year_1: 50% increase
  year_3: 200% increase
  year_5: 500% increase
capacity_targets:
  users: 100,000
  transactions_daily: 10,000,000
  data_volume: 50TB
  concurrent_sessions: 50,000
```

## Traceability Instructions

1. **Link to Business Goals**: Connect NFRs to business objectives from BRD
2. **Reference Functional Context**: Note which FRD functions require these NFRs
3. **Unique IDs**: Use hierarchical numbering (NFR-CAT-001.1)
4. **Measurable Targets**: Every NFR must have quantifiable acceptance criteria
5. **Verification Method**: Specify how each NFR will be tested/validated

## Quality Criteria

Your NFRD must:
- Define measurable, testable requirements
- Include specific target values and thresholds
- Cover all quality attribute categories
- Specify monitoring and measurement methods
- Address compliance and regulatory needs
- Consider growth and scalability
- Be achievable within project constraints
- Support business objectives

## Output Format

Provide the complete NFRD in Markdown format with:
- Proper YAML frontmatter
- Categorized requirements sections
- YAML blocks for detailed specifications
- Clear acceptance criteria
- Measurement methods
- Priority assignments
- Traceability references

## Chain-of-Thought Instructions

When creating NFRs:
1. Review business goals and constraints
2. Analyze functional requirements for quality needs
3. Consider user expectations and SLAs
4. Define measurable targets
5. Ensure testability
6. Plan for monitoring
7. Address all quality attributes
8. Validate against constraints

## Iterative Requirements Elicitation

After generating the initial Non-Functional Requirements Document, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the NFRD requirements.

### 11. Client Clarification Questions

Think critically about performance criteria, security requirements, usability standards, reliability expectations, scalability needs, and compliance obligations that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: NFRD-QUESTION-001
category: [Performance|Security|Usability|Reliability|Scalability|Compliance|Maintainability|Portability|Other]
question: [Specific question for the client]
rationale: [Why this question is critical for NFRD success]
related_requirements: [NFR-XXX-XXX, FRD-XXX, or PRD-FEAT-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect system quality attributes or implementation]
```

#### Question Categories:

**Performance Questions:**
- Response time expectations for different user scenarios
- Peak load definitions and seasonal variations
- Performance degradation acceptance thresholds
- Resource utilization limits and monitoring
- Caching strategy requirements

**Security Questions:**
- Specific compliance standards and audit requirements
- Data classification and protection levels
- Authentication method preferences
- Incident response procedures
- Security monitoring and alerting needs

**Usability Questions:**
- Accessibility requirements and user groups
- Browser and device support priorities
- User training and onboarding expectations
- Error message and help system requirements
- Internationalization and localization needs

**Reliability Questions:**
- Acceptable downtime windows and maintenance schedules
- Disaster recovery expectations and testing frequency
- Data backup and retention requirements
- Failover and redundancy expectations
- Service level agreement definitions

**Scalability Questions:**
- Growth projections and capacity planning
- Auto-scaling triggers and thresholds
- Geographic distribution requirements
- Load balancing preferences
- Database scaling strategies

**Compliance Questions:**
- Regulatory requirements and audit schedules
- Data retention and deletion policies
- Privacy requirements and consent management
- Industry-specific standards
- Certification requirements

**Maintainability Questions:**
- Deployment frequency and rollback requirements
- Monitoring and alerting preferences
- Code quality standards and tools
- Documentation requirements
- Support and maintenance procedures

**Portability Questions:**
- Cloud provider preferences and constraints
- On-premise deployment requirements
- Container and orchestration preferences
- Database and technology stack flexibility
- Migration and integration requirements

### Instructions for Question Generation:

1. **Focus on Measurability**: Ask questions that will lead to specific, quantifiable requirements
2. **Consider Trade-offs**: Identify potential conflicts between quality attributes
3. **Think Operationally**: Consider how requirements will be monitored and maintained
4. **Validate Assumptions**: Question assumptions about user expectations and system constraints
5. **Consider Growth**: Think about how requirements will scale with business growth
6. **Plan for Failures**: Ask about acceptable failure modes and recovery expectations
7. **Ensure Testability**: Questions should lead to testable and verifiable requirements
8. **Link to Business Value**: Connect quality attributes to business objectives and costs

### Answer Integration Process:

When client answers are received, they should be integrated back into the NFRD using this process:

1. **Create Answer Records**:
```yaml
id: NFRD-ANSWER-001
question_id: NFRD-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing non-functional requirements]
```

2. **Update Affected Requirements**: Modify existing NFRs based on answers
3. **Create New Requirements**: Add new non-functional requirements identified through answers
4. **Refine Metrics**: Update measurement criteria and acceptance thresholds
5. **Update Priorities**: Adjust requirement priorities based on business importance
6. **Update Compliance**: Add or modify compliance requirements as needed
7. **Update Traceability**: Ensure all changes maintain proper traceability links
8. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive non-functional requirements that address all quality attributes and support successful system implementation and operation.
```

## Iterative Refinement Prompts

### Refinement Round 1: Measurability
```markdown
Review the NFRD and enhance it by:
1. Ensuring all requirements have quantifiable metrics
2. Adding specific measurement methods
3. Defining clear pass/fail criteria
4. Including monitoring approaches
5. Specifying testing procedures
```

### Refinement Round 2: Completeness
```markdown
Refine the NFRD by:
1. Checking coverage of all quality attributes
2. Adding missing compliance requirements
3. Including operational requirements
4. Addressing edge cases and failures
5. Ensuring scalability considerations
```

### Refinement Round 3: Feasibility
```markdown
Enhance the NFRD by:
1. Validating targets against constraints
2. Adjusting unrealistic requirements
3. Prioritizing conflicting requirements
4. Adding cost-benefit considerations
5. Including implementation guidance
```

## Validation Checklist

Before finalizing the NFRD, ensure:

- [ ] All NFR categories are addressed
- [ ] Every requirement is measurable
- [ ] Targets are specific and achievable
- [ ] Verification methods are defined
- [ ] Priorities reflect business importance
- [ ] Compliance requirements are complete
- [ ] Performance targets consider growth
- [ ] Security covers all threat vectors
- [ ] Usability addresses all user groups
- [ ] Monitoring strategy is comprehensive

## Pro Tips for LLM Users

1. **Business Context**: Understand business drivers for quality attributes
2. **Be Specific**: Avoid vague terms like "fast" or "secure"
3. **Consider Trade-offs**: Performance vs. Security vs. Cost
4. **Think Testing**: If you can't test it, redefine it
5. **Plan for Growth**: Design for 5-10x current scale
6. **User Focus**: Consider impact on user experience
7. **Operational View**: Include DevOps requirements

## Example Usage

```markdown
Generate an NFRD using this template with the following context:
- PRD: "E-commerce platform handling financial transactions..."
- FRD: "Payment processing, user management, reporting..."
- Compliance: "PCI-DSS Level 1, GDPR, SOX required..."
- Current Load: "10K users, 100K transactions daily..."
- Growth: "Expecting 10x growth in 2 years..."
[Continue with all required inputs]