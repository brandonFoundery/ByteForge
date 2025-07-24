'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ProjectOverview, ProjectPhase } from '@/types/monitoring';
import { Folder, CheckCircle2, Circle, AlertCircle } from 'lucide-react';

interface ProjectOverviewCardProps {
  overview: ProjectOverview;
  className?: string;
}

export const ProjectOverviewCard: React.FC<ProjectOverviewCardProps> = ({ 
  overview, 
  className = '' 
}) => {
  const phaseOrder = [
    ProjectPhase.Initialization,
    ProjectPhase.RequirementsGathering,
    ProjectPhase.DocumentGeneration,
    ProjectPhase.CodeGeneration,
    ProjectPhase.Testing,
    ProjectPhase.Deployment,
    ProjectPhase.Completed
  ];

  const getPhaseIcon = (phase: ProjectPhase, isCurrent: boolean, isCompleted: boolean) => {
    if (isCompleted) return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    if (isCurrent) return <Circle className="h-5 w-5 text-blue-500 animate-pulse" />;
    return <Circle className="h-5 w-5 text-gray-300" />;
  };

  const formatPhaseName = (phase: ProjectPhase) => {
    return phase.replace(/([A-Z])/g, ' $1').trim();
  };

  const currentPhaseIndex = phaseOrder.indexOf(overview.currentPhase);

  return (
    <Card className={className} data-testid="project-overview-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center">
              <Folder className="h-5 w-5 mr-2" />
              {overview.projectName}
            </CardTitle>
            <CardDescription>
              {overview.projectType} • Created {new Date(overview.createdAt).toLocaleDateString()}
            </CardDescription>
          </div>
          {overview.hasErrors && (
            <Badge variant="destructive">
              <AlertCircle className="h-3 w-3 mr-1" />
              Has Errors
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Overall Progress */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-2xl font-bold" data-testid="overall-progress">
              {overview.overallProgress}%
            </span>
          </div>
          <Progress value={overview.overallProgress} className="h-3" />
          {overview.estimatedCompletion && (
            <p className="text-xs text-muted-foreground mt-1">
              Est. completion: {new Date(overview.estimatedCompletion).toLocaleDateString()}
            </p>
          )}
        </div>

        {/* Phase Progress */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Project Phases</h4>
          <div className="space-y-2">
            {phaseOrder.map((phase, index) => {
              const isCompleted = index < currentPhaseIndex;
              const isCurrent = phase === overview.currentPhase;
              const phaseProgress = overview.phases.find(p => p.phase === phase);

              return (
                <div 
                  key={phase} 
                  className={`flex items-center space-x-3 ${
                    !isCompleted && !isCurrent ? 'opacity-50' : ''
                  }`}
                  data-testid={`phase-${formatPhaseName(phase).toLowerCase().replace(' ', '-')}`}
                >
                  {getPhaseIcon(phase, isCurrent, isCompleted)}
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">{formatPhaseName(phase)}</span>
                      {phaseProgress && (
                        <span className="text-xs text-muted-foreground">
                          {phaseProgress.progress}%
                        </span>
                      )}
                    </div>
                    {isCurrent && phaseProgress && (
                      <Progress 
                        value={phaseProgress.progress} 
                        className="h-1 mt-1" 
                      />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Active Components */}
        <div className="pt-3 border-t">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Active Documents</p>
              <p className="font-semibold">
                {Object.keys(overview.documentProgress).length}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">Active Agents</p>
              <p className="font-semibold">{overview.activeAgents.length}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};