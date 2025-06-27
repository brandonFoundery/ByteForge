# Claude Code Instructions: testRigor Test Generation

## Context
You are converting the frontend test plan into executable testRigor test scripts for the FY.WB.Midway application.

## Input Files
- **Test Plan**: `generated_documents/testing/frontend_test_plan.md`
- **testRigor Templates**: `Development_Prompts/testRigor_*.md`

## Commands to Execute

1. **Read Test Plan**:
   ```bash
   cat generated_documents/testing/frontend_test_plan.md
   ```

2. **Review testRigor Templates**:
   ```bash
   ls Development_Prompts/testRigor_*.md
   cat Development_Prompts/testRigor_FY_WB_Midway_Implementation.md
   ```

3. **Create Test Directory Structure**:
   ```bash
   mkdir -p generated_documents/testing/testrigor_tests/page_load_tests
   mkdir -p generated_documents/testing/testrigor_tests/interactive_tests
   mkdir -p generated_documents/testing/testrigor_tests/modal_tests
   mkdir -p generated_documents/testing/testrigor_tests/workflow_tests
   ```

4. **Generate Test Files**:
   Create individual testRigor test files for each category following the prompt requirements.

## testRigor Syntax Reference
- `open url "http://localhost:4001/page"`
- `click "Button Text"`
- `enter "text" into "Field Name"`
- `wait until page contains "Expected Text"`
- `check that page does not contain "Error"`
- `save screenshot as "test-checkpoint"`

## Success Criteria
- [ ] All test tasks converted to testRigor format
- [ ] Tests organized in logical directory structure
- [ ] Each test is executable and independent
- [ ] Comprehensive error checking included
- [ ] Master test suite created for full execution

## Notes
- Use **natural language** for element identification
- Include **wait strategies** for dynamic content
- Add **error checking** after each significant action
- Create **reusable test components** where possible
