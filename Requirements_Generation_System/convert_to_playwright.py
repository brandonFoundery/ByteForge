#!/usr/bin/env python3
"""
Generate comprehensive Playwright tests for local execution
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
        # Create Playwright tests directory
        base_path = Path(__file__).parent.parent
        playwright_dir = base_path / "generated_documents" / "testing" / "playwright_tests"
        playwright_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate comprehensive Playwright test files
        await generate_playwright_config(playwright_dir)
        await generate_playwright_package_json(playwright_dir)
        await generate_playwright_page_tests(playwright_dir)
        await generate_playwright_auth_tests(playwright_dir)
        await generate_playwright_interactive_tests(playwright_dir)
        await generate_playwright_admin_tests(playwright_dir)
        await generate_playwright_workflow_tests(playwright_dir)
        await generate_playwright_responsive_tests(playwright_dir)
        await generate_playwright_utils(playwright_dir)
        
        console.print(f"[bold green]🎉 Playwright Tests Generated![/bold green]")
        console.print(f"[cyan]Location: {playwright_dir}[/cyan]")
        console.print(f"\n[yellow]To run the tests:[/yellow]")
        console.print(f"1. cd {playwright_dir}")
        console.print(f"2. npm install")
        console.print(f"3. npx playwright install")
        console.print(f"4. npm test")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error converting tests: {e}[/red]")
        return False


async def generate_playwright_config(playwright_dir):
    """Generate Playwright configuration"""
    
    config_content = """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:4001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
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
  ],

  webServer: {
    command: 'echo "Make sure your frontend is running on http://localhost:4001"',
    url: 'http://localhost:4001',
    reuseExistingServer: !process.env.CI,
  },
});
"""
    
    config_file = playwright_dir / "playwright.config.ts"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)


async def generate_playwright_package_json(playwright_dir):
    """Generate package.json for Playwright tests"""
    
    package_content = """{
  "name": "fy-wb-midway-tests",
  "version": "1.0.0",
  "description": "Playwright tests for FY.WB.Midway frontend",
  "scripts": {
    "test": "playwright test",
    "test:headed": "playwright test --headed",
    "test:debug": "playwright test --debug",
    "report": "playwright show-report"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "@types/node": "^20.0.0"
  }
}
"""
    
    package_file = playwright_dir / "package.json"
    with open(package_file, 'w', encoding='utf-8') as f:
        f.write(package_content)


async def generate_playwright_page_tests(playwright_dir):
    """Generate Playwright page load tests"""
    
    tests_dir = playwright_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    page_test_content = """import { test, expect } from '@playwright/test';

test.describe('Page Load Tests', () => {
  test('Homepage loads correctly', async ({ page }) => {
    await page.goto('/');
    await expect(page).not.toHaveTitle(/404|Error/);
    await page.screenshot({ path: 'homepage_load_test.png' });
  });

  test('Login page loads correctly', async ({ page }) => {
    await page.goto('/login');
    await expect(page).not.toContainText('404');
    await expect(page).not.toContainText('Error');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await page.screenshot({ path: 'login_load_test.png' });
  });

  test('Dashboard loads after login', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
    await expect(page).toHaveURL(/dashboard/);
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'dashboard_load_test.png' });
  });

  test('Admin panel loads correctly', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
    
    // Navigate to admin
    await page.goto('/admin');
    await expect(page).not.toContainText('Unauthorized');
    await expect(page).not.toContainText('404');
    await page.screenshot({ path: 'admin_load_test.png' });
  });

  test('Customers page loads correctly', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
    
    await page.goto('/customers');
    await expect(page).not.toContainText('404');
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'customers_load_test.png' });
  });

  test('Loads page loads correctly', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
    
    await page.goto('/loads');
    await expect(page).not.toContainText('404');
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'loads_load_test.png' });
  });
});
"""
    
    page_test_file = tests_dir / "page-load.spec.ts"
    with open(page_test_file, 'w', encoding='utf-8') as f:
        f.write(page_test_content)


async def generate_playwright_interactive_tests(playwright_dir):
    """Generate Playwright interactive tests"""
    
    tests_dir = playwright_dir / "tests"
    
    interactive_test_content = """import { test, expect } from '@playwright/test';

test.describe('Interactive Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('Customer creation workflow', async ({ page }) => {
    await page.goto('/customers/new');
    
    // Fill customer form
    await page.fill('input[name="companyName"], input[placeholder*="Company"]', 'Test Company Inc.');
    await page.fill('input[name="contactName"], input[placeholder*="Contact"]', 'John Doe');
    await page.fill('input[name="email"], input[type="email"]', 'test@example.com');
    await page.fill('input[name="phone"], input[placeholder*="Phone"]', '+1-555-123-4567');
    
    // Submit form
    await page.click('button:has-text("Save"), button[type="submit"]');
    
    // Verify success
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'customer_creation_success.png' });
  });

  test('Load creation workflow', async ({ page }) => {
    await page.goto('/loads/new');
    
    // Fill load form
    await page.fill('input[name="origin"], input[placeholder*="Origin"]', 'Chicago, IL');
    await page.fill('input[name="destination"], input[placeholder*="Destination"]', 'Dallas, TX');
    await page.fill('input[name="weight"], input[placeholder*="Weight"]', '5000');
    
    // Select equipment type if dropdown exists
    const equipmentSelect = page.locator('select[name="equipmentType"], select:has-text("Equipment")');
    if (await equipmentSelect.count() > 0) {
      await equipmentSelect.selectOption('Dry Van');
    }
    
    // Submit form
    await page.click('button:has-text("Save"), button[type="submit"]');
    
    // Verify success
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'load_creation_success.png' });
  });

  test('Invoice creation workflow', async ({ page }) => {
    await page.goto('/invoices/new');
    
    // Fill invoice form
    const customerSelect = page.locator('select[name="customer"], select:has-text("Customer")');
    if (await customerSelect.count() > 0) {
      await customerSelect.selectOption({ index: 1 }); // Select first customer
    }
    
    await page.fill('input[name="description"], textarea[name="description"]', 'Test Invoice');
    await page.fill('input[name="amount"], input[placeholder*="Amount"]', '1000.00');
    
    // Submit form
    await page.click('button:has-text("Save"), button[type="submit"]');
    
    // Verify success
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'invoice_creation_success.png' });
  });

  test('Navigation menu functionality', async ({ page }) => {
    // Test main navigation links
    const navLinks = ['Customers', 'Loads', 'Invoices', 'Reports'];
    
    for (const linkText of navLinks) {
      const link = page.locator(`a:has-text("${linkText}"), button:has-text("${linkText}")`);
      if (await link.count() > 0) {
        await link.click();
        await expect(page).not.toContainText('404');
        await expect(page).not.toContainText('Error');
        await page.screenshot({ path: `navigation_${linkText.toLowerCase()}.png` });
      }
    }
  });
});
"""
    
    interactive_test_file = tests_dir / "interactive.spec.ts"
    with open(interactive_test_file, 'w', encoding='utf-8') as f:
        f.write(interactive_test_content)


async def generate_playwright_auth_tests(playwright_dir):
    """Generate authentication-specific tests"""

    tests_dir = playwright_dir / "tests"

    auth_test_content = """import { test, expect } from '@playwright/test';

test.describe('Authentication Tests', () => {
  test('Login page loads correctly', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveTitle(/Login|Sign In/i);
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"], button:has-text("Login")')).toBeVisible();
  });

  test('Valid login works', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/dashboard|admin/);
    await expect(page).not.toContainText('Invalid credentials');
    await expect(page).not.toContainText('Login failed');
  });

  test('Invalid login shows error', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"], button:has-text("Login")');

    // Should show error message
    await expect(page).toContainText(/Invalid|Error|Failed/i);
    await expect(page).toHaveURL(/login/);
  });

  test('Empty form validation', async ({ page }) => {
    await page.goto('/login');
    await page.click('button[type="submit"], button:has-text("Login")');

    // Should show validation errors
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');

    await expect(emailInput).toHaveAttribute('required', '');
    await expect(passwordInput).toHaveAttribute('required', '');
  });

  test('Logout functionality', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');

    // Find and click logout
    const logoutButton = page.locator('button:has-text("Logout"), a:has-text("Logout"), button:has-text("Sign Out")');
    if (await logoutButton.count() > 0) {
      await logoutButton.click();
      await expect(page).toHaveURL(/login|home/);
    }
  });

  test('Protected route redirects to login', async ({ page }) => {
    // Try to access protected route without login
    await page.goto('/admin');
    await expect(page).toHaveURL(/login/);
  });
});
"""

    auth_test_file = tests_dir / "auth.spec.ts"
    with open(auth_test_file, 'w', encoding='utf-8') as f:
        f.write(auth_test_content)


async def generate_playwright_admin_tests(playwright_dir):
    """Generate admin panel tests"""

    tests_dir = playwright_dir / "tests"

    admin_test_content = """import { test, expect } from '@playwright/test';

test.describe('Admin Panel Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
    await expect(page).toHaveURL(/dashboard|admin/);
  });

  test('Admin dashboard loads', async ({ page }) => {
    await page.goto('/admin');
    await expect(page).not.toContainText('Unauthorized');
    await expect(page).not.toContainText('403');
    await expect(page).not.toContainText('Access Denied');
  });

  test('User management page loads', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page).not.toContainText('404');
    await expect(page).not.toContainText('Error');

    // Should show user-related content
    await expect(page).toContainText(/Users|User Management/i);
  });

  test('Tenant management page loads', async ({ page }) => {
    await page.goto('/admin/tenants');
    await expect(page).not.toContainText('404');
    await expect(page).not.toContainText('Error');

    // Should show tenant-related content
    await expect(page).toContainText(/Tenants|Tenant Management/i);
  });

  test('Settings page loads', async ({ page }) => {
    await page.goto('/admin/settings');
    await expect(page).not.toContainText('404');
    await expect(page).not.toContainText('Error');

    // Should show settings content
    await expect(page).toContainText(/Settings|Configuration/i);
  });

  test('Admin navigation menu', async ({ page }) => {
    await page.goto('/admin');

    // Test admin navigation links
    const adminLinks = ['Users', 'Tenants', 'Settings'];

    for (const linkText of adminLinks) {
      const link = page.locator(`a:has-text("${linkText}"), button:has-text("${linkText}")`);
      if (await link.count() > 0) {
        await link.click();
        await expect(page).not.toContainText('404');
        await expect(page).not.toContainText('Error');
      }
    }
  });
});
"""

    admin_test_file = tests_dir / "admin.spec.ts"
    with open(admin_test_file, 'w', encoding='utf-8') as f:
        f.write(admin_test_content)


async def generate_playwright_responsive_tests(playwright_dir):
    """Generate responsive design tests"""

    tests_dir = playwright_dir / "tests"

    responsive_test_content = """import { test, expect } from '@playwright/test';

test.describe('Responsive Design Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
  });

  test('Mobile viewport - Dashboard', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');

    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'mobile-dashboard.png' });

    // Check if mobile menu exists
    const mobileMenu = page.locator('button[aria-label*="menu"], .mobile-menu, .hamburger');
    if (await mobileMenu.count() > 0) {
      await expect(mobileMenu).toBeVisible();
    }
  });

  test('Tablet viewport - Customers', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/customers');

    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'tablet-customers.png' });
  });

  test('Desktop viewport - Loads', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/loads');

    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'desktop-loads.png' });
  });

  test('Form responsiveness', async ({ page }) => {
    const viewports = [
      { width: 375, height: 667, name: 'mobile' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1920, height: 1080, name: 'desktop' }
    ];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.goto('/customers/new');

      // Check if form is usable
      const form = page.locator('form');
      if (await form.count() > 0) {
        await expect(form).toBeVisible();

        // Check if form inputs are accessible
        const inputs = page.locator('input, select, textarea');
        const inputCount = await inputs.count();
        if (inputCount > 0) {
          await expect(inputs.first()).toBeVisible();
        }
      }

      await page.screenshot({ path: `form-${viewport.name}.png` });
    }
  });
});
"""

    responsive_test_file = tests_dir / "responsive.spec.ts"
    with open(responsive_test_file, 'w', encoding='utf-8') as f:
        f.write(responsive_test_content)


async def generate_playwright_utils(playwright_dir):
    """Generate utility functions for tests"""

    utils_content = """import { Page, expect } from '@playwright/test';

export class TestUtils {
  constructor(private page: Page) {}

  async login(email: string = 'admin@example.com', password: string = 'AdminPass123!') {
    await this.page.goto('/login');
    await this.page.fill('input[type="email"]', email);
    await this.page.fill('input[type="password"]', password);
    await this.page.click('button[type="submit"], button:has-text("Login")');
    await expect(this.page).toHaveURL(/dashboard|admin/);
  }

  async logout() {
    const logoutButton = this.page.locator('button:has-text("Logout"), a:has-text("Logout"), button:has-text("Sign Out")');
    if (await logoutButton.count() > 0) {
      await logoutButton.click();
    }
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).not.toContainText('Loading...');
  }

  async checkNoErrors() {
    await expect(this.page).not.toContainText('Error');
    await expect(this.page).not.toContainText('404');
    await expect(this.page).not.toContainText('500');
    await expect(this.page).not.toContainText('Something went wrong');
  }

  async fillForm(formData: Record<string, string>) {
    for (const [field, value] of Object.entries(formData)) {
      const input = this.page.locator(`input[name="${field}"], input[placeholder*="${field}"], textarea[name="${field}"]`);
      if (await input.count() > 0) {
        await input.fill(value);
      }
    }
  }

  async submitForm() {
    await this.page.click('button[type="submit"], button:has-text("Save"), button:has-text("Submit")');
  }

  async navigateToPage(path: string) {
    await this.page.goto(path);
    await this.waitForPageLoad();
    await this.checkNoErrors();
  }
}

export const testData = {
  customer: {
    companyName: 'Test Company Inc.',
    contactName: 'John Doe',
    email: 'test@example.com',
    phone: '+1-555-123-4567'
  },
  load: {
    origin: 'Chicago, IL',
    destination: 'Dallas, TX',
    weight: '5000',
    equipmentType: 'Dry Van'
  },
  invoice: {
    description: 'Test Invoice',
    amount: '1000.00'
  }
};
"""

    utils_file = playwright_dir / "utils" / "test-utils.ts"
    utils_file.parent.mkdir(exist_ok=True)
    with open(utils_file, 'w', encoding='utf-8') as f:
        f.write(utils_content)


async def generate_playwright_workflow_tests(playwright_dir):
    """Generate Playwright workflow tests"""

    tests_dir = playwright_dir / "tests"

    workflow_test_content = """import { test, expect } from '@playwright/test';

test.describe('End-to-End Workflows', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'AdminPass123!');
    await page.click('button[type="submit"], button:has-text("Login")');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('Complete customer workflow', async ({ page }) => {
    // Step 1: Create Customer
    await page.goto('/customers/new');
    await page.fill('input[name="companyName"], input[placeholder*="Company"]', 'Workflow Test Company');
    await page.fill('input[name="contactName"], input[placeholder*="Contact"]', 'Workflow Contact');
    await page.fill('input[name="email"], input[type="email"]', 'workflow@test.com');
    await page.click('button:has-text("Save"), button[type="submit"]');
    await expect(page).not.toContainText('Error');
    
    // Step 2: Create Load for Customer
    await page.goto('/loads/new');
    const customerSelect = page.locator('select[name="customer"], select:has-text("Customer")');
    if (await customerSelect.count() > 0) {
      await customerSelect.selectOption('Workflow Test Company');
    }
    await page.fill('input[name="origin"]', 'Chicago, IL');
    await page.fill('input[name="destination"]', 'Dallas, TX');
    await page.click('button:has-text("Save"), button[type="submit"]');
    await expect(page).not.toContainText('Error');
    
    // Step 3: Generate Invoice
    await page.goto('/invoices/new');
    const invoiceCustomerSelect = page.locator('select[name="customer"], select:has-text("Customer")');
    if (await invoiceCustomerSelect.count() > 0) {
      await invoiceCustomerSelect.selectOption('Workflow Test Company');
    }
    await page.fill('input[name="description"], textarea[name="description"]', 'Workflow Invoice');
    await page.click('button:has-text("Save"), button[type="submit"]');
    await expect(page).not.toContainText('Error');
    
    await page.screenshot({ path: 'complete_workflow_success.png' });
  });

  test('Admin management workflow', async ({ page }) => {
    // Step 1: Access Admin Panel
    await page.goto('/admin');
    await expect(page).not.toContainText('Unauthorized');
    await expect(page).toContainText('Admin', { timeout: 10000 });
    
    // Step 2: Check Users Management
    const usersLink = page.locator('a:has-text("Users"), button:has-text("Users")');
    if (await usersLink.count() > 0) {
      await usersLink.click();
      await expect(page).not.toContainText('404');
    }
    
    // Step 3: Check System Settings
    const settingsLink = page.locator('a:has-text("Settings"), button:has-text("Settings")');
    if (await settingsLink.count() > 0) {
      await settingsLink.click();
      await expect(page).not.toContainText('404');
    }
    
    await page.screenshot({ path: 'admin_workflow_success.png' });
  });

  test('Responsive design check', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'mobile_dashboard.png' });
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/customers');
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'tablet_customers.png' });
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/loads');
    await expect(page).not.toContainText('Error');
    await page.screenshot({ path: 'desktop_loads.png' });
  });
});
"""
    
    workflow_test_file = tests_dir / "workflows.spec.ts"
    with open(workflow_test_file, 'w', encoding='utf-8') as f:
        f.write(workflow_test_content)


async def main():
    """Main function"""
    success = await generate_comprehensive_playwright_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
