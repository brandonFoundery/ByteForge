import { Page } from '@playwright/test';

export class NavigationHelper {
  constructor(private page: Page) {}

  async goToHome() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async goToDashboard() {
    await this.page.goto('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  async goToLogin() {
    await this.page.goto('/auth/login');
    await this.page.waitForLoadState('networkidle');
  }

  async goToRegister() {
    await this.page.goto('/auth/register');
    await this.page.waitForLoadState('networkidle');
  }

  async goToSettings() {
    await this.page.goto('/settings');
    await this.page.waitForLoadState('networkidle');
  }

  async clickNavLink(linkText: string) {
    await this.page.click(`nav a:has-text("${linkText}")`);
    await this.page.waitForLoadState('networkidle');
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  async isOnPage(urlPattern: string | RegExp): Promise<boolean> {
    const currentUrl = await this.getCurrentUrl();
    if (typeof urlPattern === 'string') {
      return currentUrl.includes(urlPattern);
    }
    return urlPattern.test(currentUrl);
  }

  async waitForNavigation(urlPattern?: string | RegExp) {
    if (urlPattern) {
      await this.page.waitForURL(urlPattern);
    } else {
      await this.page.waitForLoadState('networkidle');
    }
  }

  async goBack() {
    await this.page.goBack();
    await this.waitForPageLoad();
  }

  async goForward() {
    await this.page.goForward();
    await this.waitForPageLoad();
  }

  async refresh() {
    await this.page.reload();
    await this.waitForPageLoad();
  }
}