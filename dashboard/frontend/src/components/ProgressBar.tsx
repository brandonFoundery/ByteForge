import React from 'react';
import { 
  Box, 
  CircularProgress, 
  Typography, 
  Paper,
  Stack,
  Chip
} from '@mui/material';
import type { GenerationSummary } from '../types';

interface ProgressBarProps {
  summary: GenerationSummary;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ summary }) => {
  // Format time remaining
  const formatTimeRemaining = (seconds?: number): string => {
    if (!seconds || seconds <= 0) return 'Calculating...';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (minutes < 1) {
      return `${remainingSeconds}s remaining`;
    }
    
    return `${minutes}m ${remainingSeconds}s remaining`;
  };

  // Format average document time
  const formatAverageTime = (seconds?: number): string => {
    if (!seconds) return 'N/A';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (minutes < 1) {
      return `${remainingSeconds}s`;
    }
    
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Calculate progress percentage
  const progress = Math.round(summary.overall_progress);
  
  // Determine if generation is complete
  const isComplete = summary.completed + summary.failed >= summary.total_documents;
  
  // Format start time
  const formatStartTime = (timestamp?: string): string => {
    if (!timestamp) return 'Not started';
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, alignItems: 'center', gap: 3 }}>
        {/* Progress Circle */}
        <Box sx={{ position: 'relative', display: 'inline-flex' }}>
          <CircularProgress 
            variant="determinate" 
            value={progress} 
            size={100} 
            thickness={5}
            color={isComplete ? 'success' : 'primary'}
          />
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: 'absolute',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant="h5" component="div" color="text.secondary">
              {`${progress}%`}
            </Typography>
          </Box>
        </Box>
        
        {/* Status Information */}
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h6" gutterBottom>
            Generation Progress
          </Typography>
          
          <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
            <Chip 
              label={`${summary.completed} Completed`} 
              color="success" 
              variant="outlined"
            />
            <Chip 
              label={`${summary.in_progress} In Progress`} 
              color="primary" 
              variant="outlined"
            />
            <Chip 
              label={`${summary.failed} Failed`} 
              color="error" 
              variant="outlined"
            />
            <Chip 
              label={`${summary.not_started} Not Started`} 
              color="default" 
              variant="outlined"
            />
          </Stack>
          
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Started at: {formatStartTime(summary.generation_started_at)}
          </Typography>
          
          {!isComplete && (
            <>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                ETA: {formatTimeRemaining(summary.estimated_time_remaining)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average document time: {formatAverageTime(summary.average_document_time)}
              </Typography>
            </>
          )}
          
          {isComplete && (
            <Typography variant="body1" color="success.main" fontWeight="bold">
              Generation Complete!
            </Typography>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default ProgressBar;