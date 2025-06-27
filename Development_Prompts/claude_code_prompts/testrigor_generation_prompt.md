# testRigor Test Generation for FY.WB.Midway

## Objective
You are a senior test automation engineer tasked with converting the frontend test plan into executable testRigor test scripts. Your goal is to create comprehensive, maintainable testRigor tests that follow natural language patterns.

## Input
- **Test Plan**: `generated_documents/testing/frontend_test_plan.md`
- **testRigor Prompt Templates**: `Development_Prompts/testRigor_*.md`

## Your Tasks

### 1. Read and Analyze Test Plan
1. **Load the test plan** from the generated file
2. **Parse test tasks** by page and category
3. **Identify test dependencies** and prerequisites
4. **Group related tests** for efficient execution

### 2. Generate testRigor Tests
For each test task in the plan, create testRigor test scripts using natural language:

#### Test Structure:
```
[Test Name]

# Test setup and navigation
open url "http://localhost:4001[route]"
wait until page loads

# Test steps (natural language)
[specific test actions]

# Verification steps
check that page does not contain "Error"
check that page does not contain "404"
save screenshot as "[test-name]-result"
```

### 3. Test Categories to Generate

#### Page Load Tests
- Basic page loading and error checking
- Style compliance verification
- Responsive design testing

#### Interactive Element Tests
- Button click tests with expected outcomes
- Form submission tests with validation
- Navigation tests between pages

#### Modal Tests
- Modal opening and closing
- Modal form interactions
- Modal error handling

#### Workflow Tests
- End-to-end user workflows
- Cross-page navigation scenarios
- Data persistence tests

### 4. testRigor Best Practices
- Use **natural language** descriptions for elements
- Include **wait strategies** for dynamic content
- Add **screenshot capture** at key points
- Implement **error checking** after each action
- Use **variables** for reusable test data

## Output Structure

Create organized test files:

```
generated_documents/testing/testrigor_tests/
├── page_load_tests/
│   ├── homepage_load_test.txt
│   ├── login_page_load_test.txt
│   └── dashboard_load_test.txt
├── interactive_tests/
│   ├── login_form_test.txt
│   ├── customer_creation_test.txt
│   └── load_management_test.txt
├── modal_tests/
│   ├── customer_modal_test.txt
│   └── load_modal_test.txt
├── workflow_tests/
│   ├── complete_customer_workflow.txt
│   └── load_creation_workflow.txt
└── master_test_suite.txt
```

## Quality Standards
- Each test should be **executable in testRigor**
- Use **clear, descriptive test names**
- Include **comprehensive error checking**
- Follow **testRigor natural language syntax**
- Ensure **test independence** (each test can run standalone)

Begin by reading the test plan and generating the testRigor test scripts.
