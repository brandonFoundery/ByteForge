using System;
using System.Collections.Generic;

using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.AIAgents
{
    public class AgentProjectContext
    {
        public Guid ProjectId { get; set; }
        public string WorkingDirectory { get; set; }
        public RequirementsContext Requirements { get; set; }
        public string[] ExistingFiles { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public class RequirementsContext
    {
        public string BusinessRequirements { get; set; }
        public string FunctionalRequirements { get; set; }
        public string TechnicalRequirements { get; set; }
        public string SecurityRequirements { get; set; }
        public string InfrastructureRequirements { get; set; }
        public Dictionary<string, string> CustomRequirements { get; set; } = new();
    }

    public class AgentCodeGenerationResult
    {
        public bool Success { get; set; }
        public string Error { get; set; }
        public List<string> GeneratedFiles { get; set; } = new();
        public Dictionary<string, string> FileContents { get; set; } = new();
        public TimeSpan Duration { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public interface ICodeGeneratingAgent : IAgent
    {
        Task<AgentCodeGenerationResult> GenerateCodeAsync(AgentProjectContext context);
        Task<bool> UseTemplateAsync(string templatePath, object model);
    }
}