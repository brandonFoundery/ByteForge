'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { useSignalR } from '@/hooks/useSignalR';
import { monitoringService } from '@/services/monitoringService';
import { 
  DocumentGenerationStatus,
  AgentStatus,
  ProjectOverview,
  SystemMetrics,
  DocumentGenerationAnalytics,
  AgentPerformanceAnalytics,
  AnalyticsExportFormat,
  FileSystemChangeEventArgs
} from '@/types/monitoring';
import { DocumentGenerationCard } from './Dashboard/DocumentGenerationCard';
import { AgentStatusPanel } from './Dashboard/AgentStatusPanel';
import { ProjectOverviewCard } from './Dashboard/ProjectOverviewCard';
import { SystemMetricsCard } from './Dashboard/SystemMetricsCard';
import { AnalyticsPanel } from './Dashboard/AnalyticsPanel';
import { FileSystemChangesPanel } from './Dashboard/FileSystemChangesPanel';
import { RefreshCw, Download, Activity } from 'lucide-react';

interface MonitoringDashboardProps {
  initialProjectId?: string;
}

export const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({ 
  initialProjectId 
}) => {
  const { toast } = useToast();
  const { isConnected, subscribe, unsubscribe } = useSignalR();
  
  // State
  const [selectedProjectId, setSelectedProjectId] = useState<string>(initialProjectId || '');
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Dashboard data
  const [documentStatus, setDocumentStatus] = useState<DocumentGenerationStatus | null>(null);
  const [activeAgents, setActiveAgents] = useState<AgentStatus[]>([]);
  const [projectOverview, setProjectOverview] = useState<ProjectOverview | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [documentAnalytics, setDocumentAnalytics] = useState<DocumentGenerationAnalytics | null>(null);
  const [agentAnalytics, setAgentAnalytics] = useState<AgentPerformanceAnalytics | null>(null);
  const [fileChanges, setFileChanges] = useState<FileSystemChangeEventArgs[]>([]);
  
  // Date range for analytics
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // Last 7 days
    to: new Date()
  });

  // Load initial data
  useEffect(() => {
    loadProjects();
  }, []);

  // Load project data when selection changes
  useEffect(() => {
    if (selectedProjectId) {
      loadDashboardData();
      subscribeToUpdates();
    }
    
    return () => {
      if (selectedProjectId) {
        unsubscribeFromUpdates();
      }
    };
  }, [selectedProjectId]);

  // Load system metrics periodically
  useEffect(() => {
    loadSystemMetrics();
    const interval = setInterval(loadSystemMetrics, 10000); // Every 10 seconds
    
    return () => clearInterval(interval);
  }, []);

  const loadProjects = async () => {
    try {
      const projectsStatus = await monitoringService.getAllProjectsStatus();
      const projectList = projectsStatus.map(p => ({ 
        id: p.projectId, 
        name: p.projectName 
      }));
      setProjects(projectList);
      
      if (!selectedProjectId && projectList.length > 0) {
        setSelectedProjectId(projectList[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
      setError('Failed to load projects');
    }
  };

  const loadDashboardData = async () => {
    if (!selectedProjectId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const [
        docStatus,
        agents,
        overview,
        docAnalytics,
        agentPerf
      ] = await Promise.all([
        monitoringService.getDocumentGenerationStatus(selectedProjectId),
        monitoringService.getActiveAgents(),
        monitoringService.getProjectOverview(selectedProjectId),
        monitoringService.getDocumentGenerationAnalytics(dateRange.from, dateRange.to),
        monitoringService.getAgentPerformanceAnalytics(dateRange.from, dateRange.to)
      ]);
      
      setDocumentStatus(docStatus);
      setActiveAgents(agents.filter(a => a.projectId === selectedProjectId));
      setProjectOverview(overview);
      setDocumentAnalytics(docAnalytics);
      setAgentAnalytics(agentPerf);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load monitoring data');
    } finally {
      setIsLoading(false);
    }
  };

  const loadSystemMetrics = async () => {
    try {
      const metrics = await monitoringService.getSystemMetrics();
      setSystemMetrics(metrics);
    } catch (err) {
      console.error('Failed to load system metrics:', err);
    }
  };

  const subscribeToUpdates = () => {
    if (!selectedProjectId) return;
    
    // Subscribe to project updates
    subscribe(`project-${selectedProjectId}`, 'DocumentProgress', (data: any) => {
      // Update document progress
      if (documentStatus && data.entityId.includes(selectedProjectId)) {
        const updatedStatus = { ...documentStatus };
        const docType = data.data.documentType;
        if (updatedStatus.documents[docType]) {
          updatedStatus.documents[docType].progress = data.data.progress;
          updatedStatus.documents[docType].status = data.data.status;
        }
        setDocumentStatus(updatedStatus);
      }
    });
    
    subscribe(`project-${selectedProjectId}`, 'AgentStatus', (data: any) => {
      // Update agent status
      setActiveAgents(prev => {
        const updated = [...prev];
        const index = updated.findIndex(a => a.agentId === data.entityId);
        if (index >= 0) {
          updated[index] = { ...updated[index], state: data.data.state };
        }
        return updated;
      });
    });
    
    subscribe('dashboard', 'FileSystemChange', (data: FileSystemChangeEventArgs) => {
      // Add file system change
      setFileChanges(prev => [data, ...prev].slice(0, 100)); // Keep last 100 changes
    });
  };

  const unsubscribeFromUpdates = () => {
    unsubscribe(`project-${selectedProjectId}`, 'DocumentProgress');
    unsubscribe(`project-${selectedProjectId}`, 'AgentStatus');
    unsubscribe('dashboard', 'FileSystemChange');
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDashboardData();
    await loadSystemMetrics();
    setIsRefreshing(false);
    
    toast({
      title: 'Dashboard refreshed',
      description: 'All data has been updated',
    });
  };

  const handleExport = async (format: AnalyticsExportFormat) => {
    try {
      const blob = await monitoringService.exportAnalytics(format, dateRange.from, dateRange.to);
      const filename = `analytics_${dateRange.from.toISOString().split('T')[0]}_${dateRange.to.toISOString().split('T')[0]}.${format.toLowerCase()}`;
      monitoringService.downloadFile(blob, filename);
      
      toast({
        title: 'Export successful',
        description: `Analytics exported as ${format}`,
      });
    } catch (err) {
      console.error('Export failed:', err);
      toast({
        title: 'Export failed',
        description: 'Failed to export analytics',
        variant: 'destructive',
      });
    }
  };

  const handleRetry = () => {
    setError(null);
    loadDashboardData();
  };

  if (error) {
    return (
      <Card className="w-full">
        <CardContent className="flex flex-col items-center justify-center py-10">
          <p className="text-red-500 mb-4" data-testid="error-message">{error}</p>
          <Button onClick={handleRetry} data-testid="retry-button">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full space-y-4" data-testid="monitoring-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-3xl font-bold">Monitoring Dashboard</h1>
          <Badge 
            variant={isConnected ? 'default' : 'secondary'}
            className={isConnected ? 'bg-green-500' : ''}
            data-testid="realtime-indicator"
          >
            <Activity className="w-3 h-3 mr-1" />
            {isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-2">
          <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
            <SelectTrigger className="w-[200px]" data-testid="project-selector">
              <SelectValue placeholder="Select project" />
            </SelectTrigger>
            <SelectContent>
              {projects.map(project => (
                <SelectItem key={project.id} value={project.id}>
                  {project.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Button
            variant="outline"
            size="icon"
            onClick={handleRefresh}
            disabled={isRefreshing}
            data-testid="refresh-button"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
          
          <Button variant="outline" data-testid="export-button">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Current Project ID (for testing) */}
      <div className="hidden" data-testid="current-project-id">{selectedProjectId}</div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center py-8" data-testid="loading-spinner">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )}

      {/* Main Dashboard Content */}
      {!isLoading && selectedProjectId && (
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="agents">AI Agents</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {projectOverview && (
                <ProjectOverviewCard 
                  overview={projectOverview} 
                  className="lg:col-span-2"
                />
              )}
              {documentStatus && (
                <DocumentGenerationCard 
                  status={documentStatus}
                />
              )}
            </div>
            
            <FileSystemChangesPanel changes={fileChanges} />
          </TabsContent>

          <TabsContent value="agents" className="space-y-4">
            <AgentStatusPanel agents={activeAgents} />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <AnalyticsPanel
              documentAnalytics={documentAnalytics}
              agentAnalytics={agentAnalytics}
              dateRange={dateRange}
              onDateRangeChange={setDateRange}
              onExport={handleExport}
            />
          </TabsContent>

          <TabsContent value="system" className="space-y-4">
            {systemMetrics && <SystemMetricsCard metrics={systemMetrics} />}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};