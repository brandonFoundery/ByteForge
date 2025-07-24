import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { authService } from '@/services/authService';

// Mock the auth service
jest.mock('@/services/authService');
const mockedAuthService = authService as jest.Mocked<typeof authService>;

// Test component to use the auth context
const TestComponent = () => {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();

  return (
    <div>
      <div data-testid="loading">{isLoading ? 'Loading' : 'Not Loading'}</div>
      <div data-testid="authenticated">{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>
      <div data-testid="user">{user ? user.email : 'No User'}</div>
      <button onClick={() => login({ email: 'test@example.com', password: 'password' })}>
        Login
      </button>
      <button onClick={() => logout()}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should provide initial state', () => {
    mockedAuthService.isAuthenticated.mockReturnValue(false);
    mockedAuthService.getCurrentUser.mockReturnValue(null);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    expect(screen.getByTestId('authenticated')).toHaveTextContent('Not Authenticated');
    expect(screen.getByTestId('user')).toHaveTextContent('No User');
  });

  it('should initialize with authenticated user', async () => {
    const mockUser = { id: '1', email: 'test@example.com', userName: 'testuser' };
    mockedAuthService.isAuthenticated.mockReturnValue(true);
    mockedAuthService.getCurrentUser.mockReturnValue(mockUser);
    mockedAuthService.ensureValidToken.mockResolvedValue();

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('Authenticated');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
  });

  it('should handle login', async () => {
    const mockUser = { id: '1', email: 'test@example.com', userName: 'testuser' };
    const mockLoginResult = {
      accessToken: 'token',
      refreshToken: 'refresh',
      expiresIn: 3600,
      tokenType: 'Bearer',
      user: mockUser
    };

    mockedAuthService.isAuthenticated.mockReturnValue(false);
    mockedAuthService.getCurrentUser.mockReturnValue(null);
    mockedAuthService.login.mockResolvedValue(mockLoginResult);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for initial loading to complete
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not Loading');
    });

    // Click login button
    fireEvent.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('Authenticated');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    expect(mockedAuthService.login).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password'
    });
  });

  it('should handle logout', async () => {
    const mockUser = { id: '1', email: 'test@example.com', userName: 'testuser' };
    mockedAuthService.isAuthenticated.mockReturnValue(true);
    mockedAuthService.getCurrentUser.mockReturnValue(mockUser);
    mockedAuthService.ensureValidToken.mockResolvedValue();
    mockedAuthService.logout.mockResolvedValue();

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for initial authentication
    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('Authenticated');
    });

    // Click logout button
    fireEvent.click(screen.getByText('Logout'));

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('Not Authenticated');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('No User');
    expect(mockedAuthService.logout).toHaveBeenCalled();
  });

  it('should handle token refresh failure', async () => {
    const mockUser = { id: '1', email: 'test@example.com', userName: 'testuser' };
    mockedAuthService.isAuthenticated.mockReturnValue(true);
    mockedAuthService.getCurrentUser.mockReturnValue(mockUser);
    mockedAuthService.ensureValidToken.mockRejectedValue(new Error('Token expired'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('Not Authenticated');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('No User');
  });

  it('should handle logout event from window', async () => {
    const mockUser = { id: '1', email: 'test@example.com', userName: 'testuser' };
    mockedAuthService.isAuthenticated.mockReturnValue(true);
    mockedAuthService.getCurrentUser.mockReturnValue(mockUser);
    mockedAuthService.ensureValidToken.mockResolvedValue();

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for initial authentication
    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('Authenticated');
    });

    // Simulate logout event from API client
    window.dispatchEvent(new CustomEvent('auth:logout'));

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('Not Authenticated');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('No User');
  });
});