// Document Generation Types
export interface DocumentGenerationStatus {
  projectId: string;
  documents: Record<string, DocumentProgress>;
  overallProgress: number;
  startedAt: Date;
  completedAt?: Date;
  isComplete: boolean;
  hasErrors: boolean;
}

export interface DocumentProgress {
  documentType: string;
  progress: number;
  status: string;
  startedAt: Date;
  completedAt?: Date;
  error?: string;
  milestones: string[];
}

export interface DocumentGenerationProgress {
  projectId: string;
  documentType: string;
  progress: number;
  status: string;
  timestamp: Date;
}

// AI Agent Types
export interface AgentStatus {
  agentId: string;
  agentType: string;
  projectId: string;
  state: AgentState;
  currentTask?: string;
  startedAt: Date;
  lastHeartbeat: Date;
  tasksCompleted: number;
  tasksFailed: number;
}

export enum AgentState {
  Idle = 'Idle',
  Starting = 'Starting',
  Running = 'Running',
  Paused = 'Paused',
  Stopping = 'Stopping',
  Stopped = 'Stopped',
  Failed = 'Failed',
  Completed = 'Completed'
}

export interface AgentHealthReport {
  agentId: string;
  agentType: string;
  isHealthy: boolean;
  cpuUsage: number;
  memoryUsage: number;
  requestsPerMinute: number;
  averageResponseTime: number;
  errorCount: number;
  lastError: Date;
  lastErrorMessage?: string;
  customMetrics: Record<string, any>;
}

export interface AgentMetrics {
  cpuUsage: number;
  memoryUsage: number;
  requestCount: number;
  responseTime: number;
  customMetrics: Record<string, any>;
  timestamp: Date;
}

// Project Types
export interface ProjectOverview {
  projectId: string;
  projectName: string;
  projectType: string;
  overallProgress: number;
  currentPhase: ProjectPhase;
  createdAt: Date;
  estimatedCompletion?: Date;
  phases: PhaseProgress[];
  documentProgress: Record<string, number>;
  activeAgents: string[];
  hasErrors: boolean;
}

export enum ProjectPhase {
  Initialization = 'Initialization',
  RequirementsGathering = 'RequirementsGathering',
  DocumentGeneration = 'DocumentGeneration',
  CodeGeneration = 'CodeGeneration',
  Testing = 'Testing',
  Deployment = 'Deployment',
  Completed = 'Completed'
}

export interface PhaseProgress {
  phase: ProjectPhase;
  progress: number;
  status: string;
  startedAt?: Date;
  completedAt?: Date;
}

export interface ProjectStatus {
  projectId: string;
  projectName: string;
  status: string;
  progress: number;
  lastUpdated: Date;
}

export interface ProjectUpdate {
  projectId: string;
  updateType: string;
  component: string;
  message: string;
  progress?: number;
  data: Record<string, any>;
  timestamp: Date;
}

// System Types
export interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskSpaceUsed: number;
  diskSpaceAvailable: number;
  activeProjects: number;
  activeAgents: number;
  queuedTasks: number;
  systemLoad: number;
  serviceHealth: Record<string, ServiceHealth>;
  timestamp: Date;
}

export interface ServiceHealth {
  serviceName: string;
  isHealthy: boolean;
  lastCheck: Date;
  errorMessage?: string;
}

export interface ResourceUsage {
  cpuHistory: ResourceSnapshot[];
  memoryHistory: ResourceSnapshot[];
  diskHistory: ResourceSnapshot[];
  networkHistory: ResourceSnapshot[];
}

export interface ResourceSnapshot {
  value: number;
  timestamp: Date;
}

export interface SystemEvent {
  eventType: string;
  source: string;
  message: string;
  severity: EventSeverity;
  data: Record<string, any>;
  timestamp: Date;
}

export enum EventSeverity {
  Debug = 'Debug',
  Info = 'Info',
  Warning = 'Warning',
  Error = 'Error',
  Critical = 'Critical'
}

// Analytics Types
export interface DocumentGenerationAnalytics {
  totalDocumentsGenerated: number;
  successfulGenerations: number;
  failedGenerations: number;
  successRate: number;
  averageGenerationTime: number;
  documentTypeCounts: Record<string, number>;
  documentTypeAverageTimes: Record<string, number>;
  dailyTrends: GenerationTrend[];
}

export interface GenerationTrend {
  date: Date;
  count: number;
  averageTime: number;
  successRate: number;
}

export interface AgentPerformanceAnalytics {
  agentPerformance: Record<string, AgentPerformance>;
  overallSuccessRate: number;
  averageTaskDuration: number;
  totalTasksCompleted: number;
  totalTasksFailed: number;
  efficiencyTrends: AgentEfficiencyTrend[];
}

export interface AgentPerformance {
  agentType: string;
  tasksCompleted: number;
  tasksFailed: number;
  successRate: number;
  averageTaskDuration: number;
  averageCpuUsage: number;
  averageMemoryUsage: number;
}

export interface AgentEfficiencyTrend {
  date: Date;
  agentEfficiency: Record<string, number>;
}

export interface SystemHealthReport {
  generatedAt: Date;
  overallHealth: string;
  currentMetrics: SystemMetrics;
  issues: SystemIssue[];
  recommendations: SystemRecommendation[];
  serviceHealthHistory: Record<string, ServiceHealthHistory>;
}

export interface SystemIssue {
  issueType: string;
  description: string;
  severity: EventSeverity;
  detectedAt: Date;
  isResolved: boolean;
}

export interface SystemRecommendation {
  category: string;
  recommendation: string;
  impact: string;
  priority: number;
}

export interface ServiceHealthHistory {
  serviceName: string;
  uptime: number;
  errorCount: number;
  incidents: ServiceIncident[];
}

export interface ServiceIncident {
  startTime: Date;
  endTime?: Date;
  description: string;
  resolution: string;
}

// File System Types
export interface FileSystemChangeEventArgs {
  path: string;
  changeType: FileSystemChangeType;
  oldPath?: string;
  timestamp: Date;
}

export enum FileSystemChangeType {
  Created = 'Created',
  Modified = 'Modified',
  Deleted = 'Deleted',
  Renamed = 'Renamed'
}

// Export Types
export enum AnalyticsExportFormat {
  CSV = 'CSV',
  JSON = 'JSON',
  PDF = 'PDF',
  Excel = 'Excel'
}