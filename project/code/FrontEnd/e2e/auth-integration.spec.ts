import { test, expect } from '@playwright/test';

test.describe('Authentication Integration Tests', () => {
  const baseUrl = 'http://localhost:5000'; // Backend URL
  const frontendUrl = 'http://localhost:3020'; // Frontend URL
  
  // Test credentials from DbSeeder.cs
  const testCredentials = {
    admin: {
      email: 'admin@leadprocessing.com',
      password: 'Admin123!',
      firstName: 'Admin',
      lastName: 'User'
    },
    testUser: {
      email: 'test@leadprocessing.com', 
      password: 'Test123!',
      firstName: 'Test',
      lastName: 'User'
    }
  };

  test.beforeEach(async ({ page }) => {
    // Check if backend is running
    try {
      const response = await page.request.get(`${baseUrl}/health`);
      if (!response.ok()) {
        test.skip('Backend not running - skipping integration tests');
      }
    } catch (error) {
      test.skip('Backend not accessible - skipping integration tests');
    }
  });

  test('should authenticate via API with admin credentials', async ({ page, request }) => {
    // Test direct API authentication
    const loginResponse = await request.post(`${baseUrl}/api/v1/auth/login`, {
      data: {
        email: testCredentials.admin.email,
        password: testCredentials.admin.password,
        rememberMe: false
      }
    });

    expect(loginResponse.ok()).toBeTruthy();
    
    const loginResult = await loginResponse.json();
    expect(loginResult).toHaveProperty('accessToken');
    expect(loginResult).toHaveProperty('user');
    expect(loginResult.user.email).toBe(testCredentials.admin.email);
  });

  test('should authenticate via API with test user credentials', async ({ page, request }) => {
    // Test direct API authentication with test user
    const loginResponse = await request.post(`${baseUrl}/api/v1/auth/login`, {
      data: {
        email: testCredentials.testUser.email,
        password: testCredentials.testUser.password,
        rememberMe: false
      }
    });

    expect(loginResponse.ok()).toBeTruthy();
    
    const loginResult = await loginResponse.json();
    expect(loginResult).toHaveProperty('accessToken');
    expect(loginResult).toHaveProperty('user');
    expect(loginResult.user.email).toBe(testCredentials.testUser.email);
  });

  test('should reject invalid credentials', async ({ page, request }) => {
    const loginResponse = await request.post(`${baseUrl}/api/v1/auth/login`, {
      data: {
        email: 'invalid@example.com',
        password: 'wrongpassword',
        rememberMe: false
      }
    });

    expect(loginResponse.ok()).toBeFalsy();
    expect([400, 401, 403]).toContain(loginResponse.status());
  });

  test('should access protected API endpoints with valid token', async ({ page, request }) => {
    // First authenticate
    const loginResponse = await request.post(`${baseUrl}/api/v1/auth/login`, {
      data: {
        email: testCredentials.admin.email,
        password: testCredentials.admin.password,
        rememberMe: false
      }
    });

    const loginResult = await loginResponse.json();
    const token = loginResult.accessToken;

    // Try to access protected endpoint
    const protectedResponse = await request.get(`${baseUrl}/api/leads`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    expect(protectedResponse.ok()).toBeTruthy();
  });

  test('should be rejected from protected endpoints without token', async ({ page, request }) => {
    // Try to access protected endpoint without authentication
    const protectedResponse = await request.get(`${baseUrl}/api/leads`);
    
    // Should either be unauthorized or require auth
    expect([401, 403]).toContain(protectedResponse.status());
  });

  test.describe('Frontend Authentication Flow', () => {
    test('should display login page', async ({ page }) => {
      await page.goto(`${frontendUrl}/`);
      
      // Look for login-related elements
      const loginLink = page.getByRole('link', { name: /login|sign in/i });
      const loginForm = page.locator('form:has(input[type="email"])');
      
      if (await loginLink.isVisible()) {
        await loginLink.click();
      }
      
      // Check if we're on a login page or if login form is visible
      const hasLoginForm = await loginForm.isVisible();
      const hasEmailInput = await page.locator('input[type="email"]').isVisible();
      const hasPasswordInput = await page.locator('input[type="password"]').isVisible();
      
      expect(hasLoginForm || (hasEmailInput && hasPasswordInput)).toBeTruthy();
    });

    test('should handle login form submission', async ({ page }) => {
      await page.goto(`${frontendUrl}/`);
      
      // Try to find and fill login form
      const emailInput = page.locator('input[type="email"]').first();
      const passwordInput = page.locator('input[type="password"]').first();
      const submitButton = page.locator('button[type="submit"], input[type="submit"]').first();
      
      if (await emailInput.isVisible() && await passwordInput.isVisible()) {
        await emailInput.fill(testCredentials.testUser.email);
        await passwordInput.fill(testCredentials.testUser.password);
        
        if (await submitButton.isVisible()) {
          await submitButton.click();
          
          // Wait for potential redirect or success indication
          await page.waitForTimeout(2000);
          
          // Check for successful login indicators
          const userMenu = page.locator('[data-testid="user-menu"]');
          const dashboardAccess = page.locator('h1:has-text("Dashboard")');
          const welcomeMessage = page.locator(':has-text("Welcome")');
          
          const loginSuccessful = await userMenu.isVisible() || 
                                 await dashboardAccess.isVisible() || 
                                 await welcomeMessage.isVisible();
          
          // This might pass or fail depending on implementation
          // If it fails, it indicates the frontend auth flow needs work
          expect(loginSuccessful).toBeTruthy();
        }
      } else {
        test.skip('Login form not found - authentication may be handled differently');
      }
    });
  });

  test.describe('JWT Token Tests', () => {
    test('should validate JWT token structure', async ({ page, request }) => {
      const loginResponse = await request.post(`${baseUrl}/api/v1/auth/login`, {
        data: {
          email: testCredentials.admin.email,
          password: testCredentials.admin.password,
          rememberMe: false
        }
      });

      const loginResult = await loginResponse.json();
      const token = loginResult.accessToken;

      // Basic JWT structure validation (3 parts separated by dots)
      const tokenParts = token.split('.');
      expect(tokenParts).toHaveLength(3);
      
      // Each part should be base64 encoded
      expect(tokenParts[0]).toMatch(/^[A-Za-z0-9_-]+$/);
      expect(tokenParts[1]).toMatch(/^[A-Za-z0-9_-]+$/);
      expect(tokenParts[2]).toMatch(/^[A-Za-z0-9_-]+$/);
    });
  });
});