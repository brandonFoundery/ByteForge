import type { StatusUpdate } from '../types';

type MessageHandler = (data: StatusUpdate) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectTimer: number | null = null;
  private messageHandlers: MessageHandler[] = [];
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000; // 3 seconds
  private url: string;

  constructor(url: string = 'ws://localhost:8000/ws/status') {
    this.url = url;
  }

  connect(): void {
    if (this.socket) {
      return;
    }

    try {
      console.log(`Connecting to WebSocket at ${this.url}...`);
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        console.log('WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // Send initial ping to verify connection
        this.sendMessage('ping');
        
        // Send ping every 15 seconds to keep connection alive
        setInterval(() => {
          if (this.isConnected && this.socket?.readyState === WebSocket.OPEN) {
            console.log('Sending ping to keep connection alive');
            this.sendMessage('ping');
          }
        }, 15000);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as StatusUpdate;
          this.notifyHandlers(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.socket = null;
        
        // Try to reconnect
        this.scheduleReconnect();
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.socket?.close();
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * this.reconnectAttempts;
      
      console.log(`Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      this.reconnectTimer = window.setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    } else {
      console.error('Max reconnect attempts reached. Please refresh the page.');
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    this.isConnected = false;
  }

  sendMessage(message: string): void {
    if (this.socket && this.isConnected) {
      this.socket.send(message);
    }
  }

  addMessageHandler(handler: MessageHandler): void {
    this.messageHandlers.push(handler);
  }

  removeMessageHandler(handler: MessageHandler): void {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }

  private notifyHandlers(data: StatusUpdate): void {
    this.messageHandlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error('Error in message handler:', error);
      }
    });
  }

  isSocketConnected(): boolean {
    return this.isConnected;
  }
}

// Create a singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;