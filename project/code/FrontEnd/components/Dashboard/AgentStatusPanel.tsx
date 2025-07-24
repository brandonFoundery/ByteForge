'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { AgentStatus, AgentState } from '@/types/monitoring';
import { Bot, Activity, AlertCircle, CheckCircle2, XCircle, Pause, Play } from 'lucide-react';

interface AgentStatusPanelProps {
  agents: AgentStatus[];
  className?: string;
}

export const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({ 
  agents, 
  className = '' 
}) => {
  const getStateIcon = (state: AgentState) => {
    switch (state) {
      case AgentState.Running:
        return <Play className="h-4 w-4 text-green-500" />;
      case AgentState.Paused:
        return <Pause className="h-4 w-4 text-yellow-500" />;
      case AgentState.Failed:
        return <XCircle className="h-4 w-4 text-red-500" />;
      case AgentState.Completed:
        return <CheckCircle2 className="h-4 w-4 text-blue-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStateBadge = (state: AgentState) => {
    const variants: Record<AgentState, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      [AgentState.Running]: 'default',
      [AgentState.Paused]: 'secondary',
      [AgentState.Failed]: 'destructive',
      [AgentState.Completed]: 'outline',
      [AgentState.Starting]: 'secondary',
      [AgentState.Stopping]: 'secondary',
      [AgentState.Stopped]: 'outline',
      [AgentState.Idle]: 'outline',
    };

    return (
      <Badge variant={variants[state] || 'outline'} data-testid="agent-state">
        {state}
      </Badge>
    );
  };

  const getAgentTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      'BackendAgent': '🔧',
      'FrontendAgent': '🎨',
      'SecurityAgent': '🔒',
      'InfrastructureAgent': '🏗️',
      'IntegrationAgent': '🔌',
    };
    return icons[type] || '🤖';
  };

  const calculateSuccessRate = (completed: number, failed: number) => {
    const total = completed + failed;
    return total > 0 ? Math.round((completed / total) * 100) : 0;
  };

  if (agents.length === 0) {
    return (
      <Card className={className} data-testid="agent-status-panel">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bot className="h-5 w-5 mr-2" />
            AI Agent Status
          </CardTitle>
          <CardDescription>
            Monitor active AI agents and their health
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No active agents
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={`space-y-4 ${className}`} data-testid="agent-status-panel">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bot className="h-5 w-5 mr-2" />
            AI Agent Status
          </CardTitle>
          <CardDescription>
            {agents.length} active agent{agents.length !== 1 ? 's' : ''}
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {agents.map(agent => {
          const successRate = calculateSuccessRate(agent.tasksCompleted, agent.tasksFailed);
          const timeSinceHeartbeat = Date.now() - new Date(agent.lastHeartbeat).getTime();
          const isHealthy = timeSinceHeartbeat < 60000; // Less than 1 minute

          return (
            <Card 
              key={agent.agentId} 
              data-testid={`agent-card-${agent.agentId}`}
              className="relative overflow-hidden"
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{getAgentTypeIcon(agent.agentType)}</span>
                    <div>
                      <h3 className="font-semibold" data-testid="agent-type">
                        {agent.agentType}
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        {agent.agentId}
                      </p>
                    </div>
                  </div>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <div 
                          className={`h-2 w-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}
                          data-testid="agent-health"
                        />
                      </TooltipTrigger>
                      <TooltipContent>
                        {isHealthy ? 'Healthy' : 'No recent heartbeat'}
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  {getStateIcon(agent.state)}
                  {getStateBadge(agent.state)}
                </div>

                {agent.currentTask && (
                  <p className="text-sm text-muted-foreground truncate">
                    {agent.currentTask}
                  </p>
                )}

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Success Rate</span>
                    <span>{successRate}%</span>
                  </div>
                  <Progress value={successRate} className="h-2" />
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p className="text-muted-foreground">Completed</p>
                    <p className="font-semibold text-green-600">{agent.tasksCompleted}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Failed</p>
                    <p className="font-semibold text-red-600">{agent.tasksFailed}</p>
                  </div>
                </div>

                <div className="text-xs text-muted-foreground">
                  Started: {new Date(agent.startedAt).toLocaleTimeString()}
                </div>
              </CardContent>

              {/* Status indicator bar */}
              <div 
                className={`absolute bottom-0 left-0 right-0 h-1 ${
                  agent.state === AgentState.Running ? 'bg-green-500' :
                  agent.state === AgentState.Failed ? 'bg-red-500' :
                  agent.state === AgentState.Completed ? 'bg-blue-500' :
                  'bg-gray-300'
                }`}
              />
            </Card>
          );
        })}
      </div>
    </div>
  );
};