import { Page, APIRequestContext } from '@playwright/test';

export class ApiHelper {
  constructor(
    private page: Page,
    private request: APIRequestContext
  ) {}

  async get(endpoint: string, options?: any) {
    const response = await this.request.get(`${this.getBaseUrl()}${endpoint}`, options);
    return {
      status: response.status(),
      data: await response.json().catch(() => null),
      headers: response.headers(),
    };
  }

  async post(endpoint: string, data?: any, options?: any) {
    const response = await this.request.post(`${this.getBaseUrl()}${endpoint}`, {
      data,
      ...options,
    });
    return {
      status: response.status(),
      data: await response.json().catch(() => null),
      headers: response.headers(),
    };
  }

  async put(endpoint: string, data?: any, options?: any) {
    const response = await this.request.put(`${this.getBaseUrl()}${endpoint}`, {
      data,
      ...options,
    });
    return {
      status: response.status(),
      data: await response.json().catch(() => null),
      headers: response.headers(),
    };
  }

  async delete(endpoint: string, options?: any) {
    const response = await this.request.delete(`${this.getBaseUrl()}${endpoint}`, options);
    return {
      status: response.status(),
      data: await response.json().catch(() => null),
      headers: response.headers(),
    };
  }

  async waitForResponse(endpoint: string, action: () => Promise<void>) {
    const responsePromise = this.page.waitForResponse(
      (response) => response.url().includes(endpoint)
    );
    await action();
    return await responsePromise;
  }

  private getBaseUrl(): string {
    return process.env.API_BASE_URL || 'http://localhost:5000/api';
  }
}