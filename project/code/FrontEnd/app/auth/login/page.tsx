'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { AuthForm } from '@/components/auth/AuthForm';
import { useAuthForm } from '@/hooks/useAuth';

export default function LoginPage() {
  const router = useRouter();
  const { handleLogin, isLoading, error, isAuthenticated } = useAuthForm();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (data: Record<string, string>) => {
    try {
      await handleLogin(data.email, data.password);
      router.push('/dashboard');
    } catch (err) {
      // Error is handled by useAuthForm hook
    }
  };

  const formFields = [
    {
      name: 'email',
      label: 'Email Address',
      type: 'email' as const,
      placeholder: 'Enter your email',
      required: true,
      defaultValue: 'admin@leadprocessing.com'
    },
    {
      name: 'password',
      label: 'Password',
      type: 'password' as const,
      placeholder: 'Enter your password',
      required: true,
      defaultValue: 'Admin123!'
    }
  ];

  return (
    <AuthLayout
      title="Welcome Back"
      subtitle="Sign in to your account to continue"
    >
      <AuthForm
        title="Sign In"
        fields={formFields}
        submitText="Sign In"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        error={error}
      >
        <div className="space-y-4">
          <div className="text-center">
            <Link
              href="/auth/forgot-password"
              className="text-sm text-purple-300 hover:text-purple-200 transition-colors"
            >
              Forgot your password?
            </Link>
          </div>
          
          <div className="text-center">
            <span className="text-sm text-gray-400">
              Don't have an account?{' '}
            </span>
            <Link
              href="/auth/register"
              className="text-sm text-purple-300 hover:text-purple-200 transition-colors font-medium"
            >
              Sign up
            </Link>
          </div>
        </div>
      </AuthForm>
    </AuthLayout>
  );
}