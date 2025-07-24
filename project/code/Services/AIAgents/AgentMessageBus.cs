using System;
using System.Collections.Concurrent;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.AIAgents
{
    public class AgentMessageBus : IAgentMessageBus
    {
        private readonly ConcurrentDictionary<Guid, Func<AgentMessage, Task>> _subscribers = new();
        private readonly ILogger<AgentMessageBus> _logger;

        public AgentMessageBus(ILogger<AgentMessageBus> logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<MessageResult> PublishAsync(AgentMessage message)
        {
            if (message == null)
            {
                throw new ArgumentNullException(nameof(message));
            }

            _logger.LogDebug("Publishing message {MessageId} from {SenderId} to {ReceiverId}", 
                message.Id, message.SenderId, message.ReceiverId ?? (object)"all");

            var result = new MessageResult();

            try
            {
                // Handle broadcast messages
                if (message.Type == MessageType.Broadcast || !message.ReceiverId.HasValue)
                {
                    var tasks = _subscribers
                        .Where(kvp => kvp.Key != message.SenderId) // Don't send to self
                        .Select(kvp => DeliverMessageAsync(kvp.Value, message))
                        .ToList();

                    await Task.WhenAll(tasks);
                    
                    result.Delivered = tasks.Any();
                    result.DeliveredAt = DateTime.UtcNow;
                    
                    if (!result.Delivered)
                    {
                        result.Error = "No subscribers found for broadcast";
                    }
                }
                // Handle targeted messages
                else
                {
                    if (_subscribers.TryGetValue(message.ReceiverId.Value, out var handler))
                    {
                        await DeliverMessageAsync(handler, message);
                        result.Delivered = true;
                        result.DeliveredAt = DateTime.UtcNow;
                    }
                    else
                    {
                        result.Delivered = false;
                        result.Error = "Recipient not found";
                    }
                }

                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error publishing message {MessageId}", message.Id);
                result.Delivered = false;
                result.Error = ex.Message;
                return result;
            }
        }

        public Task SubscribeAsync(Guid agentId, Func<AgentMessage, Task> handler)
        {
            if (handler == null)
            {
                throw new ArgumentNullException(nameof(handler));
            }

            _subscribers.AddOrUpdate(agentId, handler, (_, __) => handler);
            _logger.LogInformation("Agent {AgentId} subscribed to message bus", agentId);
            
            return Task.CompletedTask;
        }

        public Task UnsubscribeAsync(Guid agentId)
        {
            if (_subscribers.TryRemove(agentId, out _))
            {
                _logger.LogInformation("Agent {AgentId} unsubscribed from message bus", agentId);
            }
            
            return Task.CompletedTask;
        }

        private async Task DeliverMessageAsync(Func<AgentMessage, Task> handler, AgentMessage message)
        {
            try
            {
                await handler(message);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error delivering message {MessageId} to handler", message.Id);
            }
        }
    }
}