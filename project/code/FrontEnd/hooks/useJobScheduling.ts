import { useState, useEffect, useCallback } from 'react';

// Types
export interface JobSchedule {
  jobName: string;
  displayName: string;
  cronExpression: string;
  description: string;
  isEnabled: boolean;
  friendlySchedule: string;
  lastModified: string;
  modifiedBy: string;
}

export interface JobPreset {
  label: string;
  cron: string;
  category: string;
}

export interface PresetCategories {
  testing: JobPreset[];
  minutes: JobPreset[];
  hours: JobPreset[];
  daily: JobPreset[];
  weekly: JobPreset[];
}

interface UpdateJobRequest {
  cronExpression: string;
  isEnabled: boolean;
  notes?: string;
  modifiedBy?: string;
}

interface SetEnabledRequest {
  enabled: boolean;
  modifiedBy?: string;
}

// Hook
export function useJobScheduling() {
  const [jobs, setJobs] = useState<JobSchedule[]>([]);
  const [presets, setPresets] = useState<PresetCategories | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const baseUrl = 'http://localhost:5000/api/v1/jobscheduling';

  // Fetch all job schedules
  const fetchJobs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(baseUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.statusText}`);
      }
      
      const data = await response.json();
      setJobs(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error fetching jobs:', err);
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  // Fetch preset frequencies
  const fetchPresets = useCallback(async () => {
    try {
      const response = await fetch(`${baseUrl}/presets`);
      if (!response.ok) {
        throw new Error(`Failed to fetch presets: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPresets(data);
    } catch (err) {
      console.error('Error fetching presets:', err);
    }
  }, [baseUrl]);

  // Update job schedule
  const updateJob = useCallback(async (jobName: string, request: UpdateJobRequest) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${baseUrl}/${jobName}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Failed to update job: ${response.statusText}`);
      }

      // Refresh jobs after update
      await fetchJobs();
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error updating job:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, [baseUrl, fetchJobs]);

  // Toggle job enabled status
  const toggleJobEnabled = useCallback(async (jobName: string, enabled: boolean, modifiedBy: string = 'User') => {
    try {
      setLoading(true);
      setError(null);

      const request: SetEnabledRequest = {
        enabled,
        modifiedBy,
      };

      const response = await fetch(`${baseUrl}/${jobName}/enabled`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Failed to toggle job: ${response.statusText}`);
      }

      // Refresh jobs after update
      await fetchJobs();
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error toggling job:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, [baseUrl, fetchJobs]);

  // Get friendly description for cron expression
  const getCronDescription = useCallback(async (expression: string): Promise<string> => {
    try {
      const encodedExpression = encodeURIComponent(expression);
      const response = await fetch(`${baseUrl}/cron/${encodedExpression}/description`);
      
      if (!response.ok) {
        return `Custom: ${expression}`;
      }
      
      const data = await response.json();
      return data.description || `Custom: ${expression}`;
    } catch (err) {
      console.error('Error getting cron description:', err);
      return `Custom: ${expression}`;
    }
  }, [baseUrl]);

  // Initialize data on mount
  useEffect(() => {
    fetchJobs();
    fetchPresets();
  }, [fetchJobs, fetchPresets]);

  return {
    jobs,
    presets,
    loading,
    error,
    fetchJobs,
    updateJob,
    toggleJobEnabled,
    getCronDescription,
  };
}