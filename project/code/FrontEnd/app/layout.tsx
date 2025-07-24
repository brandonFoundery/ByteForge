import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { LeadProvider } from '@/contexts/LeadContext';
import { AuthProvider } from '@/contexts/AuthContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Lead Processing - AI-Powered Solutions',
  description: 'Transform your business with AI-powered lead generation and processing solutions',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} union-gradient`}>
        <AuthProvider>
          <LeadProvider>
            {children}
          </LeadProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
