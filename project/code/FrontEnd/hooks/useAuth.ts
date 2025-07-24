import { useAuth as useAuthContext } from '@/contexts/AuthContext';
import { useState } from 'react';

export interface UseAuthReturn {
  user: any;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

export function useAuth(): UseAuthReturn {
  const context = useAuthContext();
  
  // Wrapper functions to provide a more convenient API
  const login = async (email: string, password: string) => {
    await context.login({ email, password });
  };

  const register = async (email: string, password: string, confirmPassword: string) => {
    await context.register({ email, password, confirmPassword });
  };

  return {
    user: context.user,
    isAuthenticated: context.isAuthenticated,
    isLoading: context.isLoading,
    login,
    register,
    logout: context.logout,
    refreshToken: context.refreshToken
  };
}

// Custom hook for handling authentication forms
export function useAuthForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const auth = useAuth();

  const handleLogin = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      await auth.login(email, password);
    } catch (err: any) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (email: string, password: string, confirmPassword: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      if (password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }
      
      await auth.register(email, password, confirmPassword);
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await auth.logout();
    } catch (err: any) {
      setError(err.message || 'Logout failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError(null);

  return {
    isLoading,
    error,
    handleLogin,
    handleRegister,
    handleLogout,
    clearError,
    ...auth
  };
}

// Custom hook for automatic token refresh
export function useTokenRefresh() {
  const { refreshToken, isAuthenticated } = useAuth();
  
  // Set up automatic token refresh
  useState(() => {
    if (isAuthenticated) {
      // Refresh token every 30 minutes
      const interval = setInterval(async () => {
        try {
          await refreshToken();
        } catch (error) {
          console.error('Automatic token refresh failed:', error);
          // The auth context will handle logout automatically
        }
      }, 30 * 60 * 1000); // 30 minutes

      return () => clearInterval(interval);
    }
  });

  return { refreshToken };
}