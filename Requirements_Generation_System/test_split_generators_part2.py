"""
Test Plan Split Document Generators - Part 2
Additional methods for generating test case documents
"""

def generate_performance_test_cases_doc(content):
    """Generate the performance test cases document"""
    return """# Performance Test Cases

## Performance Testing Strategy

### Test Types
- **Load Testing**: Normal expected load
- **Stress Testing**: Beyond normal capacity
- **Spike Testing**: Sudden load increases
- **Volume Testing**: Large amounts of data
- **Endurance Testing**: Extended periods

## API Performance Test Cases

### TC-PERF-001: API Response Time Under Normal Load
```yaml
test_case:
  id: TC-PERF-001
  title: API Response Time Under Normal Load
  priority: High
  type: Performance
  requirement_ref: [NFR-PERF-001]
  preconditions:
    - System is deployed in performance environment
    - No other load tests running
    - Monitoring tools are active
  test_data:
    - concurrent_users: 100
    - request_rate: 1000 req/min
    - test_duration: 30 minutes
  test_steps:
    1. Configure JMeter with 100 concurrent threads
    2. Start test execution
    3. Monitor response times
    4. Analyze results
  expected_results:
    - 95th percentile < 200ms
    - 99th percentile < 500ms
    - No errors returned
    - System remains stable
  postconditions:
    - Test results are saved
    - No memory leaks detected
  automation_status: Automated
  automation_script: /performance/jmeter/normal_load.jmx
```

### TC-PERF-002: Database Performance Under Load
```yaml
test_case:
  id: TC-PERF-002
  title: Database Query Performance
  priority: High
  type: Performance
  requirement_ref: [NFR-PERF-002]
  preconditions:
    - Database is populated with test data
    - Performance monitoring enabled
  test_data:
    - concurrent_connections: 50
    - query_types: [SELECT, INSERT, UPDATE]
    - test_duration: 15 minutes
  test_steps:
    1. Execute concurrent database operations
    2. Monitor query execution times
    3. Check connection pool utilization
    4. Analyze slow query logs
  expected_results:
    - Average query time < 100ms
    - No connection pool exhaustion
    - No deadlocks detected
  automation_status: Automated
```

## Load Testing Scenarios

### TC-PERF-003: Peak Load Simulation
```yaml
test_case:
  id: TC-PERF-003
  title: System Performance at Peak Load
  priority: Critical
  type: Load Testing
  requirement_ref: [NFR-SCALE-001]
  preconditions:
    - Production-like environment
    - Full dataset loaded
  test_data:
    - concurrent_users: 1000
    - ramp_up_time: 10 minutes
    - test_duration: 60 minutes
  test_steps:
    1. Gradually increase load to 1000 users
    2. Maintain peak load for 60 minutes
    3. Monitor all system metrics
    4. Verify auto-scaling behavior
  expected_results:
    - System handles 1000 concurrent users
    - Auto-scaling triggers appropriately
    - Response times within SLA
    - No system failures
  automation_status: Automated
```

### TC-PERF-004: Stress Testing Beyond Capacity
```yaml
test_case:
  id: TC-PERF-004
  title: System Behavior Beyond Normal Capacity
  priority: High
  type: Stress Testing
  requirement_ref: [NFR-SCALE-002]
  preconditions:
    - System at baseline performance
    - Monitoring and alerting active
  test_data:
    - max_users: 2000
    - ramp_up_time: 5 minutes
    - test_duration: 30 minutes
  test_steps:
    1. Rapidly increase load beyond capacity
    2. Monitor system degradation
    3. Verify graceful degradation
    4. Test recovery after load reduction
  expected_results:
    - System degrades gracefully
    - No data corruption
    - Quick recovery after load reduction
    - Appropriate error messages
  automation_status: Automated
```

## Navigation

- [← Back to Master Document](./test_plan.md)
- [← Functional Test Cases](./test_cases_functional.md)
- [Security Test Cases →](./test_cases_security.md)
"""

def generate_security_test_cases_doc(content):
    """Generate the security test cases document"""
    return """# Security Test Cases

## Security Testing Strategy

### Test Categories
- **Authentication Testing**: Login, session management
- **Authorization Testing**: Access control, permissions
- **Input Validation Testing**: Injection attacks, XSS
- **Data Protection Testing**: Encryption, data leakage
- **Infrastructure Testing**: Network security, configuration

## Authentication Security Test Cases

### TC-SEC-001: SQL Injection Prevention
```yaml
test_case:
  id: TC-SEC-001
  title: SQL Injection Attack Prevention
  priority: Critical
  type: Security
  requirement_ref: [NFR-SEC-001]
  preconditions:
    - Application is deployed
    - Database is accessible
  test_data:
    - malicious_input: "'; DROP TABLE users; --"
    - endpoint: "/api/customers/search"
  test_steps:
    1. Send malicious SQL in search parameter
    2. Monitor database for unauthorized queries
    3. Verify error handling
    4. Check application logs
  expected_results:
    - Input is properly sanitized
    - No SQL injection occurs
    - Appropriate error message returned
    - Security event is logged
  automation_status: Automated
  automation_script: /security/sql_injection_tests.py
```

### TC-SEC-002: Cross-Site Scripting (XSS) Prevention
```yaml
test_case:
  id: TC-SEC-002
  title: XSS Attack Prevention
  priority: High
  type: Security
  requirement_ref: [NFR-SEC-002]
  preconditions:
    - Web application is accessible
    - User input fields are available
  test_data:
    - xss_payload: "<script>alert('XSS')</script>"
    - target_fields: [name, description, comments]
  test_steps:
    1. Submit XSS payload in input fields
    2. Verify output encoding
    3. Check for script execution
    4. Validate CSP headers
  expected_results:
    - Script tags are encoded/stripped
    - No JavaScript execution
    - CSP headers prevent inline scripts
  automation_status: Automated
```

### TC-SEC-003: Authentication Bypass Testing
```yaml
test_case:
  id: TC-SEC-003
  title: Authentication Bypass Attempt
  priority: Critical
  type: Security
  requirement_ref: [NFR-SEC-003]
  preconditions:
    - Protected endpoints are identified
    - Authentication is required
  test_data:
    - protected_endpoint: "/api/admin/users"
    - bypass_attempts: [no_token, invalid_token, expired_token]
  test_steps:
    1. Attempt access without authentication
    2. Try with invalid/expired tokens
    3. Test session fixation
    4. Verify access controls
  expected_results:
    - All unauthorized access denied
    - Proper HTTP status codes (401/403)
    - Security events logged
  automation_status: Automated
```

## Data Protection Test Cases

### TC-SEC-004: Data Encryption Verification
```yaml
test_case:
  id: TC-SEC-004
  title: Sensitive Data Encryption
  priority: Critical
  type: Security
  requirement_ref: [NFR-SEC-004]
  preconditions:
    - Database contains sensitive data
    - Encryption is configured
  test_data:
    - sensitive_fields: [password, ssn, credit_card]
  test_steps:
    1. Query database directly
    2. Verify data is encrypted at rest
    3. Check encryption algorithms
    4. Validate key management
  expected_results:
    - Sensitive data is encrypted
    - Strong encryption algorithms used
    - Keys are properly managed
  automation_status: Manual
```

### TC-SEC-005: PCI DSS Compliance Testing
```yaml
test_case:
  id: TC-SEC-005
  title: PCI DSS Compliance Validation
  priority: Critical
  type: Compliance
  requirement_ref: [NFR-COMP-001]
  preconditions:
    - Payment processing is implemented
    - PCI DSS requirements documented
  test_data:
    - card_data: "4111111111111111"
  test_steps:
    1. Verify card data encryption
    2. Check access logging
    3. Validate network segmentation
    4. Test vulnerability management
  expected_results:
    - Card data is properly protected
    - Access is logged and monitored
    - Network is segmented
    - Vulnerabilities are managed
  automation_status: Manual
```

## Infrastructure Security Test Cases

### TC-SEC-006: Network Security Testing
```yaml
test_case:
  id: TC-SEC-006
  title: Network Security Configuration
  priority: High
  type: Security
  requirement_ref: [NFR-SEC-005]
  preconditions:
    - Network infrastructure is deployed
    - Security groups are configured
  test_steps:
    1. Scan for open ports
    2. Test firewall rules
    3. Verify SSL/TLS configuration
    4. Check for unnecessary services
  expected_results:
    - Only required ports are open
    - Firewall rules are restrictive
    - Strong SSL/TLS configuration
    - No unnecessary services running
  automation_status: Automated
```

## Navigation

- [← Back to Master Document](./test_plan.md)
- [← Performance Test Cases](./test_cases_performance.md)
- [Test Automation →](./test_automation.md)
"""

def generate_test_automation_doc(content):
    """Generate the test automation document"""
    return """# Test Automation Framework and Scripts

## Automation Strategy

### Automation Pyramid
- **Unit Tests (70%)**: Fast, isolated, developer-written
- **Integration Tests (20%)**: Service-to-service communication
- **UI Tests (10%)**: End-to-end user workflows

### Automation Goals
- **Coverage**: 70% of all test cases automated
- **Execution**: Automated regression suite runs on every build
- **Maintenance**: Self-healing tests with minimal maintenance
- **Reporting**: Comprehensive test reports and metrics

## Test Automation Framework

### Framework Architecture
```
Test Automation Framework
├── Core Framework
│   ├── WebDriver Manager
│   ├── Test Data Manager
│   ├── Configuration Manager
│   └── Reporting Engine
├── Page Objects
│   ├── Login Page
│   ├── Dashboard Page
│   └── Feature Pages
├── Test Utilities
│   ├── Database Utils
│   ├── API Utils
│   └── File Utils
└── Test Suites
    ├── Smoke Tests
    ├── Regression Tests
    └── API Tests
```

### Technology Stack
- **Web UI**: Selenium WebDriver with Java
- **API Testing**: REST Assured
- **Mobile**: Appium
- **Performance**: JMeter, Gatling
- **BDD**: Cucumber
- **Reporting**: Allure, ExtentReports

## Test Scripts Organization

### API Test Scripts
```java
@Test
public class CustomerAPITests {
    
    @Test(priority = 1)
    public void testCreateCustomer() {
        // Test customer creation API
        given()
            .contentType(ContentType.JSON)
            .body(customerData)
        .when()
            .post("/api/customers")
        .then()
            .statusCode(201)
            .body("id", notNullValue())
            .body("status", equalTo("ACTIVE"));
    }
    
    @Test(priority = 2)
    public void testGetCustomer() {
        // Test customer retrieval API
        given()
            .pathParam("id", customerId)
        .when()
            .get("/api/customers/{id}")
        .then()
            .statusCode(200)
            .body("id", equalTo(customerId));
    }
}
```

### UI Test Scripts
```java
@Test
public class LoginTests extends BaseTest {
    
    @Test
    public void testSuccessfulLogin() {
        LoginPage loginPage = new LoginPage(driver);
        DashboardPage dashboard = loginPage
            .enterUsername("testuser@example.com")
            .enterPassword("ValidPass123!")
            .clickLogin();
        
        Assert.assertTrue(dashboard.isUserLoggedIn());
        Assert.assertEquals(dashboard.getWelcomeMessage(), 
                          "Welcome, Test User");
    }
}
```

## Continuous Integration Integration

### CI/CD Pipeline Integration
```yaml
test_automation:
  stages:
    - unit_tests:
        command: mvn test
        coverage_threshold: 80%
        
    - integration_tests:
        command: mvn verify -Pintegration
        environment: test
        
    - api_tests:
        command: mvn test -Papi-tests
        parallel: true
        
    - ui_tests:
        command: mvn test -Pui-tests
        browsers: [chrome, firefox]
        
    - performance_tests:
        command: jmeter -n -t load_test.jmx
        trigger: nightly
```

### Test Execution Strategy
- **Smoke Tests**: Every build (5 minutes)
- **Regression Tests**: Every merge to main (30 minutes)
- **Full Suite**: Nightly (2 hours)
- **Performance Tests**: Weekly (4 hours)

## Test Data Management

### Test Data Strategy
```java
public class TestDataManager {
    
    public static Customer createTestCustomer() {
        return Customer.builder()
            .name("Test Customer " + UUID.randomUUID())
            .email("test+" + System.currentTimeMillis() + "@example.com")
            .phone("+1-555-" + RandomUtils.nextInt(1000000, 9999999))
            .build();
    }
    
    public static void cleanupTestData(String customerId) {
        // Cleanup test data after test execution
        DatabaseUtils.deleteCustomer(customerId);
    }
}
```

### Environment Configuration
```properties
# Test Environment Configuration
test.environment=staging
test.base.url=https://staging.fywebmidway.com
test.api.url=https://api-staging.fywebmidway.com
test.database.url=jdbc:postgresql://staging-db:5432/fywebmidway
test.browser=chrome
test.headless=true
test.timeout=30
```

## Test Reporting and Metrics

### Automated Reporting
- **Test Execution Reports**: Pass/fail status, execution time
- **Coverage Reports**: Code coverage, requirement coverage
- **Performance Reports**: Response times, throughput
- **Defect Reports**: Automated defect creation for failures

### Key Metrics
- **Test Automation Coverage**: 70% target
- **Test Execution Time**: <30 minutes for regression
- **Test Stability**: <5% flaky test rate
- **Defect Detection**: 90% of defects caught by automation

## Navigation

- [← Back to Master Document](./test_plan.md)
- [← Security Test Cases](./test_cases_security.md)
- [← Performance Test Cases](./test_cases_performance.md)
"""
