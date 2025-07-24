# SignalR Real-Time Lead Processing Implementation

## Overview

This document describes the implementation of real-time updates for the Lead Processing Dashboard using SignalR. The system provides live updates when leads are added, processed, or updated through various workflow stages.

## Architecture

### Backend Components

#### 1. SignalR Hub (`Hubs/LeadUpdatesHub.cs`)
- **Purpose**: Central communication hub for real-time updates
- **Authentication**: Requires user authentication
- **Groups**: 
  - `LeadUpdates`: General updates for all connected clients
  - `Lead_{id}`: Specific updates for individual leads

#### 2. Message Models
- **LeadUpdateMessage**: Contains lead-specific updates (new leads, status changes, scores)
- **MetricsUpdateMessage**: Contains dashboard metrics updates

#### 3. Notification Service (`Services/LeadNotificationService.cs`)
- **Interface**: `ILeadNotificationService`
- **Methods**:
  - `NotifyNewLeadAsync()`: New lead added
  - `NotifyLeadStatusUpdateAsync()`: Status changed
  - `NotifyLeadScoreUpdateAsync()`: Score updated
  - `NotifyLeadEnrichmentAsync()`: Enrichment completed
  - `NotifyWorkflowStartedAsync()`: Workflow initiated
  - `NotifyWorkflowCompletedAsync()`: Workflow finished
  - `NotifyWorkflowFailedAsync()`: Workflow error
  - `NotifyMetricsUpdateAsync()`: Dashboard metrics updated

#### 4. Database Change Interceptor (`Data/LeadChangeInterceptor.cs`)
- **Purpose**: Automatically detect database changes
- **Triggers**: Entity Framework save operations
- **Captures**: Lead additions, modifications, deletions

### Frontend Components

#### 1. SignalR Service (`services/signalRService.ts`)
- **Connection Management**: Automatic reconnection with exponential backoff
- **Event Handling**: Lead updates, metrics updates, connection state
- **Groups**: Join/leave specific lead groups

#### 2. React Hook (`hooks/useSignalR.ts`)
- **State Management**: Connection status, last updates
- **Event Subscriptions**: Automatic cleanup on unmount
- **Group Management**: Join/leave lead-specific groups

#### 3. Lead Context (`contexts/LeadContext.tsx`)
- **Integration**: SignalR updates with React state
- **Fallback**: Mock data when disconnected
- **Status Mapping**: Backend to frontend status conversion

## Message Types

### Lead Update Messages

```typescript
interface LeadUpdateMessage {
  type: 'NEW_LEAD' | 'STATUS_UPDATE' | 'SCORE_UPDATE' | 'ENRICHMENT_UPDATE' | 
        'WORKFLOW_STARTED' | 'WORKFLOW_COMPLETED' | 'WORKFLOW_FAILED';
  leadId?: number;
  lead?: Lead;
  source?: string;
  previousStatus?: string;
  newStatus?: string;
  timestamp: string;
  message?: string;
}
```

### Metrics Update Messages

```typescript
interface MetricsUpdateMessage {
  type: 'METRICS_UPDATE';
  metrics: {
    totalLeads: number;
    qualifiedLeads: number;
    conversionRate: number;
    activeHarvesters: number;
    processingTime: number;
    scoreAverage: number;
    dailyGrowth: number;
    weeklyGrowth: number;
    newLeadsToday: number;
    processedToday: number;
    leadsBySource: Record<string, number>;
    leadsByStatus: Record<string, number>;
  };
  timestamp: string;
}
```

## Integration Points

### 1. Lead Scrapers
- **GoogleLeadJob**: Notifies when new leads are scraped and workflows started
- **Other Scrapers**: Similar integration pattern for LinkedIn, Facebook, Yellow Pages

### 2. Workflow Activities
- **EnrichLeadActivity**: Notifies enrichment completion and status changes
- **ScoreLeadActivity**: Notifies score updates and status changes
- **VetLeadActivity**: Notifies vetting completion
- **ZohoUpsertActivity**: Notifies CRM integration completion

### 3. API Controllers
- **LeadController**: Manual lead operations trigger notifications

## Connection Management

### Backend Configuration
```csharp
// Program.cs
builder.Services.AddSignalR();
builder.Services.AddScoped<ILeadNotificationService, LeadNotificationService>();

// Hub mapping
app.MapHub<LeadUpdatesHub>("/leadupdates");
```

### Frontend Connection
```typescript
// Automatic connection with retry logic
const signalRService = new SignalRService('/leadupdates');
await signalRService.start();
```

### Reconnection Strategy
- **Exponential Backoff**: 1s, 2s, 4s, 8s, 16s maximum
- **Max Attempts**: 5 reconnection attempts
- **Automatic Retry**: Built-in SignalR reconnection
- **Fallback Mode**: Mock data when disconnected

## Error Handling

### Backend
- **Service Errors**: Logged and don't break workflow execution
- **Connection Errors**: Logged with client connection ID
- **Database Errors**: Interceptor handles gracefully

### Frontend
- **Connection Failures**: Automatic retry with exponential backoff
- **Message Errors**: Logged to console, doesn't break UI
- **Fallback Data**: Mock data continues when disconnected

## Performance Considerations

### Backend
- **Batching**: Metrics updates are calculated efficiently
- **Caching**: Database queries optimized for metrics calculation
- **Groups**: Targeted messaging reduces unnecessary traffic

### Frontend
- **State Updates**: Efficient React state management
- **Memory Management**: Automatic event handler cleanup
- **Reconnection**: Intelligent retry strategy prevents spam

## Security

### Authentication
- **Hub Authorization**: `[Authorize]` attribute on hub
- **Connection Context**: User identity available in hub methods
- **Group Security**: Users can only join appropriate groups

### Data Validation
- **Message Validation**: Type-safe message structures
- **Input Sanitization**: All user inputs validated
- **Error Boundaries**: Graceful error handling

## Monitoring and Debugging

### Logging
- **Backend**: Structured logging with Serilog
- **Frontend**: Console logging for development
- **Connection Events**: All connection state changes logged

### Health Checks
- **Connection Status**: Real-time connection indicator in UI
- **Processing Status**: Visual indicators for active processing
- **Error States**: Clear error messaging and recovery options

## Testing Strategy

### Unit Tests
- **Notification Service**: Mock SignalR hub context
- **Message Handling**: Verify correct message formatting
- **State Management**: Test React state updates

### Integration Tests
- **End-to-End**: Full workflow from scraper to UI update
- **Connection Handling**: Test reconnection scenarios
- **Error Recovery**: Verify graceful degradation

## Deployment Considerations

### Production Configuration
- **Connection Strings**: Secure configuration management
- **Scaling**: SignalR backplane for multiple instances
- **Monitoring**: Application insights integration

### Performance Monitoring
- **Connection Metrics**: Track active connections
- **Message Throughput**: Monitor message rates
- **Error Rates**: Track connection and message failures

## Future Enhancements

### Planned Features
- **User-Specific Filtering**: Personalized lead updates
- **Real-Time Notifications**: Browser notifications for important events
- **Historical Playback**: Replay lead processing history
- **Advanced Analytics**: Real-time processing analytics

### Scalability Improvements
- **Redis Backplane**: Multi-server SignalR scaling
- **Message Queuing**: Reliable message delivery
- **Caching Layer**: Improved performance for metrics