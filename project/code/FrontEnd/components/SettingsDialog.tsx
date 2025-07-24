'use client';

import { useState } from 'react';
import { useMediaQuery } from '@/hooks/useMediaQuery';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from '@/components/ui/drawer';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Settings, Workflow, Key } from 'lucide-react';
import { WorkflowSettings } from './WorkflowSettings';

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const [activeTab, setActiveTab] = useState('workflow');
  const isDesktop = useMediaQuery('(min-width: 768px)');

  const content = (
    <>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-blue-600/20 flex items-center justify-center">
          <Settings className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-white">Settings</h2>
          <p className="text-sm text-gray-400">Configure workflow scheduling and API keys</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-gray-800/50 border border-gray-700">
          <TabsTrigger 
            value="workflow" 
            className="flex items-center gap-2 data-[state=active]:bg-blue-600 data-[state=active]:text-white"
          >
            <Workflow className="w-4 h-4" />
            <span className="hidden sm:inline">Workflow</span>
          </TabsTrigger>
          <TabsTrigger 
            value="apikeys" 
            className="flex items-center gap-2 data-[state=active]:bg-blue-600 data-[state=active]:text-white"
          >
            <Key className="w-4 h-4" />
            <span className="hidden sm:inline">API Keys</span>
          </TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="workflow" className="mt-0">
            <WorkflowSettings />
          </TabsContent>

          <TabsContent value="apikeys" className="mt-0">
            <div className="space-y-6">
              <div className="text-center py-12">
                <Key className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white mb-2">API Keys Management</h3>
                <p className="text-gray-400 mb-6">
                  Configure API keys for external lead sources and CRM integrations.
                </p>
                <div className="flex flex-wrap gap-2 justify-center mb-6">
                  <Badge variant="outline" className="text-gray-400 border-gray-600">Google</Badge>
                  <Badge variant="outline" className="text-gray-400 border-gray-600">Facebook</Badge>
                  <Badge variant="outline" className="text-gray-400 border-gray-600">LinkedIn</Badge>
                  <Badge variant="outline" className="text-gray-400 border-gray-600">YellowPages</Badge>
                  <Badge variant="outline" className="text-gray-400 border-gray-600">Zoho CRM</Badge>
                </div>
                <Button 
                  variant="outline" 
                  onClick={() => window.open('/Settings', '_blank')}
                  className="border-gray-600 text-gray-300 hover:bg-gray-800"
                >
                  Open Legacy Settings
                </Button>
              </div>
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </>
  );

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[700px] max-h-[90vh] bg-gray-900 border-gray-700 text-white p-0 overflow-hidden flex flex-col">
          <DialogHeader className="sr-only">
            <DialogTitle>Settings</DialogTitle>
            <DialogDescription>Configure workflow scheduling and API keys</DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-y-auto p-6">
            {content}
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent className="bg-gray-900 border-gray-700 text-white p-0 max-h-[90vh] overflow-hidden flex flex-col">
        <DrawerHeader className="sr-only">
          <DrawerTitle>Settings</DrawerTitle>
          <DrawerDescription>Configure workflow scheduling and API keys</DrawerDescription>
        </DrawerHeader>
        <div className="flex-1 overflow-y-auto p-6">
          {content}
        </div>
      </DrawerContent>
    </Drawer>
  );
}