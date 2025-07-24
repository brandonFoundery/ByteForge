'use client';

import { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  ConnectionLineType,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Position,
  Handle,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';
import { Search, Database, Shield, Award, Download, Zap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { NppesFilterModal } from './NppesFilterModal';

function HarvesterNode({ data }: { data: any }) {
  const handleClick = () => {
    if (data.isClickable && data.onClick) {
      data.onClick(data.label);
    }
  };

  const isNppes = data.label === 'NPPES';
  const baseClasses = isNppes 
    ? "px-4 py-3 bg-gradient-to-br from-orange-900 to-orange-800 border-2 border-orange-700 rounded-lg shadow-lg"
    : "px-4 py-3 bg-gradient-to-br from-purple-900 to-purple-800 border-2 border-purple-700 rounded-lg shadow-lg";
  
  const clickableClasses = data.isClickable 
    ? "cursor-pointer hover:scale-105 transition-transform duration-200" 
    : "";

  return (
    <motion.div
      className={`${baseClasses} ${clickableClasses}`}
      animate={data.isActive ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 2, repeat: Infinity }}
      onClick={handleClick}
    >
      <Handle
        type="source"
        position={Position.Right}
        id="source"
        style={{
          background: isNppes ? 'rgba(234, 88, 12, 0.8)' : 'rgba(147, 51, 234, 0.8)',
          border: '2px solid rgba(255, 255, 255, 0.2)',
          width: 8,
          height: 8,
        }}
      />
      <div className="flex items-center space-x-2">
        <Search className={`w-5 h-5 ${isNppes ? 'text-orange-300' : 'text-purple-300'}`} />
        <div>
          <div className="font-semibold text-white text-sm">{data.label}</div>
          <div className={`text-xs ${isNppes ? 'text-orange-200' : 'text-purple-200'}`}>
            {data.isActive ? 'Active' : 'Idle'} • {data.leads} leads
            {data.isClickable && <span className="ml-1">📋</span>}
          </div>
        </div>
        {data.isActive && (
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
        )}
      </div>
    </motion.div>
  );
}

function EnrichmentNode({ data }: { data: any }) {
  return (
    <motion.div
      className="px-4 py-3 bg-gradient-to-br from-blue-900 to-blue-800 border-2 border-blue-700 rounded-lg shadow-lg"
      animate={data.processing ? { scale: [1, 1.02, 1] } : {}}
      transition={{ duration: 1.5, repeat: Infinity }}
    >
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
      <div className="flex items-center space-x-2">
        <Database className="w-5 h-5 text-blue-300" />
        <div>
          <div className="font-semibold text-white text-sm">{data.label}</div>
          <div className="text-xs text-blue-200">
            {data.processing ? 'Processing' : 'Ready'} • {data.enriched} enriched
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function VettingNode({ data }: { data: any }) {
  return (
    <motion.div
      className="px-4 py-3 bg-gradient-to-br from-green-900 to-green-800 border-2 border-green-700 rounded-lg shadow-lg"
      animate={data.vetting ? { scale: [1, 1.02, 1] } : {}}
      transition={{ duration: 1.2, repeat: Infinity }}
    >
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
      <div className="flex items-center space-x-2">
        <Shield className="w-5 h-5 text-green-300" />
        <div>
          <div className="font-semibold text-white text-sm">{data.label}</div>
          <div className="text-xs text-green-200">
            {data.vetting ? 'Vetting' : 'Ready'} • {data.approved} approved
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ScoringNode({ data }: { data: any }) {
  return (
    <motion.div
      className="px-4 py-3 bg-gradient-to-br from-orange-900 to-orange-800 border-2 border-orange-700 rounded-lg shadow-lg"
      animate={data.scoring ? { scale: [1, 1.02, 1] } : {}}
      transition={{ duration: 1, repeat: Infinity }}
    >
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
      <div className="flex items-center space-x-2">
        <Award className="w-5 h-5 text-orange-300" />
        <div>
          <div className="font-semibold text-white text-sm">{data.label}</div>
          <div className="text-xs text-orange-200">
            {data.scoring ? 'Scoring' : 'Ready'} • {data.avgScore}/100 avg
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ExportNode({ data }: { data: any }) {
  return (
    <motion.div
      className="px-4 py-3 bg-gradient-to-br from-pink-900 to-pink-800 border-2 border-pink-700 rounded-lg shadow-lg"
      animate={data.exporting ? { scale: [1, 1.02, 1] } : {}}
      transition={{ duration: 0.8, repeat: Infinity }}
    >
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
      <div className="flex items-center space-x-2">
        <Download className="w-5 h-5 text-pink-300" />
        <div>
          <div className="font-semibold text-white text-sm">{data.label}</div>
          <div className="text-xs text-pink-200">
            {data.exporting ? 'Exporting' : 'Ready'} • {data.exported} exported
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Move nodeTypes definition outside component to avoid recreation warnings
const nodeTypes = {
  harvester: HarvesterNode,
  enrichment: EnrichmentNode,
  vetting: VettingNode,
  scoring: ScoringNode,
  export: ExportNode,
};

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'harvester',
    position: { x: 0, y: 100 },
    data: { label: 'Google Jobs', isActive: true, leads: 1247 },
    sourcePosition: Position.Right,
  },
  {
    id: '2',
    type: 'harvester',
    position: { x: 0, y: 200 },
    data: { label: 'Superpages', isActive: false, leads: 894 },
    sourcePosition: Position.Right,
  },
  {
    id: '3',
    type: 'harvester',
    position: { x: 0, y: 300 },
    data: { label: 'LinkedIn', isActive: true, leads: 2156 },
    sourcePosition: Position.Right,
  },
  {
    id: '8',
    type: 'harvester',
    position: { x: 0, y: 400 },
    data: { label: 'NPPES', isActive: false, leads: 0, isClickable: true },
    sourcePosition: Position.Right,
  },
  {
    id: '4',
    type: 'enrichment',
    position: { x: 300, y: 250 },
    data: { label: 'Data Enrichment', processing: true, enriched: 3521 },
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  },
  {
    id: '5',
    type: 'vetting',
    position: { x: 600, y: 250 },
    data: { label: 'Lead Vetting', vetting: true, approved: 2845 },
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  },
  {
    id: '6',
    type: 'scoring',
    position: { x: 900, y: 250 },
    data: { label: 'Lead Scoring', scoring: true, avgScore: 87 },
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  },
  {
    id: '7',
    type: 'export',
    position: { x: 1200, y: 250 },
    data: { label: 'CRM Export', exporting: false, exported: 1956 },
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
    style: { stroke: '#8b5cf6', strokeWidth: 2 },
  },
  {
    id: 'e2-4',
    source: '2',
    sourceHandle: 'source',
    target: '4',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#64748b', strokeWidth: 2 },
  },
  {
    id: 'e3-4',
    source: '3',
    sourceHandle: 'source',
    target: '4',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#8b5cf6', strokeWidth: 2 },
  },
  {
    id: 'e8-4',
    source: '8',
    sourceHandle: 'source',
    target: '4',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#64748b', strokeWidth: 2 },
  },
  {
    id: 'e4-5',
    source: '4',
    sourceHandle: 'source',
    target: '5',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 2 },
  },
  {
    id: 'e5-6',
    source: '5',
    sourceHandle: 'source',
    target: '6',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#10b981', strokeWidth: 2 },
  },
  {
    id: 'e6-7',
    source: '6',
    sourceHandle: 'source',
    target: '7',
    targetHandle: 'target',
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#f59e0b', strokeWidth: 2 },
  },
];

export function PipelineFlow() {
  const [showNppesModal, setShowNppesModal] = useState(false);

  const handleNodeClick = useCallback((nodeLabel: string) => {
    if (nodeLabel === 'NPPES') {
      setShowNppesModal(true);
    }
  }, []);

  const [nodes, setNodes, onNodesChange] = useNodesState(
    initialNodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        onClick: node.data.isClickable ? handleNodeClick : undefined
      }
    }))
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setNodes((nodes) =>
        nodes.map((node) => {
          if (node.type === 'harvester') {
            return {
              ...node,
              data: {
                ...node.data,
                isActive: Math.random() > 0.3,
                leads: node.data.leads + Math.floor(Math.random() * 10),
              },
            };
          }
          return node;
        })
      );
    }, 3000);

    return () => clearInterval(interval);
  }, [setNodes]);

  return (
    <div className="w-full h-full bg-slate-950 rounded-lg hidden md:block">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
        attributionPosition="bottom-left"
        className="bg-slate-950"
        zoomOnScroll={false}
        zoomOnPinch={false}
        zoomOnDoubleClick={false}
        panOnDrag={false}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
      >
        <Background color="#334155" gap={16} />
      </ReactFlow>
      
      <NppesFilterModal 
        open={showNppesModal} 
        onOpenChange={setShowNppesModal}
        onSave={(config) => {
          console.log('NPPES configuration saved:', config);
          // TODO: Refresh pipeline data or show success message
        }}
      />
    </div>
  );
}
