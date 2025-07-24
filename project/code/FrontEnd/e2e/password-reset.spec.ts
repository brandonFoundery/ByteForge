import { test, expect } from '@playwright/test';

test.describe('Password Reset', () => {
  test.describe('Forgot Password Page', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/auth/forgot-password');
    });

    test('should display forgot password form', async ({ page }) => {
      // Check that forgot password page loads correctly
      await expect(page).toHaveTitle(/Lead Processing/);
      
      // Should show forgot password form elements
      await expect(page.getByRole('heading', { name: /Forgot Password/i })).toBeVisible();
      await expect(page.locator('input[name="email"]')).toBeVisible();
      await expect(page.getByRole('button', { name: /Send Reset Link/i })).toBeVisible();
      
      // Should have navigation links
      await expect(page.getByRole('link', { name: /Remember your password\? Sign in/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /Sign up/i })).toBeVisible();
    });

    test('should show validation error on empty email submission', async ({ page }) => {
      // Try to submit empty form
      await page.getByRole('button', { name: /Send Reset Link/i }).click();
      
      // Should show HTML5 validation error
      const emailField = page.locator('input[name="email"]');
      await expect(emailField).toHaveAttribute('required');
    });

    test('should handle successful forgot password submission', async ({ page }) => {
      // Fill in email
      await page.locator('input[name="email"]').fill('test@example.com');
      
      // Submit form
      await page.getByRole('button', { name: /Send Reset Link/i }).click();
      
      // Should show success message
      await expect(page.getByRole('heading', { name: /Check Your Email/i })).toBeVisible({ timeout: 5000 });
      await expect(page.getByText(/we've sent you a password reset link/i)).toBeVisible();
      
      // Should have option to try again
      await expect(page.getByRole('button', { name: /Try again/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /Back to Sign In/i })).toBeVisible();
    });

    test('should allow user to try again after success', async ({ page }) => {
      // Fill in email and submit
      await page.locator('input[name="email"]').fill('test@example.com');
      await page.getByRole('button', { name: /Send Reset Link/i }).click();
      
      // Wait for success message
      await expect(page.getByRole('heading', { name: /Check Your Email/i })).toBeVisible({ timeout: 5000 });
      
      // Click try again
      await page.getByRole('button', { name: /Try again/i }).click();
      
      // Should be back to the form
      await expect(page.getByRole('heading', { name: /Forgot Password/i })).toBeVisible();
      await expect(page.locator('input[name="email"]')).toBeVisible();
    });

    test('should navigate to login page', async ({ page }) => {
      // Click sign in link
      await page.getByRole('link', { name: /Remember your password\? Sign in/i }).click();
      await page.waitForLoadState('networkidle');
      
      // Should be on login page
      await expect(page).toHaveURL(/.*\/auth\/login/);
      await expect(page.getByRole('heading', { name: /Welcome Back/i })).toBeVisible();
    });

    test('should navigate to registration page', async ({ page }) => {
      // Click sign up link
      await page.getByRole('link', { name: /Sign up/i }).click();
      await page.waitForLoadState('networkidle');
      
      // Should be on registration page
      await expect(page).toHaveURL(/.*\/auth\/register/);
      await expect(page.getByRole('heading', { name: /Create Account/i })).toBeVisible();
    });
  });

  test.describe('Reset Password Page', () => {
    test('should show invalid token message when no token provided', async ({ page }) => {
      // Navigate to reset password page without token
      await page.goto('/auth/reset-password');
      
      // Should show invalid token message
      await expect(page.getByRole('heading', { name: /Invalid Reset Link/i })).toBeVisible();
      await expect(page.getByText(/invalid, expired, or has already been used/i)).toBeVisible();
      
      // Should have navigation links
      await expect(page.getByRole('link', { name: /Request a new reset link/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /Back to Sign In/i })).toBeVisible();
    });

    test('should show reset form with valid token', async ({ page }) => {
      // Navigate to reset password page with token
      await page.goto('/auth/reset-password?token=valid-reset-token');
      
      // Should show reset password form
      await expect(page.getByRole('heading', { name: /Reset Password/i })).toBeVisible();
      await expect(page.locator('input[name="password"]')).toBeVisible();
      await expect(page.locator('input[name="confirmPassword"]')).toBeVisible();
      await expect(page.getByRole('button', { name: /Reset Password/i })).toBeVisible();
      
      // Should have back to sign in link
      await expect(page.getByRole('link', { name: /Back to Sign In/i })).toBeVisible();
    });

    test('should show validation errors on empty form submission', async ({ page }) => {
      // Navigate with valid token
      await page.goto('/auth/reset-password?token=valid-reset-token');
      
      // Try to submit empty form
      await page.getByRole('button', { name: /Reset Password/i }).click();
      
      // Should show HTML5 validation errors
      const passwordField = page.locator('input[name="password"]');
      const confirmPasswordField = page.locator('input[name="confirmPassword"]');
      
      await expect(passwordField).toHaveAttribute('required');
      await expect(confirmPasswordField).toHaveAttribute('required');
    });

    test('should show password mismatch error', async ({ page }) => {
      // Navigate with valid token
      await page.goto('/auth/reset-password?token=valid-reset-token');
      
      // Fill in mismatched passwords
      await page.locator('input[name="password"]').fill('newpassword123');
      await page.locator('input[name="confirmPassword"]').fill('differentpassword');
      
      // Submit form
      await page.getByRole('button', { name: /Reset Password/i }).click();
      
      // Should show password mismatch error
      await expect(page.getByText(/Passwords do not match/i)).toBeVisible({ timeout: 5000 });
    });

    test('should handle successful password reset', async ({ page }) => {
      // Navigate with valid token
      await page.goto('/auth/reset-password?token=valid-reset-token');
      
      // Fill in matching passwords
      await page.locator('input[name="password"]').fill('newpassword123');
      await page.locator('input[name="confirmPassword"]').fill('newpassword123');
      
      // Submit form
      await page.getByRole('button', { name: /Reset Password/i }).click();
      
      // Should show success message
      await expect(page.getByRole('heading', { name: /Password Reset Successful/i })).toBeVisible({ timeout: 5000 });
      await expect(page.getByText(/successfully reset/i)).toBeVisible();
      
      // Should have continue to sign in link
      await expect(page.getByRole('link', { name: /Continue to Sign In/i })).toBeVisible();
    });

    test('should navigate to login after successful reset', async ({ page }) => {
      // Navigate with valid token
      await page.goto('/auth/reset-password?token=valid-reset-token');
      
      // Fill in matching passwords and submit
      await page.locator('input[name="password"]').fill('newpassword123');
      await page.locator('input[name="confirmPassword"]').fill('newpassword123');
      await page.getByRole('button', { name: /Reset Password/i }).click();
      
      // Wait for success message
      await expect(page.getByRole('heading', { name: /Password Reset Successful/i })).toBeVisible({ timeout: 5000 });
      
      // Click continue to sign in
      await page.getByRole('link', { name: /Continue to Sign In/i }).click();
      await page.waitForLoadState('networkidle');
      
      // Should be on login page
      await expect(page).toHaveURL(/.*\/auth\/login/);
      await expect(page.getByRole('heading', { name: /Welcome Back/i })).toBeVisible();
    });

    test('should navigate to forgot password from invalid token page', async ({ page }) => {
      // Navigate without token
      await page.goto('/auth/reset-password');
      
      // Click request new reset link
      await page.getByRole('link', { name: /Request a new reset link/i }).click();
      await page.waitForLoadState('networkidle');
      
      // Should be on forgot password page
      await expect(page).toHaveURL(/.*\/auth\/forgot-password/);
      await expect(page.getByRole('heading', { name: /Forgot Password/i })).toBeVisible();
    });
  });
});