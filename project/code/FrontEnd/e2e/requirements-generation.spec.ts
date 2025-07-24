import { test, expect } from '@playwright/test';
import { APIHelper } from './helpers/api-helper';
import { AuthHelper } from './helpers/auth-helper';
import { NavigationHelper } from './helpers/navigation-helper';

test.describe('Requirements Generation Workflow', () => {
  let apiHelper: APIHelper;
  let authHelper: AuthHelper;
  let navigationHelper: NavigationHelper;
  let projectId: string;

  test.beforeAll(async ({ request }) => {
    apiHelper = new APIHelper(request);
    
    // Create a test project
    const projectResponse = await apiHelper.post('/api/projects', {
      name: 'E2E Test CRM Project',
      description: 'CRM system for managing customer relationships',
      clientRequirements: 'Need to track customers, manage sales pipeline, generate reports',
      templateId: 'crm-template'
    });
    
    projectId = projectResponse.data.id;
  });

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    navigationHelper = new NavigationHelper(page);
    
    await authHelper.login('test@example.com', 'Test123!');
  });

  test.afterAll(async ({ request }) => {
    // Cleanup: Delete test project
    if (projectId) {
      await apiHelper.delete(`/api/projects/${projectId}`);
    }
  });

  test('should generate all requirement documents in proper order', async ({ page, request }) => {
    // Navigate to project details
    await navigationHelper.goToProjectDetails(projectId);
    
    // Start requirements generation
    await page.click('button:has-text("Generate Requirements")');
    
    // Verify generation modal appears
    await expect(page.locator('.requirements-generation-modal')).toBeVisible();
    
    // Configure generation options
    await page.fill('input[name="projectName"]', 'E2E Test CRM System');
    await page.fill('textarea[name="additionalContext"]', 'Focus on small business needs');
    
    // Select document types to generate
    await page.check('input[value="BRD"]');
    await page.check('input[value="PRD"]');
    await page.check('input[value="FRD"]');
    await page.check('input[value="TRD"]');
    
    // Start generation
    await page.click('button:has-text("Start Generation")');
    
    // Monitor progress
    await expect(page.locator('.generation-progress')).toBeVisible();
    
    // Wait for BRD generation
    await expect(page.locator('.document-status[data-type="BRD"]')).toHaveText(/Completed/, { timeout: 60000 });
    
    // Verify PRD starts after BRD completes (dependency check)
    await expect(page.locator('.document-status[data-type="PRD"]')).toHaveText(/In Progress/);
    
    // Wait for all documents to complete
    await expect(page.locator('.overall-progress')).toHaveText('100%', { timeout: 180000 });
    
    // Verify all documents were generated
    const generatedDocs = await apiHelper.get(`/api/projects/${projectId}/documents`);
    expect(generatedDocs.data).toHaveLength(4);
    
    const docTypes = generatedDocs.data.map((doc: any) => doc.documentType);
    expect(docTypes).toContain('BRD');
    expect(docTypes).toContain('PRD');
    expect(docTypes).toContain('FRD');
    expect(docTypes).toContain('TRD');
  });

  test('should validate document traceability', async ({ page, request }) => {
    // Navigate to traceability view
    await navigationHelper.goToProjectDetails(projectId);
    await page.click('a:has-text("Traceability")');
    
    // Generate traceability matrix
    await page.click('button:has-text("Generate RTM")');
    
    // Wait for matrix generation
    await expect(page.locator('.rtm-container')).toBeVisible({ timeout: 30000 });
    
    // Verify requirements are properly linked
    const matrixData = await apiHelper.get(`/api/projects/${projectId}/traceability/matrix`);
    
    expect(matrixData.data.statistics.totalRequirements).toBeGreaterThan(0);
    expect(matrixData.data.statistics.totalLinks).toBeGreaterThan(0);
    expect(matrixData.data.statistics.orphanedRequirements).toBe(0);
    
    // Validate traceability
    const validationResponse = await apiHelper.get(`/api/projects/${projectId}/traceability/validate`);
    
    expect(validationResponse.data.isValid).toBe(true);
    expect(validationResponse.data.orphanedRequirements).toHaveLength(0);
    expect(validationResponse.data.unimplementedRequirements).toHaveLength(0);
    expect(validationResponse.data.brokenLinks).toHaveLength(0);
  });

  test('should analyze change impact across requirements', async ({ page, request }) => {
    // Navigate to a specific requirement
    await navigationHelper.goToProjectDetails(projectId);
    await page.click('a:has-text("Requirements")');
    
    // Find and select a business requirement
    await page.click('.requirement-item[data-id^="BR"]:first-child');
    
    // Click analyze impact
    await page.click('button:has-text("Analyze Impact")');
    
    // Fill in change details
    await page.fill('textarea[name="changeDescription"]', 'Adding multi-factor authentication requirement');
    await page.selectOption('select[name="changeType"]', 'modification');
    
    // Run analysis
    await page.click('button:has-text("Analyze")');
    
    // Wait for results
    await expect(page.locator('.impact-analysis-results')).toBeVisible({ timeout: 10000 });
    
    // Verify impact results show affected requirements
    await expect(page.locator('.directly-affected-list')).toContainText('PR');
    await expect(page.locator('.indirectly-affected-list')).toContainText('FR');
    
    // Verify severity assessment
    await expect(page.locator('.impact-severity')).toContainText(/High|Critical/);
  });

  test('should export traceability matrix in multiple formats', async ({ page, request }) => {
    // Navigate to traceability view
    await navigationHelper.goToProjectDetails(projectId);
    await page.click('a:has-text("Traceability")');
    
    // Test CSV export
    const [csvDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Export CSV")')
    ]);
    
    expect(csvDownload.suggestedFilename()).toMatch(/RTM.*\.csv$/);
    
    // Test HTML export
    const [htmlDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Export HTML")')
    ]);
    
    expect(htmlDownload.suggestedFilename()).toMatch(/RTM.*\.html$/);
    
    // Verify export content via API
    const csvExport = await apiHelper.get(`/api/projects/${projectId}/traceability/export?format=csv`);
    expect(csvExport.data.content).toContain('Source,Target,Link Type');
    expect(csvExport.data.content).toContain('BR');
    expect(csvExport.data.content).toContain('PR');
  });

  test('should show real-time progress updates during generation', async ({ page, request }) => {
    // Create a new project for this test
    const newProjectResponse = await apiHelper.post('/api/projects', {
      name: 'Progress Test Project',
      description: 'Testing progress updates'
    });
    
    const newProjectId = newProjectResponse.data.id;
    
    try {
      // Navigate to project
      await navigationHelper.goToProjectDetails(newProjectId);
      
      // Start generation
      await page.click('button:has-text("Generate Requirements")');
      await page.click('button:has-text("Start Generation")');
      
      // Verify WebSocket connection for real-time updates
      await expect(page.locator('.connection-status')).toHaveText('Connected');
      
      // Monitor progress updates
      const progressElement = page.locator('.generation-progress-bar');
      
      // Progress should increase over time
      const initialProgress = await progressElement.getAttribute('aria-valuenow');
      await page.waitForTimeout(5000);
      const updatedProgress = await progressElement.getAttribute('aria-valuenow');
      
      expect(Number(updatedProgress)).toBeGreaterThan(Number(initialProgress));
      
      // Verify activity updates
      await expect(page.locator('.current-activity')).toContainText(/Generating/);
      
      // Verify individual document progress
      await expect(page.locator('.document-progress[data-type="BRD"] .progress-bar')).toBeVisible();
    } finally {
      // Cleanup
      await apiHelper.delete(`/api/projects/${newProjectId}`);
    }
  });

  test('should handle generation failures gracefully', async ({ page, request }) => {
    // Create a project with invalid data to trigger failure
    const failProjectResponse = await apiHelper.post('/api/projects', {
      name: 'Fail Test Project',
      description: 'Testing failure handling',
      clientRequirements: '' // Empty requirements might cause issues
    });
    
    const failProjectId = failProjectResponse.data.id;
    
    try {
      // Navigate and start generation
      await navigationHelper.goToProjectDetails(failProjectId);
      await page.click('button:has-text("Generate Requirements")');
      
      // Intentionally misconfigure to cause failure
      await page.fill('input[name="projectName"]', ''); // Empty name
      await page.click('button:has-text("Start Generation")');
      
      // Should show validation error
      await expect(page.locator('.validation-error')).toContainText('Project name is required');
      
      // Fix and try again with simulated API failure
      await page.fill('input[name="projectName"]', 'Test Project');
      
      // Mock API to return error
      await page.route(`**/api/projects/${failProjectId}/requirements/generate`, route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'LLM service unavailable' })
        });
      });
      
      await page.click('button:has-text("Start Generation")');
      
      // Should show error message
      await expect(page.locator('.error-alert')).toContainText('LLM service unavailable');
      
      // Should show retry option
      await expect(page.locator('button:has-text("Retry")')).toBeVisible();
    } finally {
      // Cleanup
      await apiHelper.delete(`/api/projects/${failProjectId}`);
    }
  });

  test('should support regenerating individual documents', async ({ page, request }) => {
    // Navigate to project documents
    await navigationHelper.goToProjectDetails(projectId);
    await page.click('a:has-text("Documents")');
    
    // Find PRD document
    await page.click('.document-row:has-text("PRD")');
    
    // Click regenerate
    await page.click('button:has-text("Regenerate")');
    
    // Confirm regeneration
    await expect(page.locator('.regenerate-dialog')).toBeVisible();
    await page.fill('textarea[name="reason"]', 'Updated business requirements');
    await page.click('button:has-text("Confirm Regeneration")');
    
    // Monitor regeneration progress
    await expect(page.locator('.regeneration-progress')).toBeVisible();
    
    // Wait for completion
    await expect(page.locator('.regeneration-status')).toHaveText('Completed', { timeout: 60000 });
    
    // Verify new version was created
    const documents = await apiHelper.get(`/api/projects/${projectId}/documents`);
    const prdDocs = documents.data.filter((doc: any) => doc.documentType === 'PRD');
    
    expect(prdDocs.length).toBeGreaterThan(1); // Should have multiple versions
    expect(prdDocs[0].version).not.toBe('1.0.0'); // Latest should have new version
  });
});