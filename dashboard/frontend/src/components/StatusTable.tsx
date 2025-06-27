import React from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Chip,
  Tooltip,
  Typography
} from '@mui/material';
import type { DocumentInfo } from '../types';

interface StatusTableProps {
  documents: Record<string, DocumentInfo>;
}

const StatusTable: React.FC<StatusTableProps> = ({ documents }) => {
  // Define status emoji and colors
  type ChipColor = 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  
  const statusConfig: Record<string, { emoji: string; color: ChipColor }> = {
    not_started: { emoji: '⏸️', color: 'default' },
    in_progress: { emoji: '🔄', color: 'primary' },
    generated: { emoji: '✅', color: 'success' },
    refining: { emoji: '🔧', color: 'info' },
    refined: { emoji: '🔧', color: 'success' },
    validating: { emoji: '🔍', color: 'warning' },
    validated: { emoji: '✨', color: 'success' },
    failed: { emoji: '❌', color: 'error' }
  };

  // Sort documents by ID
  const sortedDocuments = Object.values(documents).sort((a, b) => {
    // Sort by document type first (BRD, PRD, etc.)
    const typeA = a.id.split('-')[0];
    const typeB = b.id.split('-')[0];
    if (typeA !== typeB) return typeA.localeCompare(typeB);
    
    // Then by numeric ID
    const numA = parseInt(a.id.split('-')[1] || '0');
    const numB = parseInt(b.id.split('-')[1] || '0');
    return numA - numB;
  });

  // Format file size
  const formatFileSize = (bytes?: number): string => {
    if (bytes === undefined) return 'N/A';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Format timestamp
  const formatTimestamp = (timestamp?: string): string => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell>Document</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Size</TableCell>
            <TableCell>Refinements</TableCell>
            <TableCell>Generated At</TableCell>
            <TableCell>Dependencies</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sortedDocuments.map((doc) => (
            <TableRow key={doc.id} hover>
              <TableCell>
                <Typography variant="body2" fontWeight="bold">
                  {doc.id}
                </Typography>
                <Typography variant="caption" display="block">
                  {doc.title}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip 
                  label={`${statusConfig[doc.status].emoji} ${doc.status}`}
                  color={statusConfig[doc.status].color}
                  size="small"
                />
                {doc.error_message && (
                  <Tooltip title={doc.error_message}>
                    <Chip 
                      label="Error" 
                      color="error" 
                      size="small" 
                      sx={{ ml: 1 }}
                    />
                  </Tooltip>
                )}
              </TableCell>
              <TableCell>{formatFileSize(doc.file_size)}</TableCell>
              <TableCell>{doc.refined_count}</TableCell>
              <TableCell>{formatTimestamp(doc.generated_at)}</TableCell>
              <TableCell>
                {doc.dependencies.length > 0 ? (
                  <Typography variant="caption">
                    {doc.dependencies.join(', ')}
                  </Typography>
                ) : (
                  <Typography variant="caption" color="text.secondary">
                    None
                  </Typography>
                )}
              </TableCell>
            </TableRow>
          ))}
          {sortedDocuments.length === 0 && (
            <TableRow>
              <TableCell colSpan={6} align="center">
                <Typography variant="body2" color="text.secondary" py={2}>
                  No documents found. Generation may not have started yet.
                </Typography>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default StatusTable;