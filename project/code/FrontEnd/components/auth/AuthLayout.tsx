'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen union-gradient flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header with Logo */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center space-x-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold union-text-gradient">
                Union Eleven
              </h1>
              <p className="text-sm text-gray-400">AI-Powered Lead Processing</p>
            </div>
          </Link>
          
          <div className="mt-6">
            <h2 className="text-3xl font-bold text-white">
              {title}
            </h2>
            {subtitle && (
              <p className="mt-2 text-sm text-gray-300">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {/* Main Content Card */}
        <div className="union-card border-purple-500/20 p-8">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="text-sm text-gray-400">
            © 2025 Union Eleven. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}