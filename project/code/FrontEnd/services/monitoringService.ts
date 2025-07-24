import axios from 'axios';
import { 
  DocumentGenerationStatus,
  DocumentGenerationProgress,
  AgentStatus,
  AgentHealthReport,
  ProjectOverview,
  ProjectStatus,
  SystemMetrics,
  ResourceUsage,
  SystemEvent,
  DocumentGenerationAnalytics,
  AgentPerformanceAnalytics,
  SystemHealthReport,
  AgentState,
  AnalyticsExportFormat,
  EventSeverity,
  AgentMetrics
} from '../types/monitoring';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5005/api';

class MonitoringService {
  private apiClient = axios.create({
    baseURL: `${API_BASE_URL}/monitoring`,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    // Add auth token to requests
    this.apiClient.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Document Generation Monitoring
  async getDocumentGenerationStatus(projectId: string): Promise<DocumentGenerationStatus> {
    const response = await this.apiClient.get(`/documents/${projectId}/status`);
    return response.data;
  }

  async getDocumentProgress(projectId: string): Promise<DocumentGenerationProgress[]> {
    const response = await this.apiClient.get(`/documents/${projectId}/progress`);
    return response.data;
  }

  async startDocumentGeneration(projectId: string, documentType: string): Promise<void> {
    await this.apiClient.post(`/documents/${projectId}/start`, { documentType });
  }

  async updateDocumentProgress(
    projectId: string,
    documentType: string,
    progress: number,
    status: string
  ): Promise<void> {
    await this.apiClient.put(`/documents/${projectId}/progress`, {
      documentType,
      progress,
      status,
    });
  }

  async completeDocumentGeneration(
    projectId: string,
    documentType: string,
    success: boolean,
    error?: string
  ): Promise<void> {
    await this.apiClient.post(`/documents/${projectId}/complete`, {
      documentType,
      success,
      error,
    });
  }

  // AI Agent Monitoring
  async getActiveAgents(): Promise<AgentStatus[]> {
    const response = await this.apiClient.get('/agents/active');
    return response.data;
  }

  async getAgentHealth(agentId: string): Promise<AgentHealthReport> {
    const response = await this.apiClient.get(`/agents/${agentId}/health`);
    return response.data;
  }

  async startAgentMonitoring(agentId: string, agentType: string, projectId: string): Promise<void> {
    await this.apiClient.post(`/agents/${agentId}/start`, {
      agentType,
      projectId,
    });
  }

  async updateAgentStatus(agentId: string, state: AgentState, message?: string): Promise<void> {
    await this.apiClient.put(`/agents/${agentId}/status`, {
      state,
      message,
    });
  }

  async recordAgentMetrics(agentId: string, metrics: AgentMetrics): Promise<void> {
    await this.apiClient.post(`/agents/${agentId}/metrics`, metrics);
  }

  // Project Monitoring
  async getProjectOverview(projectId: string): Promise<ProjectOverview> {
    const response = await this.apiClient.get(`/projects/${projectId}/overview`);
    return response.data;
  }

  async getAllProjectsStatus(): Promise<ProjectStatus[]> {
    const response = await this.apiClient.get('/projects/status');
    return response.data;
  }

  async updateProjectProgress(projectId: string, progress: number): Promise<void> {
    await this.apiClient.put(`/projects/${projectId}/progress`, { progress });
  }

  // System Metrics
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await this.apiClient.get('/system/metrics');
    return response.data;
  }

  async getResourceUsage(): Promise<ResourceUsage> {
    const response = await this.apiClient.get('/system/resources');
    return response.data;
  }

  async recordSystemEvent(event: SystemEvent): Promise<void> {
    await this.apiClient.post('/system/events', event);
  }

  // Analytics and Reporting
  async getDocumentGenerationAnalytics(
    from?: Date,
    to?: Date
  ): Promise<DocumentGenerationAnalytics> {
    const params = new URLSearchParams();
    if (from) params.append('from', from.toISOString());
    if (to) params.append('to', to.toISOString());
    
    const response = await this.apiClient.get(`/analytics/documents?${params.toString()}`);
    return response.data;
  }

  async getAgentPerformanceAnalytics(
    from?: Date,
    to?: Date
  ): Promise<AgentPerformanceAnalytics> {
    const params = new URLSearchParams();
    if (from) params.append('from', from.toISOString());
    if (to) params.append('to', to.toISOString());
    
    const response = await this.apiClient.get(`/analytics/agents?${params.toString()}`);
    return response.data;
  }

  async generateSystemHealthReport(): Promise<SystemHealthReport> {
    const response = await this.apiClient.get('/analytics/health-report');
    return response.data;
  }

  async exportAnalytics(
    format: AnalyticsExportFormat,
    from?: Date,
    to?: Date
  ): Promise<Blob> {
    const params = new URLSearchParams();
    params.append('format', format);
    if (from) params.append('from', from.toISOString());
    if (to) params.append('to', to.toISOString());
    
    const response = await this.apiClient.get(`/analytics/export?${params.toString()}`, {
      responseType: 'blob',
    });
    
    return response.data;
  }

  // File System Monitoring
  async startFileSystemMonitoring(path: string): Promise<void> {
    await this.apiClient.post('/filesystem/start', { path });
  }

  async stopFileSystemMonitoring(path: string): Promise<void> {
    await this.apiClient.post('/filesystem/stop', { path });
  }

  // Utility method to download exported files
  downloadFile(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

export const monitoringService = new MonitoringService();