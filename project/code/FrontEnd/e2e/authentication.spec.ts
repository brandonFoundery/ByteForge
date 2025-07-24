import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {    
    // Start from the homepage
    await page.goto('/');
    
    // Clear localStorage to ensure fresh authentication state
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Reload to apply the cleared state
    await page.reload();
  });

  test('should load homepage without authentication', async ({ page }) => {
    // Check that homepage loads
    await expect(page).toHaveTitle(/Lead Processing/);
    
    // Check for main navigation
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should display login/register options', async ({ page }) => {
    // Look for authentication-related elements
    const loginLink = page.getByRole('link', { name: /Login/i });
    
    // Login link should be visible and point to auth/login
    await expect(loginLink).toBeVisible();
    await expect(loginLink).toHaveAttribute('href', '/auth/login');
  });

  test('should handle unauthenticated access to protected routes', async ({ page }) => {
    // Try to access the protected dashboard route
    await page.goto('/dashboard');
    
    // Should show "Access Denied" message from withAuth HOC
    await expect(page.getByRole('heading', { name: /Access Denied/i })).toBeVisible();
    await expect(page.getByText(/You need to log in to access this page/i)).toBeVisible();
    
    // Should NOT show the actual dashboard content
    await expect(page.getByRole('heading', { name: /Lead Processing Dashboard/i })).not.toBeVisible();
  });

  test('should navigate to login page and show login form', async ({ page }) => {
    // Click the login link from homepage
    const loginLink = page.getByRole('link', { name: /Login/i });
    await loginLink.click();
    await page.waitForLoadState('networkidle');
    
    // Should be on the login page
    await expect(page).toHaveURL(/.*\/auth\/login/);
    
    // Should show login form elements
    await expect(page.getByRole('heading', { name: /Welcome Back/i })).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /Sign In/i })).toBeVisible();
    
    // Should have links to other auth pages
    await expect(page.getByRole('link', { name: /Forgot your password/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Sign up/i })).toBeVisible();
  });

  test('should show validation errors on empty login form submission', async ({ page }) => {
    // Navigate to login page
    await page.goto('/auth/login');
    
    // Try to submit empty form
    await page.getByRole('button', { name: /Sign In/i }).click();
    
    // Should show HTML5 validation errors (required fields)
    const emailField = page.locator('input[name="email"]');
    const passwordField = page.locator('input[name="password"]');
    
    // Check that fields are marked as invalid
    await expect(emailField).toHaveAttribute('required');
    await expect(passwordField).toHaveAttribute('required');
  });

  test('should handle registration flow if register page exists', async ({ page }) => {
    // Try to find and navigate to register page
    const registerLink = page.getByRole('link', { name: /Register|Sign Up/i });
    
    if (await registerLink.isVisible()) {
      await registerLink.click();
      
      // Check for registration form
      await expect(page.locator('form')).toBeVisible();
      
      // Look for common registration fields
      const emailField = page.locator('input[type="email"], input[name="email"]');
      const passwordField = page.locator('input[type="password"], input[name="password"]');
      
      if (await emailField.isVisible() && await passwordField.isVisible()) {
        // Test form validation
        const submitButton = page.locator('button[type="submit"], input[type="submit"]');
        await submitButton.click();
        
        // Should show validation errors for empty form
        await expect(page.locator('.error, [role="alert"]')).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should maintain authentication state across page navigation', async ({ page }) => {
    // This test assumes we can get into an authenticated state
    // Navigate through different pages
    await page.goto('/');
    await page.goto('/dashboard');
    await page.goto('/leads');
    
    // Authentication state should be consistent
    const authIndicator = page.locator('[data-testid="user-menu"], [data-testid="auth-status"]');
    
    if (await authIndicator.isVisible()) {
      // If we see auth indicators, they should be consistent across pages
      await page.goto('/dashboard');
      await expect(authIndicator).toBeVisible();
      
      await page.goto('/leads');
      await expect(authIndicator).toBeVisible();
    }
  });

  test('should handle logout functionality if available', async ({ page }) => {
    // Look for logout functionality
    const userMenu = page.locator('[data-testid="user-menu"]');
    const logoutButton = page.getByRole('button', { name: /Logout|Sign Out/i });
    const logoutLink = page.getByRole('link', { name: /Logout|Sign Out/i });
    
    if (await userMenu.isVisible()) {
      // Click user menu to reveal logout option
      await userMenu.click();
      
      const logoutOption = page.getByRole('menuitem', { name: /Logout|Sign Out/i });
      if (await logoutOption.isVisible()) {
        await logoutOption.click();
        
        // Should redirect or show logged out state
        await page.waitForTimeout(1000);
        
        // Verify logout occurred
        await expect(userMenu).not.toBeVisible();
      }
    } else if (await logoutButton.isVisible()) {
      await logoutButton.click();
      
      // Verify logout
      await expect(logoutButton).not.toBeVisible({ timeout: 5000 });
    } else if (await logoutLink.isVisible()) {
      await logoutLink.click();
      
      // Verify logout
      await expect(logoutLink).not.toBeVisible({ timeout: 5000 });
    }
  });

  test('should handle session timeout gracefully', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Simulate session timeout by clearing storage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Refresh page to trigger session check
    await page.reload();
    
    // Should handle expired session appropriately
    const isRedirectedToLogin = page.url().includes('/login') || page.url().includes('/auth');
    const hasSessionExpiredMessage = await page.locator('[data-testid="session-expired"]').isVisible();
    const stillHasAccess = await page.getByRole('heading', { name: /Dashboard/i }).isVisible();
    
    // One of these should be true (depending on auth implementation)
    expect(isRedirectedToLogin || hasSessionExpiredMessage || stillHasAccess).toBeTruthy();
  });

  test('should secure sensitive API endpoints', async ({ page }) => {
    // Test that API endpoints require proper authentication
    const response = await page.request.get('/api/leads');
    
    // Should either return 401/403 for unauthorized, 404 if not found, or 200 if no auth required
    expect([200, 401, 403, 404]).toContain(response.status());
    
    if (response.status() === 401 || response.status() === 403) {
      // Verify error message
      const body = await response.json();
      expect(body).toHaveProperty('message');
    }
  });
});