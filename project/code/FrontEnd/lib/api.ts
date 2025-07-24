import axios, { AxiosInstance, AxiosError } from 'axios';
import { ApiResponse } from '@/types/api';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public errors?: string[]
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;
  private accessToken: string | null = null;

  constructor(baseURL: string = 'http://localhost:5000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken();
          // Dispatch logout event
          window.dispatchEvent(new CustomEvent('auth:logout'));
        }

        // Handle API error responses
        if (error.response?.data) {
          const apiError = error.response.data as ApiResponse<any>;
          throw new ApiError(
            apiError.message || 'An error occurred',
            error.response.status,
            apiError.errors
          );
        }

        // Handle network errors
        if (error.code === 'ECONNABORTED') {
          throw new ApiError('Request timeout', 408);
        }

        if (error.code === 'ERR_NETWORK') {
          throw new ApiError('Network error', 0);
        }

        throw new ApiError(
          error.message || 'An unexpected error occurred',
          error.response?.status || 500
        );
      }
    );
  }

  setToken(token: string) {
    this.accessToken = token;
    localStorage.setItem('accessToken', token);
  }

  getToken(): string | null {
    if (!this.accessToken) {
      this.accessToken = localStorage.getItem('accessToken');
    }
    return this.accessToken;
  }

  clearToken() {
    this.accessToken = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<ApiResponse<T>>(url, { params });
    return response.data.data!;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data);
    return response.data.data!;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data);
    return response.data.data!;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url);
    return response.data.data!;
  }

  async postWithoutData(url: string, data?: any): Promise<void> {
    await this.client.post<ApiResponse<void>>(url, data);
  }

  async deleteWithoutData(url: string): Promise<void> {
    await this.client.delete<ApiResponse<void>>(url);
  }

  // Health check
  async ping(): Promise<boolean> {
    try {
      await axios.get(`${this.baseURL}/health`, { timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }
}

// Singleton instance
export const apiClient = new ApiClient();