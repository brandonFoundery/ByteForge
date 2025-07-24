using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

using System.Linq;
namespace ByteForgeFrontend.Services.AIAgents
{
    public class InfrastructureAgent : BaseAgent, ICodeGeneratingAgent
    {
        private readonly ILLMService _llmService;
        private readonly IDocumentTemplateService _documentService;
        private readonly ILogger<InfrastructureAgent> _agentLogger;

        public InfrastructureAgent(IServiceProvider serviceProvider, string name) 
            : base(serviceProvider, name)
        {
            _llmService = serviceProvider.GetService<ILLMService>();
            _documentService = serviceProvider.GetService<IDocumentTemplateService>();
            _agentLogger = serviceProvider.GetRequiredService<ILogger<InfrastructureAgent>>();
        }

        public async Task<AgentCodeGenerationResult> GenerateCodeAsync(AgentProjectContext context)
        {
            var stopwatch = Stopwatch.StartNew();
            var result = new AgentCodeGenerationResult();

            try
            {
                _agentLogger.LogInformation("Infrastructure agent starting code generation for project {ProjectId}", 
                    context.ProjectId);

                // Generate Docker configuration
                var dockerFiles = await GenerateDockerConfigurationAsync(context);
                result.GeneratedFiles.AddRange(dockerFiles.Keys);
                foreach (var file in dockerFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate CI/CD pipelines
                var cicdFiles = await GenerateCICDPipelinesAsync(context);
                result.GeneratedFiles.AddRange(cicdFiles.Keys);
                foreach (var file in cicdFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate infrastructure as code
                var iacFiles = await GenerateInfrastructureAsCodeAsync(context);
                result.GeneratedFiles.AddRange(iacFiles.Keys);
                foreach (var file in iacFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate monitoring configuration
                var monitoringFiles = await GenerateMonitoringConfigAsync(context);
                result.GeneratedFiles.AddRange(monitoringFiles.Keys);
                foreach (var file in monitoringFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                result.Success = true;
                _agentLogger.LogInformation("Infrastructure agent generated {FileCount} files", result.GeneratedFiles.Count);
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Error = ex.Message;
                _agentLogger.LogError(ex, "Infrastructure agent failed to generate code");
            }
            finally
            {
                stopwatch.Stop();
                result.Duration = stopwatch.Elapsed;
            }

            return result;
        }

        public async Task<bool> UseTemplateAsync(string templatePath, object model)
        {
            try
            {
                if (_documentService == null)
                {
                    _agentLogger.LogWarning("Document service not available for template usage");
                    return false;
                }

                var template = await _documentService.LoadTemplateAsync(templatePath);
                var modelDict = model as Dictionary<string, object> ?? new Dictionary<string, object>();
                var rendered = await _documentService.ProcessTemplateAsync(template, modelDict);
                
                _agentLogger.LogDebug("Successfully used template {TemplatePath}", templatePath);
                return true;
            }
            catch (Exception ex)
            {
                _agentLogger.LogError(ex, "Failed to use template {TemplatePath}", templatePath);
                return false;
            }
        }

        protected override async Task<AgentResult> PerformWorkAsync(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                await Task.Delay(1000, cancellationToken);
            }

            return new AgentResult { Success = true };
        }

        private async Task<Dictionary<string, string>> GenerateDockerConfigurationAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                _agentLogger.LogWarning("LLM service not available, using mock generation");
                files["docker/Dockerfile.backend"] = GenerateMockDockerfile("backend");
                files["docker/Dockerfile.frontend"] = GenerateMockDockerfile("frontend");
                files["docker/docker-compose.yml"] = GenerateMockDockerCompose();
                files["docker/.dockerignore"] = GenerateMockDockerIgnore();
                return files;
            }

            var prompt = BuildDockerGenerationPrompt(context);
            var request = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a DevOps expert generating Docker configuration files.",
                Temperature = 0.7,
                MaxTokens = 2000
            };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, "");
                foreach (var file in generatedFiles)
                {
                    files[$"docker/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateCICDPipelinesAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                files["cicd/azure-pipelines.yml"] = GenerateMockAzurePipeline();
                files["cicd/github-actions.yml"] = GenerateMockGitHubActions();
                return files;
            }

            var prompt = BuildCICDPrompt(context);
            var request = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a DevOps expert generating CI/CD pipeline configuration.",
                Temperature = 0.7,
                MaxTokens = 2000
            };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".yml");
                foreach (var file in generatedFiles)
                {
                    files[$"cicd/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateInfrastructureAsCodeAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                files["iac/terraform/main.tf"] = GenerateMockTerraform();
                files["iac/terraform/variables.tf"] = GenerateMockTerraformVariables();
                return files;
            }

            var prompt = BuildIaCPrompt(context);
            var request = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a cloud infrastructure expert generating Infrastructure as Code.",
                Temperature = 0.7,
                MaxTokens = 2000
            };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".tf");
                foreach (var file in generatedFiles)
                {
                    files[$"iac/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateMonitoringConfigAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();
            files["monitoring/prometheus.yml"] = GenerateMockPrometheusConfig();
            files["monitoring/grafana-dashboard.json"] = GenerateMockGrafanaDashboard();
            return files;
        }

        private string BuildDockerGenerationPrompt(AgentProjectContext context)
        {
            var requirements = context.Requirements;
            return $@"Generate Docker configuration based on:

Infrastructure Requirements:
{requirements.InfrastructureRequirements}

Technical Requirements:
{requirements.TechnicalRequirements}

Include:
- Multi-stage Dockerfile for backend (ASP.NET Core)
- Dockerfile for frontend (React/Next.js)
- docker-compose.yml with all services
- nginx configuration for reverse proxy
- Environment variable management
- Health checks
- Volume mounts for development";
        }

        private string BuildCICDPrompt(AgentProjectContext context)
        {
            return $@"Generate CI/CD pipeline configuration for:

Requirements:
{context.Requirements.InfrastructureRequirements}

Include:
- Build and test stages
- Docker image building and pushing
- Deployment to staging and production
- Environment-specific configurations
- Secret management
- Rollback procedures";
        }

        private string BuildIaCPrompt(AgentProjectContext context)
        {
            return $@"Generate Infrastructure as Code for:

Requirements:
{context.Requirements.InfrastructureRequirements}

Include:
- Cloud resource provisioning (Azure/AWS)
- Networking configuration
- Security groups
- Database infrastructure
- Container orchestration
- Monitoring and logging setup";
        }

        private Dictionary<string, string> ParseGeneratedFiles(string llmResponse, string fileSuffix)
        {
            var files = new Dictionary<string, string>();
            var lines = llmResponse.Split('\n');
            string currentFile = null;
            var currentContent = new List<string>();

            foreach (var line in lines)
            {
                if (line.StartsWith("// File:") || line.StartsWith("# File:"))
                {
                    if (currentFile != null && currentContent.Any())
                    {
                        files[currentFile] = string.Join("\n", currentContent);
                    }
                    currentFile = line.Substring(line.IndexOf(':') + 1).Trim();
                    currentContent.Clear();
                }
                else if (currentFile != null)
                {
                    currentContent.Add(line);
                }
            }

            if (currentFile != null && currentContent.Any())
            {
                files[currentFile] = string.Join("\n", currentContent);
            }

            if (!files.Any() && !string.IsNullOrWhiteSpace(llmResponse))
            {
                files[$"Generated{fileSuffix}"] = llmResponse;
            }

            return files;
        }

        private string GenerateMockDockerfile(string service)
        {
            if (service == "backend")
            {
                return @"# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj and restore
COPY *.csproj ./
RUN dotnet restore

# Copy everything else and build
COPY . .
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

EXPOSE 80
ENTRYPOINT [""dotnet"", ""ByteForgeFrontend.dll""]";
            }
            else
            {
                return @"# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD [""nginx"", ""-g"", ""daemon off;""]";
            }
        }

        private string GenerateMockDockerCompose()
        {
            return @"version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - ConnectionStrings__DefaultConnection=Server=db;Database=ByteForge;User=sa;Password=${DB_PASSWORD}
    ports:
      - ""5000:80""
    depends_on:
      - db
      - redis
    networks:
      - byteforge-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - ""3000:80""
    depends_on:
      - backend
    networks:
      - byteforge-network

  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=${DB_PASSWORD}
    volumes:
      - db-data:/var/opt/mssql
    ports:
      - ""1433:1433""
    networks:
      - byteforge-network

  redis:
    image: redis:alpine
    ports:
      - ""6379:6379""
    networks:
      - byteforge-network

  nginx:
    image: nginx:alpine
    ports:
      - ""80:80""
      - ""443:443""
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - byteforge-network

volumes:
  db-data:

networks:
  byteforge-network:
    driver: bridge";
        }

        private string GenerateMockDockerIgnore()
        {
            return @"# Git
.git
.gitignore

# CI
.github
.gitlab-ci.yml
.travis.yml

# Docker
docker-compose.yml
Dockerfile
.dockerignore

# Byte-compiled / optimized / DLL files
bin/
obj/
*.dll
*.exe
*.pdb

# Visual Studio
.vs/
*.user
*.suo
*.sln.docstates

# Node
node_modules/
npm-debug.log
yarn-error.log

# Testing
TestResults/
*.trx
*.coverage

# OS
.DS_Store
Thumbs.db

# Build results
[Dd]ebug/
[Rr]elease/
x64/
x86/
[Bb]in/
[Oo]bj/
build/
dist/";
        }

        private string GenerateMockAzurePipeline()
        {
            return @"trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  buildConfiguration: 'Release'
  dockerRegistry: 'yourregistry.azurecr.io'

stages:
  - stage: Build
    jobs:
      - job: BuildBackend
        steps:
          - task: UseDotNet@2
            inputs:
              version: '8.0.x'
          
          - script: dotnet restore
            displayName: 'Restore packages'
          
          - script: dotnet build --configuration $(buildConfiguration)
            displayName: 'Build solution'
          
          - script: dotnet test --configuration $(buildConfiguration) --logger trx
            displayName: 'Run tests'
          
          - task: PublishTestResults@2
            inputs:
              testResultsFormat: 'VSTest'
              testResultsFiles: '**/*.trx'

      - job: BuildFrontend
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: '18.x'
          
          - script: npm ci
            displayName: 'Install dependencies'
          
          - script: npm run test
            displayName: 'Run tests'
          
          - script: npm run build
            displayName: 'Build application'

  - stage: Deploy
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - job: DeployToProduction
        steps:
          - task: Docker@2
            inputs:
              command: 'buildAndPush'
              containerRegistry: $(dockerRegistry)
              repository: 'byteforge'
              tags: |
                $(Build.BuildId)
                latest";
        }

        private string GenerateMockGitHubActions()
        {
            return @"name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: 8.0.x
      
      - name: Restore dependencies
        run: dotnet restore
      
      - name: Build
        run: dotnet build --no-restore
      
      - name: Test
        run: dotnet test --no-build --verbosity normal

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}";
        }

        private string GenerateMockTerraform()
        {
            return @"terraform {
  required_providers {
    azurerm = {
      source  = ""hashicorp/azurerm""
      version = ""~> 3.0""
    }
  }
}

provider ""azurerm"" {
  features {}
}

resource ""azurerm_resource_group"" ""main"" {
  name     = ""${var.project_name}-rg""
  location = var.location
}

resource ""azurerm_container_registry"" ""acr"" {
  name                = ""${var.project_name}acr""
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = ""Standard""
  admin_enabled       = true
}

resource ""azurerm_kubernetes_cluster"" ""aks"" {
  name                = ""${var.project_name}-aks""
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.project_name

  default_node_pool {
    name       = ""default""
    node_count = var.node_count
    vm_size    = ""Standard_D2_v2""
  }

  identity {
    type = ""SystemAssigned""
  }
}

resource ""azurerm_sql_server"" ""sql"" {
  name                         = ""${var.project_name}-sql""
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = ""12.0""
  administrator_login          = var.db_admin_username
  administrator_login_password = var.db_admin_password
}

resource ""azurerm_sql_database"" ""db"" {
  name                = ""${var.project_name}-db""
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  server_name         = azurerm_sql_server.sql.name
  edition             = ""Standard""
  requested_service_objective_name = ""S1""
}";
        }

        private string GenerateMockTerraformVariables()
        {
            return @"variable ""project_name"" {
  description = ""The name of the project""
  type        = string
  default     = ""byteforge""
}

variable ""location"" {
  description = ""Azure region for resources""
  type        = string
  default     = ""East US""
}

variable ""node_count"" {
  description = ""Number of nodes in the AKS cluster""
  type        = number
  default     = 3
}

variable ""db_admin_username"" {
  description = ""Administrator username for SQL Server""
  type        = string
  sensitive   = true
}

variable ""db_admin_password"" {
  description = ""Administrator password for SQL Server""
  type        = string
  sensitive   = true
}";
        }

        private string GenerateMockPrometheusConfig()
        {
            return @"global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'byteforge-backend'
    static_configs:
      - targets: ['backend:80']
    metrics_path: /metrics

  - job_name: 'byteforge-frontend'
    static_configs:
      - targets: ['frontend:80']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']";
        }

        private string GenerateMockGrafanaDashboard()
        {
            return @"{
  ""dashboard"": {
    ""title"": ""ByteForge Monitoring"",
    ""panels"": [
      {
        ""title"": ""API Response Time"",
        ""type"": ""graph"",
        ""targets"": [
          {
            ""expr"": ""http_request_duration_seconds""
          }
        ]
      },
      {
        ""title"": ""Request Rate"",
        ""type"": ""graph"",
        ""targets"": [
          {
            ""expr"": ""rate(http_requests_total[5m])""
          }
        ]
      }
    ]
  }
}";
        }
    }
}