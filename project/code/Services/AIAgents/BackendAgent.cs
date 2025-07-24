using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

using Microsoft.AspNetCore.Mvc;
namespace ByteForgeFrontend.Services.AIAgents
{
    public class BackendAgent : BaseAgent, ICodeGeneratingAgent
    {
        private readonly ILLMService _llmService;
        private readonly IDocumentGenerationService _documentService;
        private readonly ILogger<BackendAgent> _agentLogger;

        public BackendAgent(IServiceProvider serviceProvider, string name) 
            : base(serviceProvider, name)
        {
            _llmService = serviceProvider.GetService<ILLMService>();
            _documentService = serviceProvider.GetService<IDocumentGenerationService>();
            _agentLogger = serviceProvider.GetRequiredService<ILogger<BackendAgent>>();
        }

        public async Task<AgentCodeGenerationResult> GenerateCodeAsync(AgentProjectContext context)
        {
            var stopwatch = Stopwatch.StartNew();
            var result = new AgentCodeGenerationResult();

            try
            {
                _agentLogger.LogInformation("Backend agent starting code generation for project {ProjectId}", 
                    context.ProjectId);

                // Validate context
                if (context.Requirements == null)
                {
                    throw new ArgumentException("Requirements context is required");
                }

                // Generate API controllers
                var apiFiles = await GenerateApiControllersAsync(context);
                result.GeneratedFiles.AddRange(apiFiles.Keys);
                foreach (var file in apiFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate business logic
                var businessFiles = await GenerateBusinessLogicAsync(context);
                result.GeneratedFiles.AddRange(businessFiles.Keys);
                foreach (var file in businessFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                // Generate data models
                var modelFiles = await GenerateDataModelsAsync(context);
                result.GeneratedFiles.AddRange(modelFiles.Keys);
                foreach (var file in modelFiles)
                {
                    result.FileContents[file.Key] = file.Value;
                }

                result.Success = true;
                _agentLogger.LogInformation("Backend agent generated {FileCount} files", result.GeneratedFiles.Count);
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Error = ex.Message;
                _agentLogger.LogError(ex, "Backend agent failed to generate code");
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

                var template = await _documentService.GetTemplateAsync(templatePath);
                var modelDict = model as Dictionary<string, object> ?? new Dictionary<string, object> { { "model", model } };
                var rendered = await _documentService.RenderTemplateAsync(template, modelDict);
                
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
            // This method is for continuous background work if needed
            // For now, we'll just keep the agent running
            while (!cancellationToken.IsCancellationRequested)
            {
                await Task.Delay(1000, cancellationToken);
            }

            return new AgentResult { Success = true };
        }

        private async Task<Dictionary<string, string>> GenerateApiControllersAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                _agentLogger.LogWarning("LLM service not available, using mock generation");
                files["Controllers/API/UserController.cs"] = GenerateMockController("User");
                return files;
            }

            var prompt = BuildApiGenerationPrompt(context);
            var request = new LLMGenerationRequest { Prompt = prompt };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                // Parse and extract generated files from LLM response
                var generatedFiles = ParseGeneratedFiles(response.Content, "Controller.cs");
                foreach (var file in generatedFiles)
                {
                    files[$"Controllers/API/{file.Key}"] = file.Value;
                }
            }
            else
            {
                throw new Exception($"LLM service failed: {response.Error}");
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateBusinessLogicAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                _agentLogger.LogWarning("LLM service not available, using mock generation");
                files["Services/UserService.cs"] = GenerateMockService("User");
                return files;
            }

            var prompt = BuildBusinessLogicPrompt(context);
            var request = new LLMGenerationRequest { Prompt = prompt };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, "Service.cs");
                foreach (var file in generatedFiles)
                {
                    files[$"Services/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private async Task<Dictionary<string, string>> GenerateDataModelsAsync(AgentProjectContext context)
        {
            var files = new Dictionary<string, string>();

            if (_llmService == null)
            {
                _agentLogger.LogWarning("LLM service not available, using mock generation");
                files["Models/User.cs"] = GenerateMockModel("User");
                return files;
            }

            var prompt = BuildDataModelPrompt(context);
            var request = new LLMGenerationRequest { Prompt = prompt };
            var response = await _llmService.GenerateAsync(request, CancellationToken.None);

            if (response.Success)
            {
                var generatedFiles = ParseGeneratedFiles(response.Content, ".cs");
                foreach (var file in generatedFiles)
                {
                    files[$"Models/{file.Key}"] = file.Value;
                }
            }

            return files;
        }

        private string BuildApiGenerationPrompt(AgentProjectContext context)
        {
            var requirements = context.Requirements;
            var existingFilesInfo = context.ExistingFiles != null && context.ExistingFiles.Any()
                ? $"\n\nExisting files to consider: {string.Join(", ", context.ExistingFiles)}"
                : "";

            return $@"Generate ASP.NET Core 8.0 API controllers based on the following requirements:

Functional Requirements:
{requirements.FunctionalRequirements}

Technical Requirements:
{requirements.TechnicalRequirements}

Use Clean Architecture patterns with:
- CQRS pattern using MediatR
- Repository pattern
- Dependency injection
- Proper error handling
- Input validation
- Authorization attributes{existingFilesInfo}

Generate complete, production-ready controller code.";
        }

        private string BuildBusinessLogicPrompt(AgentProjectContext context)
        {
            return $@"Generate business logic services for ASP.NET Core based on:

Requirements:
{context.Requirements.FunctionalRequirements}

Technical Stack:
{context.Requirements.TechnicalRequirements}

Include:
- Service interfaces and implementations
- Business rules validation
- Error handling
- Logging
- Unit of work pattern if applicable";
        }

        private string BuildDataModelPrompt(AgentProjectContext context)
        {
            return $@"Generate data models and entities for:

Requirements:
{context.Requirements.FunctionalRequirements}

Include:
- Entity classes with proper annotations
- DTOs for API communication
- AutoMapper profiles
- Validation attributes
- Entity configurations for EF Core";
        }

        private Dictionary<string, string> ParseGeneratedFiles(string llmResponse, string fileSuffix)
        {
            var files = new Dictionary<string, string>();
            
            // Simple parsing logic - in production, this would be more sophisticated
            // For now, assume the LLM returns code blocks with file markers
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

            // If no file markers found, treat entire response as a single file
            if (!files.Any() && !string.IsNullOrWhiteSpace(llmResponse))
            {
                files[$"Generated{fileSuffix}"] = llmResponse;
            }

            return files;
        }

        private string GenerateMockController(string entityName)
        {
            return $@"using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace ByteForgeFrontend.Controllers.API
{{
    [ApiController]
    [Route(""api/[controller]"")]
    [Authorize]
    public class {entityName}Controller : ControllerBase
    {{
        [HttpGet]
        public IActionResult GetAll()
        {{
            return Ok(new {{ message = ""Mock {entityName} list"" }});
        }}

        [HttpGet(""{{id}}"")]
        public IActionResult GetById(int id)
        {{
            return Ok(new {{ id = id, name = ""Mock {entityName}"" }});
        }}

        [HttpPost]
        public IActionResult Create([FromBody] object model)
        {{
            return CreatedAtAction(nameof(GetById), new {{ id = 1 }}, model);
        }}
    }}
}}";
        }

        private string GenerateMockService(string entityName)
        {
            return $@"using System.Collections.Generic;
using System.Threading.Tasks;

namespace ByteForgeFrontend.Services
{{
    public interface I{entityName}Service
    {{
        Task<IEnumerable<object>> GetAllAsync();
        Task<object> GetByIdAsync(int id);
        Task<object> CreateAsync(object model);
    }}

    public class {entityName}Service : I{entityName}Service
    {{
        public Task<IEnumerable<object>> GetAllAsync()
        {{
            return Task.FromResult<IEnumerable<object>>(new List<object>());
        }}

        public Task<object> GetByIdAsync(int id)
        {{
            return Task.FromResult<object>(new {{ Id = id }});
        }}

        public Task<object> CreateAsync(object model)
        {{
            return Task.FromResult(model);
        }}
    }}
}}";
        }

        private string GenerateMockModel(string entityName)
        {
            return $@"using System;
using System.ComponentModel.DataAnnotations;

namespace ByteForgeFrontend.Models
{{
    public class {entityName}
    {{
        public int Id {{ get; set; }}
        
        [Required]
        public string Name {{ get; set; }}
        
        public DateTime CreatedAt {{ get; set; }}
        public DateTime? UpdatedAt {{ get; set; }}
    }}
}}";
        }
    }
}