'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { AuthForm } from '@/components/auth/AuthForm';
import { useAuthForm } from '@/hooks/useAuth';

export default function RegisterPage() {
  const router = useRouter();
  const { handleRegister, isLoading, error, isAuthenticated } = useAuthForm();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (data: Record<string, string>) => {
    try {
      await handleRegister(data.email, data.password, data.confirmPassword);
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
      required: true
    },
    {
      name: 'password',
      label: 'Password',
      type: 'password' as const,
      placeholder: 'Create a password',
      required: true
    },
    {
      name: 'confirmPassword',
      label: 'Confirm Password',
      type: 'password' as const,
      placeholder: 'Confirm your password',
      required: true
    }
  ];

  return (
    <AuthLayout
      title="Create Account"
      subtitle="Join us to start processing leads with AI"
    >
      <AuthForm
        title="Sign Up"
        fields={formFields}
        submitText="Create Account"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        error={error}
      >
        <div className="space-y-4">
          <div className="text-center">
            <span className="text-sm text-gray-400">
              Already have an account?{' '}
            </span>
            <Link
              href="/auth/login"
              className="text-sm text-purple-300 hover:text-purple-200 transition-colors font-medium"
            >
              Sign in
            </Link>
          </div>
          
          <div className="text-xs text-gray-400 text-center">
            By creating an account, you agree to our{' '}
            <Link href="/terms" className="text-purple-300 hover:text-purple-200">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/privacy" className="text-purple-300 hover:text-purple-200">
              Privacy Policy
            </Link>
          </div>
        </div>
      </AuthForm>
    </AuthLayout>
  );
}