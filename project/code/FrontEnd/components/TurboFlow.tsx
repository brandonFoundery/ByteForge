'use client';

import React, { useCallback, useEffect, useState } from 'react';
import {
  ReactFlow,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  type Node,
  type Edge,
  type OnConnect,
  Position,
  Background,
  MiniMap,
  Handle,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { 
  Search, 
  Database, 
  Shield, 
  Award, 
  Download, 
  Zap, 
  TrendingUp,
  Users,
  FileText,
  Activity,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';

// Custom Node Types
const TurboNode = ({ data }: { data: any }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'active';
      case 'processing': return 'processing';
      case 'error': return 'error';
      default: return 'inactive';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />;
      case 'processing': return <Clock className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="turbo-node">
      {data.hasSource && (
        <Handle
          type="source"
          position={Position.Right}
          id="source"
          style={{
            background: 'rgba(147, 51, 234, 0.8)',
            border: '2px solid rgba(255, 255, 255, 0.2)',
            width: 8,
            height: 8,
          }}
        />
      )}
      {data.hasTarget && (
        <Handle
          type="target"
          position={Position.Left}
          id="target"
          style={{
            background: 'rgba(147, 51, 234, 0.8)',
            border: '2px solid rgba(255, 255, 255, 0.2)',
            width: 8,
            height: 8,
          }}
        />
      )}
      <div className="turbo-node-content">
        <div className="turbo-node-icon">
          {data.icon}
        </div>
        <div className="turbo-node-text">
          <div className="turbo-node-title">{data.title}</div>
          <div className="turbo-node-subtitle">{data.subtitle}</div>
          {data.metrics && (
            <div className="turbo-node-metrics">
              <span>📊 {data.metrics.count}</span>
              <span>⚡ {data.metrics.rate}/min</span>
              <span>✅ {data.metrics.success}%</span>
            </div>
          )}
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className={`turbo-node-status ${getStatusColor(data.status)}`} />
          <div className="text-xs text-gray-400">
            {getStatusIcon(data.status)}
          </div>
        </div>
      </div>
    </div>
  );
};

// Move nodeTypes and edgeTypes outside component to avoid recreation warnings
const nodeTypes = {
  turbo: TurboNode,
};

// Initial nodes with real metrics and status
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'turbo',
    position: { x: 0, y: 100 },
    data: { 
      icon: <Search className="w-6 h-6" />, 
      title: 'Google Lead Scraper', 
      subtitle: 'google-jobs.com',
      status: 'active',
      hasSource: true,
      hasTarget: false,
      metrics: {
        count: '1,247',
        rate: '45',
        success: '98.5'
      }
    },
    draggable: false,
    connectable: false,
    sourcePosition: Position.Right,
  },
  {
    id: '2',
    type: 'turbo',
    position: { x: 0, y: 200 },
    data: { 
      icon: <Search className="w-6 h-6" />, 
      title: 'LinkedIn Scraper', 
      subtitle: 'linkedin.com',
      status: 'active',
      hasSource: true,
      hasTarget: false,
      metrics: {
        count: '2,156',
        rate: '32',
        success: '94.2'
      }
    },
    draggable: false,
    connectable: false,
    sourcePosition: Position.Right,
  },
  {
    id: '3',
    type: 'turbo',
    position: { x: 0, y: 300 },
    data: { 
      icon: <Search className="w-6 h-6" />, 
      title: 'Yellow Pages Scraper', 
      subtitle: 'yellowpages.com',
      status: 'processing',
      hasSource: true,
      hasTarget: false,
      metrics: {
        count: '894',
        rate: '28',
        success: '91.8'
      }
    },
    draggable: false,
    connectable: false,
    sourcePosition: Position.Right,
  },
  {
    id: '4',
    type: 'turbo',
    position: { x: 350, y: 150 },
    data: { 
      icon: <Database className="w-6 h-6" />, 
      title: 'Data Enrichment', 
      subtitle: 'Contact & Company Info',
      status: 'active',
      hasSource: true,
      hasTarget: true,
      metrics: {
        count: '3,521',
        rate: '89',
        success: '96.1'
      }
    },
    draggable: false,
    connectable: false,
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  },
  {
    id: '5',
    type: 'turbo',
    position: { x: 350, y: 250 },
    data: { 
      icon: <TrendingUp className="w-6 h-6" />, 
      title: 'Lead Scoring', 
      subtitle: 'AI-Powered Analysis',
      status: 'active',
      hasSource: true,
      hasTarget: true,
      metrics: {
        count: '3,297',
        rate: '78',
        success: '99.2'
      }
    },
    draggable: false,
    connectable: false,
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  },
  {
    id: '6',
    type: 'turbo',
    position: { x: 700, y: 150 },
    data: { 
      icon: <Shield className="w-6 h-6" />, 
      title: 'Lead Vetting', 
      subtitle: 'Quality Assurance',
      status: 'active',
      hasSource: true,
      hasTarget: true,
      metrics: {
        count: '2,845',
        rate: '65',
        success: '97.8'
      }
    },
    draggable: false,
    connectable: false,
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  },
  {
    id: '7',
    type: 'turbo',
    position: { x: 700, y: 250 },
    data: { 
      icon: <Award className="w-6 h-6" />, 
      title: 'Final Scoring', 
      subtitle: 'Priority Ranking',
      status: 'active',
      hasSource: true,
      hasTarget: true,
      metrics: {
        count: '2,634',
        rate: '58',
        success: '99.8'
      }
    },
    draggable: false,
    connectable: false,
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  },
  {
    id: '8',
    type: 'turbo',
    position: { x: 1050, y: 200 },
    data: { 
      icon: <Download className="w-6 h-6" />, 
      title: 'CRM Export', 
      subtitle: 'Zoho Integration',
      status: 'processing',
      hasSource: false,
      hasTarget: true,
      metrics: {
        count: '1,956',
        rate: '42',
        success: '99.9'
      }
    },
    draggable: false,
    connectable: false,
    targetPosition: Position.Left,
  },
];

const initialEdges: Edge[] = [
  {
    id: 'e1-4',
    source: '1',
    sourceHandle: 'source',
    target: '4',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
  {
    id: 'e2-4',
    source: '2',
    sourceHandle: 'source',
    target: '4',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
  {
    id: 'e3-4',
    source: '3',
    sourceHandle: 'source',
    target: '4',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
  {
    id: 'e4-5',
    source: '4',
    sourceHandle: 'source',
    target: '5',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
  {
    id: 'e4-6',
    source: '4',
    sourceHandle: 'source',
    target: '6',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
  {
    id: 'e5-7',
    source: '5',
    sourceHandle: 'source',
    target: '7',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
  {
    id: 'e6-7',
    source: '6',
    sourceHandle: 'source',
    target: '7',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
  {
    id: 'e7-8',
    source: '7',
    sourceHandle: 'source',
    target: '8',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
  },
];

export function TurboFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect: OnConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setNodes((nodes) =>
        nodes.map((node) => {
          const newMetrics = {
            ...node.data.metrics,
            count: (parseInt(node.data.metrics.count.replace(',', '')) + Math.floor(Math.random() * 10)).toLocaleString(),
          };
          
          return {
            ...node,
            data: {
              ...node.data,
              metrics: newMetrics,
            },
          };
        })
      );
    }, 5000);

    return () => clearInterval(interval);
  }, [setNodes]);

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={true}
        zoomOnScroll={true}
        zoomOnPinch={true}
        zoomOnDoubleClick={false}
        className="union-gradient"
      >
        <Background 
          color="rgba(147, 51, 234, 0.1)" 
          gap={20}
          size={1}
        />
        <Controls 
          showInteractive={false}
          className="union-controls"
        />
        <MiniMap 
          className="union-minimap"
          nodeColor={(node) => {
            switch (node.data.status) {
              case 'active': return '#10b981';
              case 'processing': return '#f59e0b';
              case 'error': return '#ef4444';
              default: return '#6b7280';
            }
          }}
        />
        <svg>
          <defs>
            <linearGradient id="edge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#9333ea" />
              <stop offset="100%" stopColor="#ec4899" />
            </linearGradient>
          </defs>
        </svg>
      </ReactFlow>
    </div>
  );
}
