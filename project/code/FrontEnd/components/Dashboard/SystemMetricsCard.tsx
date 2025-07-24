'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { SystemMetrics } from '@/types/monitoring';
import { Cpu, HardDrive, Server, Activity, CheckCircle, XCircle } from 'lucide-react';

interface SystemMetricsCardProps {
  metrics: SystemMetrics;
  className?: string;
}

interface MetricGaugeProps {
  label: string;
  value: number;
  max?: number;
  unit?: string;
  icon: React.ReactNode;
  testId: string;
}

const MetricGauge: React.FC<MetricGaugeProps> = ({ 
  label, 
  value, 
  max = 100, 
  unit = '%',
  icon,
  testId
}) => {
  const percentage = (value / max) * 100;
  const isHigh = percentage > 80;
  const isMedium = percentage > 60;
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="space-y-2" data-testid={testId}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {icon}
                <span className="text-sm font-medium">{label}</span>
              </div>
              <span className={`text-sm font-bold ${
                isHigh ? 'text-red-500' : isMedium ? 'text-yellow-500' : 'text-green-500'
              }`}>
                {value}{unit}
              </span>
            </div>
            <Progress 
              value={percentage} 
              className={`h-2 ${
                isHigh ? '[&>div]:bg-red-500' : isMedium ? '[&>div]:bg-yellow-500' : ''
              }`}
            />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>{label}: {value}{unit}</p>
          {isHigh && <p className="text-xs text-red-400">High usage detected</p>}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export const SystemMetricsCard: React.FC<SystemMetricsCardProps> = ({ 
  metrics, 
  className = '' 
}) => {
  const formatBytes = (bytes: number): { value: number; unit: string } => {
    const gb = bytes / (1024 * 1024 * 1024);
    if (gb > 1) return { value: Math.round(gb * 10) / 10, unit: 'GB' };
    
    const mb = bytes / (1024 * 1024);
    return { value: Math.round(mb), unit: 'MB' };
  };

  const diskUsed = formatBytes(metrics.diskSpaceUsed);
  const diskAvailable = formatBytes(metrics.diskSpaceAvailable);
  const diskTotal = metrics.diskSpaceUsed + metrics.diskSpaceAvailable;
  const diskUsagePercent = Math.round((metrics.diskSpaceUsed / diskTotal) * 100);

  return (
    <Card className={className} data-testid="system-metrics-card">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Server className="h-5 w-5 mr-2" />
          System Metrics
        </CardTitle>
        <CardDescription>
          Real-time system performance and health
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Resource Metrics */}
        <div className="space-y-4">
          <MetricGauge
            label="CPU Usage"
            value={Math.round(metrics.cpuUsage)}
            icon={<Cpu className="h-4 w-4" />}
            testId="cpu-gauge"
          />
          
          <MetricGauge
            label="Memory Usage"
            value={Math.round(metrics.memoryUsage / 1024)} // Convert MB to GB
            max={16} // Assuming 16GB total
            unit="GB"
            icon={<Server className="h-4 w-4" />}
            testId="memory-gauge"
          />
          
          <MetricGauge
            label="Disk Usage"
            value={diskUsagePercent}
            icon={<HardDrive className="h-4 w-4" />}
            testId="disk-gauge"
          />
        </div>

        {/* System Stats */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Active Projects</p>
            <p className="text-2xl font-bold">{metrics.activeProjects}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Active Agents</p>
            <p className="text-2xl font-bold">{metrics.activeAgents}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Queued Tasks</p>
            <p className="text-2xl font-bold">{metrics.queuedTasks}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">System Load</p>
            <p className="text-2xl font-bold">{metrics.systemLoad.toFixed(2)}</p>
          </div>
        </div>

        {/* Service Health */}
        <div className="space-y-3 pt-4 border-t">
          <h4 className="text-sm font-medium">Service Health</h4>
          <div className="space-y-2">
            {Object.entries(metrics.serviceHealth).map(([name, health]) => (
              <div 
                key={name} 
                className="flex items-center justify-between"
                data-testid={`service-health-${name.toLowerCase().replace(' ', '-')}`}
              >
                <div className="flex items-center space-x-2">
                  {health.isHealthy ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                  <span className="text-sm">{name}</span>
                </div>
                <Badge variant={health.isHealthy ? 'default' : 'destructive'}>
                  {health.isHealthy ? 'Healthy' : 'Unhealthy'}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Disk Space Details */}
        <div className="text-xs text-muted-foreground pt-2 border-t">
          <p>Disk: {diskUsed.value}{diskUsed.unit} used / {diskAvailable.value}{diskAvailable.unit} available</p>
          <p>Last updated: {new Date(metrics.timestamp).toLocaleTimeString()}</p>
        </div>
      </CardContent>
    </Card>
  );
};