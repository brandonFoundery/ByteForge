import * as signalR from '@microsoft/signalr';

export enum NotificationSeverity {
  Info = 'Info',
  Success = 'Success',
  Warning = 'Warning',
  Error = 'Error',
  Critical = 'Critical'
}

export interface NotificationMessage {
  type: string;
  entityType: string;
  entityId: string;
  title?: string;
  message?: string;
  severity: NotificationSeverity;
  data: Record<string, any>;
  timestamp: string;
  userId?: string;
  groupId?: string;
}

export interface MetricsUpdateMessage {
  type: string;
  metricCategory: string;
  metrics: {
    counters: Record<string, number>;
    rates: Record<string, number>;
    timings: Record<string, number>;
    statusCounts: Record<string, Record<string, number>>;
    // ByteForge specific
    activeProjects: number;
    completedDocuments: number;
    activeAgents: number;
    pendingRequests: number;
    averageGenerationTime: number;
    successRate: number;
    documentsByType: Record<string, number>;
    requestsByProvider: Record<string, number>;
  };
  timestamp: string;
}

export interface SignalRConnectionOptions {
  hubUrl?: string;
  accessTokenFactory?: () => string | Promise<string>;
  maxReconnectAttempts?: number;
  reconnectDelay?: number;
}

export class NotificationService {
  private connection: signalR.HubConnection | null = null;
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private accessTokenFactory?: () => string | Promise<string>;

  // Event handlers
  private onNotificationHandlers: ((message: NotificationMessage) => void)[] = [];
  private onMetricsUpdateHandlers: ((message: MetricsUpdateMessage) => void)[] = [];
  private onConnectionStateHandlers: ((connected: boolean) => void)[] = [];
  private onErrorHandlers: ((error: Error) => void)[] = [];

  constructor(options: SignalRConnectionOptions = {}) {
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectDelay = options.reconnectDelay || 1000;
    this.accessTokenFactory = options.accessTokenFactory;
  }

  async start(hubUrl: string = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/notificationHub` : 'http://localhost:5000/notificationHub'): Promise<void> {
    if (this.connection && this.isConnected) {
      return;
    }

    try {
      const connectionBuilder = new signalR.HubConnectionBuilder()
        .withUrl(hubUrl, {
          accessTokenFactory: this.accessTokenFactory
        })
        .withAutomaticReconnect({
          nextRetryDelayInMilliseconds: (retryContext) => {
            const delay = Math.min(1000 * Math.pow(2, retryContext.previousRetryCount), 16000);
            console.log(`SignalR reconnecting in ${delay}ms (attempt ${retryContext.previousRetryCount + 1})`);
            return delay;
          }
        })
        .configureLogging(signalR.LogLevel.Information);

      this.connection = connectionBuilder.build();

      // Set up generic notification handlers
      this.connection.on('Notification', (notification: NotificationMessage) => {
        console.log('Received notification:', notification);
        this.onNotificationHandlers.forEach(handler => handler(notification));
      });

      this.connection.on('MetricsUpdate', (metrics: MetricsUpdateMessage) => {
        console.log('Received metrics update:', metrics);
        this.onMetricsUpdateHandlers.forEach(handler => handler(metrics));
      });

      // Connection state handlers
      this.connection.onclose((error) => {
        console.log('SignalR connection closed:', error);
        this.isConnected = false;
        this.notifyConnectionState(false);
        if (error) {
          this.notifyError(new Error(`Connection closed: ${error.message || error}`));
        }
      });

      this.connection.onreconnecting((error) => {
        console.log('SignalR reconnecting:', error);
        this.isConnected = false;
        this.notifyConnectionState(false);
        if (error) {
          this.notifyError(new Error(`Reconnecting: ${error.message || error}`));
        }
      });

      this.connection.onreconnected((connectionId) => {
        console.log('SignalR reconnected:', connectionId);
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyConnectionState(true);
      });

      await this.connection.start();
      this.isConnected = true;
      this.reconnectAttempts = 0;
      console.log('SignalR connected successfully');
      this.notifyConnectionState(true);

      // Automatically join dashboard group
      try {
        await this.joinDashboard();
      } catch (error) {
        console.warn('Failed to join dashboard group, but connection is still active:', error);
      }

    } catch (error) {
      console.error('Failed to start SignalR connection:', error);
      this.isConnected = false;
      this.notifyConnectionState(false);
      this.notifyError(error instanceof Error ? error : new Error('Failed to start SignalR connection'));
      
      // Retry connection
      this.scheduleReconnect();
    }
  }

  async stop(): Promise<void> {
    if (this.connection) {
      await this.connection.stop();
      this.isConnected = false;
      this.notifyConnectionState(false);
      console.log('SignalR connection stopped');
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;

    setTimeout(() => {
      console.log(`Attempting to reconnect (attempt ${this.reconnectAttempts})`);
      this.start();
    }, delay);
  }

  private notifyConnectionState(connected: boolean): void {
    this.onConnectionStateHandlers.forEach(handler => handler(connected));
  }

  private notifyError(error: Error): void {
    this.onErrorHandlers.forEach(handler => handler(error));
  }

  // Event subscription methods
  onNotification(handler: (message: NotificationMessage) => void): () => void {
    this.onNotificationHandlers.push(handler);
    return () => {
      const index = this.onNotificationHandlers.indexOf(handler);
      if (index > -1) {
        this.onNotificationHandlers.splice(index, 1);
      }
    };
  }

  onMetricsUpdate(handler: (message: MetricsUpdateMessage) => void): () => void {
    this.onMetricsUpdateHandlers.push(handler);
    return () => {
      const index = this.onMetricsUpdateHandlers.indexOf(handler);
      if (index > -1) {
        this.onMetricsUpdateHandlers.splice(index, 1);
      }
    };
  }

  onConnectionStateChange(handler: (connected: boolean) => void): () => void {
    this.onConnectionStateHandlers.push(handler);
    return () => {
      const index = this.onConnectionStateHandlers.indexOf(handler);
      if (index > -1) {
        this.onConnectionStateHandlers.splice(index, 1);
      }
    };
  }

  onError(handler: (error: Error) => void): () => void {
    this.onErrorHandlers.push(handler);
    return () => {
      const index = this.onErrorHandlers.indexOf(handler);
      if (index > -1) {
        this.onErrorHandlers.splice(index, 1);
      }
    };
  }

  // Utility methods
  getConnection(): signalR.HubConnection | null {
    return this.connection;
  }

  getConnectionState(): signalR.HubConnectionState | null {
    return this.connection?.state || null;
  }

  isConnectionActive(): boolean {
    return this.isConnected && this.connection?.state === signalR.HubConnectionState.Connected;
  }

  // Group management
  async joinGroup(groupName: string): Promise<void> {
    if (this.isConnectionActive()) {
      try {
        await this.connection!.invoke('JoinGroup', groupName);
        console.log(`Joined group: ${groupName}`);
      } catch (error) {
        console.error(`Failed to join group ${groupName}:`, error);
        this.notifyError(error instanceof Error ? error : new Error(`Failed to join group ${groupName}`));
        throw error;
      }
    } else {
      throw new Error('SignalR connection is not active');
    }
  }

  async leaveGroup(groupName: string): Promise<void> {
    if (this.isConnectionActive()) {
      try {
        await this.connection!.invoke('LeaveGroup', groupName);
        console.log(`Left group: ${groupName}`);
      } catch (error) {
        console.error(`Failed to leave group ${groupName}:`, error);
        this.notifyError(error instanceof Error ? error : new Error(`Failed to leave group ${groupName}`));
        throw error;
      }
    } else {
      throw new Error('SignalR connection is not active');
    }
  }

  async joinDashboard(): Promise<void> {
    return this.joinGroup('dashboard');
  }

  async joinProject(projectId: string): Promise<void> {
    return this.joinGroup(`project-${projectId}`);
  }

  async leaveProject(projectId: string): Promise<void> {
    return this.leaveGroup(`project-${projectId}`);
  }

  // Update authentication token
  updateAccessToken(accessTokenFactory: () => string | Promise<string>): void {
    this.accessTokenFactory = accessTokenFactory;
  }

  // Reconnect with new token
  async reconnectWithAuth(): Promise<void> {
    if (this.connection) {
      await this.stop();
    }
    await this.start();
  }
}

// Factory function to create notification service with authentication
export function createNotificationService(accessTokenFactory?: () => string | Promise<string>): NotificationService {
  return new NotificationService({
    accessTokenFactory
  });
}

// Default singleton instance
export const notificationService = new NotificationService();