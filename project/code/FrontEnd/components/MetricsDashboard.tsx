'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Users, Target, Zap, Clock, Award, Database } from 'lucide-react';
import { motion } from 'framer-motion';

interface MetricsData {
  totalLeads: number;
  qualifiedLeads: number;
  conversionRate: number;
  activeHarvesters: number;
  processingTime: number;
  scoreAverage: number;
  dailyGrowth: number;
  weeklyGrowth: number;
}

interface MetricsDashboardProps {
  metrics: MetricsData;
}

export function MetricsDashboard({ metrics }: MetricsDashboardProps) {
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
    <motion.div 
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <Card className="bg-gradient-to-br from-purple-900/50 to-purple-800/50 border-purple-700/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-200">Total Leads</p>
                <p className="text-2xl font-bold text-white">{metrics.totalLeads.toLocaleString()}</p>
                <div className="flex items-center mt-1">
                  <TrendingUp className="w-4 h-4 text-green-400 mr-1" />
                  <span className="text-sm text-green-400">+{metrics.dailyGrowth}%</span>
                </div>
              </div>
              <Users className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card className="bg-gradient-to-br from-blue-900/50 to-blue-800/50 border-blue-700/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-200">Qualified Leads</p>
                <p className="text-2xl font-bold text-white">{metrics.qualifiedLeads.toLocaleString()}</p>
                <div className="flex items-center mt-1">
                  <Target className="w-4 h-4 text-blue-400 mr-1" />
                  <span className="text-sm text-blue-400">{metrics.conversionRate}% conversion</span>
                </div>
              </div>
              <Award className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card className="bg-gradient-to-br from-green-900/50 to-green-800/50 border-green-700/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-200">Active Harvesters</p>
                <p className="text-2xl font-bold text-white">{metrics.activeHarvesters}</p>
                <div className="flex items-center mt-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
                  <span className="text-sm text-green-400">Processing</span>
                </div>
              </div>
              <Zap className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card className="bg-gradient-to-br from-orange-900/50 to-orange-800/50 border-orange-700/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-200">Avg. Score</p>
                <p className="text-2xl font-bold text-white">{metrics.scoreAverage}/100</p>
                <div className="flex items-center mt-1">
                  <Clock className="w-4 h-4 text-orange-400 mr-1" />
                  <span className="text-sm text-orange-400">{metrics.processingTime}s avg</span>
                </div>
              </div>
              <Database className="w-8 h-8 text-orange-400" />
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}