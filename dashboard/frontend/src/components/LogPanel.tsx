import React, { useRef, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';

interface LogPanelProps {
  logs: string[];
  maxHeight?: number;
}

const LogPanel: React.FC<LogPanelProps> = ({ logs, maxHeight = 300 }) => {
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when logs update
  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Parse log level and add appropriate color
  const getLogStyle = (log: string): { color: string } => {
    if (log.includes('[ERROR]') || log.includes('error')) {
      return { color: '#f44336' }; // Red for errors
    }
    if (log.includes('[WARNING]') || log.includes('warning')) {
      return { color: '#ff9800' }; // Orange for warnings
    }
    if (log.includes('[INFO]') || log.includes('info')) {
      return { color: '#2196f3' }; // Blue for info
    }
    if (log.includes('success') || log.includes('completed')) {
      return { color: '#4caf50' }; // Green for success
    }
    return { color: 'inherit' }; // Default color
  };

  // Format timestamp if present
  const formatLogEntry = (log: string): { time: string; message: string } => {
    // Try to extract timestamp in format [HH:MM:SS]
    const timeMatch = log.match(/\[(\d{2}:\d{2}:\d{2})\]/);
    
    if (timeMatch) {
      const time = timeMatch[1];
      const message = log.replace(timeMatch[0], '').trim();
      return { time, message };
    }
    
    // Try ISO format
    const isoMatch = log.match(/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/);
    if (isoMatch) {
      try {
        const date = new Date(isoMatch[1]);
        const time = date.toLocaleTimeString();
        const message = log.replace(isoMatch[0], '').trim();
        return { time, message };
      } catch {
        // If date parsing fails, return original
      }
    }
    
    return { time: '', message: log };
  };

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Generation Logs
      </Typography>
      
      <Box 
        sx={{ 
          maxHeight, 
          overflowY: 'auto', 
          bgcolor: '#f5f5f5', 
          borderRadius: 1,
          fontFamily: 'monospace',
          fontSize: '0.875rem'
        }}
      >
        <List dense disablePadding>
          {logs.length === 0 ? (
            <ListItem>
              <ListItemText 
                primary="No logs available yet. Generation may not have started."
                primaryTypographyProps={{ color: 'text.secondary', fontStyle: 'italic' }}
              />
            </ListItem>
          ) : (
            logs.map((log, index) => {
              const { time, message } = formatLogEntry(log);
              const style = getLogStyle(log);
              
              return (
                <React.Fragment key={index}>
                  <ListItem sx={{ py: 0.5 }}>
                    {time && (
                      <Typography 
                        component="span" 
                        variant="caption" 
                        color="text.secondary"
                        sx={{ mr: 1, minWidth: '70px', display: 'inline-block' }}
                      >
                        {time}
                      </Typography>
                    )}
                    <Typography 
                      component="span" 
                      variant="body2" 
                      sx={{ ...style, wordBreak: 'break-word' }}
                    >
                      {message}
                    </Typography>
                  </ListItem>
                  {index < logs.length - 1 && <Divider component="li" />}
                </React.Fragment>
              );
            })
          )}
          <div ref={logEndRef} />
        </List>
      </Box>
    </Paper>
  );
};

export default LogPanel;