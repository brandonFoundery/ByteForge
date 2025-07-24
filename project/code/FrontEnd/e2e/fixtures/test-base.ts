import { test as base, expect } from '@playwright/test';
import { ApiHelper } from '../helpers/api-helper';
import { AuthHelper } from '../helpers/auth-helper';
import { NavigationHelper } from '../helpers/navigation-helper';

// Define custom fixtures
type TestFixtures = {
  apiHelper: ApiHelper;
  authHelper: AuthHelper;
  navigationHelper: NavigationHelper;
};

// Extend base test with custom fixtures
export const test = base.extend<TestFixtures>({
  apiHelper: async ({ page, request }, use) => {
    const apiHelper = new ApiHelper(page, request);
    await use(apiHelper);
  },

  authHelper: async ({ page, request }, use) => {
    const authHelper = new AuthHelper(page, request);
    await use(authHelper);
  },

  navigationHelper: async ({ page }, use) => {
    const navigationHelper = new NavigationHelper(page);
    await use(navigationHelper);
  },
});

export { expect };