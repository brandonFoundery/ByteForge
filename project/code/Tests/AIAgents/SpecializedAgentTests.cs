using System;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.AIAgents;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;
using Moq;

namespace ByteForgeFrontend.Tests.AIAgents
{
    public class SpecializedAgentTests
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly Mock<ILLMService> _mockLLMService;
        private readonly Mock<IDocumentGenerationService> _mockDocService;
        private readonly Mock<IProjectService> _mockProjectService;

        public SpecializedAgentTests()
        {
            var services = new ServiceCollection();
            
            _mockLLMService = new Mock<ILLMService>();
            _mockDocService = new Mock<IDocumentGenerationService>();
            _mockProjectService = new Mock<IProjectService>();
            
            services.AddSingleton(_mockLLMService.Object);
            services.AddSingleton(_mockDocService.Object);
            services.AddSingleton(_mockProjectService.Object);
            services.AddSingleton(Mock.Of<ILogger<BaseAgent>>());
            services.AddSingleton(Mock.Of<ILogger<BackendAgent>>());
            services.AddSingleton(Mock.Of<ILogger<FrontendAgent>>());
            services.AddSingleton(Mock.Of<ILogger<SecurityAgent>>());
            services.AddSingleton(Mock.Of<ILogger<InfrastructureAgent>>());
            
            _serviceProvider = services.BuildServiceProvider();
        }

        [Fact]
        public async Task BackendAgent_Should_Generate_API_Code()
        {
            // Arrange
            var backendAgent = new BackendAgent(_serviceProvider, "backend-agent");
            var projectContext = new AgentProjectContext
            {
                ProjectId = Guid.NewGuid(),
                WorkingDirectory = "/test/backend",
                Requirements = new RequirementsContext
                {
                    FunctionalRequirements = "API for user management",
                    TechnicalRequirements = "ASP.NET Core 8.0, Clean Architecture"
                }
            };

            _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new LLMResponse 
                { 
                    Success = true, 
                    Content = "Generated API code..."
                });

            // Act
            var result = await backendAgent.GenerateCodeAsync(projectContext);

            // Assert
            Assert.True(result.Success);
            Assert.Contains("API", result.GeneratedFiles);
            _mockLLMService.Verify(x => x.GenerateAsync(
                It.Is<string>(p => p.Contains("ASP.NET Core") && p.Contains("Clean Architecture")), 
                It.IsAny<CancellationToken>()), 
                Times.AtLeastOnce);
        }

        [Fact]
        public async Task FrontendAgent_Should_Generate_React_Components()
        {
            // Arrange
            var frontendAgent = new FrontendAgent(_serviceProvider, "frontend-agent");
            var projectContext = new AgentProjectContext
            {
                ProjectId = Guid.NewGuid(),
                WorkingDirectory = "/test/frontend",
                Requirements = new RequirementsContext
                {
                    FunctionalRequirements = "User dashboard with charts",
                    TechnicalRequirements = "React, TypeScript, Material-UI"
                }
            };

            _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new LLMResponse 
                { 
                    Success = true, 
                    Content = "Generated React component..."
                });

            // Act
            var result = await frontendAgent.GenerateCodeAsync(projectContext);

            // Assert
            Assert.True(result.Success);
            Assert.Contains("components", result.GeneratedFiles);
            _mockLLMService.Verify(x => x.GenerateAsync(
                It.Is<string>(p => p.Contains("React") && p.Contains("TypeScript")), 
                It.IsAny<CancellationToken>()), 
                Times.AtLeastOnce);
        }

        [Fact]
        public async Task SecurityAgent_Should_Generate_Auth_Code()
        {
            // Arrange
            var securityAgent = new SecurityAgent(_serviceProvider, "security-agent");
            var projectContext = new AgentProjectContext
            {
                ProjectId = Guid.NewGuid(),
                WorkingDirectory = "/test/security",
                Requirements = new RequirementsContext
                {
                    SecurityRequirements = "JWT authentication, role-based authorization",
                    TechnicalRequirements = "ASP.NET Core Identity"
                }
            };

            _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new LLMResponse 
                { 
                    Success = true, 
                    Content = "Generated security code..."
                });

            // Act
            var result = await securityAgent.GenerateCodeAsync(projectContext);

            // Assert
            Assert.True(result.Success);
            Assert.Contains("authentication", result.GeneratedFiles);
            _mockLLMService.Verify(x => x.GenerateAsync(
                It.Is<string>(p => p.Contains("JWT") && p.Contains("role-based")), 
                It.IsAny<CancellationToken>()), 
                Times.AtLeastOnce);
        }

        [Fact]
        public async Task InfrastructureAgent_Should_Generate_Docker_Config()
        {
            // Arrange
            var infraAgent = new InfrastructureAgent(_serviceProvider, "infrastructure-agent");
            var projectContext = new AgentProjectContext
            {
                ProjectId = Guid.NewGuid(),
                WorkingDirectory = "/test/infrastructure",
                Requirements = new RequirementsContext
                {
                    InfrastructureRequirements = "Docker containers, nginx reverse proxy",
                    TechnicalRequirements = "Azure deployment, CI/CD"
                }
            };

            _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new LLMResponse 
                { 
                    Success = true, 
                    Content = "Generated Docker configuration..."
                });

            // Act
            var result = await infraAgent.GenerateCodeAsync(projectContext);

            // Assert
            Assert.True(result.Success);
            Assert.Contains("docker", result.GeneratedFiles);
            _mockLLMService.Verify(x => x.GenerateAsync(
                It.Is<string>(p => p.Contains("Docker") && p.Contains("nginx")), 
                It.IsAny<CancellationToken>()), 
                Times.AtLeastOnce);
        }

        [Fact]
        public async Task Agents_Should_Use_Document_Templates()
        {
            // Arrange
            var backendAgent = new BackendAgent(_serviceProvider, "backend-agent");
            var templateContent = "namespace {{ProjectName}} { }";
            
            _mockDocService.Setup(x => x.GetTemplateAsync("backend/controller", It.IsAny<CancellationToken>()))
                .ReturnsAsync(templateContent);

            _mockDocService.Setup(x => x.RenderTemplateAsync(
                It.IsAny<string>(), 
                It.IsAny<object>(), 
                It.IsAny<CancellationToken>()))
                .ReturnsAsync("namespace TestProject { }");

            // Act
            await backendAgent.StartAsync();
            var templateUsed = await backendAgent.UseTemplateAsync("backend/controller", new { ProjectName = "TestProject" });

            // Assert
            Assert.True(templateUsed);
            _mockDocService.Verify(x => x.GetTemplateAsync("backend/controller", It.IsAny<CancellationToken>()), Times.Once);
            _mockDocService.Verify(x => x.RenderTemplateAsync(templateContent, It.IsAny<object>(), It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task Agents_Should_Handle_LLM_Failures()
        {
            // Arrange
            var backendAgent = new BackendAgent(_serviceProvider, "backend-agent");
            var projectContext = new AgentProjectContext
            {
                ProjectId = Guid.NewGuid(),
                WorkingDirectory = "/test/backend"
            };

            _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new LLMResponse 
                { 
                    Success = false, 
                    Error = "LLM service unavailable"
                });

            // Act
            var result = await backendAgent.GenerateCodeAsync(projectContext);

            // Assert
            Assert.False(result.Success);
            Assert.Contains("LLM service unavailable", result.Error);
        }

        [Fact]
        public async Task Agents_Should_Support_Incremental_Generation()
        {
            // Arrange
            var frontendAgent = new FrontendAgent(_serviceProvider, "frontend-agent");
            var projectContext = new AgentProjectContext
            {
                ProjectId = Guid.NewGuid(),
                WorkingDirectory = "/test/frontend",
                ExistingFiles = new[] { "App.tsx", "index.tsx" }
            };

            _mockLLMService.Setup(x => x.GenerateAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                .ReturnsAsync(new LLMResponse 
                { 
                    Success = true, 
                    Content = "New component code..."
                });

            // Act
            var result = await frontendAgent.GenerateCodeAsync(projectContext);

            // Assert
            Assert.True(result.Success);
            Assert.DoesNotContain("App.tsx", result.GeneratedFiles); // Should not regenerate existing files
            _mockLLMService.Verify(x => x.GenerateAsync(
                It.Is<string>(p => p.Contains("existing files")), 
                It.IsAny<CancellationToken>()), 
                Times.AtLeastOnce);
        }
    }
}