using ByteForgeFrontend.Models.ProjectManagement;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.ProjectManagement;

public interface IProjectService
{
    Task<Project> CreateProjectAsync(CreateProjectRequest request);
    Task<Project?> GetProjectAsync(string projectId);
    Task<IEnumerable<Project>> GetProjectsAsync(ProjectStatus? status = null);
    Task<Project?> UpdateProjectStatusAsync(string projectId, ProjectStatus status);
    Task<bool> DeleteProjectAsync(string projectId);
    Task<ProjectDocument> AddDocumentToProjectAsync(AddDocumentRequest request);
    Task<IEnumerable<ProjectDocument>> GetProjectDocumentsAsync(string projectId);
}

public class CreateProjectRequest
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? TemplateId { get; set; }
    public string? ClientRequirements { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
}

public class AddDocumentRequest
{
    public string ProjectId { get; set; } = string.Empty;
    public string DocumentType { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string Version { get; set; } = "1.0.0";
    public Dictionary<string, object>? Metadata { get; set; }
}