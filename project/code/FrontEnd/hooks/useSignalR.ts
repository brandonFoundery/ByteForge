import { useEffect, useState, useCallback, useMemo } from 'react';
import { createSignalRService, LeadUpdateMessage, MetricsUpdateMessage } from '@/services/signalRService';
import { apiClient } from '@/lib/api';
import * as signalR from '@microsoft/signalr';

export interface UseSignalRReturn {
  connection: signalR.HubConnection | null;
  isConnected: boolean;
  connectionState: string;
  lastLeadUpdate: LeadUpdateMessage | null;
  lastMetricsUpdate: MetricsUpdateMessage | null;
  error: Error | null;
  joinLeadGroup: (leadId: string) => Promise<void>;
  leaveLeadGroup: (leadId: string) => Promise<void>;
  reconnect: () => Promise<void>;
}

export function useSignalR(): UseSignalRReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('Disconnected');
  const [lastLeadUpdate, setLastLeadUpdate] = useState<LeadUpdateMessage | null>(null);
  const [lastMetricsUpdate, setLastMetricsUpdate] = useState<MetricsUpdateMessage | null>(null);
  const [error, setError] = useState<Error | null>(null);

  // Create SignalR service with authentication
  const signalRService = useMemo(() => {
    return createSignalRService(() => {
      const token = apiClient.getToken();
      return token || '';
    });
  }, []);

  useEffect(() => {
    // Start SignalR connection
    signalRService.start().catch(console.error);

    // Subscribe to connection state changes
    const unsubscribeConnectionState = signalRService.onConnectionStateChange((connected) => {
      setIsConnected(connected);
      setConnectionState(connected ? 'Connected' : 'Disconnected');
    });

    // Subscribe to lead updates
    const unsubscribeLeadUpdates = signalRService.onLeadUpdate((message) => {
      setLastLeadUpdate(message);
    });

    // Subscribe to metrics updates
    const unsubscribeMetricsUpdates = signalRService.onMetricsUpdate((message) => {
      setLastMetricsUpdate(message);
    });

    // Subscribe to errors
    const unsubscribeErrors = signalRService.onError((error) => {
      setError(error);
    });

    // Cleanup on unmount
    return () => {
      unsubscribeConnectionState();
      unsubscribeLeadUpdates();
      unsubscribeMetricsUpdates();
      unsubscribeErrors();
    };
  }, [signalRService]);

  const joinLeadGroup = useCallback(async (leadId: string) => {
    try {
      await signalRService.joinLeadGroup(leadId);
    } catch (error) {
      console.error('Failed to join lead group:', error);
      setError(error instanceof Error ? error : new Error('Failed to join lead group'));
    }
  }, [signalRService]);

  const leaveLeadGroup = useCallback(async (leadId: string) => {
    try {
      await signalRService.leaveLeadGroup(leadId);
    } catch (error) {
      console.error('Failed to leave lead group:', error);
      setError(error instanceof Error ? error : new Error('Failed to leave lead group'));
    }
  }, [signalRService]);

  const reconnect = useCallback(async () => {
    try {
      await signalRService.reconnectWithAuth();
      setError(null);
    } catch (error) {
      console.error('Failed to reconnect:', error);
      setError(error instanceof Error ? error : new Error('Failed to reconnect'));
    }
  }, [signalRService]);

  return {
    connection: signalRService.getConnection(),
    isConnected,
    connectionState,
    lastLeadUpdate,
    lastMetricsUpdate,
    error,
    joinLeadGroup,
    leaveLeadGroup,
    reconnect,
  };
}