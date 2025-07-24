import { test, expect } from './fixtures/test-base';

test.describe('ByteForge Smoke Tests', () => {
  test('should load the home page', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/ByteForge/);
    
    // Check for main elements
    const mainHeading = page.locator('h1').first();
    await expect(mainHeading).toBeVisible();
  });

  test('should navigate to login page', async ({ page, navigationHelper }) => {
    await navigationHelper.goToLogin();
    
    // Verify we're on the login page
    await expect(page).toHaveURL(/.*\/auth\/login/);
    
    // Check for login form elements
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should navigate to register page', async ({ page, navigationHelper }) => {
    await navigationHelper.goToRegister();
    
    // Verify we're on the register page
    await expect(page).toHaveURL(/.*\/auth\/register/);
    
    // Check for registration form elements
    await expect(page.locator('input[name="firstName"]')).toBeVisible();
    await expect(page.locator('input[name="lastName"]')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
  });

  test('should have responsive design', async ({ page }) => {
    await page.goto('/');
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('body')).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('body')).toBeVisible();
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('body')).toBeVisible();
  });

  test('should handle 404 pages gracefully', async ({ page }) => {
    await page.goto('/non-existent-page');
    
    // Should show 404 or redirect to home
    const is404 = await page.locator('text=/404|not found/i').isVisible().catch(() => false);
    const isHome = await page.url().endsWith('/');
    
    expect(is404 || isHome).toBeTruthy();
  });
});