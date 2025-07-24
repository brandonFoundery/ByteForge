import { Page, APIRequestContext } from '@playwright/test';

export class AuthHelper {
  constructor(
    private page: Page,
    private request: APIRequestContext
  ) {}

  async login(email: string, password: string) {
    await this.page.goto('/auth/login');
    await this.page.fill('input[name="email"]', email);
    await this.page.fill('input[name="password"]', password);
    await this.page.click('button[type="submit"]');
    
    // Wait for navigation after successful login
    await this.page.waitForURL('**/dashboard', { timeout: 10000 });
  }

  async loginViaAPI(email: string, password: string) {
    const response = await this.request.post('/api/auth/login', {
      data: { email, password },
    });
    
    const data = await response.json();
    if (response.ok() && data.accessToken) {
      // Store auth token in local storage
      await this.page.addInitScript((token) => {
        localStorage.setItem('accessToken', token);
      }, data.accessToken);
      
      if (data.refreshToken) {
        await this.page.addInitScript((token) => {
          localStorage.setItem('refreshToken', token);
        }, data.refreshToken);
      }
      
      if (data.user) {
        await this.page.addInitScript((user) => {
          localStorage.setItem('user', JSON.stringify(user));
        }, data.user);
      }
    }
    
    return data;
  }

  async logout() {
    // Click logout button if visible
    const logoutButton = this.page.locator('button:has-text("Logout")').first();
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
    }
    
    // Clear local storage
    await this.page.evaluate(() => {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    });
  }

  async register(email: string, password: string, firstName: string, lastName: string) {
    await this.page.goto('/auth/register');
    await this.page.fill('input[name="firstName"]', firstName);
    await this.page.fill('input[name="lastName"]', lastName);
    await this.page.fill('input[name="email"]', email);
    await this.page.fill('input[name="password"]', password);
    await this.page.fill('input[name="confirmPassword"]', password);
    await this.page.click('button[type="submit"]');
    
    // Wait for navigation or success message
    await Promise.race([
      this.page.waitForURL('**/auth/login'),
      this.page.waitForURL('**/dashboard'),
    ]);
  }

  async isAuthenticated(): Promise<boolean> {
    const token = await this.page.evaluate(() => localStorage.getItem('accessToken'));
    return !!token;
  }

  async getAuthToken(): Promise<string | null> {
    return await this.page.evaluate(() => localStorage.getItem('accessToken'));
  }

  async setupAuthenticatedSession() {
    // Use default test user credentials
    const testUser = {
      email: process.env.TEST_USER_EMAIL || 'test@byteforge.com',
      password: process.env.TEST_USER_PASSWORD || 'TestPassword123!',
    };
    
    await this.loginViaAPI(testUser.email, testUser.password);
  }
}