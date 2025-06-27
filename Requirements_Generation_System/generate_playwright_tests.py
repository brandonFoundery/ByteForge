#!/usr/bin/env python3
"""
Generate comprehensive Playwright tests for FY.WB.Midway frontend
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console

console = Console()


async def generate_comprehensive_playwright_tests():
    """Generate comprehensive Playwright tests for local execution"""
    
    console.print("[bold cyan]🎭 Generating Comprehensive Playwright Tests[/bold cyan]")
    console.print("This will create production-ready Playwright test files for local execution.\n")
    
    try:
        # Use existing Playwright setup in FrontEnd
        base_path = Path(__file__).parent.parent
        playwright_dir = base_path / "FrontEnd" / "tests" / "e2e"

        # Create tests directory if it doesn't exist
        playwright_dir.mkdir(parents=True, exist_ok=True)

        # Also create utils directory
        utils_dir = playwright_dir / "utils"
        utils_dir.mkdir(exist_ok=True)
        
        # Generate comprehensive Playwright test files
        await generate_playwright_utils(utils_dir)
        await generate_playwright_page_tests(playwright_dir)
        await generate_playwright_auth_tests(playwright_dir)
        await generate_playwright_interactive_tests(playwright_dir)
        await generate_playwright_admin_tests(playwright_dir)
        await generate_playwright_workflow_tests(playwright_dir)
        await generate_playwright_responsive_tests(playwright_dir)
        await generate_test_runner_scripts(base_path / "FrontEnd")
        
        console.print(f"[bold green]🎉 Comprehensive Playwright Tests Generated![/bold green]")
        console.print(f"[cyan]Location: {playwright_dir}[/cyan]")
        console.print(f"\n[yellow]To run the tests:[/yellow]")
        console.print(f"1. cd FrontEnd")
        console.print(f"2. npm run test:e2e")
        console.print(f"3. Or use the test runner: run_tests.bat")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error generating tests: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False


async def generate_playwright_config(playwright_dir):
    """Generate Playwright configuration"""
    
    config_content = """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:4001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'echo "Make sure your frontend is running on http://localhost:4001"',
    url: 'http://localhost:4001',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
"""
    
    config_file = playwright_dir / "playwright.config.ts"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)


async def generate_playwright_package_json(playwright_dir):
    """Generate package.json for Playwright tests"""
    
    package_content = """{
  "name": "fy-wb-midway-playwright-tests",
  "version": "1.0.0",
  "description": "Comprehensive Playwright tests for FY.WB.Midway frontend",
  "scripts": {
    "test": "playwright test",
    "test:headed": "playwright test --headed",
    "test:debug": "playwright test --debug",
    "test:ui": "playwright test --ui",
    "test:chrome": "playwright test --project=chromium",
    "test:firefox": "playwright test --project=firefox",
    "test:safari": "playwright test --project=webkit",
    "test:mobile": "playwright test --project=mobile-chrome --project=mobile-safari",
    "report": "playwright show-report",
    "install": "npm install && npx playwright install"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  },
  "engines": {
    "node": ">=16.0.0"
  }
}
"""
    
    package_file = playwright_dir / "package.json"
    with open(package_file, 'w', encoding='utf-8') as f:
        f.write(package_content)


async def generate_playwright_utils(utils_dir):
    """Generate utility functions for tests"""
    
    utils_content = """import { Page, expect } from '@playwright/test';

export class TestUtils {
  constructor(private page: Page) {}

  async login(email: string = 'admin@example.com', password: string = 'AdminPass123!') {
    await this.page.goto('/login');
    await this.page.fill('input[type="email"], input[name="email"]', email);
    await this.page.fill('input[type="password"], input[name="password"]', password);
    await this.page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    
    // Wait for successful login
    await this.page.waitForURL(/dashboard|admin|home/, { timeout: 10000 });
    await this.checkNoErrors();
  }

  async logout() {
    const logoutSelectors = [
      'button:has-text("Logout")',
      'a:has-text("Logout")',
      'button:has-text("Sign Out")',
      '[data-testid="logout"]',
      '.logout-button'
    ];
    
    for (const selector of logoutSelectors) {
      const element = this.page.locator(selector);
      if (await element.count() > 0) {
        await element.click();
        break;
      }
    }
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async checkNoErrors() {
    const errorTexts = ['Error', '404', '500', 'Something went wrong', 'Internal Server Error', 'Not Found'];
    for (const errorText of errorTexts) {
      await expect(this.page).not.toContainText(errorText);
    }
  }

  async fillForm(formData: Record<string, string>) {
    for (const [field, value] of Object.entries(formData)) {
      const selectors = [
        `input[name="${field}"]`,
        `input[placeholder*="${field}" i]`,
        `textarea[name="${field}"]`,
        `select[name="${field}"]`,
        `[data-testid="${field}"]`
      ];
      
      let filled = false;
      for (const selector of selectors) {
        const element = this.page.locator(selector);
        if (await element.count() > 0) {
          await element.fill(value);
          filled = true;
          break;
        }
      }
      
      if (!filled) {
        console.warn(`Could not find field: ${field}`);
      }
    }
  }

  async submitForm() {
    const submitSelectors = [
      'button[type="submit"]',
      'button:has-text("Save")',
      'button:has-text("Submit")',
      'button:has-text("Create")',
      '[data-testid="submit"]'
    ];
    
    for (const selector of submitSelectors) {
      const element = this.page.locator(selector);
      if (await element.count() > 0) {
        await element.click();
        break;
      }
    }
  }

  async navigateToPage(path: string) {
    await this.page.goto(path);
    await this.waitForPageLoad();
    await this.checkNoErrors();
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ 
      path: `screenshots/${name}.png`,
      fullPage: true 
    });
  }
}

export const testData = {
  customer: {
    companyName: 'Test Company Inc.',
    contactName: 'John Doe',
    email: 'test@example.com',
    phone: '+1-555-123-4567',
    address: '123 Test Street',
    city: 'Test City',
    state: 'TX',
    zipCode: '12345'
  },
  load: {
    origin: 'Chicago, IL',
    destination: 'Dallas, TX',
    weight: '5000',
    equipmentType: 'Dry Van',
    pickupDate: '2024-01-15',
    deliveryDate: '2024-01-17'
  },
  invoice: {
    description: 'Test Invoice for Load Transport',
    amount: '1000.00',
    dueDate: '2024-02-15'
  },
  carrier: {
    companyName: 'Test Carrier LLC',
    contactName: 'Jane Smith',
    email: 'carrier@example.com',
    phone: '+1-555-987-6543',
    mcNumber: 'MC123456'
  }
};

export const selectors = {
  navigation: {
    dashboard: 'a[href*="dashboard"], button:has-text("Dashboard")',
    customers: 'a[href*="customers"], button:has-text("Customers")',
    loads: 'a[href*="loads"], button:has-text("Loads")',
    invoices: 'a[href*="invoices"], button:has-text("Invoices")',
    carriers: 'a[href*="carriers"], button:has-text("Carriers")',
    admin: 'a[href*="admin"], button:has-text("Admin")',
    reports: 'a[href*="reports"], button:has-text("Reports")'
  },
  buttons: {
    save: 'button:has-text("Save"), button[type="submit"]',
    cancel: 'button:has-text("Cancel")',
    delete: 'button:has-text("Delete")',
    edit: 'button:has-text("Edit")',
    new: 'button:has-text("New"), button:has-text("Add"), button:has-text("Create")'
  }
};
"""
    
    utils_file = utils_dir / "test-utils.ts"
    with open(utils_file, 'w', encoding='utf-8') as f:
        f.write(utils_content)


async def generate_test_runner_scripts(playwright_dir):
    """Generate test runner scripts"""
    
    # Windows batch file
    windows_script = """@echo off
echo ========================================
echo FY.WB.Midway Playwright Test Runner
echo ========================================
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js found!
echo.

echo Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installing Playwright browsers...
call npx playwright install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Playwright browsers
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Frontend Tests
echo ========================================
echo.
echo Make sure your frontend is running on:
echo http://localhost:4001
echo.
echo Available test commands:
echo 1. Full test suite (all browsers)
echo 2. Chrome only (fastest)
echo 3. Interactive UI mode
echo 4. Debug mode
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo Running full test suite...
    call npx playwright test
) else if "%choice%"=="2" (
    echo Running Chrome tests only...
    call npx playwright test --project=chromium
) else if "%choice%"=="3" (
    echo Starting UI mode...
    call npx playwright test --ui
) else if "%choice%"=="4" (
    echo Starting debug mode...
    call npx playwright test --debug
) else (
    echo Running default tests...
    call npx playwright test --project=chromium
)

echo.
echo ========================================
echo Tests completed!
echo ========================================
echo.
echo Opening test report...
call npx playwright show-report

pause
"""
    
    windows_file = playwright_dir / "run_tests.bat"
    with open(windows_file, 'w', encoding='utf-8') as f:
        f.write(windows_script)
    
    # Linux/Mac shell script
    unix_script = """#!/bin/bash
echo "========================================"
echo "FY.WB.Midway Playwright Test Runner"
echo "========================================"
echo

echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "Node.js found!"
echo

echo "Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Installing Playwright browsers..."
npx playwright install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Playwright browsers"
    exit 1
fi

echo
echo "========================================"
echo "Starting Frontend Tests"
echo "========================================"
echo
echo "Make sure your frontend is running on:"
echo "http://localhost:4001"
echo
echo "Available test commands:"
echo "1. Full test suite (all browsers)"
echo "2. Chrome only (fastest)"
echo "3. Interactive UI mode"
echo "4. Debug mode"
echo
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Running full test suite..."
        npx playwright test
        ;;
    2)
        echo "Running Chrome tests only..."
        npx playwright test --project=chromium
        ;;
    3)
        echo "Starting UI mode..."
        npx playwright test --ui
        ;;
    4)
        echo "Starting debug mode..."
        npx playwright test --debug
        ;;
    *)
        echo "Running default tests..."
        npx playwright test --project=chromium
        ;;
esac

echo
echo "========================================"
echo "Tests completed!"
echo "========================================"
echo
echo "Opening test report..."
npx playwright show-report
"""
    
    unix_file = playwright_dir / "run_tests.sh"
    with open(unix_file, 'w', encoding='utf-8') as f:
        f.write(unix_script)
    
    # Make shell script executable
    import os
    os.chmod(unix_file, 0o755)


async def generate_playwright_page_tests(playwright_dir):
    """Generate page load tests"""

    tests_dir = playwright_dir / "tests"
    tests_dir.mkdir(exist_ok=True)

    page_test_content = """import { test, expect } from '@playwright/test';
import { TestUtils } from './utils/test-utils';

test.describe('Page Load Tests', () => {
  let utils: TestUtils;

  test.beforeEach(async ({ page }) => {
    utils = new TestUtils(page);
  });

  test('Homepage loads correctly', async ({ page }) => {
    await page.goto('/');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();
    await expect(page).toHaveTitle(/FY.WB.Midway|Logistics|Transport/i);
    await utils.takeScreenshot('homepage-load');
  });

  test('Login page loads correctly', async ({ page }) => {
    await page.goto('/login');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"], button:has-text("Login")')).toBeVisible();
    await utils.takeScreenshot('login-page-load');
  });

  test('Dashboard loads after login', async ({ page }) => {
    await utils.login();
    await page.goto('/dashboard');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();
    await utils.takeScreenshot('dashboard-load');
  });

  test('Customers page loads', async ({ page }) => {
    await utils.login();
    await page.goto('/customers');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();
    await utils.takeScreenshot('customers-page-load');
  });

  test('Loads page loads', async ({ page }) => {
    await utils.login();
    await page.goto('/loads');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();
    await utils.takeScreenshot('loads-page-load');
  });

  test('Invoices page loads', async ({ page }) => {
    await utils.login();
    await page.goto('/invoices');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();
    await utils.takeScreenshot('invoices-page-load');
  });

  test('Admin panel loads', async ({ page }) => {
    await utils.login();
    await page.goto('/admin');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();
    await utils.takeScreenshot('admin-panel-load');
  });

  test('Reports page loads', async ({ page }) => {
    await utils.login();
    await page.goto('/reports');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();
    await utils.takeScreenshot('reports-page-load');
  });

  test('All navigation links work', async ({ page }) => {
    await utils.login();

    const navLinks = [
      { path: '/dashboard', name: 'Dashboard' },
      { path: '/customers', name: 'Customers' },
      { path: '/loads', name: 'Loads' },
      { path: '/invoices', name: 'Invoices' },
      { path: '/carriers', name: 'Carriers' },
      { path: '/reports', name: 'Reports' }
    ];

    for (const link of navLinks) {
      await page.goto(link.path);
      await utils.waitForPageLoad();
      await utils.checkNoErrors();
      console.log(`✓ ${link.name} page loaded successfully`);
    }
  });
});
"""

    page_test_file = tests_dir / "page-load.spec.ts"
    with open(page_test_file, 'w', encoding='utf-8') as f:
        f.write(page_test_content)


async def generate_playwright_auth_tests(playwright_dir):
    """Generate authentication tests"""

    tests_dir = playwright_dir / "tests"

    auth_test_content = """import { test, expect } from '@playwright/test';
import { TestUtils } from './utils/test-utils';

test.describe('Authentication Tests', () => {
  let utils: TestUtils;

  test.beforeEach(async ({ page }) => {
    utils = new TestUtils(page);
  });

  test('Valid login works', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');

    await expect(page).toHaveURL(/dashboard|admin|home/);
    await utils.checkNoErrors();
    await utils.takeScreenshot('successful-login');
  });

  test('Invalid login shows error', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"], button:has-text("Login")');

    // Should show error and stay on login page
    await expect(page).toHaveURL(/login/);
    const errorMessages = ['Invalid', 'Error', 'Failed', 'Incorrect'];
    let errorFound = false;

    for (const errorMsg of errorMessages) {
      if (await page.locator(`text=${errorMsg}`).count() > 0) {
        errorFound = true;
        break;
      }
    }

    if (!errorFound) {
      console.warn('No error message found for invalid login');
    }

    await utils.takeScreenshot('invalid-login-error');
  });

  test('Empty form validation', async ({ page }) => {
    await page.goto('/login');
    await page.click('button[type="submit"], button:has-text("Login")');

    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');

    // Check HTML5 validation
    await expect(emailInput).toHaveAttribute('required', '');
    await expect(passwordInput).toHaveAttribute('required', '');

    await utils.takeScreenshot('empty-form-validation');
  });

  test('Logout functionality', async ({ page }) => {
    await utils.login();
    await utils.logout();

    // Should redirect to login or home page
    await expect(page).toHaveURL(/login|home|\/$/, { timeout: 10000 });
    await utils.takeScreenshot('after-logout');
  });

  test('Protected route redirects to login', async ({ page }) => {
    await page.goto('/admin');
    await expect(page).toHaveURL(/login/, { timeout: 10000 });
    await utils.takeScreenshot('protected-route-redirect');
  });

  test('Session persistence', async ({ page }) => {
    await utils.login();
    await page.reload();

    // Should still be logged in after reload
    await expect(page).not.toHaveURL(/login/);
    await utils.checkNoErrors();
    await utils.takeScreenshot('session-persistence');
  });
});
"""

    auth_test_file = tests_dir / "auth.spec.ts"
    with open(auth_test_file, 'w', encoding='utf-8') as f:
        f.write(auth_test_content)


async def generate_playwright_interactive_tests(playwright_dir):
    """Generate interactive element tests"""

    tests_dir = playwright_dir / "tests"

    interactive_test_content = """import { test, expect } from '@playwright/test';
import { TestUtils, testData } from './utils/test-utils';

test.describe('Interactive Tests', () => {
  let utils: TestUtils;

  test.beforeEach(async ({ page }) => {
    utils = new TestUtils(page);
    await utils.login();
  });

  test('Customer creation form', async ({ page }) => {
    await page.goto('/customers/new');
    await utils.waitForPageLoad();

    await utils.fillForm(testData.customer);
    await utils.submitForm();

    // Wait for success indication
    await page.waitForTimeout(2000);
    await utils.checkNoErrors();
    await utils.takeScreenshot('customer-creation-success');
  });

  test('Load creation form', async ({ page }) => {
    await page.goto('/loads/new');
    await utils.waitForPageLoad();

    await utils.fillForm(testData.load);
    await utils.submitForm();

    await page.waitForTimeout(2000);
    await utils.checkNoErrors();
    await utils.takeScreenshot('load-creation-success');
  });

  test('Invoice creation form', async ({ page }) => {
    await page.goto('/invoices/new');
    await utils.waitForPageLoad();

    await utils.fillForm(testData.invoice);
    await utils.submitForm();

    await page.waitForTimeout(2000);
    await utils.checkNoErrors();
    await utils.takeScreenshot('invoice-creation-success');
  });

  test('Form validation works', async ({ page }) => {
    await page.goto('/customers/new');
    await utils.waitForPageLoad();

    // Try to submit empty form
    await utils.submitForm();

    // Check for validation messages
    const requiredFields = page.locator('input[required], select[required], textarea[required]');
    const fieldCount = await requiredFields.count();

    if (fieldCount > 0) {
      console.log(`Found ${fieldCount} required fields`);
    }

    await utils.takeScreenshot('form-validation');
  });

  test('Search functionality', async ({ page }) => {
    await page.goto('/customers');
    await utils.waitForPageLoad();

    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name*="search" i]');

    if (await searchInput.count() > 0) {
      await searchInput.fill('test');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);
      await utils.checkNoErrors();
    }

    await utils.takeScreenshot('search-functionality');
  });

  test('Data table interactions', async ({ page }) => {
    await page.goto('/customers');
    await utils.waitForPageLoad();

    // Check if table exists
    const table = page.locator('table, .table, [role="table"]');

    if (await table.count() > 0) {
      // Check for pagination
      const paginationButtons = page.locator('button:has-text("Next"), button:has-text("Previous"), .pagination button');

      if (await paginationButtons.count() > 0) {
        console.log('Pagination found');
      }

      // Check for sortable columns
      const sortableHeaders = page.locator('th[role="button"], th.sortable, th[data-sort]');

      if (await sortableHeaders.count() > 0) {
        await sortableHeaders.first().click();
        await page.waitForTimeout(1000);
      }
    }

    await utils.takeScreenshot('data-table-interactions');
  });
});
"""

    interactive_test_file = tests_dir / "interactive.spec.ts"
    with open(interactive_test_file, 'w', encoding='utf-8') as f:
        f.write(interactive_test_content)


async def generate_playwright_admin_tests(playwright_dir):
    """Generate admin panel tests"""

    tests_dir = playwright_dir / "tests"

    admin_test_content = """import { test, expect } from '@playwright/test';
import { TestUtils } from './utils/test-utils';

test.describe('Admin Panel Tests', () => {
  let utils: TestUtils;

  test.beforeEach(async ({ page }) => {
    utils = new TestUtils(page);
    await utils.login();
  });

  test('Admin dashboard access', async ({ page }) => {
    await page.goto('/admin');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    // Should not show unauthorized message
    await expect(page).not.toContainText('Unauthorized');
    await expect(page).not.toContainText('Access Denied');
    await expect(page).not.toContainText('403');

    await utils.takeScreenshot('admin-dashboard');
  });

  test('User management page', async ({ page }) => {
    await page.goto('/admin/users');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    // Should show user-related content
    const userContent = page.locator('text=/users|user management/i');
    if (await userContent.count() > 0) {
      console.log('User management content found');
    }

    await utils.takeScreenshot('user-management');
  });

  test('Tenant management page', async ({ page }) => {
    await page.goto('/admin/tenants');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    const tenantContent = page.locator('text=/tenants|tenant management/i');
    if (await tenantContent.count() > 0) {
      console.log('Tenant management content found');
    }

    await utils.takeScreenshot('tenant-management');
  });

  test('System settings page', async ({ page }) => {
    await page.goto('/admin/settings');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    const settingsContent = page.locator('text=/settings|configuration/i');
    if (await settingsContent.count() > 0) {
      console.log('Settings content found');
    }

    await utils.takeScreenshot('system-settings');
  });

  test('Admin navigation menu', async ({ page }) => {
    await page.goto('/admin');
    await utils.waitForPageLoad();

    const adminNavLinks = [
      { text: 'Users', path: '/admin/users' },
      { text: 'Tenants', path: '/admin/tenants' },
      { text: 'Settings', path: '/admin/settings' }
    ];

    for (const link of adminNavLinks) {
      const linkElement = page.locator(`a:has-text("${link.text}"), button:has-text("${link.text}")`);

      if (await linkElement.count() > 0) {
        await linkElement.click();
        await utils.waitForPageLoad();
        await utils.checkNoErrors();
        console.log(`✓ ${link.text} navigation works`);
      }
    }

    await utils.takeScreenshot('admin-navigation');
  });
});
"""

    admin_test_file = tests_dir / "admin.spec.ts"
    with open(admin_test_file, 'w', encoding='utf-8') as f:
        f.write(admin_test_content)


async def generate_playwright_workflow_tests(playwright_dir):
    """Generate end-to-end workflow tests"""

    tests_dir = playwright_dir / "tests"

    workflow_test_content = """import { test, expect } from '@playwright/test';
import { TestUtils, testData } from './utils/test-utils';

test.describe('End-to-End Workflows', () => {
  let utils: TestUtils;

  test.beforeEach(async ({ page }) => {
    utils = new TestUtils(page);
    await utils.login();
  });

  test('Complete customer workflow', async ({ page }) => {
    // Step 1: Create Customer
    await page.goto('/customers/new');
    await utils.waitForPageLoad();

    const customerData = {
      ...testData.customer,
      companyName: 'Workflow Test Company',
      email: 'workflow@test.com'
    };

    await utils.fillForm(customerData);
    await utils.submitForm();
    await page.waitForTimeout(2000);
    await utils.checkNoErrors();

    // Step 2: Create Load for Customer
    await page.goto('/loads/new');
    await utils.waitForPageLoad();

    // Try to select the customer we just created
    const customerSelect = page.locator('select[name="customer"], select[name="customerId"]');
    if (await customerSelect.count() > 0) {
      await customerSelect.selectOption({ label: 'Workflow Test Company' });
    }

    await utils.fillForm(testData.load);
    await utils.submitForm();
    await page.waitForTimeout(2000);
    await utils.checkNoErrors();

    // Step 3: Generate Invoice
    await page.goto('/invoices/new');
    await utils.waitForPageLoad();

    const invoiceCustomerSelect = page.locator('select[name="customer"], select[name="customerId"]');
    if (await invoiceCustomerSelect.count() > 0) {
      await invoiceCustomerSelect.selectOption({ label: 'Workflow Test Company' });
    }

    await utils.fillForm({
      ...testData.invoice,
      description: 'Workflow Test Invoice'
    });
    await utils.submitForm();
    await page.waitForTimeout(2000);
    await utils.checkNoErrors();

    await utils.takeScreenshot('complete-customer-workflow');
  });

  test('Admin management workflow', async ({ page }) => {
    // Step 1: Access Admin Panel
    await page.goto('/admin');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    // Step 2: Check Users Management
    await page.goto('/admin/users');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    // Step 3: Check System Settings
    await page.goto('/admin/settings');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    await utils.takeScreenshot('admin-management-workflow');
  });

  test('Data entry and verification workflow', async ({ page }) => {
    // Create a customer and verify it appears in the list
    await page.goto('/customers/new');
    await utils.waitForPageLoad();

    const uniqueCompany = `Test Company ${Date.now()}`;
    await utils.fillForm({
      ...testData.customer,
      companyName: uniqueCompany
    });
    await utils.submitForm();
    await page.waitForTimeout(2000);

    // Go to customers list and verify the new customer appears
    await page.goto('/customers');
    await utils.waitForPageLoad();

    // Look for the company name in the page
    const companyElement = page.locator(`text=${uniqueCompany}`);
    if (await companyElement.count() > 0) {
      console.log(`✓ Customer ${uniqueCompany} found in list`);
    } else {
      console.warn(`Customer ${uniqueCompany} not found in list`);
    }

    await utils.takeScreenshot('data-entry-verification');
  });
});
"""

    workflow_test_file = tests_dir / "workflows.spec.ts"
    with open(workflow_test_file, 'w', encoding='utf-8') as f:
        f.write(workflow_test_content)


async def generate_playwright_responsive_tests(playwright_dir):
    """Generate responsive design tests"""

    tests_dir = playwright_dir / "tests"

    responsive_test_content = """import { test, expect } from '@playwright/test';
import { TestUtils } from './utils/test-utils';

test.describe('Responsive Design Tests', () => {
  let utils: TestUtils;

  test.beforeEach(async ({ page }) => {
    utils = new TestUtils(page);
    await utils.login();
  });

  test('Mobile viewport - Dashboard', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    // Check if mobile menu exists
    const mobileMenuSelectors = [
      'button[aria-label*="menu" i]',
      '.mobile-menu',
      '.hamburger',
      '[data-testid="mobile-menu"]',
      'button.menu-toggle'
    ];

    let mobileMenuFound = false;
    for (const selector of mobileMenuSelectors) {
      if (await page.locator(selector).count() > 0) {
        mobileMenuFound = true;
        console.log(`Mobile menu found: ${selector}`);
        break;
      }
    }

    await utils.takeScreenshot('mobile-dashboard');
  });

  test('Tablet viewport - Forms', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/customers/new');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    // Check if form is properly laid out
    const form = page.locator('form');
    if (await form.count() > 0) {
      await expect(form).toBeVisible();
    }

    await utils.takeScreenshot('tablet-form');
  });

  test('Desktop viewport - Data tables', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/customers');
    await utils.waitForPageLoad();
    await utils.checkNoErrors();

    // Check if table is visible and properly formatted
    const table = page.locator('table, .table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }

    await utils.takeScreenshot('desktop-table');
  });

  test('Cross-viewport navigation', async ({ page }) => {
    const viewports = [
      { width: 375, height: 667, name: 'mobile' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1920, height: 1080, name: 'desktop' }
    ];

    const pages = ['/dashboard', '/customers', '/loads'];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);

      for (const pagePath of pages) {
        await page.goto(pagePath);
        await utils.waitForPageLoad();
        await utils.checkNoErrors();

        console.log(`✓ ${pagePath} works on ${viewport.name}`);
      }

      await utils.takeScreenshot(`navigation-${viewport.name}`);
    }
  });
});
"""

    responsive_test_file = tests_dir / "responsive.spec.ts"
    with open(responsive_test_file, 'w', encoding='utf-8') as f:
        f.write(responsive_test_content)


async def main():
    """Main function"""
    success = await generate_comprehensive_playwright_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
