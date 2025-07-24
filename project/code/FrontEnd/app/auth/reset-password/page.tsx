'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { AuthForm } from '@/components/auth/AuthForm';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, AlertTriangle } from 'lucide-react';
import { authService } from '@/services/authService';

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      setError('Invalid or missing reset token');
    } else {
      setToken(tokenParam);
    }
  }, [searchParams]);

  const handleSubmit = async (data: Record<string, string>) => {
    if (!token) {
      setError('Invalid reset token');
      return;
    }

    if (data.password !== data.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      await authService.resetPassword(token, data.password);
      setIsSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  const formFields = [
    {
      name: 'password',
      label: 'New Password',
      type: 'password' as const,
      placeholder: 'Enter your new password',
      required: true
    },
    {
      name: 'confirmPassword',
      label: 'Confirm New Password',
      type: 'password' as const,
      placeholder: 'Confirm your new password',
      required: true
    }
  ];

  if (!token && !error) {
    return (
      <AuthLayout
        title="Reset Password"
        subtitle="Loading..."
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
        </div>
      </AuthLayout>
    );
  }

  if (error && !token) {
    return (
      <AuthLayout
        title="Invalid Reset Link"
        subtitle="This password reset link is invalid or has expired"
      >
        <div className="space-y-6">
          <Alert className="border-red-500/50 bg-red-500/10">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-200">
              This password reset link is invalid, expired, or has already been used.
            </AlertDescription>
          </Alert>
          
          <div className="space-y-4">
            <div className="text-center">
              <Link
                href="/auth/forgot-password"
                className="text-sm text-purple-300 hover:text-purple-200 transition-colors font-medium"
              >
                Request a new reset link
              </Link>
            </div>
            
            <div className="text-center">
              <Link
                href="/auth/login"
                className="text-sm text-purple-300 hover:text-purple-200 transition-colors"
              >
                Back to Sign In
              </Link>
            </div>
          </div>
        </div>
      </AuthLayout>
    );
  }

  if (isSuccess) {
    return (
      <AuthLayout
        title="Password Reset Successful"
        subtitle="Your password has been updated"
      >
        <div className="space-y-6">
          <Alert className="border-green-500/50 bg-green-500/10">
            <CheckCircle className="h-4 w-4 text-green-400" />
            <AlertDescription className="text-green-200">
              Your password has been successfully reset. You can now sign in with your new password.
            </AlertDescription>
          </Alert>
          
          <div className="text-center">
            <Link
              href="/auth/login"
              className="text-sm text-purple-300 hover:text-purple-200 transition-colors font-medium"
            >
              Continue to Sign In
            </Link>
          </div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Reset Password"
      subtitle="Enter your new password"
    >
      <AuthForm
        title="Set New Password"
        fields={formFields}
        submitText="Reset Password"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        error={error}
      >
        <div className="text-center">
          <Link
            href="/auth/login"
            className="text-sm text-purple-300 hover:text-purple-200 transition-colors"
          >
            Back to Sign In
          </Link>
        </div>
      </AuthForm>
    </AuthLayout>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <AuthLayout
        title="Reset Password"
        subtitle="Loading..."
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
        </div>
      </AuthLayout>
    }>
      <ResetPasswordContent />
    </Suspense>
  );
}