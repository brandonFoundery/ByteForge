'use client';

import { useState, useEffect } from 'react';
import { useJobScheduling, JobSchedule, JobPreset } from '@/hooks/useJobScheduling';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, Clock, Play, Pause, Save, RotateCcw, Loader2, CheckCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export function WorkflowSettings() {
  const { jobs, presets, loading, error, updateJob, toggleJobEnabled, getCronDescription } = useJobScheduling();
  const [editingJob, setEditingJob] = useState<string | null>(null);
  const [pendingChanges, setPendingChanges] = useState<Record<string, { cronExpression: string; isEnabled: boolean }>>({});
  const [customCron, setCustomCron] = useState<Record<string, string>>({});
  const [cronDescriptions, setCronDescriptions] = useState<Record<string, string>>({});
  const [savingJobs, setSavingJobs] = useState<Record<string, boolean>>({});

  // Get cron description when custom cron changes
  useEffect(() => {
    const updateDescriptions = async () => {
      for (const [jobName, cron] of Object.entries(customCron)) {
        if (cron && cron !== jobs.find(j => j.jobName === jobName)?.cronExpression) {
          const description = await getCronDescription(cron);
          setCronDescriptions(prev => ({ ...prev, [jobName]: description }));
        }
      }
    };

    updateDescriptions();
  }, [customCron, getCronDescription, jobs]);

  const handlePresetSelect = (jobName: string, cronExpression: string) => {
    setPendingChanges(prev => ({
      ...prev,
      [jobName]: {
        cronExpression,
        isEnabled: jobs.find(j => j.jobName === jobName)?.isEnabled ?? true
      }
    }));
    setCustomCron(prev => ({ ...prev, [jobName]: cronExpression }));
  };

  const handleCustomCronChange = (jobName: string, value: string) => {
    setCustomCron(prev => ({ ...prev, [jobName]: value }));
    setPendingChanges(prev => ({
      ...prev,
      [jobName]: {
        cronExpression: value,
        isEnabled: jobs.find(j => j.jobName === jobName)?.isEnabled ?? true
      }
    }));
  };

  const handleToggleEnabled = async (jobName: string, enabled: boolean) => {
    setSavingJobs(prev => ({ ...prev, [jobName]: true }));
    
    const success = await toggleJobEnabled(jobName, enabled, 'Mobile Settings');
    
    setSavingJobs(prev => ({ ...prev, [jobName]: false }));

    if (success) {
      // Remove from pending changes if it was there
      setPendingChanges(prev => {
        const updated = { ...prev };
        delete updated[jobName];
        return updated;
      });
    }
  };

  const handleSaveJob = async (jobName: string) => {
    const changes = pendingChanges[jobName];
    if (!changes) return;

    setSavingJobs(prev => ({ ...prev, [jobName]: true }));

    const success = await updateJob(jobName, {
      cronExpression: changes.cronExpression,
      isEnabled: changes.isEnabled,
      modifiedBy: 'Mobile Settings'
    });

    setSavingJobs(prev => ({ ...prev, [jobName]: false }));

    if (success) {
      // Remove from pending changes
      setPendingChanges(prev => {
        const updated = { ...prev };
        delete updated[jobName];
        return updated;
      });
      // Clear custom cron
      setCustomCron(prev => {
        const updated = { ...prev };
        delete updated[jobName];
        return updated;
      });
      setEditingJob(null);
    }
  };

  const handleResetJob = (jobName: string) => {
    setPendingChanges(prev => {
      const updated = { ...prev };
      delete updated[jobName];
      return updated;
    });
    setCustomCron(prev => {
      const updated = { ...prev };
      delete updated[jobName];
      return updated;
    });
    setEditingJob(null);
  };

  const getJobIcon = (jobName: string) => {
    switch (jobName) {
      case 'google-leads': return '🌐';
      case 'facebook-leads': return '📘';
      case 'linkedin-leads': return '💼';
      case 'yellowpages-leads': return '📞';
      default: return '⚡';
    }
  };

  const getStatusColor = (job: JobSchedule) => {
    if (!job.isEnabled) return 'bg-red-600/20 text-red-400 border-red-600/30';
    return 'bg-green-600/20 text-green-400 border-green-600/30';
  };

  if (error) {
    return (
      <Alert className="border-red-600/30 bg-red-600/10">
        <AlertCircle className="h-4 w-4 text-red-400" />
        <AlertDescription className="text-red-200">
          Failed to load workflow settings: {error}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-2">Workflow Scheduling</h3>
        <p className="text-gray-400 text-sm">
          Configure how frequently each lead generation workflow runs. Changes apply immediately to the job scheduler.
        </p>
      </div>

      {loading && jobs.length === 0 ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          <span className="ml-2 text-gray-400">Loading workflow settings...</span>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job) => {
            const isEditing = editingJob === job.jobName;
            const hasPendingChanges = pendingChanges[job.jobName];
            const isSaving = savingJobs[job.jobName];
            const currentCron = customCron[job.jobName] || job.cronExpression;
            const currentDescription = cronDescriptions[job.jobName] || job.friendlySchedule;

            return (
              <Card key={job.jobName} className="bg-gray-800/50 border-gray-700">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{getJobIcon(job.jobName)}</span>
                      <div>
                        <CardTitle className="text-white text-base">{job.displayName}</CardTitle>
                        <CardDescription className="text-xs text-gray-400">
                          {job.description}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={getStatusColor(job)}>
                        {job.isEnabled ? 'Active' : 'Paused'}
                      </Badge>
                      <Switch
                        checked={job.isEnabled}
                        onCheckedChange={(enabled) => handleToggleEnabled(job.jobName, enabled)}
                        disabled={isSaving}
                      />
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="space-y-4">
                    {/* Current Schedule Display */}
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-300">{currentDescription}</span>
                      {hasPendingChanges && (
                        <Badge variant="outline" className="text-yellow-400 border-yellow-600/30">
                          Unsaved
                        </Badge>
                      )}
                    </div>

                    {/* Frequency Controls */}
                    {isEditing && presets ? (
                      <div className="space-y-4 border-t border-gray-700 pt-4">
                        <Tabs defaultValue="presets" className="w-full">
                          <TabsList className="grid w-full grid-cols-2 bg-gray-700/50">
                            <TabsTrigger value="presets">Presets</TabsTrigger>
                            <TabsTrigger value="custom">Custom</TabsTrigger>
                          </TabsList>
                          
                          <TabsContent value="presets" className="space-y-3 mt-4">
                            {Object.entries(presets).map(([category, categoryPresets]) => (
                              <div key={category}>
                                <Label className="text-sm font-medium text-gray-300 capitalize">
                                  {category}
                                </Label>
                                <div className="grid grid-cols-2 gap-2 mt-2">
                                  {categoryPresets.map((preset: JobPreset) => (
                                    <Button
                                      key={preset.cron}
                                      variant={currentCron === preset.cron ? "default" : "outline"}
                                      size="sm"
                                      onClick={() => handlePresetSelect(job.jobName, preset.cron)}
                                      className="justify-start text-xs h-8 px-2"
                                    >
                                      {preset.label}
                                    </Button>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </TabsContent>

                          <TabsContent value="custom" className="space-y-3 mt-4">
                            <div>
                              <Label className="text-sm font-medium text-gray-300">
                                Custom Cron Expression
                              </Label>
                              <Input
                                value={currentCron}
                                onChange={(e) => handleCustomCronChange(job.jobName, e.target.value)}
                                placeholder="0 */5 * * *"
                                className="bg-gray-700 border-gray-600 text-white mt-1"
                              />
                              <p className="text-xs text-gray-400 mt-1">
                                Format: second minute hour day month dayofweek
                              </p>
                            </div>
                          </TabsContent>
                        </Tabs>

                        {/* Action Buttons */}
                        <div className="flex gap-2 pt-2 border-t border-gray-700">
                          <Button
                            size="sm"
                            onClick={() => handleSaveJob(job.jobName)}
                            disabled={!hasPendingChanges || isSaving}
                            className="bg-blue-600 hover:bg-blue-700"
                          >
                            {isSaving ? (
                              <Loader2 className="w-3 h-3 animate-spin mr-1" />
                            ) : (
                              <Save className="w-3 h-3 mr-1" />
                            )}
                            Save
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleResetJob(job.jobName)}
                            className="border-gray-600"
                          >
                            <RotateCcw className="w-3 h-3 mr-1" />
                            Reset
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingJob(job.jobName)}
                        className="border-gray-600 text-gray-300 hover:bg-gray-700"
                      >
                        <Clock className="w-3 h-3 mr-1" />
                        Change Frequency
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Summary Footer */}
      <div className="border-t border-gray-700 pt-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">
            {jobs.filter(j => j.isEnabled).length} of {jobs.length} workflows active
          </span>
          <div className="flex items-center gap-1 text-green-400">
            <CheckCircle className="w-3 h-3" />
            <span>Real-time scheduling</span>
          </div>
        </div>
      </div>
    </div>
  );
}