import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  AppBar, 
  Toolbar, 
  CssBaseline,
  Alert,
  Snackbar,
  Paper,
  Tab,
  Tabs,
  CircularProgress,
  Link
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import StatusTable from './components/StatusTable';
import ProgressBar from './components/ProgressBar';
import LogPanel from './components/LogPanel';
import type { GenerationSummary } from './types';
import { fetchSummary, fetchLogs } from './services/ApiService';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  // State
  const [summary, setSummary] = useState<GenerationSummary>({
    total_documents: 10,
    completed: 0,
    in_progress: 0,
    failed: 0,
    not_started: 10,
    overall_progress: 0,
    documents: {}
  });
  const [logs, setLogs] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Handle tab change
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Initialize data and set up polling
  useEffect(() => {
    const initializeData = async () => {
      try {
        // Fetch initial data
        const initialSummary = await fetchSummary();
        setSummary(initialSummary);
        
        const initialLogs = await fetchLogs(100);
        setLogs(initialLogs);
        
        setLoading(false);
        setConnected(true);
      } catch (error) {
        console.error('Error initializing data:', error);
        setError('Failed to load initial data. Please check if the backend server is running.');
        setLoading(false);
        setConnected(false);
      }
    };
    
    initializeData();
    
    // Set up polling for summary updates
    const summaryInterval = setInterval(async () => {
      try {
        const updatedSummary = await fetchSummary();
        setSummary(updatedSummary);
        setConnected(true);
      } catch (error) {
        console.error('Error fetching summary:', error);
        setConnected(false);
      }
    }, 2000); // Poll every 2 seconds
    
    // Set up polling for logs
    const logsInterval = setInterval(async () => {
      try {
        const newLogs = await fetchLogs(100);
        setLogs(newLogs);
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    }, 5000); // Refresh logs every 5 seconds
    
    // Cleanup intervals on unmount
    return () => {
      clearInterval(summaryInterval);
      clearInterval(logsInterval);
    };
  }, []);

  // Show loading state
  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100vh' 
          }}
        >
          <CircularProgress />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Loading dashboard...
          </Typography>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Requirements Generation Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box 
              sx={{ 
                width: 10, 
                height: 10, 
                borderRadius: '50%', 
                bgcolor: connected ? 'success.main' : 'error.main',
                mr: 1
              }} 
            />
            <Typography variant="body2">
              {connected ? 'Connected' : 'Disconnected'}
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Error message */}
        <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
          <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>
        
        {/* Progress summary */}
        <ProgressBar summary={summary} />
        
        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
          >
            <Tab label="Documents" />
            <Tab label="Logs" />
          </Tabs>
          
          {/* Tab panels */}
          <Box sx={{ p: 2 }}>
            {tabValue === 0 && (
              <StatusTable documents={summary.documents} />
            )}
            
            {tabValue === 1 && (
              <LogPanel logs={logs} maxHeight={400} />
            )}
          </Box>
        </Paper>
        
        {/* Footer */}
        <Box sx={{ mt: 4, textAlign: 'center', color: 'text.secondary' }}>
          <Typography variant="body2">
            FY.WB.Midway Requirements Generation System
          </Typography>
          <Typography variant="caption">
            <Link href="https://github.com/your-repo/requirements-generation" target="_blank">
              View on GitHub
            </Link>
          </Typography>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
