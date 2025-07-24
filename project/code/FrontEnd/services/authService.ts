import { apiClient } from '@/lib/api';
import { LoginRequest, RegisterRequest, RefreshTokenRequest, LoginResult, UserDto } from '@/types/api';

export class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResult> {
    const result = await apiClient.post<LoginResult>('/auth/login', credentials);
    
    // Store tokens
    apiClient.setToken(result.accessToken);
    localStorage.setItem('refreshToken', result.refreshToken);
    localStorage.setItem('user', JSON.stringify(result.user));
    
    return result;
  }

  async register(userData: RegisterRequest): Promise<UserDto> {
    return await apiClient.post<UserDto>('/auth/register', userData);
  }

  async refreshToken(): Promise<LoginResult> {
    const accessToken = apiClient.getToken();
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (!accessToken || !refreshToken) {
      throw new Error('No tokens available');
    }

    const result = await apiClient.post<LoginResult>('/auth/refresh', {
      accessToken,
      refreshToken
    } as RefreshTokenRequest);

    // Update stored tokens
    apiClient.setToken(result.accessToken);
    localStorage.setItem('refreshToken', result.refreshToken);
    localStorage.setItem('user', JSON.stringify(result.user));

    return result;
  }

  async logout(): Promise<void> {
    try {
      await apiClient.postWithoutData('/auth/logout');
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      this.clearAllAuthData();
    }
  }

  private clearAllAuthData() {
    // Clear local storage first
    apiClient.clearToken();
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('user');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('accessToken');
    }
    
    // Clear all cookies (especially any auth-related ones)
    if (typeof document !== 'undefined') {
      // Get all cookies
      const cookies = document.cookie.split(';');
      
      // Clear each cookie
      cookies.forEach(cookie => {
        const eqPos = cookie.indexOf('=');
        const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
        
        // Clear cookie for current domain and all parent domains
        const domains = [location.hostname];
        const parts = location.hostname.split('.');
        for (let i = 1; i < parts.length; i++) {
          domains.push('.' + parts.slice(i).join('.'));
        }
        
        domains.forEach(domain => {
          document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=${domain}`;
          document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
        });
      });
    }
    
    // Clear session storage as well
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.clear();
    }
  }

  async getProfile(): Promise<UserDto> {
    return await apiClient.get<UserDto>('/auth/profile');
  }

  async forgotPassword(email: string): Promise<void> {
    // TODO: Implement when backend endpoint is available
    // await apiClient.post('/auth/forgot-password', { email });
    
    // For now, simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  async resetPassword(token: string, password: string): Promise<void> {
    // TODO: Implement when backend endpoint is available
    // await apiClient.post('/auth/reset-password', { token, password });
    
    // For now, simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  getCurrentUser(): UserDto | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  isAuthenticated(): boolean {
    const token = apiClient.getToken();
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  clearSession() {
    this.clearAllAuthData();
  }

  private clearLocalStorage() {
    apiClient.clearToken();
    localStorage.removeItem('user');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('accessToken');
  }

  // Auto-refresh token when it's about to expire
  async ensureValidToken(): Promise<void> {
    const token = apiClient.getToken();
    if (!token) return;

    try {
      // Try to decode token to check expiration
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      
      // Refresh if token expires in less than 5 minutes
      if (payload.exp - currentTime < 300) {
        await this.refreshToken();
      }
    } catch (error) {
      console.error('Token validation failed:', error);
      // If token is invalid, try to refresh
      try {
        await this.refreshToken();
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        this.clearLocalStorage();
        throw refreshError;
      }
    }
  }
}

export const authService = new AuthService();