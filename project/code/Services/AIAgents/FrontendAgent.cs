using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace ByteForgeFrontend.Services.AIAgents
{
    public class FrontendAgent : BaseAgent, ICodeGeneratingAgent
    {
        private readonly ILLMService _llmService;
        private readonly IDocumentTemplateService _documentService;
        private readonly ILogger<FrontendAgent> _agentLogger;

        public FrontendAgent(IServiceProvider serviceProvider, string name) 
            : base(serviceProvider, name)
        {
            _llmService = serviceProvider.GetService<ILLMService>();
            _documentService = serviceProvider.GetService<IDocumentTemplateService>();
            _agentLogger = serviceProvider.GetRequiredService<ILogger<FrontendAgent>>();
        }

        public async Task<AgentCodeGenerationResult> GenerateCodeAsync(AgentProjectContext context)
        {
            var stopwatch = Stopwatch.StartNew();
            var result = new AgentCodeGenerationResult();

            try
            {
                _agentLogger.LogInformation("Frontend agent starting code generation for project {ProjectId}", 
                    context.ProjectId);

                // Generate React components
                var componentFiles = await GenerateReactComponentsAsync(context);
                result.GeneratedFiles.AddRange(componentFiles.Keys);
                foreach (var file in componentFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate pages
                var pageFiles = await GeneratePagesAsync(context);
                result.GeneratedFiles.AddRange(pageFiles.Keys);
                foreach (var file in pageFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate services
                var serviceFiles = await GenerateServicesAsync(context);
                result.GeneratedFiles.AddRange(serviceFiles.Keys);
                foreach (var file in serviceFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate styles
                var styleFiles = await GenerateStylesAsync(context);
                result.GeneratedFiles.AddRange(styleFiles.Keys);
                foreach (var file in styleFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                result.Success = true;
                _agentLogger.LogInformation("Frontend agent generated {FileCount} files", result.GeneratedFiles.Count);
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Error = ex.Message;
                _agentLogger.LogError(ex, "Frontend agent failed to generate code");
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

        private async Task<Dictionary<string, string>> GenerateReactComponentsAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                _agentLogger.LogWarning("LLM service not available, using mock generation");
                files["components/UserList.tsx"] = GenerateMockComponent("UserList");
                files["components/Dashboard.tsx"] = GenerateMockComponent("Dashboard");
                return files;
            }

            var prompt = BuildComponentGenerationPrompt(context);
            var request = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a React expert generating TypeScript/TSX components.",
                Temperature = 0.7,
                MaxTokens = 2000
            };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".tsx");
                foreach (var file in generatedFiles)
                {
                    files[$"components/{file.Key}"] = file.Value;
                }
            }
            else
            {
                throw new Exception($"LLM service failed: {response.Error}");
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GeneratePagesAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                files["pages/Home.tsx"] = GenerateMockPage("Home");
                return files;
            }

            var prompt = BuildPageGenerationPrompt(context);
            var request = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a React expert generating Next.js pages with TypeScript.",
                Temperature = 0.7,
                MaxTokens = 2000
            };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".tsx");
                foreach (var file in generatedFiles)
                {
                    files[$"pages/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateServicesAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                files["services/api.ts"] = GenerateMockApiService();
                return files;
            }

            var prompt = BuildServiceGenerationPrompt(context);
            var request = new LLMGenerationRequest
            {
                Prompt = prompt,
                SystemPrompt = "You are a TypeScript expert generating API service files.",
                Temperature = 0.7,
                MaxTokens = 2000
            };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".ts");
                foreach (var file in generatedFiles)
                {
                    files[$"services/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateStylesAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();
            files["styles/components.css"] = GenerateMockStyles();
            return files;
        }

        private string BuildComponentGenerationPrompt(AgentProjectContext context)
        {
            var requirements = context.Requirements;
            var existingFilesInfo = context.ExistingFiles != null && context.ExistingFiles.Any()
                ? $"\n\nExisting files (do not regenerate): {string.Join(", ", context.ExistingFiles)}"
                : "";

            return $@"Generate React components with TypeScript based on:

Functional Requirements:
{requirements.FunctionalRequirements}

Technical Requirements:
{requirements.TechnicalRequirements}

Use:
- React 18+ with functional components and hooks
- TypeScript for type safety
- Material-UI components where appropriate
- Proper error boundaries
- Loading states
- Responsive design{existingFilesInfo}

Generate complete, production-ready component code.";
        }

        private string BuildPageGenerationPrompt(AgentProjectContext context)
        {
            return $@"Generate React page components for:

Requirements:
{context.Requirements.FunctionalRequirements}

Include:
- Proper routing setup
- Layout components
- SEO metadata
- Authentication checks where needed
- Error handling";
        }

        private string BuildServiceGenerationPrompt(AgentProjectContext context)
        {
            return $@"Generate TypeScript service modules for:

Requirements:
{context.Requirements.FunctionalRequirements}

Include:
- API client with axios or fetch
- Type definitions for requests/responses
- Error handling and retry logic
- Authentication headers
- Request/response interceptors";
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

        private string GenerateMockComponent(string componentName)
        {
            return $@"import React from 'react';
import {{ Box, Typography, Paper }} from '@mui/material';

interface {componentName}Props {{
  title?: string;
}}

const {componentName}: React.FC<{componentName}Props> = ({{ title = '{componentName}' }}) => {{
  return (
    <Paper sx={{ p: 3, m: 2 }}>
      <Typography variant=""h4"" component=""h2"" gutterBottom>
        {{title}}
      </Typography>
      <Box sx={{ mt: 2 }}>
        <Typography variant=""body1"">
          This is a mock {componentName} component generated by the Frontend Agent.
        </Typography>
      </Box>
    </Paper>
  );
}};

export default {componentName};";
        }

        private string GenerateMockPage(string pageName)
        {
            return $@"import React from 'react';
import {{ Container, Typography }} from '@mui/material';

const {pageName}Page: React.FC = () => {{
  return (
    <Container maxWidth=""lg"">
      <Typography variant=""h2"" component=""h1"" gutterBottom>
        {pageName}
      </Typography>
      <Typography variant=""body1"">
        Welcome to the {pageName} page.
      </Typography>
    </Container>
  );
}};

export default {pageName}Page;";
        }

        private string GenerateMockApiService()
        {
            return @"import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;";
        }

        private string GenerateMockStyles()
        {
            return @"/* Component styles */
.component-container {
  padding: 16px;
  margin: 8px;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.error-message {
  color: #f44336;
  padding: 16px;
  border-radius: 4px;
  background-color: #ffebee;
}";
        }
    }
}