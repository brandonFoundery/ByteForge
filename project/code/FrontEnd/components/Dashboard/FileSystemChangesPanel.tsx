'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { FileSystemChangeEventArgs, FileSystemChangeType } from '@/types/monitoring';
import { FileText, FilePlus, FileX, FileEdit, FolderOpen } from 'lucide-react';

interface FileSystemChangesPanelProps {
  changes: FileSystemChangeEventArgs[];
  className?: string;
}

export const FileSystemChangesPanel: React.FC<FileSystemChangesPanelProps> = ({ 
  changes, 
  className = '' 
}) => {
  const getChangeIcon = (changeType: FileSystemChangeType) => {
    switch (changeType) {
      case FileSystemChangeType.Created:
        return <FilePlus className="h-4 w-4 text-green-500" />;
      case FileSystemChangeType.Modified:
        return <FileEdit className="h-4 w-4 text-blue-500" />;
      case FileSystemChangeType.Deleted:
        return <FileX className="h-4 w-4 text-red-500" />;
      case FileSystemChangeType.Renamed:
        return <FileText className="h-4 w-4 text-yellow-500" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  const getChangeBadge = (changeType: FileSystemChangeType) => {
    const variants: Record<FileSystemChangeType, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      [FileSystemChangeType.Created]: 'default',
      [FileSystemChangeType.Modified]: 'secondary',
      [FileSystemChangeType.Deleted]: 'destructive',
      [FileSystemChangeType.Renamed]: 'outline',
    };

    return (
      <Badge variant={variants[changeType]} className="text-xs" data-testid="change-type">
        {changeType}
      </Badge>
    );
  };

  const formatPath = (path: string) => {
    // Extract filename and parent directory
    const parts = path.split(/[/\\]/);
    const filename = parts[parts.length - 1];
    const parent = parts[parts.length - 2] || '';
    
    return { filename, parent };
  };

  const formatTimestamp = (timestamp: Date) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <Card className={className} data-testid="file-changes-panel">
      <CardHeader>
        <CardTitle className="flex items-center">
          <FolderOpen className="h-5 w-5 mr-2" />
          File System Changes
        </CardTitle>
        <CardDescription>
          Real-time tracking of document and code changes
        </CardDescription>
      </CardHeader>
      <CardContent>
        {changes.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No file changes detected
          </div>
        ) : (
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-2">
              {changes.map((change, index) => {
                const { filename, parent } = formatPath(change.path);
                
                return (
                  <div
                    key={`${change.path}-${change.timestamp}-${index}`}
                    className="flex items-start space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                    data-testid={`file-change-${index}`}
                  >
                    <div className="mt-0.5">
                      {getChangeIcon(change.changeType)}
                    </div>
                    
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-sm" data-testid="change-path">
                            {filename}
                          </span>
                          {getChangeBadge(change.changeType)}
                        </div>
                        <span className="text-xs text-muted-foreground" data-testid="change-timestamp">
                          {formatTimestamp(change.timestamp)}
                        </span>
                      </div>
                      
                      {parent && (
                        <p className="text-xs text-muted-foreground">
                          in {parent}/
                        </p>
                      )}
                      
                      {change.changeType === FileSystemChangeType.Renamed && change.oldPath && (
                        <p className="text-xs text-muted-foreground">
                          from: {formatPath(change.oldPath).filename}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        )}
        
        {changes.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Showing {changes.length} recent changes</span>
              <span>Auto-updates enabled</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};