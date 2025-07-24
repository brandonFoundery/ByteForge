'use client';

import { useState, FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Eye, EyeOff, Loader2 } from 'lucide-react';

interface FormField {
  name: string;
  label: string;
  type: 'email' | 'password' | 'text';
  placeholder?: string;
  required?: boolean;
  defaultValue?: string;
}

interface AuthFormProps {
  title: string;
  fields: FormField[];
  submitText: string;
  onSubmit: (data: Record<string, string>) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  children?: React.ReactNode;
}

export function AuthForm({
  title,
  fields,
  submitText,
  onSubmit,
  isLoading = false,
  error,
  children
}: AuthFormProps) {
  // Initialize form data with default values
  const [formData, setFormData] = useState<Record<string, string>>(() => {
    const initialData: Record<string, string> = {};
    fields.forEach(field => {
      if (field.defaultValue) {
        initialData[field.name] = field.defaultValue;
      }
    });
    return initialData;
  });
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});

  const handleInputChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const togglePasswordVisibility = (fieldName: string) => {
    setShowPasswords(prev => ({ ...prev, [fieldName]: !prev[fieldName] }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <Alert className="border-red-500/50 bg-red-500/10">
          <AlertDescription className="text-red-200">
            {error}
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        {fields.map((field) => (
          <div key={field.name}>
            <Label htmlFor={field.name} className="text-gray-200">
              {field.label}
            </Label>
            <div className="mt-1 relative">
              <Input
                id={field.name}
                name={field.name}
                type={
                  field.type === 'password' && showPasswords[field.name]
                    ? 'text'
                    : field.type
                }
                placeholder={field.placeholder}
                required={field.required}
                value={formData[field.name] || ''}
                onChange={(e) => handleInputChange(field.name, e.target.value)}
                className="bg-gray-800/50 border-gray-700 text-white placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500"
                disabled={isLoading}
              />
              {field.type === 'password' && (
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => togglePasswordVisibility(field.name)}
                  disabled={isLoading}
                >
                  {showPasswords[field.name] ? (
                    <EyeOff className="h-4 w-4 text-gray-400 hover:text-gray-300" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400 hover:text-gray-300" />
                  )}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <Button
        type="submit"
        className="w-full union-button"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Processing...
          </>
        ) : (
          submitText
        )}
      </Button>

      {children && (
        <div className="mt-6 text-center">
          {children}
        </div>
      )}
    </form>
  );
}