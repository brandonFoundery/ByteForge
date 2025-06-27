# Claude Code Instructions: Frontend Test Plan Generation

## Context
You are generating a comprehensive test plan for the FY.WB.Midway frontend application. This test plan will be used to create testRigor automation tests.

## Directory Context
- **Frontend Source**: `FrontEnd/src/`
- **Pages Directory**: `FrontEnd/src/pages/`
- **Components Directory**: `FrontEnd/src/components/`
- **Style Guide**: `FrontEnd/style_guide.html`
- **Output Directory**: `generated_documents/testing/`

## Commands to Execute

1. **Analyze Frontend Structure**:
   ```bash
   find FrontEnd/src/pages -name "*.tsx" -type f | head -20
   find FrontEnd/src/components -name "*.tsx" -type f | head -10
   ```

2. **Check Frontend Server Status**:
   ```bash
   echo "Frontend should be running on http://localhost:4001"
   curl -s -o /dev/null -w "%{http_code}" http://localhost:4001 || echo "Frontend not running"
   ```

3. **Examine Key Pages** (examine at least these critical pages):
   ```bash
   cat FrontEnd/src/pages/index.tsx
   cat FrontEnd/src/pages/login.tsx
   cat FrontEnd/src/pages/dashboard.tsx
   cat FrontEnd/src/pages/admin/index.tsx
   cat FrontEnd/src/pages/customers/index.tsx
   cat FrontEnd/src/pages/loads/index.tsx
   ```

3. **Check Style Guide**:
   ```bash
   cat FrontEnd/style_guide.html | head -50
   ```

4. **Create Output Directory**:
   ```bash
   mkdir -p generated_documents/testing
   ```

5. **Generate Test Plan**:
   Create the comprehensive test plan file following the prompt requirements.

## Success Criteria
- [ ] All pages analyzed and documented
- [ ] Interactive elements identified for each page
- [ ] Modal components documented with triggers
- [ ] Test tasks created in actionable format
- [ ] Output saved to correct location
- [ ] Test plan follows testRigor natural language patterns

## Notes
- Focus on **actionable test tasks** that can be automated
- Include **both UI and functional testing**
- Consider **error scenarios** and edge cases
- Ensure **comprehensive coverage** of user workflows
