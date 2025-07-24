using ByteForgeFrontend.Models.ProjectManagement;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.ProjectManagement;

public interface IProjectTemplateService
{
    Task<ProjectTemplate?> GetTemplateAsync(string templateId);
    Task<IEnumerable<ProjectTemplate>> GetAllTemplatesAsync();
    Task<IEnumerable<ProjectTemplate>> GetTemplatesByCategoryAsync(string category);
    Task<TemplateStructure?> GetTemplateStructureAsync(string templateId);
    Task<TemplateValidationResult> ValidateTemplateAsync(string templateId);
    Task<ProjectTemplate?> CloneTemplateAsync(string sourceTemplateId, string newTemplateId, string newName);
}