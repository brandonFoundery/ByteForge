"""
Test Plan Split Document Generators
Methods for generating split Test Plan and Test Cases documents
"""

def generate_master_test_plan_doc(content):
    """Generate the master test plan document with links to split documents"""
    return """# Test Plan - FY.WB.Midway Enterprise Logistics Platform

## Overview

This is the master document for the FY.WB.Midway Enterprise Logistics Platform Test Plan. The complete testing strategy and test cases are organized into multiple linked documents for better maintainability and execution tracking.

## Test Objectives

### Primary Objectives
- Verify all functional requirements are correctly implemented
- Validate non-functional requirements are met
- Ensure system reliability and stability under load
- Identify defects before production release
- Achieve comprehensive test coverage

### Quality Goals
- **Requirement Coverage**: 100% of critical and high-priority requirements
- **Code Coverage**: >80% for unit tests
- **Critical Defect Escape Rate**: 0%
- **Test Automation**: >70% of regression tests
- **Performance SLA**: Meet all NFR-PERF requirements

## Document Structure

The complete test plan is organized into the following documents:

### Test Strategy and Planning
- **[Test Strategy](./test_strategy.md)** - Overall testing approach, levels, and methodology

### Test Cases by Category
- **[Functional Test Cases](./test_cases_functional.md)** - Core business functionality testing
- **[Performance Test Cases](./test_cases_performance.md)** - Load, stress, and performance testing
- **[Security Test Cases](./test_cases_security.md)** - Security and compliance testing

### Test Automation
- **[Test Automation Framework](./test_automation.md)** - Automation strategy, tools, and scripts

## Test Scope

### In Scope
- **Customer Management**: Registration, profile management, KYC
- **Payment Processing**: Secure payment transactions, PCI compliance
- **Load Management**: Booking, tracking, optimization
- **Invoice Processing**: Generation, reporting, financial operations
- **Carrier Management**: Registration, self-service portal
- **Security**: Authentication, authorization, data protection
- **Performance**: Response times, throughput, scalability
- **Integration**: API contracts, service communication

### Out of Scope
- Legacy system testing (except integration points)
- Third-party service internal testing
- Hardware compatibility testing
- Localization testing (Phase 2)

## Test Environment Strategy

### Environment Types
- **Development**: Developer testing and debugging
- **QA**: Functional and integration testing
- **Staging**: User acceptance and performance testing
- **Production**: Limited production validation

## Risk Assessment

### High-Risk Areas
- **Payment Processing**: Financial transactions, PCI compliance
- **Data Security**: Customer PII, financial data protection
- **Integration Points**: External service dependencies
- **Performance**: High-load scenarios, scalability limits

## Success Criteria

### Release Readiness
- All critical and high-priority test cases passed
- No critical or high-severity defects open
- Performance SLAs met in staging environment
- Security testing completed with no critical findings
- User acceptance testing sign-off received

## Navigation

- [← Back to Requirements](../Requirements/)
- [Test Strategy →](./test_strategy.md)
- [Functional Test Cases →](./test_cases_functional.md)

## Traceability Matrix

| Document | Requirements Covered | Test Types |
|----------|---------------------|------------|
| [Test Strategy](./test_strategy.md) | All requirements | Strategy, approach, methodology |
| [Functional Test Cases](./test_cases_functional.md) | FRD-*, PRD-* | Functional, integration, user acceptance |
| [Performance Test Cases](./test_cases_performance.md) | NFR-PERF-*, NFR-SCALE-* | Load, stress, volume, endurance |
| [Security Test Cases](./test_cases_security.md) | NFR-SEC-*, Compliance | Security, penetration, compliance |
| [Test Automation](./test_automation.md) | All automated tests | Unit, integration, regression, API |
"""

def generate_test_strategy_doc(content):
    """Generate the test strategy document"""
    return """# Test Strategy and Approach

## Testing Methodology

### Agile Testing Approach
- **Shift-Left Testing**: Early testing in development cycle
- **Continuous Testing**: Automated testing in CI/CD pipeline
- **Risk-Based Testing**: Focus on high-risk areas
- **Exploratory Testing**: Unscripted testing for edge cases
- **Collaborative Testing**: Cross-functional team involvement

## Test Levels

### Unit Testing
- **Responsibility**: Development Team
- **Coverage Target**: 80% code coverage
- **Automation**: 100% automated
- **Tools**: JUnit, Mockito, Jest
- **Execution**: Every code commit

### Integration Testing
- **Responsibility**: QA Team with Dev support
- **Coverage Target**: 100% of service interfaces
- **Automation**: 80% automated
- **Tools**: TestContainers, Postman, REST Assured
- **Execution**: Daily automated runs

### System Testing
- **Responsibility**: QA Team
- **Coverage Target**: 100% of functional requirements
- **Automation**: 70% automated
- **Tools**: Selenium, Cypress, API testing tools
- **Execution**: Sprint-based testing cycles

### User Acceptance Testing
- **Responsibility**: Business Users + QA
- **Coverage Target**: 100% of user stories
- **Automation**: 30% automated
- **Tools**: Manual testing, BDD frameworks
- **Execution**: Pre-release validation

## Test Types

### Functional Testing
- **Smoke Testing**: Basic functionality verification
- **Regression Testing**: Ensure existing functionality works
- **End-to-End Testing**: Complete user workflows
- **API Testing**: Service contract validation
- **Database Testing**: Data integrity and CRUD operations

### Non-Functional Testing
- **Performance Testing**: Load, stress, volume testing
- **Security Testing**: Vulnerability and penetration testing
- **Usability Testing**: User experience validation
- **Compatibility Testing**: Browser and device compatibility
- **Accessibility Testing**: WCAG compliance

### Specialized Testing
- **Chaos Engineering**: Fault tolerance testing
- **Disaster Recovery Testing**: Backup and recovery validation
- **Compliance Testing**: Regulatory requirement validation
- **Data Migration Testing**: Legacy data migration validation

## Test Design Techniques

### Black Box Techniques
- **Equivalence Partitioning**: Input domain partitioning
- **Boundary Value Analysis**: Edge case testing
- **Decision Table Testing**: Complex business rule testing
- **State Transition Testing**: Workflow and state testing
- **Use Case Testing**: User scenario testing

### White Box Techniques
- **Statement Coverage**: Code line execution
- **Branch Coverage**: Decision point testing
- **Path Coverage**: Execution path testing
- **Condition Coverage**: Boolean expression testing

## Test Data Management

### Test Data Strategy
- **Synthetic Data**: Generated test data for development
- **Production-Like Data**: Anonymized production data for staging
- **Edge Case Data**: Boundary and error condition data
- **Volume Data**: Large datasets for performance testing

### Data Privacy and Security
- **Data Masking**: PII anonymization
- **Data Retention**: Automated cleanup policies
- **Access Control**: Role-based data access
- **Compliance**: GDPR and PCI DSS requirements

## Defect Management

### Defect Lifecycle
1. **Discovery**: Defect identification and logging
2. **Triage**: Priority and severity assignment
3. **Assignment**: Developer assignment
4. **Resolution**: Fix implementation
5. **Verification**: Fix validation
6. **Closure**: Defect closure

### Severity and Priority Matrix
- **Critical/P1**: System crash, data loss, security breach
- **High/P2**: Major functionality broken, performance issues
- **Medium/P3**: Minor functionality issues, usability problems
- **Low/P4**: Cosmetic issues, enhancement requests

## Test Automation Strategy

### Automation Pyramid
- **Unit Tests**: 70% of total tests
- **Integration Tests**: 20% of total tests
- **UI Tests**: 10% of total tests

### Automation Tools
- **API Testing**: REST Assured, Postman/Newman
- **Web UI Testing**: Selenium WebDriver, Cypress
- **Mobile Testing**: Appium
- **Performance Testing**: JMeter, Gatling
- **Security Testing**: OWASP ZAP, Burp Suite

### Automation Framework
- **Page Object Model**: UI test maintainability
- **Data-Driven Testing**: External test data sources
- **Keyword-Driven Testing**: Business-readable tests
- **BDD Framework**: Cucumber for acceptance tests

## Navigation

- [← Back to Master Document](./test_plan.md)
- [Functional Test Cases →](./test_cases_functional.md)
- [Performance Test Cases →](./test_cases_performance.md)
"""

def generate_functional_test_cases_doc(content):
    """Generate the functional test cases document"""
    return """# Functional Test Cases

## Test Case Template

```yaml
test_case:
  id: TC-[Module]-[Number]
  title: [Test Case Title]
  priority: Critical|High|Medium|Low
  type: Functional|Integration|E2E
  requirement_ref: [FRD-XXX, PRD-US-XXX]
  preconditions: [List of preconditions]
  test_data: [Required test data]
  steps: [Detailed test steps]
  expected_results: [Expected outcomes]
  postconditions: [System state after test]
  automation_status: Manual|Automated|Planned
```

## Authentication Module Test Cases

### TC-AUTH-001: Successful User Login
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
    1. Navigate to login page
    2. Enter valid username
    3. Enter valid password
    4. Click 'Login' button
  expected_results:
    - User is redirected to dashboard
    - User name appears in header
    - Session cookie is set
    - Login attempt is logged
  postconditions:
    - User session is active
    - User can access authorized resources
  automation_status: Automated
```

### TC-AUTH-002: Failed Login with Invalid Password
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
    1. Navigate to login page
    2. Enter valid username
    3. Enter invalid password
    4. Click 'Login' button
  expected_results:
    - Error message: "Invalid username or password"
    - User remains on login page
    - Password field is cleared
    - Failed attempt counter increments
  postconditions:
    - User is not logged in
    - Failed attempt is logged
  automation_status: Automated
```

## Customer Management Test Cases

### TC-CUST-001: Customer Registration
```yaml
test_case:
  id: TC-CUST-001
  title: New Customer Registration
  priority: Critical
  type: Functional
  requirement_ref: [FRD-CUST-001, PRD-US-002]
  preconditions:
    - Registration page is accessible
    - Email address is not already registered
  test_data:
    - company_name: "Test Logistics Inc"
    - email: "test@testlogistics.com"
    - phone: "+1-555-123-4567"
    - address: "123 Test Street, Test City, TS 12345"
  steps:
    1. Navigate to customer registration page
    2. Fill in company information
    3. Enter contact details
    4. Upload required documents
    5. Submit registration form
  expected_results:
    - Registration confirmation message displayed
    - Verification email sent
    - Customer record created in database
    - KYC workflow initiated
  postconditions:
    - Customer status is 'PENDING_VERIFICATION'
    - Welcome email is sent
  automation_status: Automated
```

## Payment Processing Test Cases

### TC-PAY-001: Credit Card Payment Processing
```yaml
test_case:
  id: TC-PAY-001
  title: Process Credit Card Payment
  priority: Critical
  type: Functional
  requirement_ref: [FRD-PAY-001, NFR-SEC-001]
  preconditions:
    - User is logged in
    - Valid payment method is available
    - Invoice exists and is unpaid
  test_data:
    - card_number: "4111111111111111" (test card)
    - expiry_date: "12/25"
    - cvv: "123"
    - amount: "$1,250.00"
  steps:
    1. Navigate to payment page
    2. Select invoice to pay
    3. Enter credit card details
    4. Confirm payment amount
    5. Submit payment
  expected_results:
    - Payment processing confirmation
    - Transaction ID generated
    - Invoice status updated to 'PAID'
    - Payment confirmation email sent
  postconditions:
    - Payment record created
    - Audit trail logged
  automation_status: Automated
```

## Load Management Test Cases

### TC-LOAD-001: Load Booking
```yaml
test_case:
  id: TC-LOAD-001
  title: Book New Load
  priority: Critical
  type: Functional
  requirement_ref: [FRD-LOAD-001, PRD-US-003]
  preconditions:
    - Customer is logged in
    - Customer account is verified
    - Route is available
  test_data:
    - pickup_location: "Chicago, IL"
    - delivery_location: "Dallas, TX"
    - pickup_date: "2025-07-01"
    - load_type: "Full Truckload"
    - weight: "45,000 lbs"
  steps:
    1. Navigate to load booking page
    2. Enter pickup and delivery details
    3. Select load specifications
    4. Choose preferred carrier (if any)
    5. Submit booking request
  expected_results:
    - Load booking confirmation
    - Load ID generated
    - Carrier matching initiated
    - Booking confirmation email sent
  postconditions:
    - Load status is 'BOOKED'
    - Carrier notification sent
  automation_status: Automated
```

### TC-LOAD-002: Real-time Load Tracking
```yaml
test_case:
  id: TC-LOAD-002
  title: Track Load Status in Real-time
  priority: High
  type: Functional
  requirement_ref: [FRD-LOAD-002]
  preconditions:
    - Load is booked and in transit
    - GPS tracking is enabled
    - User has access to load
  test_data:
    - load_id: "LD-2025-001234"
  steps:
    1. Navigate to load tracking page
    2. Enter load ID
    3. View current location
    4. Check status updates
    5. View estimated delivery time
  expected_results:
    - Current location displayed on map
    - Status shows 'IN_TRANSIT'
    - ETA is calculated and displayed
    - Recent status updates visible
  postconditions:
    - Tracking data is logged
    - Customer notification sent if delayed
  automation_status: Automated
```

## Invoice Processing Test Cases

### TC-INV-001: Automated Invoice Generation
```yaml
test_case:
  id: TC-INV-001
  title: Generate Invoice for Completed Load
  priority: Critical
  type: Functional
  requirement_ref: [FRD-INV-001, PRD-US-004]
  preconditions:
    - Load is completed and delivered
    - Delivery confirmation received
    - Pricing information is available
  test_data:
    - load_id: "LD-2025-001234"
    - base_rate: "$2,500.00"
    - fuel_surcharge: "$125.00"
    - additional_fees: "$75.00"
  steps:
    1. Load completion triggers invoice generation
    2. System calculates total charges
    3. Invoice is generated automatically
    4. Invoice is sent to customer
    5. Payment due date is set
  expected_results:
    - Invoice PDF generated
    - Invoice number assigned
    - Customer receives invoice email
    - Payment tracking initiated
  postconditions:
    - Invoice status is 'SENT'
    - Payment reminder scheduled
  automation_status: Automated
```

## Navigation

- [← Back to Master Document](./test_plan.md)
- [← Test Strategy](./test_strategy.md)
- [Performance Test Cases →](./test_cases_performance.md)
"""
