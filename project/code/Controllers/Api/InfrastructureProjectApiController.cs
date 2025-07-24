using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Models.Api;

using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[ApiController]
[Route("api/infrastructure")]
[Authorize]
public class InfrastructureProjectApiController : ControllerBase
{
    private readonly IProjectService _projectService;
    private readonly IProjectTemplateService _templateService;
    private readonly ILogger<InfrastructureProjectApiController> _logger;

    public InfrastructureProjectApiController(
        IProjectService projectService,
        IProjectTemplateService templateService,
        ILogger<InfrastructureProjectApiController> logger)
    {
        _projectService = projectService;
        _templateService = templateService;
        _logger = logger;
    }

    [HttpPost("projects")]
    public async Task<IActionResult> CreateProject([FromBody] CreateProjectRequest request)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Invalid request",
                    Error = "Please check the project details"
                });
            }

            var project = await _projectService.CreateProjectAsync(request);
            
            return Ok(new ApiResponse<Project>
            {
                Success = true,
                Data = project,
                Message = "Project created successfully"
            });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to create project",
                Error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating project");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to create project",
                Error = ex.Message
            });
        }
    }

    [HttpGet("projects/{projectId}")]
    public async Task<IActionResult> GetProject(Guid projectId)
    {
        try
        {
            var project = await _projectService.GetProjectAsync(projectId.ToString());
            
            if (project == null)
            {
                return NotFound(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Project not found",
                    Error = $"No project found with ID: {projectId}"
                });
            }

            return Ok(new ApiResponse<Project>
            {
                Success = true,
                Data = project,
                Message = "Project retrieved successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting project {ProjectId}", projectId);
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to get project",
                Error = ex.Message
            });
        }
    }

    [HttpGet("projects")]
    public async Task<IActionResult> GetProjects([FromQuery] ProjectStatus? status = null)
    {
        try
        {
            var projects = await _projectService.GetProjectsAsync(status);
            
            return Ok(new ApiResponse<IEnumerable<Project>>
            {
                Success = true,
                Data = projects,
                Message = "Projects retrieved successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting projects");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to get projects",
                Error = ex.Message
            });
        }
    }

    [HttpPut("projects/{projectId}/status")]
    public async Task<IActionResult> UpdateProjectStatus(Guid projectId, [FromBody] UpdateProjectStatusRequest request)
    {
        try
        {
            var project = await _projectService.UpdateProjectStatusAsync(projectId.ToString(), request.Status);
            
            if (project == null)
            {
                return NotFound(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Project not found",
                    Error = $"No project found with ID: {projectId}"
                });
            }

            return Ok(new ApiResponse<Project>
            {
                Success = true,
                Data = project,
                Message = "Project status updated successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating project status");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to update project status",
                Error = ex.Message
            });
        }
    }

    [HttpDelete("projects/{projectId}")]
    public async Task<IActionResult> DeleteProject(Guid projectId)
    {
        try
        {
            var success = await _projectService.DeleteProjectAsync(projectId.ToString());
            
            if (!success)
            {
                return NotFound(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Project not found",
                    Error = $"No project found with ID: {projectId}"
                });
            }

            return Ok(new ApiResponse<object>
            {
                Success = true,
                Message = "Project deleted successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting project");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to delete project",
                Error = ex.Message
            });
        }
    }

    [HttpGet("projects/{projectId}/documents")]
    public async Task<IActionResult> GetProjectDocuments(Guid projectId)
    {
        try
        {
            var documents = await _projectService.GetProjectDocumentsAsync(projectId.ToString());
            
            return Ok(new ApiResponse<IEnumerable<ProjectDocument>>
            {
                Success = true,
                Data = documents,
                Message = "Documents retrieved successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting project documents");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to get project documents",
                Error = ex.Message
            });
        }
    }

    [HttpGet("templates")]
    public async Task<IActionResult> GetTemplates()
    {
        try
        {
            var templates = await _templateService.GetAllTemplatesAsync();
            
            return Ok(new ApiResponse<IEnumerable<ProjectTemplate>>
            {
                Success = true,
                Data = templates,
                Message = "Templates retrieved successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting templates");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to get templates",
                Error = ex.Message
            });
        }
    }

    [HttpGet("templates/{templateId}")]
    public async Task<IActionResult> GetTemplate(string templateId)
    {
        try
        {
            var template = await _templateService.GetTemplateAsync(templateId);
            
            if (template == null)
            {
                return NotFound(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Template not found",
                    Error = $"No template found with ID: {templateId}"
                });
            }

            return Ok(new ApiResponse<ProjectTemplate>
            {
                Success = true,
                Data = template,
                Message = "Template retrieved successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to get template",
                Error = ex.Message
            });
        }
    }

    [HttpPost("templates/{templateId}/validate")]
    public async Task<IActionResult> ValidateTemplate(string templateId)
    {
        try
        {
            var result = await _templateService.ValidateTemplateAsync(templateId);
            
            return Ok(new ApiResponse<TemplateValidationResult>
            {
                Success = result.IsValid,
                Data = result,
                Message = result.IsValid ? "Template is valid" : "Template validation failed"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to validate template",
                Error = ex.Message
            });
        }
    }
}

public class UpdateProjectStatusRequest
{
    public ProjectStatus Status { get; set; }
}