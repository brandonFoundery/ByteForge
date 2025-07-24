'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from '@/components/ui/drawer';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Settings, 
  X, 
  Clock, 
  Key, 
  PlayCircle, 
  PauseCircle,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { JobFrequencyEditor } from './job-frequency-editor';
import { useJobScheduling } from '@/hooks/useJobScheduling';
import { useMediaQuery } from '@/hooks/useMediaQuery';

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const [activeTab, setActiveTab] = useState('workflow');
  const isDesktop = useMediaQuery('(min-width: 768px)');
  
  const {
    jobs,
    isLoading,
    error,
    updateJobSchedule,
    toggleJobEnabled,
    refetch
  } = useJobScheduling();

  useEffect(() => {
    if (open) {
      refetch();
    }
  }, [open, refetch]);

  const content = (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <Settings className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Settings</h2>
            <p className="text-sm text-slate-400">Configure workflow processing and API integrations</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onOpenChange(false)}
          className="text-slate-400 hover:text-white"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Navigation Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="px-6 py-4">
          <TabsList className="grid w-full grid-cols-2 bg-slate-800">
            <TabsTrigger 
              value="workflow" 
              className="flex items-center space-x-2 data-[state=active]:bg-purple-600 data-[state=active]:text-white"
            >
              <Clock className="w-4 h-4" />
              <span>Workflow</span>
            </TabsTrigger>
            <TabsTrigger 
              value="api" 
              className="flex items-center space-x-2 data-[state=active]:bg-purple-600 data-[state=active]:text-white"
            >
              <Key className="w-4 h-4" />
              <span>API Keys</span>
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 px-6 pb-6">
          {/* Workflow Tab */}
          <TabsContent value="workflow" className="mt-0 h-full">
            <ScrollArea className="h-full">
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-white mb-2">Job Scheduling</h3>
                  <p className="text-sm text-slate-400 mb-4">
                    Configure the frequency for each lead generation job. Changes take effect immediately.
                  </p>
                </div>

                {isLoading && (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-purple-400" />
                    <span className="ml-2 text-slate-400">Loading job schedules...</span>
                  </div>
                )}

                {error && (
                  <div className="flex items-center space-x-2 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-400" />
                    <span className="text-sm text-red-400">{error}</span>
                  </div>
                )}

                {!isLoading && !error && jobs.length === 0 && (
                  <div className="text-center py-8">
                    <Clock className="w-12 h-12 mx-auto mb-4 text-slate-600" />
                    <p className="text-slate-400">No job schedules found</p>
                  </div>
                )}

                {!isLoading && !error && jobs.length > 0 && (
                  <div className="space-y-4">
                    {jobs.map((job) => (
                      <div key={job.jobName} className="border border-slate-700 rounded-lg p-4 bg-slate-800/50">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className="flex items-center space-x-2">
                              {job.isEnabled ? (
                                <PlayCircle className="w-4 h-4 text-green-400" />
                              ) : (
                                <PauseCircle className="w-4 h-4 text-slate-400" />
                              )}
                              <h4 className="font-medium text-white">{job.displayName}</h4>
                            </div>
                            <Badge
                              variant={job.isEnabled ? "default" : "secondary"}
                              className={job.isEnabled ? "bg-green-500/20 text-green-300" : "bg-slate-600 text-slate-300"}
                            >
                              {job.isEnabled ? "Active" : "Paused"}
                            </Badge>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => toggleJobEnabled(job.jobName, !job.isEnabled)}
                            className="text-sm"
                          >
                            {job.isEnabled ? "Pause" : "Start"}
                          </Button>
                        </div>

                        <p className="text-sm text-slate-400 mb-3">{job.description}</p>

                        <JobFrequencyEditor
                          job={job}
                          onUpdate={(cronExpression) => updateJobSchedule(job.jobName, cronExpression, job.isEnabled)}
                        />

                        <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                          <span>Current: {job.friendlySchedule}</span>
                          {job.modifiedBy && (
                            <span>Modified by {job.modifiedBy} on {new Date(job.lastModified).toLocaleDateString()}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          {/* API Keys Tab */}
          <TabsContent value="api" className="mt-0 h-full">
            <ScrollArea className="h-full">
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-white mb-2">API Configuration</h3>
                  <p className="text-sm text-slate-400 mb-4">
                    Configure API keys for external services. Leave blank to continue using fake data for development.
                  </p>
                </div>

                <div className="border border-amber-500/20 rounded-lg p-4 bg-amber-500/5">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                    <span className="text-sm font-medium text-amber-300">Coming Soon</span>
                  </div>
                  <p className="text-sm text-slate-400">
                    API key management will be available in a future update. Currently, the system uses the existing 
                    settings page for API configuration.
                  </p>
                </div>

                <div className="space-y-3">
                  {[
                    { name: "Google Places API", status: "Not Configured" },
                    { name: "Facebook Graph API", status: "Not Configured" },
                    { name: "LinkedIn API", status: "Not Configured" },
                    { name: "YellowPages API", status: "Not Configured" },
                    { name: "Zoho CRM API", status: "Not Configured" }
                  ].map((api) => (
                    <div key={api.name} className="flex items-center justify-between p-3 border border-slate-700 rounded-lg bg-slate-800/30">
                      <div className="flex items-center space-x-3">
                        <Key className="w-4 h-4 text-slate-400" />
                        <span className="text-white">{api.name}</span>
                      </div>
                      <Badge variant="secondary" className="bg-slate-600 text-slate-300">
                        {api.status}
                      </Badge>
                    </div>
                  ))}
                </div>

                <div className="text-center py-4">
                  <Button 
                    variant="outline" 
                    className="border-slate-600 text-slate-400 hover:bg-slate-800"
                    disabled
                  >
                    Configure APIs (Coming Soon)
                  </Button>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl max-h-[90vh] bg-slate-900 border-slate-700 text-white p-0">
          {content}
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent className="max-h-[95vh] bg-slate-900 border-slate-700 text-white">
        {content}
      </DrawerContent>
    </Drawer>
  );
}