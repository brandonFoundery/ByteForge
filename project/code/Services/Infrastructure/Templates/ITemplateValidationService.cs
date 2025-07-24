using ByteForgeFrontend.Models.ProjectManagement;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.Templates;

public interface ITemplateValidationService
{
    Task<TemplateValidationResult> ValidateTemplateAsync(ProjectTemplate template);
    Task<TemplateValidationResult> ValidateTemplateStructureAsync(TemplateStructure structure);
    Task<TemplateValidationResult> ValidateDefaultSettingsAsync(Dictionary<string, object> settings);
    Task<TemplateValidationResult> ValidateTemplateMetadataAsync(ProjectTemplate template);
    Task<bool> IsValidTemplateIdAsync(string templateId);
    Task<bool> IsValidDocumentTypeAsync(string documentType);
    Task<IEnumerable<string>> GetValidCategoriesAsync();
    Task<IEnumerable<string>> GetValidDocumentTypesAsync();
}