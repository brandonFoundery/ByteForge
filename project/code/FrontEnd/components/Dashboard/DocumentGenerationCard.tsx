'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { DocumentGenerationStatus, DocumentProgress } from '@/types/monitoring';
import { FileText, CheckCircle, XCircle, Clock } from 'lucide-react';

interface DocumentGenerationCardProps {
  status: DocumentGenerationStatus;
  className?: string;
}

export const DocumentGenerationCard: React.FC<DocumentGenerationCardProps> = ({ 
  status, 
  className = '' 
}) => {
  const getStatusIcon = (doc: DocumentProgress) => {
    if (doc.error) return <XCircle className="h-4 w-4 text-red-500" />;
    if (doc.progress === 100) return <CheckCircle className="h-4 w-4 text-green-500" />;
    return <Clock className="h-4 w-4 text-yellow-500" />;
  };

  const getStatusBadge = (doc: DocumentProgress) => {
    if (doc.error) return <Badge variant="destructive">Failed</Badge>;
    if (doc.progress === 100) return <Badge variant="default">Completed</Badge>;
    if (doc.progress > 0) return <Badge variant="secondary">In Progress</Badge>;
    return <Badge variant="outline">Pending</Badge>;
  };

  const documentTypes = ['BRD', 'PRD', 'FRD', 'TRD'];

  return (
    <Card className={className} data-testid="document-generation-card">
      <CardHeader>
        <CardTitle className="flex items-center">
          <FileText className="h-5 w-5 mr-2" />
          Document Generation
        </CardTitle>
        <CardDescription>
          Progress tracking for requirements documents
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Overall Progress */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Overall Progress</span>
              <span>{status.overallProgress}%</span>
            </div>
            <Progress value={status.overallProgress} className="h-2" />
          </div>

          {/* Document Progress */}
          <ScrollArea className="h-[300px]">
            <div className="space-y-3">
              {documentTypes.map(docType => {
                const doc = status.documents[docType] || {
                  documentType: docType,
                  progress: 0,
                  status: 'Not Started',
                  startedAt: new Date(),
                  milestones: []
                };

                return (
                  <div 
                    key={docType} 
                    className="border rounded-lg p-3 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(doc)}
                        <span className="font-medium">{docType}</span>
                      </div>
                      {getStatusBadge(doc)}
                    </div>
                    
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>{doc.status}</span>
                        <span data-testid={`progress-value-${docType}`}>
                          {doc.progress}%
                        </span>
                      </div>
                      <Progress 
                        value={doc.progress} 
                        className="h-2"
                        data-testid={`progress-bar-${docType}`}
                      />
                    </div>

                    {doc.error && (
                      <p className="text-sm text-red-500">{doc.error}</p>
                    )}

                    {doc.milestones.length > 0 && (
                      <div className="text-xs text-muted-foreground">
                        Latest: {doc.milestones[doc.milestones.length - 1]}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </ScrollArea>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 gap-2 pt-2 border-t">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-500">
                {Object.values(status.documents).filter(d => d.progress === 100).length}
              </p>
              <p className="text-xs text-muted-foreground">Completed</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-500">
                {Object.values(status.documents).filter(d => d.progress > 0 && d.progress < 100).length}
              </p>
              <p className="text-xs text-muted-foreground">In Progress</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};