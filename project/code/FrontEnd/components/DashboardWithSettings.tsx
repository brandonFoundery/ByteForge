'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Settings, 
  TrendingUp, 
  Users, 
  Target, 
  Zap, 
  Clock, 
  Award, 
  Database,
  RefreshCcw,
  Activity
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { SettingsDialog } from './SettingsDialog';
import { MetricsDashboard } from './MetricsDashboard';

interface DashboardMetrics {
  totalLeads: number;
  qualifiedLeads: number;
  conversionRate: number;
  activeHarvesters: number;
  processingTime: number;
  scoreAverage: number;
  dailyGrowth: number;
  weeklyGrowth: number;
  sourceBreakdown: Record<string, number>;
  statusBreakdown: Record<string, number>;
}

export function DashboardWithSettings() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Fetch metrics from backend
  const fetchMetrics = async () => {
    try {
      setError(null);
      const response = await fetch('http://localhost:5000/api/v1/leads/metrics');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch metrics: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Transform API data to component format
      const transformedData: DashboardMetrics = {
        totalLeads: data.counts.total,
        qualifiedLeads: data.counts.qualified || 0,
        conversionRate: data.averageScore || 0,
        activeHarvesters: Object.keys(data.sourceBreakdown).length,
        processingTime: 2, // Static for now
        scoreAverage: data.averageScore || 0,
        dailyGrowth: data.counts.daily || 0,
        weeklyGrowth: data.counts.weekly || 0,
        sourceBreakdown: data.sourceBreakdown,
        statusBreakdown: data.statusBreakdown
      };
      
      setMetrics(transformedData);
      setLastUpdated(new Date());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load and periodic refresh
  useEffect(() => {
    fetchMetrics();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Listen for messages from parent window (MVC view)
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'OPEN_SETTINGS') {
        setSettingsOpen(true);
      }
    };

    window.addEventListener('message', handleMessage);
    
    // Notify parent that dashboard is ready
    if (window.parent) {
      window.parent.postMessage({ type: 'DASHBOARD_READY' }, '*');
    }

    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black p-6">
        <div className="max-w-6xl mx-auto">
          <Card className="bg-red-900/20 border-red-700/50">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-red-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-6 h-6 text-red-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Dashboard Error</h3>
              <p className="text-red-200 mb-4">{error}</p>
              <Button onClick={fetchMetrics} variant="outline" className="border-red-600">
                <RefreshCcw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white">
      {/* Settings Button - Fixed Position */}
      <Button
        onClick={() => setSettingsOpen(true)}
        className="fixed top-6 right-6 z-50 bg-blue-600 hover:bg-blue-700 shadow-lg"
        size="icon"
      >
        <Settings className="w-5 h-5" />
      </Button>

      {/* Main Dashboard Content */}
      <div className="p-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <motion.div 
            className="mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">Lead Processing Dashboard</h1>
                <p className="text-gray-400">Real-time monitoring and workflow management</p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Clock className="w-4 h-4" />
                  Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={fetchMetrics}
                  disabled={loading}
                  className="mt-2 border-gray-600"
                >
                  <RefreshCcw className={`w-3 h-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </div>
          </motion.div>

          {/* Metrics Cards */}
          {loading && !metrics ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {[...Array(4)].map((_, i) => (
                <Card key={i} className="bg-gray-800/50 border-gray-700">
                  <CardContent className="p-4">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-700 rounded w-20 mb-2"></div>
                      <div className="h-8 bg-gray-700 rounded w-16 mb-2"></div>
                      <div className="h-3 bg-gray-700 rounded w-24"></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : metrics ? (
            <MetricsDashboard metrics={metrics} />
          ) : null}

          {/* Source Breakdown */}
          {metrics && (
            <motion.div 
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
            >
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-400" />
                    Lead Sources
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(metrics.sourceBreakdown).map(([source, count]) => {
                      const percentage = Math.round((count / metrics.totalLeads) * 100);
                      const getSourceIcon = () => {
                        switch (source.toLowerCase()) {
                          case 'google': return '🌐';
                          case 'facebook': return '📘';
                          case 'linkedin': return '💼';
                          case 'yellowpages': return '📞';
                          default: return '⚡';
                        }
                      };

                      return (
                        <div key={source} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{getSourceIcon()}</span>
                            <span className="text-white capitalize">{source}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-gray-300 border-gray-600">
                              {count}
                            </Badge>
                            <span className="text-sm text-gray-400 w-8">{percentage}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-400" />
                    Processing Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(metrics.statusBreakdown).map(([status, count]) => {
                      const percentage = Math.round((count / metrics.totalLeads) * 100);
                      const getStatusColor = () => {
                        switch (status.toLowerCase()) {
                          case 'processed': return 'text-green-400 border-green-600/30';
                          case 'hot': return 'text-red-400 border-red-600/30';
                          case 'warm': return 'text-orange-400 border-orange-600/30';
                          case 'cold': return 'text-blue-400 border-blue-600/30';
                          case 'vetted': return 'text-purple-400 border-purple-600/30';
                          case 'enriched': return 'text-yellow-400 border-yellow-600/30';
                          default: return 'text-gray-400 border-gray-600/30';
                        }
                      };

                      return (
                        <div key={status} className="flex items-center justify-between">
                          <span className="text-white capitalize">{status}</span>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className={`${getStatusColor()}`}>
                              {count}
                            </Badge>
                            <span className="text-sm text-gray-400 w-8">{percentage}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </div>

      {/* Settings Dialog */}
      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  );
}