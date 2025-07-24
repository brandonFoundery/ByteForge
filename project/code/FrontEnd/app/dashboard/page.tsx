'use client';

import { useState } from 'react';
import Link from 'next/link';
import { withAuth } from '@/contexts/AuthContext';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Search, 
  Filter, 
  Settings, 
  Download, 
  Users, 
  TrendingUp, 
  CheckCircle,
  Star,
  Activity,
  BarChart3,
  Sparkles,
  LogOut
} from 'lucide-react';
import { PipelineFlow } from '@/components/PipelineFlow';
import { MetricsDashboard } from '@/components/MetricsDashboard';
import { LeadsTable } from '@/components/LeadsTable';
import { useLeadStore } from '@/hooks/useLeadStore';
import { SettingsDialog } from '@/components/SettingsDialog';
import { motion } from 'framer-motion';

function Dashboard() {
  const { leads, metrics, isProcessing, isConnected, connectionState } = useLeadStore();
  const { logout } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [selectedScoreRange, setSelectedScoreRange] = useState('all');
  const [showSettings, setShowSettings] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      window.location.href = '/';  // Force redirect to home
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <motion.div 
        className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    LeadFlow Pro
                  </h1>
                  <p className="text-sm text-slate-400">Client Dashboard</p>
                </div>
              </Link>
              <div className="flex items-center space-x-4 ml-8">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                  <span className="text-sm text-slate-400">
                    {isConnected ? 'Live Updates' : 'Disconnected'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${isProcessing ? 'bg-blue-500 animate-pulse' : 'bg-slate-500'}`} />
                  <span className="text-sm text-slate-400">
                    {isProcessing ? 'Processing Active' : 'Idle'}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button 
                variant="outline" 
                size="sm" 
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                onClick={() => setShowSettings(true)}
              >
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <motion.div
          className="space-y-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Page Header */}
          <motion.div variants={itemVariants}>
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-white mb-2">Lead Processing Dashboard</h1>
              <p className="text-slate-400">Real-time lead generation and processing pipeline</p>
            </div>
          </motion.div>
          {/* Key Metrics */}
          <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-purple-200">Total Leads Today</p>
                    <p className="text-3xl font-bold text-white">{metrics.totalLeads.toLocaleString()}</p>
                    <p className="text-sm text-green-400">+{metrics.dailyGrowth}% today</p>
                  </div>
                  <Users className="w-8 h-8 text-purple-400" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-200">Qualified Leads Today</p>
                    <p className="text-3xl font-bold text-white">{metrics.qualifiedLeads.toLocaleString()}</p>
                    <p className="text-sm text-green-400">+{metrics.weeklyGrowth}% this week</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-200">Conversion Rate Today</p>
                    <p className="text-3xl font-bold text-white">{metrics.conversionRate.toFixed(1)}%</p>
                    <p className="text-sm text-green-400">{metrics.activeHarvesters} active harvesters</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-400" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-yellow-200">Avg. Score Today</p>
                    <p className="text-3xl font-bold text-white">{Math.round(metrics.scoreAverage)}</p>
                    <p className="text-sm text-green-400">{metrics.processingTime}s avg time</p>
                  </div>
                  <Star className="w-8 h-8 text-yellow-400" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Pipeline Flow */}
          <motion.div variants={itemVariants}>
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl text-white flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-purple-400" />
                  Lead Generation Pipeline
                  <Badge className="ml-3 bg-green-500/20 text-green-300 border-green-500/30">
                    Live
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="h-96 w-full">
                  <PipelineFlow />
                </div>
                {/* Mobile message when pipeline is hidden */}
                <div className="md:hidden p-8 text-center">
                  <Activity className="w-12 h-12 mx-auto mb-4 text-slate-600" />
                  <p className="text-slate-400">Pipeline visualization available on desktop</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Performance Analytics */}
          <motion.div variants={itemVariants}>
            <MetricsDashboard metrics={metrics} />
          </motion.div>

          {/* Leads Management */}
          <motion.div variants={itemVariants}>
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl text-white flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2 text-blue-400" />
                    Recent Leads
                  </CardTitle>
                  <div className="flex items-center space-x-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                      <Input
                        placeholder="Search leads..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-slate-800 border-slate-700 text-white placeholder-slate-400 w-64"
                      />
                    </div>
                    <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                      <SelectTrigger className="w-32 bg-slate-800 border-slate-700 text-white">
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="new">New</SelectItem>
                        <SelectItem value="enriched">Enriched</SelectItem>
                        <SelectItem value="vetted">Vetted</SelectItem>
                        <SelectItem value="scored">Scored</SelectItem>
                        <SelectItem value="exported">Exported</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={selectedScoreRange} onValueChange={setSelectedScoreRange}>
                      <SelectTrigger className="w-32 bg-slate-800 border-slate-700 text-white">
                        <SelectValue placeholder="Score" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="all">All Scores</SelectItem>
                        <SelectItem value="80+">80+ (High)</SelectItem>
                        <SelectItem value="60-79">60-79 (Good)</SelectItem>
                        <SelectItem value="40-59">40-59 (Fair)</SelectItem>
                        <SelectItem value="<40">Below 40</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={selectedSource} onValueChange={setSelectedSource}>
                      <SelectTrigger className="w-32 bg-slate-800 border-slate-700 text-white">
                        <SelectValue placeholder="Source" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="all">All Sources</SelectItem>
                        <SelectItem value="Google">Google</SelectItem>
                        <SelectItem value="Facebook">Facebook</SelectItem>
                        <SelectItem value="LinkedIn">LinkedIn</SelectItem>
                        <SelectItem value="YellowPages">YellowPages</SelectItem>
                        <SelectItem value="NPPES">NPPES</SelectItem>
                        <SelectItem value="Manual">Manual</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                      <Filter className="w-4 h-4 mr-2" />
                      Filter
                    </Button>
                    <Button variant="outline" size="sm" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <LeadsTable 
                  leads={leads} 
                  searchTerm={searchTerm}
                  selectedStatus={selectedStatus}
                  selectedSource={selectedSource}
                  selectedScoreRange={selectedScoreRange}
                />
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>

      {/* Settings Dialog */}
      <SettingsDialog 
        open={showSettings} 
        onOpenChange={setShowSettings} 
      />
    </div>
  );
}

export default withAuth(Dashboard);