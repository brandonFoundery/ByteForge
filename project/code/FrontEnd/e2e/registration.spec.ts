import { test, expect } from '@playwright/test';

test.describe('Registration', () => {
  test.beforeEach(async ({ page }) => {
    // Start from the registration page
    await page.goto('/auth/register');
  });

  test('should display registration form', async ({ page }) => {
    // Check that registration page loads correctly
    await expect(page).toHaveTitle(/Lead Processing/);
    
    // Should show registration form elements
    await expect(page.getByRole('heading', { name: /Create Account/i })).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('input[name="confirmPassword"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /Create Account/i })).toBeVisible();
    
    // Should have link to login page
    await expect(page.getByRole('link', { name: /Sign in/i })).toBeVisible();
  });

  test('should show validation errors on empty form submission', async ({ page }) => {
    // Try to submit empty form
    await page.getByRole('button', { name: /Create Account/i }).click();
    
    // Should show HTML5 validation errors (required fields)
    const emailField = page.locator('input[name="email"]');
    const passwordField = page.locator('input[name="password"]');
    const confirmPasswordField = page.locator('input[name="confirmPassword"]');
    
    // Check that fields are marked as required
    await expect(emailField).toHaveAttribute('required');
    await expect(passwordField).toHaveAttribute('required');
    await expect(confirmPasswordField).toHaveAttribute('required');
  });

  test('should navigate to login page from registration', async ({ page }) => {
    // Click the sign in link
    await page.getByRole('link', { name: /Sign in/i }).click();
    await page.waitForLoadState('networkidle');
    
    // Should be on the login page
    await expect(page).toHaveURL(/.*\/auth\/login/);
    await expect(page.getByRole('heading', { name: /Welcome Back/i })).toBeVisible();
  });

  test('should show password mismatch error', async ({ page }) => {
    // Fill in form with mismatched passwords
    await page.locator('input[name="email"]').fill('test@example.com');
    await page.locator('input[name="password"]').fill('password123');
    await page.locator('input[name="confirmPassword"]').fill('differentpassword');
    
    // Submit form
    await page.getByRole('button', { name: /Create Account/i }).click();
    
    // Should show password mismatch error
    await expect(page.getByText(/Passwords do not match/i)).toBeVisible({ timeout: 5000 });
  });

  test('should handle successful registration flow', async ({ page }) => {
    // Mock successful registration by intercepting API calls
    await page.route('**/api/v1/auth/register', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            id: '123',
            email: 'test@example.com',
            userName: 'test@example.com'
          },
          message: 'User registered successfully'
        })
      });
    });

    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            accessToken: 'mock-jwt-token',
            refreshToken: 'mock-refresh-token',
            expiresIn: 3600,
            tokenType: 'Bearer',
            user: {
              id: '123',
              email: 'test@example.com',
              userName: 'test@example.com'
            }
          },
          message: 'Login successful'
        })
      });
    });

    // Fill in registration form
    await page.locator('input[name="email"]').fill('test@example.com');
    await page.locator('input[name="password"]').fill('password123');
    await page.locator('input[name="confirmPassword"]').fill('password123');
    
    // Submit form
    await page.getByRole('button', { name: /Create Account/i }).click();
    
    // Should redirect to dashboard after successful registration and auto-login
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: /Lead Processing Dashboard/i })).toBeVisible();
  });

  test('should handle registration failure', async ({ page }) => {
    // Mock registration failure
    await page.route('**/api/v1/auth/register', async route => {
      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          message: 'User with this email already exists'
        })
      });
    });

    // Fill in registration form
    await page.locator('input[name="email"]').fill('existing@example.com');
    await page.locator('input[name="password"]').fill('password123');
    await page.locator('input[name="confirmPassword"]').fill('password123');
    
    // Submit form
    await page.getByRole('button', { name: /Create Account/i }).click();
    
    // Should show error message
    await expect(page.getByText(/User with this email already exists/i)).toBeVisible({ timeout: 5000 });
    
    // Should still be on registration page
    await expect(page).toHaveURL(/.*\/auth\/register/);
  });

  test('should redirect authenticated users to dashboard', async ({ page }) => {
    // Mock authenticated state by setting localStorage
    await page.addInitScript(() => {
      localStorage.setItem('user', JSON.stringify({
        id: '123',
        email: 'test@example.com',
        userName: 'test@example.com'
      }));
      // Mock token in apiClient
      window.localStorage.setItem('authToken', 'mock-jwt-token');
    });

    // Try to access registration page
    await page.goto('/auth/register');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 5000 });
  });
});