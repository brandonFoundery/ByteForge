'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Clock, 
  Save, 
  RotateCcw, 
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { JobScheduleViewModel } from '@/types/job-scheduling';

interface JobFrequencyEditorProps {
  job: JobScheduleViewModel;
  onUpdate: (cronExpression: string) => Promise<void>;
}

interface FrequencyOption {
  label: string;
  value: string;
  category: string;
}

const FREQUENCY_OPTIONS: FrequencyOption[] = [
  // Seconds (for testing)
  { label: 'Every 5 seconds', value: '*/5 * * * * *', category: 'Testing' },
  { label: 'Every 10 seconds', value: '*/10 * * * * *', category: 'Testing' },
  { label: 'Every 30 seconds', value: '*/30 * * * * *', category: 'Testing' },
  
  // Minutes
  { label: 'Every minute', value: '0 * * * *', category: 'Minutes' },
  { label: 'Every 5 minutes', value: '0 */5 * * *', category: 'Minutes' },
  { label: 'Every 10 minutes', value: '0 */10 * * *', category: 'Minutes' },
  { label: 'Every 15 minutes', value: '0 */15 * * *', category: 'Minutes' },
  { label: 'Every 30 minutes', value: '0 */30 * * *', category: 'Minutes' },
  
  // Hours
  { label: 'Every hour', value: '0 0 * * *', category: 'Hours' },
  { label: 'Every 2 hours', value: '0 */2 * * *', category: 'Hours' },
  { label: 'Every 2 hours (30min offset)', value: '30 */2 * * *', category: 'Hours' },
  { label: 'Every 3 hours', value: '0 */3 * * *', category: 'Hours' },
  { label: 'Every 4 hours', value: '0 */4 * * *', category: 'Hours' },
  { label: 'Every 6 hours', value: '0 */6 * * *', category: 'Hours' },
  { label: 'Every 8 hours', value: '0 */8 * * *', category: 'Hours' },
  { label: 'Every 12 hours', value: '0 */12 * * *', category: 'Hours' },
  
  // Daily
  { label: 'Daily at midnight', value: '0 0 0 * *', category: 'Daily' },
  { label: 'Daily at noon', value: '0 0 12 * *', category: 'Daily' },
  
  // Weekly/Monthly
  { label: 'Weekly (Sundays)', value: '0 0 0 * * 0', category: 'Weekly' },
  { label: 'Monthly', value: '0 0 0 1 * *', category: 'Monthly' },
];

export function JobFrequencyEditor({ job, onUpdate }: JobFrequencyEditorProps) {
  const [selectedFrequency, setSelectedFrequency] = useState(job.cronExpression);
  const [customCron, setCustomCron] = useState('');
  const [isCustom, setIsCustom] = useState(!FREQUENCY_OPTIONS.some(opt => opt.value === job.cronExpression));
  const [isUpdating, setIsUpdating] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleFrequencyChange = (value: string) => {
    if (value === 'custom') {
      setIsCustom(true);
      setCustomCron(selectedFrequency);
    } else {
      setIsCustom(false);
      setSelectedFrequency(value);
      setHasChanges(value !== job.cronExpression);
    }
  };

  const handleCustomCronChange = (value: string) => {
    setCustomCron(value);
    setSelectedFrequency(value);
    setHasChanges(value !== job.cronExpression);
  };

  const handleSave = async () => {
    setIsUpdating(true);
    try {
      await onUpdate(selectedFrequency);
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to update job schedule:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleReset = () => {
    setSelectedFrequency(job.cronExpression);
    setCustomCron(job.cronExpression);
    setIsCustom(!FREQUENCY_OPTIONS.some(opt => opt.value === job.cronExpression));
    setHasChanges(false);
  };

  const getCurrentOption = () => {
    return FREQUENCY_OPTIONS.find(opt => opt.value === selectedFrequency);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium text-slate-300">Frequency</Label>
        {hasChanges && (
          <Badge variant="outline" className="text-xs border-amber-500 text-amber-400">
            Unsaved Changes
          </Badge>
        )}
      </div>

      <div className="space-y-3">
        {!isCustom ? (
          <Select 
            value={selectedFrequency} 
            onValueChange={handleFrequencyChange}
          >
            <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
              <SelectValue placeholder="Select frequency">
                {getCurrentOption()?.label || 'Custom schedule'}
              </SelectValue>
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-600">
              {Object.entries(
                FREQUENCY_OPTIONS.reduce((acc, option) => {
                  if (!acc[option.category]) acc[option.category] = [];
                  acc[option.category].push(option);
                  return acc;
                }, {} as Record<string, FrequencyOption[]>)
              ).map(([category, options]) => (
                <div key={category}>
                  <div className="px-2 py-1.5 text-xs font-medium text-slate-400 uppercase tracking-wider">
                    {category}
                  </div>
                  {options.map((option) => (
                    <SelectItem 
                      key={option.value} 
                      value={option.value}
                      className="text-white hover:bg-slate-700"
                    >
                      {option.label}
                    </SelectItem>
                  ))}
                </div>
              ))}
              <div className="border-t border-slate-600 mt-2">
                <SelectItem value="custom" className="text-white hover:bg-slate-700">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-3 h-3" />
                    <span>Custom Cron Expression</span>
                  </div>
                </SelectItem>
              </div>
            </SelectContent>
          </Select>
        ) : (
          <div className="space-y-2">
            <Input
              value={customCron}
              onChange={(e) => handleCustomCronChange(e.target.value)}
              placeholder="Enter custom cron expression (e.g., */5 * * * * *)"
              className="bg-slate-800 border-slate-600 text-white placeholder-slate-400"
            />
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <AlertCircle className="w-3 h-3" />
              <span>Use standard cron format with seconds support</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsCustom(false)}
              className="text-xs text-slate-400 hover:text-white h-auto p-1"
            >
              ← Back to presets
            </Button>
          </div>
        )}

        {hasChanges && (
          <div className="flex items-center justify-between pt-2 border-t border-slate-700">
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <Clock className="w-3 h-3" />
              <span>Changes will take effect immediately</span>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleReset}
                className="text-xs h-7"
              >
                <RotateCcw className="w-3 h-3 mr-1" />
                Reset
              </Button>
              <Button
                size="sm"
                onClick={handleSave}
                disabled={isUpdating}
                className="text-xs h-7 bg-purple-600 hover:bg-purple-700"
              >
                {isUpdating ? (
                  <>
                    <div className="w-3 h-3 mr-1 border border-white/30 border-t-white rounded-full animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-3 h-3 mr-1" />
                    Save
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}