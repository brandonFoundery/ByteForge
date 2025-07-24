import { test, expect } from '@playwright/test';
import { AuthHelper } from './helpers/auth-helper';
import { ApiHelper } from './helpers/api-helper';

test.describe('Template Management', () => {
  let authHelper: AuthHelper;
  let apiHelper: ApiHelper;

  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    authHelper = new AuthHelper(page);
    await authHelper.login();
    await context.close();
  });

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page);
    apiHelper = new ApiHelper(page);
    await authHelper.ensureAuthenticated();
  });

  test.describe('Template List View', () => {
    test('should display available templates', async ({ page }) => {
      await page.goto('http://localhost:3006/templates');
      
      // Wait for templates to load
      await page.waitForSelector('[data-testid="template-list"]');
      
      // Verify template categories are shown
      await expect(page.getByText('Business Templates')).toBeVisible();
      await expect(page.getByText('E-commerce Templates')).toBeVisible();
      
      // Verify at least one template is displayed
      const templates = page.locator('[data-testid="template-card"]');
      await expect(templates).toHaveCount(2); // CRM and E-commerce templates
    });

    test('should filter templates by category', async ({ page }) => {
      await page.goto('http://localhost:3006/templates');
      
      // Click on Business category filter
      await page.click('[data-testid="category-filter-business"]');
      
      // Verify only business templates are shown
      const templates = page.locator('[data-testid="template-card"]');
      const count = await templates.count();
      
      for (let i = 0; i < count; i++) {
        const category = await templates.nth(i).locator('[data-testid="template-category"]').textContent();
        expect(category).toBe('Business');
      }
    });

    test('should search templates by name', async ({ page }) => {
      await page.goto('http://localhost:3006/templates');
      
      // Search for CRM
      await page.fill('[data-testid="template-search"]', 'CRM');
      
      // Verify search results
      const templates = page.locator('[data-testid="template-card"]');
      await expect(templates).toHaveCount(1);
      await expect(templates.first().locator('[data-testid="template-name"]')).toContainText('CRM');
    });
  });

  test.describe('Template Details', () => {
    test('should display template details', async ({ page }) => {
      await page.goto('http://localhost:3006/templates');
      
      // Click on CRM template
      await page.click('[data-testid="template-card-crm"]');
      
      // Verify template details page
      await expect(page).toHaveURL(/\/templates\/crm-template/);
      await expect(page.getByRole('heading', { name: 'CRM Template' })).toBeVisible();
      
      // Verify template information
      await expect(page.getByText('Customer Relationship Management')).toBeVisible();
      await expect(page.getByText('Version: 1.0.0')).toBeVisible();
      await expect(page.getByText('Category: Business')).toBeVisible();
      
      // Verify required documents section
      await expect(page.getByText('Required Documents')).toBeVisible();
      await expect(page.getByText('BRD')).toBeVisible();
      await expect(page.getByText('PRD')).toBeVisible();
      await expect(page.getByText('FRD')).toBeVisible();
      await expect(page.getByText('TRD')).toBeVisible();
    });

    test('should show template file structure', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/crm-template');
      
      // Click on file structure tab
      await page.click('[data-testid="tab-file-structure"]');
      
      // Verify file structure is displayed
      await expect(page.getByText('/src')).toBeVisible();
      await expect(page.getByText('/src/Controllers')).toBeVisible();
      await expect(page.getByText('/src/Services')).toBeVisible();
      await expect(page.getByText('/tests')).toBeVisible();
      await expect(page.getByText('README.md')).toBeVisible();
    });

    test('should show template settings', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/crm-template');
      
      // Click on settings tab
      await page.click('[data-testid="tab-settings"]');
      
      // Verify default settings are displayed
      await expect(page.getByText('Multi-Tenant')).toBeVisible();
      await expect(page.getByText('Authentication Provider: JWT')).toBeVisible();
      await expect(page.getByText('Database: SQL Server')).toBeVisible();
    });
  });

  test.describe('Template Creation', () => {
    test('should create a new template', async ({ page }) => {
      await page.goto('http://localhost:3006/templates');
      
      // Click create template button
      await page.click('[data-testid="create-template-button"]');
      
      // Fill template form
      await page.fill('[data-testid="template-id"]', 'custom-template');
      await page.fill('[data-testid="template-name"]', 'Custom Template');
      await page.fill('[data-testid="template-description"]', 'A custom template for testing');
      await page.selectOption('[data-testid="template-category"]', 'Business');
      await page.fill('[data-testid="template-version"]', '1.0.0');
      
      // Add required documents
      await page.click('[data-testid="add-required-document"]');
      await page.selectOption('[data-testid="required-document-0"]', 'BRD');
      await page.click('[data-testid="add-required-document"]');
      await page.selectOption('[data-testid="required-document-1"]', 'PRD');
      
      // Save template
      await page.click('[data-testid="save-template"]');
      
      // Verify success message
      await expect(page.getByText('Template created successfully')).toBeVisible();
      
      // Verify redirect to template details
      await expect(page).toHaveURL(/\/templates\/custom-template/);
    });

    test('should validate template creation form', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/new');
      
      // Try to save without required fields
      await page.click('[data-testid="save-template"]');
      
      // Verify validation errors
      await expect(page.getByText('Template ID is required')).toBeVisible();
      await expect(page.getByText('Template name is required')).toBeVisible();
      
      // Fill invalid version
      await page.fill('[data-testid="template-version"]', 'invalid-version');
      await page.click('[data-testid="save-template"]');
      
      await expect(page.getByText('Invalid version format')).toBeVisible();
    });

    test('should prevent duplicate template IDs', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/new');
      
      // Try to create template with existing ID
      await page.fill('[data-testid="template-id"]', 'crm-template');
      await page.fill('[data-testid="template-name"]', 'Duplicate CRM');
      await page.selectOption('[data-testid="template-category"]', 'Business');
      
      await page.click('[data-testid="save-template"]');
      
      // Verify error message
      await expect(page.getByText('Template with this ID already exists')).toBeVisible();
    });
  });

  test.describe('Template Editing', () => {
    test('should edit existing template', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/crm-template');
      
      // Click edit button
      await page.click('[data-testid="edit-template-button"]');
      
      // Update template details
      await page.fill('[data-testid="template-name"]', 'CRM Template v2');
      await page.fill('[data-testid="template-version"]', '2.0.0');
      await page.fill('[data-testid="template-description"]', 'Updated CRM template with new features');
      
      // Add optional document
      await page.click('[data-testid="add-optional-document"]');
      await page.selectOption('[data-testid="optional-document-0"]', 'UX_SPEC');
      
      // Save changes
      await page.click('[data-testid="save-template"]');
      
      // Verify success message
      await expect(page.getByText('Template updated successfully')).toBeVisible();
      
      // Verify changes are reflected
      await expect(page.getByRole('heading', { name: 'CRM Template v2' })).toBeVisible();
      await expect(page.getByText('Version: 2.0.0')).toBeVisible();
    });

    test('should not allow editing template in use', async ({ page }) => {
      // Create a project using the template
      await apiHelper.makeRequest('/api/projects', {
        method: 'POST',
        data: {
          name: 'Test Project',
          templateId: 'crm-template',
          clientName: 'Test Client'
        }
      });
      
      await page.goto('http://localhost:3006/templates/crm-template');
      
      // Edit button should be disabled
      await expect(page.getByTestId('edit-template-button')).toBeDisabled();
      await expect(page.getByText('Template is in use by 1 project')).toBeVisible();
    });
  });

  test.describe('Template Cloning', () => {
    test('should clone existing template', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/crm-template');
      
      // Click clone button
      await page.click('[data-testid="clone-template-button"]');
      
      // Fill clone form
      await page.fill('[data-testid="clone-template-id"]', 'crm-template-clone');
      await page.fill('[data-testid="clone-template-name"]', 'CRM Template Clone');
      
      // Confirm clone
      await page.click('[data-testid="confirm-clone"]');
      
      // Verify success message
      await expect(page.getByText('Template cloned successfully')).toBeVisible();
      
      // Verify redirect to cloned template
      await expect(page).toHaveURL(/\/templates\/crm-template-clone/);
      await expect(page.getByRole('heading', { name: 'CRM Template Clone' })).toBeVisible();
    });
  });

  test.describe('Template Deletion', () => {
    test('should delete unused template', async ({ page }) => {
      // Create a template to delete
      await apiHelper.makeRequest('/api/templates', {
        method: 'POST',
        data: {
          id: 'temp-template',
          name: 'Temporary Template',
          category: 'Test',
          version: '1.0.0'
        }
      });
      
      await page.goto('http://localhost:3006/templates/temp-template');
      
      // Click delete button
      await page.click('[data-testid="delete-template-button"]');
      
      // Confirm deletion
      await page.click('[data-testid="confirm-delete"]');
      
      // Verify success message
      await expect(page.getByText('Template deleted successfully')).toBeVisible();
      
      // Verify redirect to template list
      await expect(page).toHaveURL('/templates');
      
      // Verify template is not in list
      await expect(page.getByTestId('template-card-temp-template')).not.toBeVisible();
    });

    test('should prevent deletion of template in use', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/crm-template');
      
      // Delete button should be disabled if template is in use
      await expect(page.getByTestId('delete-template-button')).toBeDisabled();
    });
  });

  test.describe('Template Usage in Projects', () => {
    test('should create project from template', async ({ page }) => {
      await page.goto('http://localhost:3006/projects/new');
      
      // Select template
      await page.click('[data-testid="select-template"]');
      await page.click('[data-testid="template-option-crm"]');
      
      // Fill project details
      await page.fill('[data-testid="project-name"]', 'New CRM Project');
      await page.fill('[data-testid="client-name"]', 'Acme Corp');
      
      // Customize template settings
      await page.click('[data-testid="customize-template"]');
      await page.uncheck('[data-testid="multi-tenant"]');
      await page.selectOption('[data-testid="auth-provider"]', 'OAuth');
      
      // Create project
      await page.click('[data-testid="create-project"]');
      
      // Verify project created with template
      await expect(page.getByText('Project created successfully')).toBeVisible();
      await expect(page).toHaveURL(/\/projects\/[a-f0-9-]+/);
      await expect(page.getByText('Template: CRM Template')).toBeVisible();
    });

    test('should show template customization options', async ({ page }) => {
      await page.goto('http://localhost:3006/projects/new');
      
      // Select e-commerce template
      await page.click('[data-testid="select-template"]');
      await page.click('[data-testid="template-option-ecommerce"]');
      
      // Verify e-commerce specific options appear
      await expect(page.getByText('Payment Providers')).toBeVisible();
      await expect(page.getByText('Shipping Providers')).toBeVisible();
      
      // Select payment providers
      await page.check('[data-testid="payment-stripe"]');
      await page.check('[data-testid="payment-paypal"]');
      
      // Select shipping providers
      await page.check('[data-testid="shipping-fedex"]');
      await page.check('[data-testid="shipping-ups"]');
    });
  });

  test.describe('Template Versioning', () => {
    test('should show template version history', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/crm-template');
      
      // Click on version history tab
      await page.click('[data-testid="tab-version-history"]');
      
      // Verify version history is displayed
      await expect(page.getByText('Version History')).toBeVisible();
      await expect(page.getByText('1.0.0 - Initial release')).toBeVisible();
      
      // If template was updated, show newer versions
      const versions = page.locator('[data-testid="version-item"]');
      const count = await versions.count();
      expect(count).toBeGreaterThanOrEqual(1);
    });

    test('should compare template versions', async ({ page }) => {
      await page.goto('http://localhost:3006/templates/crm-template/versions');
      
      // Select versions to compare
      await page.selectOption('[data-testid="version-from"]', '1.0.0');
      await page.selectOption('[data-testid="version-to"]', '2.0.0');
      
      await page.click('[data-testid="compare-versions"]');
      
      // Verify comparison view
      await expect(page.getByText('Version Comparison')).toBeVisible();
      await expect(page.locator('[data-testid="version-diff"]')).toBeVisible();
    });
  });
});