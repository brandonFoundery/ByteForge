using ByteForgeFrontend.Models.ProjectManagement;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.Templates;

public interface ITemplateManagementService
{
    // CRUD Operations
    Task<ProjectTemplate> CreateTemplateAsync(ProjectTemplate template);
    Task<ProjectTemplate?> GetTemplateAsync(string templateId);
    Task<IEnumerable<ProjectTemplate>> GetAllTemplatesAsync();
    Task<IEnumerable<ProjectTemplate>> GetTemplatesByCategoryAsync(string category);
    Task<ProjectTemplate> UpdateTemplateAsync(ProjectTemplate template);
    Task<bool> DeleteTemplateAsync(string templateId);
    
    // Template Operations
    Task<ProjectTemplate> CloneTemplateAsync(string sourceTemplateId, string newTemplateId, string newName);
    Task<bool> IsTemplateInUseAsync(string templateId);
    Task<int> GetTemplateUsageCountAsync(string templateId);
    
    // Versioning
    Task<ProjectTemplate> CreateTemplateVersionAsync(string templateId, string newVersion, string changeNotes);
    Task<IEnumerable<TemplateVersion>> GetTemplateVersionsAsync(string templateId);
    Task<TemplateVersionComparison> CompareTemplateVersionsAsync(string templateId, string version1, string version2);
    
    // Import/Export
    Task<ProjectTemplate> ImportTemplateAsync(Stream templateStream, string format = "json");
    Task<Stream> ExportTemplateAsync(string templateId, string format = "json");
    
    // Template Marketplace
    Task<IEnumerable<ProjectTemplate>> SearchTemplatesAsync(string searchTerm, TemplateSearchOptions? options = null);
    Task<TemplateRating?> GetTemplateRatingAsync(string templateId);
    Task RateTemplateAsync(string templateId, int rating, string? review = null, string userId = "anonymous");
}