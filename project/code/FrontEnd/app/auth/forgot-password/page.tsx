'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { AuthForm } from '@/components/auth/AuthForm';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle } from 'lucide-react';
import { authService } from '@/services/authService';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (data: Record<string, string>) => {
    try {
      setIsLoading(true);
      setError(null);
      
      await authService.forgotPassword(data.email);
      setIsSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to send reset email');
    } finally {
      setIsLoading(false);
    }
  };

  const formFields = [
    {
      name: 'email',
      label: 'Email Address',
      type: 'email' as const,
      placeholder: 'Enter your email address',
      required: true
    }
  ];

  if (isSuccess) {
    return (
      <AuthLayout
        title="Check Your Email"
        subtitle="We've sent you a password reset link"
      >
        <div className="space-y-6">
          <Alert className="border-green-500/50 bg-green-500/10">
            <CheckCircle className="h-4 w-4 text-green-400" />
            <AlertDescription className="text-green-200">
              If an account with that email exists, we've sent you a password reset link. 
              Please check your email and follow the instructions to reset your password.
            </AlertDescription>
          </Alert>
          
          <div className="space-y-4">
            <div className="text-center">
              <Link
                href="/auth/login"
                className="text-sm text-purple-300 hover:text-purple-200 transition-colors font-medium"
              >
                Back to Sign In
              </Link>
            </div>
            
            <div className="text-center">
              <span className="text-sm text-gray-400">
                Didn't receive the email?{' '}
              </span>
              <button
                onClick={() => setIsSuccess(false)}
                className="text-sm text-purple-300 hover:text-purple-200 transition-colors font-medium"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Forgot Password"
      subtitle="Enter your email to receive a reset link"
    >
      <AuthForm
        title="Reset Password"
        fields={formFields}
        submitText="Send Reset Link"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        error={error}
      >
        <div className="space-y-4">
          <div className="text-center">
            <Link
              href="/auth/login"
              className="text-sm text-purple-300 hover:text-purple-200 transition-colors"
            >
              Remember your password? Sign in
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