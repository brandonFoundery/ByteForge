using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using ByteForgeFrontend.Services.Infrastructure.DocumentGeneration;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Models.Api;

using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[ApiController]
[Route("api/infrastructure")]
[Authorize]
public class InfrastructureDocumentApiController : ControllerBase
{
    private readonly IDocumentGenerationService _documentGenerationService;
    private readonly IDocumentTemplateService _documentTemplateService;
    private readonly IDocumentValidationService _documentValidationService;
    private readonly IProjectService _projectService;
    private readonly ILogger<InfrastructureDocumentApiController> _logger;

    public InfrastructureDocumentApiController(
        IDocumentGenerationService documentGenerationService,
        IDocumentTemplateService documentTemplateService,
        IDocumentValidationService documentValidationService,
        IProjectService projectService,
        ILogger<InfrastructureDocumentApiController> logger)
    {
        _documentGenerationService = documentGenerationService;
        _documentTemplateService = documentTemplateService;
        _documentValidationService = documentValidationService;
        _projectService = projectService;
        _logger = logger;
    }

    [HttpGet("documents/templates")]
    public IActionResult GetAvailableTemplates()
    {
        try
        {
            var templates = _documentTemplateService.GetAvailableTemplates();
            return Ok(templates);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting document templates");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to get templates",
                Error = ex.Message
            });
        }
    }

    [HttpPost("documents/generate")]
    public async Task<IActionResult> GenerateDocument([FromBody] DocumentGenerationRequest request)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Invalid request",
                    Error = "Please check the request parameters"
                });
            }

            var response = await _documentGenerationService.GenerateDocumentAsync(request);
            
            return Ok(new ApiResponse<DocumentGenerationResponse>
            {
                Success = response.Success,
                Data = response,
                Message = response.Success ? "Document generated successfully" : "Generation failed",
                Error = response.Error
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating document");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to generate document",
                Error = ex.Message
            });
        }
    }

    [HttpPost("documents/validate")]
    public async Task<IActionResult> ValidateDocument([FromBody] DocumentValidationRequest request)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Invalid request",
                    Error = "Please provide document type and content"
                });
            }

            var result = await _documentValidationService.ValidateDocumentAsync(request.DocumentType, request.Content);
            
            return Ok(new ApiResponse<DocumentValidationResult>
            {
                Success = true,
                Data = result,
                Message = result.IsValid ? "Document is valid" : "Document validation failed"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating document");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to validate document",
                Error = ex.Message
            });
        }
    }

    [HttpPost("documents")]
    public async Task<IActionResult> AddDocumentToProject([FromBody] AddDocumentRequest request)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Invalid request",
                    Error = "Please check the request parameters"
                });
            }

            var document = await _projectService.AddDocumentToProjectAsync(request);
            
            return Ok(new ApiResponse<object>
            {
                Success = true,
                Data = document,
                Message = "Document added successfully"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding document to project");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to add document",
                Error = ex.Message
            });
        }
    }
}

public class DocumentValidationRequest
{
    public string DocumentType { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}