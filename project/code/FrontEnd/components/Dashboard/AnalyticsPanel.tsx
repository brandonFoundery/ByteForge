'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  DocumentGenerationAnalytics, 
  AgentPerformanceAnalytics,
  AnalyticsExportFormat 
} from '@/types/monitoring';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Download, TrendingUp, Calendar } from 'lucide-react';

interface AnalyticsPanelProps {
  documentAnalytics: DocumentGenerationAnalytics | null;
  agentAnalytics: AgentPerformanceAnalytics | null;
  dateRange: { from: Date; to: Date };
  onDateRangeChange: (range: { from: Date; to: Date }) => void;
  onExport: (format: AnalyticsExportFormat) => void;
  className?: string;
}

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({
  documentAnalytics,
  agentAnalytics,
  dateRange,
  onDateRangeChange,
  onExport,
  className = ''
}) => {
  const [exportMenuOpen, setExportMenuOpen] = useState(false);

  const handleDateRangeSelect = (range: string) => {
    const now = new Date();
    let from = new Date();
    
    switch (range) {
      case '7days':
        from.setDate(now.getDate() - 7);
        break;
      case '30days':
        from.setDate(now.getDate() - 30);
        break;
      case '90days':
        from.setDate(now.getDate() - 90);
        break;
    }
    
    onDateRangeChange({ from, to: now });
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className={`space-y-4 ${className}`} data-testid="analytics-panel">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Analytics Dashboard
              </CardTitle>
              <CardDescription>
                Performance metrics and trends
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setExportMenuOpen(!exportMenuOpen)}
                data-testid="date-range-picker"
              >
                <Calendar className="h-4 w-4 mr-2" />
                <span data-testid="analytics-date-range">
                  {dateRange.from.toLocaleDateString()} - {dateRange.to.toLocaleDateString()}
                </span>
              </Button>
              
              <div className="relative">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setExportMenuOpen(!exportMenuOpen)}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
                
                {exportMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border">
                    <div className="py-1">
                      <button
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                        onClick={() => {
                          onExport(AnalyticsExportFormat.CSV);
                          setExportMenuOpen(false);
                        }}
                        data-testid="export-csv"
                      >
                        Export as CSV
                      </button>
                      <button
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                        onClick={() => {
                          onExport(AnalyticsExportFormat.JSON);
                          setExportMenuOpen(false);
                        }}
                        data-testid="export-json"
                      >
                        Export as JSON
                      </button>
                      <button
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                        onClick={() => {
                          onExport(AnalyticsExportFormat.PDF);
                          setExportMenuOpen(false);
                        }}
                        data-testid="export-pdf"
                      >
                        Export as PDF
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Date Range Quick Select */}
      <div className="flex space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleDateRangeSelect('7days')}
          data-testid="date-range-7days"
        >
          Last 7 days
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleDateRangeSelect('30days')}
        >
          Last 30 days
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleDateRangeSelect('90days')}
        >
          Last 90 days
        </Button>
      </div>

      <Tabs defaultValue="documents" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="documents">Document Generation</TabsTrigger>
          <TabsTrigger value="agents">Agent Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="documents" className="space-y-4">
          {documentAnalytics ? (
            <>
              {/* Summary Stats */}
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Total Generated</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{documentAnalytics.totalDocumentsGenerated}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Success Rate</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-green-500">
                      {documentAnalytics.successRate.toFixed(1)}%
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Avg. Time</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {documentAnalytics.averageGenerationTime.toFixed(1)} min
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Failed</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-red-500">
                      {documentAnalytics.failedGenerations}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Generation Trend Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Generation Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]" data-testid="generation-trend-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={documentAnalytics.dailyTrends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="date" 
                          tickFormatter={(date) => new Date(date).toLocaleDateString()}
                        />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="count" 
                          stroke="#3b82f6" 
                          name="Documents"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="successRate" 
                          stroke="#10b981" 
                          name="Success Rate %"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Document Type Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Document Type Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={Object.entries(documentAnalytics.documentTypeCounts).map(([type, count]) => ({
                            name: type,
                            value: count
                          }))}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {Object.entries(documentAnalytics.documentTypeCounts).map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-[400px]">
                <p className="text-muted-foreground">No document analytics available</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          {agentAnalytics ? (
            <>
              {/* Agent Performance Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Agent Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]" data-testid="agent-performance-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart 
                        data={Object.values(agentAnalytics.agentPerformance)}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="agentType" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="tasksCompleted" fill="#3b82f6" name="Completed" />
                        <Bar dataKey="tasksFailed" fill="#ef4444" name="Failed" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Success Rate Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Agent Success Rates</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]" data-testid="success-rate-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart 
                        data={Object.values(agentAnalytics.agentPerformance)}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="agentType" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="successRate" fill="#10b981" name="Success Rate %" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-[400px]">
                <p className="text-muted-foreground">No agent analytics available</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};