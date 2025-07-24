'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  Filter, 
  Settings, 
  Download, 
  Users, 
  TrendingUp, 
  Clock, 
  Target, 
  Zap, 
  Database, 
  Shield, 
  Award, 
  ArrowRight,
  Sparkles,
  BarChart3,
  Activity,
  CheckCircle,
  Star
} from 'lucide-react';
import { TurboFlow } from '@/components/TurboFlow';
import { MetricsDashboard } from '@/components/MetricsDashboard';
import { LeadsTable } from '@/components/LeadsTable';
import { useLeadStore } from '@/contexts/LeadContext';
import { motion } from 'framer-motion';

export default function Home() {
  const { leads, metrics, isProcessing } = useLeadStore();
  const { isAuthenticated, isLoading } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [showAuthenticatedUI, setShowAuthenticatedUI] = useState(false);

  // Only show authenticated UI after loading is complete and user is confirmed authenticated
  useEffect(() => {
    if (!isLoading) {
      setShowAuthenticatedUI(isAuthenticated);
    }
  }, [isLoading, isAuthenticated]);

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
    <div className="min-h-screen union-gradient w-full overflow-x-hidden">
      {/* Header */}
      <motion.div 
        className="union-header sticky top-0 z-50 w-full"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="w-full px-4 py-4 max-w-none">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold union-text-gradient">
                    Union Eleven
                  </h1>
                  <p className="text-sm text-gray-400">AI-Powered Lead Processing</p>
                </div>
              </div>
              <div className="flex items-center space-x-2 ml-8">
                <div className={`w-3 h-3 rounded-full ${isProcessing ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
                <span className="text-sm text-gray-300">
                  {isProcessing ? 'Processing Active' : 'System Ready'}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <nav className="hidden md:flex items-center space-x-6">
                <a href="#" className="text-gray-300 hover:text-white transition-colors">Services</a>
                <a href="#" className="text-gray-300 hover:text-white transition-colors">Why Choose Us</a>
                <a href="#" className="text-gray-300 hover:text-white transition-colors">Industries</a>
                <a href="#" className="text-gray-300 hover:text-white transition-colors">Our Process</a>
              </nav>
              <Button 
                variant="outline" 
                size="sm" 
                className="border-purple-500/50 text-purple-200 hover:bg-purple-500/10"
              >
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              {showAuthenticatedUI ? (
                <Link href="/dashboard">
                  <Button
                    size="sm"
                    className="union-button"
                  >
                    Dashboard
                  </Button>
                </Link>
              ) : (
                <Link href="/auth/login">
                  <Button
                    size="sm"
                    className="union-button"
                  >
                    Login
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Hero Section */}
      <motion.div 
        className="relative py-20 px-4 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="container mx-auto max-w-4xl">
          <div className="flex items-center justify-center mb-6">
            <div className="flex items-center space-x-2 bg-purple-500/20 border border-purple-500/30 rounded-full px-4 py-2">
              <Sparkles className="w-4 h-4 text-purple-300" />
              <span className="text-sm text-purple-200">Full-Spectrum AI Solutions</span>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Transform Your Business
            <br />
            <span className="union-text-gradient">
              with AI-Powered Solutions
            </span>
          </h1>
          
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            Leverage cutting-edge AI technology to revolutionize multiple aspects of your 
            business - from marketing and content creation to customer support, process 
            automation, data analytics, and sales optimization.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" className="union-button px-8 py-4 text-lg">
              Schedule a Consultation
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="border-purple-500/50 text-purple-200 hover:bg-purple-500/10 px-8 py-4 text-lg"
            >
              Explore Our Services
            </Button>
          </div>
          
          <div className="mt-12 text-center">
            <p className="text-sm text-gray-400 mb-4">Trusted by innovative companies</p>
            <div className="flex justify-center items-center space-x-8 opacity-50">
              <span className="text-gray-500">Flipbound</span>
              <span className="text-gray-500">Union Eleven</span>
              <span className="text-gray-500">PostKing</span>
              <span className="text-gray-500">Founderly</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="w-full px-4 py-12 max-w-7xl mx-auto">
        <motion.div
          className="space-y-8 w-full"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Key Metrics */}
          <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="union-card border-purple-500/20">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-purple-200">Total Leads</p>
                    <p className="text-3xl font-bold text-white">12,847</p>
                    <p className="text-sm text-green-400">+15% this month</p>
                  </div>
                  <Users className="w-8 h-8 text-purple-400" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="union-card border-blue-500/20">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-200">Processing Rate</p>
                    <p className="text-3xl font-bold text-white">2.3k/hr</p>
                    <p className="text-sm text-green-400">+8% faster</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="union-card border-green-500/20">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-200">Success Rate</p>
                    <p className="text-3xl font-bold text-white">98.7%</p>
                    <p className="text-sm text-green-400">+2.1% improvement</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-400" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="union-card border-yellow-500/20">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-yellow-200">Avg. Score</p>
                    <p className="text-3xl font-bold text-white">87.3</p>
                    <p className="text-sm text-green-400">+4.2 points</p>
                  </div>
                  <Star className="w-8 h-8 text-yellow-400" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Pipeline Flow */}
          <motion.div variants={itemVariants}>
            <Card className="union-card border-purple-500/20">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl text-white flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-purple-400" />
                  AI-Powered Lead Processing Pipeline
                  <Badge className="ml-3 bg-green-500/20 text-green-300 border-green-500/30">
                    Live
                  </Badge>
                </CardTitle>
                <p className="text-gray-400">
                  Real-time visualization of our automated lead processing workflow
                </p>
              </CardHeader>
              <CardContent className="p-0">
                <div className="h-[500px] w-full rounded-lg overflow-hidden">
                  <TurboFlow />
                </div>
                {/* Mobile message when pipeline is hidden */}
                <div className="md:hidden p-8 text-center">
                  <Activity className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400">Pipeline visualization available on desktop</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Performance Analytics */}
          <motion.div variants={itemVariants}>
            <MetricsDashboard metrics={metrics} />
          </motion.div>

          {/* Recent Leads */}
          <motion.div variants={itemVariants}>
            <Card className="union-card border-purple-500/20">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl text-white flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2 text-blue-400" />
                    Lead Management Dashboard
                  </CardTitle>
                  <div className="flex items-center space-x-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        placeholder="Search leads..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-gray-800/50 border-gray-700 text-white placeholder-gray-400 w-64"
                      />
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="border-purple-500/50 text-purple-200 hover:bg-purple-500/10"
                    >
                      <Filter className="w-4 h-4 mr-2" />
                      Filter
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="border-purple-500/50 text-purple-200 hover:bg-purple-500/10"
                    >
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
                />
              </CardContent>
            </Card>
          </motion.div>

          {/* Quick Actions */}
          <motion.div variants={itemVariants}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="union-card border-purple-500/20 hover:border-purple-500/40 transition-colors cursor-pointer group">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-purple-200">AI Configuration</p>
                      <p className="text-xl font-bold text-white group-hover:text-purple-300 transition-colors">
                        Optimize Models
                      </p>
                      <p className="text-sm text-gray-400 mt-1">
                        Fine-tune scoring algorithms
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Shield className="w-8 h-8 text-purple-400" />
                      <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-purple-300 transition-colors" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="union-card border-blue-500/20 hover:border-blue-500/40 transition-colors cursor-pointer group">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-blue-200">Data Integration</p>
                      <p className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors">
                        Connect Sources
                      </p>
                      <p className="text-sm text-gray-400 mt-1">
                        Manage data pipelines
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Database className="w-8 h-8 text-blue-400" />
                      <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-300 transition-colors" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="union-card border-green-500/20 hover:border-green-500/40 transition-colors cursor-pointer group">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-green-200">CRM Integration</p>
                      <p className="text-xl font-bold text-white group-hover:text-green-300 transition-colors">
                        Sync Systems
                      </p>
                      <p className="text-sm text-gray-400 mt-1">
                        Automate lead exports
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Award className="w-8 h-8 text-green-400" />
                      <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-green-300 transition-colors" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
