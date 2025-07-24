using System;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.AIAgents;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;
using Moq;

using System.Collections.Generic;
namespace ByteForgeFrontend.Tests.AIAgents
{
    public class AgentCommunicationTests
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly IAgentRegistry _agentRegistry;
        private readonly IAgentMessageBus _messageBus;

        public AgentCommunicationTests()
        {
            var services = new ServiceCollection();
            services.AddSingleton<IAgentRegistry, AgentRegistry>();
            services.AddSingleton<IAgentMessageBus, AgentMessageBus>();
            services.AddSingleton(Mock.Of<ILogger<AgentRegistry>>());
            services.AddSingleton(Mock.Of<ILogger<AgentMessageBus>>());
            services.AddSingleton(Mock.Of<ILogger<BaseAgent>>());
            
            _serviceProvider = services.BuildServiceProvider();
            _agentRegistry = _serviceProvider.GetRequiredService<IAgentRegistry>();
            _messageBus = _serviceProvider.GetRequiredService<IAgentMessageBus>();
        }

        [Fact]
        public async Task Agents_Should_Send_And_Receive_Messages()
        {
            // Arrange
            var senderAgent = new CommunicatingAgent(_serviceProvider, "sender", _messageBus);
            var receiverAgent = new CommunicatingAgent(_serviceProvider, "receiver", _messageBus);
            
            await _agentRegistry.RegisterAsync(senderAgent);
            await _agentRegistry.RegisterAsync(receiverAgent);

            // Act
            await senderAgent.StartAsync();
            await receiverAgent.StartAsync();
            
            var message = new AgentMessage
            {
                SenderId = senderAgent.Id,
                ReceiverId = receiverAgent.Id,
                Type = MessageType.Request,
                Content = "Test message"
            };
            
            await _messageBus.PublishAsync(message);
            await Task.Delay(100); // Allow message processing

            // Assert
            Assert.Single(receiverAgent.ReceivedMessages);
            Assert.Equal("Test message", receiverAgent.ReceivedMessages[0].Content);
        }

        [Fact]
        public async Task Agents_Should_Support_Broadcast_Messages()
        {
            // Arrange
            var broadcaster = new CommunicatingAgent(_serviceProvider, "broadcaster", _messageBus);
            var receiver1 = new CommunicatingAgent(_serviceProvider, "receiver1", _messageBus);
            var receiver2 = new CommunicatingAgent(_serviceProvider, "receiver2", _messageBus);
            
            await _agentRegistry.RegisterAsync(broadcaster);
            await _agentRegistry.RegisterAsync(receiver1);
            await _agentRegistry.RegisterAsync(receiver2);

            await broadcaster.StartAsync();
            await receiver1.StartAsync();
            await receiver2.StartAsync();

            // Act
            var broadcastMessage = new AgentMessage
            {
                SenderId = broadcaster.Id,
                Type = MessageType.Broadcast,
                Content = "Broadcast message"
            };
            
            await _messageBus.PublishAsync(broadcastMessage);
            await Task.Delay(100); // Allow message processing

            // Assert
            Assert.Single(receiver1.ReceivedMessages);
            Assert.Single(receiver2.ReceivedMessages);
            Assert.Equal("Broadcast message", receiver1.ReceivedMessages[0].Content);
            Assert.Equal("Broadcast message", receiver2.ReceivedMessages[0].Content);
        }

        [Fact]
        public async Task Agent_Should_Reply_To_Request()
        {
            // Arrange
            var requester = new CommunicatingAgent(_serviceProvider, "requester", _messageBus);
            var responder = new CommunicatingAgent(_serviceProvider, "responder", _messageBus)
            {
                ShouldAutoReply = true
            };
            
            await _agentRegistry.RegisterAsync(requester);
            await _agentRegistry.RegisterAsync(responder);

            await requester.StartAsync();
            await responder.StartAsync();

            // Act
            var request = new AgentMessage
            {
                SenderId = requester.Id,
                ReceiverId = responder.Id,
                Type = MessageType.Request,
                Content = "Request data"
            };
            
            await _messageBus.PublishAsync(request);
            await Task.Delay(200); // Allow request/response cycle

            // Assert
            Assert.NotEmpty(requester.ReceivedMessages);
            var response = requester.ReceivedMessages[0];
            Assert.Equal(MessageType.Response, response.Type);
            Assert.Contains("Response to: Request data", response.Content);
        }

        [Fact]
        public async Task MessageBus_Should_Handle_Undeliverable_Messages()
        {
            // Arrange
            var sender = new CommunicatingAgent(_serviceProvider, "sender", _messageBus);
            await _agentRegistry.RegisterAsync(sender);

            // Act
            var undeliverable = new AgentMessage
            {
                SenderId = sender.Id,
                ReceiverId = Guid.NewGuid(), // Non-existent agent
                Type = MessageType.Request,
                Content = "Undeliverable"
            };
            
            var result = await _messageBus.PublishAsync(undeliverable);

            // Assert
            Assert.False(result.Delivered);
            Assert.Equal("Recipient not found", result.Error);
        }

        // Test implementation for communication testing
        private class CommunicatingAgent : BaseAgent
        {
            private readonly IAgentMessageBus _messageBus;
            public List<AgentMessage> ReceivedMessages { get; } = new();
            public bool ShouldAutoReply { get; set; }

            public CommunicatingAgent(IServiceProvider serviceProvider, string name, IAgentMessageBus messageBus) 
                : base(serviceProvider, name)
            {
                _messageBus = messageBus;
            }

            protected override async Task<AgentResult> PerformWorkAsync(CancellationToken cancellationToken)
            {
                // Subscribe to messages
                await _messageBus.SubscribeAsync(Id, HandleMessage);
                
                // Keep running until cancelled
                while (!cancellationToken.IsCancellationRequested)
                {
                    await Task.Delay(10, cancellationToken);
                }
                
                return new AgentResult { Success = true };
            }

            private async Task HandleMessage(AgentMessage message)
            {
                ReceivedMessages.Add(message);
                
                if (ShouldAutoReply && message.Type == MessageType.Request)
                {
                    var reply = new AgentMessage
                    {
                        SenderId = Id,
                        ReceiverId = message.SenderId,
                        Type = MessageType.Response,
                        Content = $"Response to: {message.Content}",
                        CorrelationId = message.Id
                    };
                    
                    await _messageBus.PublishAsync(reply);
                }
            }
        }
    }
}