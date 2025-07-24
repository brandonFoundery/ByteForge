using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Data;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.ProjectManagement;

public class ProjectService : IProjectService
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<ProjectService> _logger;

    public ProjectService(ApplicationDbContext context, ILogger<ProjectService> logger)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<Project> CreateProjectAsync(CreateProjectRequest request)
    {
        try
        {
            // Check for duplicate name
            var existingProject = await _context.Projects
                .FirstOrDefaultAsync(p => p.Name == request.Name);
            
            if (existingProject != null)
            {
                throw new InvalidOperationException($"Project with name '{request.Name}' already exists");
            }

            var project = new Project
            {
                Id = Guid.NewGuid().ToString(),
                Name = request.Name,
                Description = request.Description,
                TemplateId = request.TemplateId,
                ClientRequirements = request.ClientRequirements,
                Status = ProjectStatus.Created,
                CreatedAt = DateTime.UtcNow,
                Metadata = request.Metadata ?? new Dictionary<string, object>()
            };

            _context.Projects.Add(project);
            await _context.SaveChangesAsync();

            _logger.LogInformation("Created project {ProjectId} with name {ProjectName}", project.Id, project.Name);
            return project;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating project");
            throw;
        }
    }

    public async Task<Project?> GetProjectAsync(string projectId)
    {
        try
        {
            return await _context.Projects
                .Include(p => p.Documents)
                .FirstOrDefaultAsync(p => p.Id == projectId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting project {ProjectId}", projectId);
            throw;
        }
    }

    public async Task<IEnumerable<Project>> GetProjectsAsync(ProjectStatus? status = null)
    {
        try
        {
            var query = _context.Projects.AsQueryable();

            if (status.HasValue)
            {
                query = query.Where(p => p.Status == status.Value);
            }

            return await query
                .OrderByDescending(p => p.CreatedAt)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting projects");
            throw;
        }
    }

    public async Task<Project?> UpdateProjectStatusAsync(string projectId, ProjectStatus status)
    {
        try
        {
            var project = await _context.Projects.FindAsync(projectId);
            if (project == null)
            {
                return null;
            }

            project.Status = status;
            project.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("Updated project {ProjectId} status to {Status}", projectId, status);
            return project;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating project status");
            throw;
        }
    }

    public async Task<bool> DeleteProjectAsync(string projectId)
    {
        try
        {
            var project = await _context.Projects
                .Include(p => p.Documents)
                .FirstOrDefaultAsync(p => p.Id == projectId);

            if (project == null)
            {
                return false;
            }

            // Remove all documents first
            _context.ProjectDocuments.RemoveRange(project.Documents);
            _context.Projects.Remove(project);
            
            await _context.SaveChangesAsync();

            _logger.LogInformation("Deleted project {ProjectId}", projectId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting project {ProjectId}", projectId);
            throw;
        }
    }

    public async Task<ProjectDocument> AddDocumentToProjectAsync(AddDocumentRequest request)
    {
        try
        {
            var project = await _context.Projects.FindAsync(request.ProjectId);
            if (project == null)
            {
                throw new InvalidOperationException($"Project {request.ProjectId} not found");
            }

            var document = new ProjectDocument
            {
                Id = Guid.NewGuid().ToString(),
                ProjectId = request.ProjectId,
                DocumentType = request.DocumentType,
                Content = request.Content,
                Version = request.Version,
                Status = DocumentStatus.Draft,
                CreatedAt = DateTime.UtcNow,
                Metadata = request.Metadata ?? new Dictionary<string, object>()
            };

            _context.ProjectDocuments.Add(document);
            
            // Update project status if needed
            if (project.Status == ProjectStatus.Created)
            {
                project.Status = ProjectStatus.InProgress;
                project.UpdatedAt = DateTime.UtcNow;
            }

            await _context.SaveChangesAsync();

            _logger.LogInformation("Added document {DocumentId} of type {DocumentType} to project {ProjectId}", 
                document.Id, document.DocumentType, request.ProjectId);
            
            return document;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding document to project");
            throw;
        }
    }

    public async Task<IEnumerable<ProjectDocument>> GetProjectDocumentsAsync(string projectId)
    {
        try
        {
            return await _context.ProjectDocuments
                .Where(d => d.ProjectId == projectId)
                .OrderByDescending(d => d.CreatedAt)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting project documents");
            throw;
        }
    }
}