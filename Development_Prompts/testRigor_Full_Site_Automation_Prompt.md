# testRigor Full-Site Automation Prompt for SaaS Applications

## 🎯 Master Prompt Template

Copy and customize this prompt for any SaaS application to generate comprehensive testRigor automation scripts.

---

### System Prompt
```
You are an expert QA automation engineer specializing in testRigor natural-language DSL. You create comprehensive, maintenance-free test scripts that systematically validate entire SaaS applications without requiring manual locator updates.
```

### User Prompt Template
```
**Context & Configuration**

* **Base URL**: `{{STAGING_URL}}` (e.g., `http://localhost:4000`)
* **Backend API**: `{{API_URL}}` (e.g., `http://localhost:5002`)
* **Authentication**: 
  - Login Path: `/login`
  - Admin: `admin@example.com` / `AdminPass123!`
  - Tenant User: `alex.rodriguez@techcorp.com` / `Test123!`
* **Domain Scope**: Only test internal links within `{{DOMAIN}}`
* **Destructive Actions**: Skip elements containing "delete", "remove", "reset", "purge", "clear all"
* **Special Pages**: Skip external integrations, payment gateways, and third-party redirects

**Application Architecture**
* **Frontend**: Next.js with TypeScript, Tailwind CSS
* **Backend**: ASP.NET Core with JWT authentication
* **Database**: Azure SQL with Entity Framework
* **Multi-tenant**: Role-based access (Admin, Tenant User, Carrier)

**Known Application Routes**
```
Public Routes:
- / (landing page)
- /login
- /register
- /public/about
- /public/contact

Authenticated Routes:
- /dashboard (main dashboard)
- /admin/* (admin panel - requires Admin role)
- /client/* (client management)
- /customers/* (customer management)
- /loads/* (load management)
- /invoices/* (invoice management)
- /carriers/* (carrier management)
- /payments/* (payment processing)
- /reports/* (reporting)
- /documents/* (document management)
```

**Task Requirements**

Generate a single **testRigor test case** called **"FY.WB.Midway Full-Site Smoke Test"** that:

1. **Authentication Flow**:
   - Open base URL
   - If redirected to login, authenticate as admin user
   - Verify successful login by checking for "Dashboard" or user menu
   - Store authentication state for session

2. **Systematic Page Crawling**:
   - Build array of all internal navigation links
   - Visit each discoverable page systematically
   - Handle dynamic routing (e.g., `/customers/[id]`, `/loads/[id]`)
   - Test both list views and detail views where applicable

3. **Interactive Element Testing**:
   - Click every visible button, link, and interactive element
   - Fill forms with valid test data:
     * Text fields: "Test Data"
     * Email fields: "test@example.com"
     * Phone fields: "+1-555-123-4567"
     * Dates: Current date + 30 days
     * Dropdowns: Select first available option
     * Checkboxes: Check if unchecked
   - Submit forms and verify no errors

4. **Error Detection & Validation**:
   - After each action, verify page does not contain:
     * "404", "500", "Error", "Exception"
     * "Unauthorized", "Access Denied"
     * "Something went wrong"
     * Console error indicators
   - Verify successful navigation (URL changes appropriately)
   - Check for loading states completion

5. **Multi-Role Testing**:
   - Test as Admin user (full access)
   - Logout and test as Tenant user (limited access)
   - Verify role-based restrictions work correctly

6. **Data Integrity Checks**:
   - Verify CRUD operations don't break navigation
   - Check that created test data appears in lists
   - Ensure pagination works if present
   - Validate search functionality if available

7. **Responsive & Performance**:
   - Test key workflows on mobile viewport (375px width)
   - Verify page load times under 5 seconds
   - Check for broken images or missing assets

8. **Session Management**:
   - Test session timeout handling
   - Verify logout functionality
   - Check remember me functionality if present

**Technical Implementation Requirements**

- Use testRigor's natural language commands exclusively
- Implement robust wait strategies: `wait until page contains` or `wait 3 seconds`
- Use loops for dynamic content: `click "Next" until page does not contain "Next"`
- Store page titles and URLs in variables for reporting
- Take screenshots at key checkpoints: `save screenshot as "page-name-timestamp"`
- Handle modals and popups: `if page contains "modal" then click "Close"`
- Implement error recovery: `if page contains "Error" then go back`

**Output Format**

Provide the complete testRigor script in plain text format (no markdown formatting). Include:
- Clear step numbering and comments
- Variable declarations for reusable data
- Conditional logic for different user roles
- Comprehensive error handling
- Final summary report with statistics

**Success Criteria**

The generated script should:
- Execute without manual intervention
- Adapt to UI changes automatically (testRigor AI locators)
- Provide clear pass/fail results for each major section
- Generate actionable error reports
- Complete full site crawl in under 30 minutes
- Achieve 90%+ page coverage for authenticated users
```

---

## 🔧 Customization Guide

### For Different SaaS Applications

**E-commerce Platform**:
- Add product catalog crawling
- Include shopping cart workflows
- Test checkout process (without payment)
- Verify inventory management

**CRM System**:
- Focus on contact management
- Test pipeline workflows
- Verify reporting dashboards
- Check integration points

**Project Management Tool**:
- Test project creation/editing
- Verify task management
- Check team collaboration features
- Validate time tracking

### Environment-Specific Variables

Replace these placeholders in the prompt:
- `{{STAGING_URL}}` → Your staging environment URL
- `{{API_URL}}` → Your backend API endpoint
- `{{DOMAIN}}` → Your application domain
- Update authentication credentials
- Modify route lists based on your application

### Advanced Customizations

**API Integration Testing**:
```
Add after authentication:
- Verify API endpoints return 200 status
- Check JWT token validity
- Test rate limiting behavior
```

**Database Validation**:
```
Include data verification steps:
- Create record and verify in list view
- Update record and check changes persist
- Delete record and confirm removal
```

**Performance Monitoring**:
```
Add performance checks:
- Measure page load times
- Check for memory leaks
- Monitor network requests
```

---

## 🚀 Implementation Steps

1. **Copy the prompt template above**
2. **Replace all `{{VARIABLES}}` with your application specifics**
3. **Paste into GPT-4 or equivalent LLM**
4. **Review generated testRigor script**
5. **Import into testRigor platform**
6. **Configure environment variables**
7. **Execute and iterate based on results**

---

## 🔧 Advanced Features

### API Integration Testing
Add this section to your prompt for API validation:

```
**API Testing Requirements**
- Verify backend API responses during UI interactions
- Check HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Validate JSON response structure
- Test API rate limiting
- Monitor response times (< 2 seconds for CRUD operations)
- Verify JWT token refresh functionality
```

### Performance Monitoring
Include performance checks:

```
**Performance Validation**
- Measure page load times (< 3 seconds for standard pages)
- Check for memory leaks during extended sessions
- Monitor network request counts
- Validate image optimization
- Test under simulated slow network conditions
- Verify caching mechanisms work correctly
```

### Accessibility Testing
Add accessibility validation:

```
**Accessibility Requirements**
- Verify keyboard navigation works for all interactive elements
- Check color contrast ratios meet WCAG AA standards
- Validate screen reader compatibility
- Test focus management in modals and forms
- Ensure alt text exists for images
- Verify proper heading hierarchy (h1, h2, h3...)
```

### Security Testing
Include basic security checks:

```
**Security Validation**
- Verify role-based access controls
- Test session timeout functionality
- Check for exposed sensitive data in DOM
- Validate CSRF protection on forms
- Test XSS prevention in input fields
- Verify secure cookie settings
```

---

## 📊 Expected Outcomes

The generated testRigor script will:
- ✅ Test 90%+ of application pages
- ✅ Validate all major user workflows
- ✅ Detect broken functionality automatically
- ✅ Provide detailed error reporting
- ✅ Require minimal maintenance
- ✅ Execute in CI/CD pipelines
- ✅ Scale with application changes
- ✅ Monitor performance metrics
- ✅ Validate API integrations
- ✅ Check accessibility compliance
- ✅ Verify security controls

---

## 🔍 Quality Assurance

**Before Production Use**:
- [ ] Test script on staging environment
- [ ] Verify all critical paths are covered
- [ ] Confirm error detection works
- [ ] Validate reporting accuracy
- [ ] Check execution time is acceptable
- [ ] Ensure no false positives/negatives
- [ ] Verify performance thresholds
- [ ] Test API integration points
- [ ] Validate accessibility checks
- [ ] Confirm security validations

**Maintenance Schedule**:
- Weekly: Review test results and update data
- Monthly: Audit coverage and add new features
- Quarterly: Performance optimization review
- Annually: Security and accessibility audit

---

## 🚀 CI/CD Integration

### testRigor CLI Commands
```bash
# Install testRigor CLI
npm install -g testrigor-cli

# Run full site test
testrigor run --suite "Full-Site Smoke Test" --env staging

# Run with specific browser
testrigor run --suite "Full-Site Smoke Test" --browser chrome --env production

# Generate coverage report
testrigor report --suite "Full-Site Smoke Test" --format html
```

### GitHub Actions Integration
```yaml
name: testRigor Full Site Test
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  testrigor-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run testRigor Tests
        env:
          TESTRIGOR_API_KEY: ${{ secrets.TESTRIGOR_API_KEY }}
        run: |
          npx testrigor-cli run --suite "Full-Site Smoke Test" --wait
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('testRigor Tests') {
            steps {
                script {
                    sh 'npx testrigor-cli run --suite "Full-Site Smoke Test" --env ${BRANCH_NAME}'
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'testrigor-reports',
                        reportFiles: 'index.html',
                        reportName: 'testRigor Report'
                    ])
                }
            }
        }
    }
}
```
