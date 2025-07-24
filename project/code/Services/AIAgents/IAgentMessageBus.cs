using System;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services.AIAgents
{
    public interface IAgentMessageBus
    {
        Task<MessageResult> PublishAsync(AgentMessage message);
        Task SubscribeAsync(Guid agentId, Func<AgentMessage, Task> handler);
        Task UnsubscribeAsync(Guid agentId);
    }

    public class AgentMessage
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public Guid SenderId { get; set; }
        public Guid? ReceiverId { get; set; }
        public MessageType Type { get; set; }
        public string Content { get; set; }
        public object Data { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public Guid? CorrelationId { get; set; }
    }

    public enum MessageType
    {
        Request,
        Response,
        Broadcast,
        Notification,
        Command,
        Event
    }

    public class MessageResult
    {
        public bool Delivered { get; set; }
        public string Error { get; set; }
        public DateTime DeliveredAt { get; set; }
    }
}