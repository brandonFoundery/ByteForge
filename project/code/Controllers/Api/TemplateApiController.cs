using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using ByteForgeFrontend.Models.Api;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.Templates;

using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[Authorize]
[ApiController]
[Route("api/templates")]
public class TemplateApiController : ControllerBase
{
    private readonly ITemplateManagementService _templateManagementService;
    private readonly ITemplateValidationService _templateValidationService;
    private readonly ITemplateGenerator _templateGenerator;
    private readonly ILogger<TemplateApiController> _logger;

    public TemplateApiController(
        ITemplateManagementService templateManagementService,
        ITemplateValidationService templateValidationService,
        ITemplateGenerator templateGenerator,
        ILogger<TemplateApiController> logger)
    {
        _templateManagementService = templateManagementService;
        _templateValidationService = templateValidationService;
        _templateGenerator = templateGenerator;
        _logger = logger;
    }

    [HttpGet]
    public async Task<ActionResult<ApiResponse<IEnumerable<ProjectTemplate>>>> GetAllTemplates()
    {
        try
        {
            var templates = await _templateManagementService.GetAllTemplatesAsync();
            return Ok(new ApiResponse<IEnumerable<ProjectTemplate>>
            {
                Success = true,
                Data = templates
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving templates");
            return StatusCode(500, new ApiResponse<IEnumerable<ProjectTemplate>>
            {
                Success = false,
                Error = "An error occurred while retrieving templates"
            });
        }
    }

    [HttpGet("{templateId}")]
    public async Task<ActionResult<ApiResponse<ProjectTemplate>>> GetTemplate(string templateId)
    {
        try
        {
            var template = await _templateManagementService.GetTemplateAsync(templateId);
            if (template == null)
            {
                return NotFound(new ApiResponse<ProjectTemplate>
                {
                    Success = false,
                    Error = $"Template '{templateId}' not found"
                });
            }

            return Ok(new ApiResponse<ProjectTemplate>
            {
                Success = true,
                Data = template
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = "An error occurred while retrieving the template"
            });
        }
    }

    [HttpGet("category/{category}")]
    public async Task<ActionResult<ApiResponse<IEnumerable<ProjectTemplate>>>> GetTemplatesByCategory(string category)
    {
        try
        {
            var templates = await _templateManagementService.GetTemplatesByCategoryAsync(category);
            return Ok(new ApiResponse<IEnumerable<ProjectTemplate>>
            {
                Success = true,
                Data = templates
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving templates for category {Category}", category);
            return StatusCode(500, new ApiResponse<IEnumerable<ProjectTemplate>>
            {
                Success = false,
                Error = "An error occurred while retrieving templates"
            });
        }
    }

    [HttpPost]
    public async Task<ActionResult<ApiResponse<ProjectTemplate>>> CreateTemplate([FromBody] ProjectTemplate template)
    {
        try
        {
            // Validate template
            var validationResult = await _templateValidationService.ValidateTemplateAsync(template);
            if (!validationResult.IsValid)
            {
                return BadRequest(new ApiResponse<ProjectTemplate>
                {
                    Success = false,
                    Error = string.Join("; ", validationResult.Errors)
                });
            }

            var createdTemplate = await _templateManagementService.CreateTemplateAsync(template);
            return CreatedAtAction(nameof(GetTemplate), new { templateId = createdTemplate.Id }, 
                new ApiResponse<ProjectTemplate>
                {
                    Success = true,
                    Data = createdTemplate
                });
        }
        catch (InvalidOperationException ex)
        {
            return Conflict(new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating template");
            return StatusCode(500, new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = "An error occurred while creating the template"
            });
        }
    }

    [HttpPut("{templateId}")]
    public async Task<ActionResult<ApiResponse<ProjectTemplate>>> UpdateTemplate(string templateId, [FromBody] ProjectTemplate template)
    {
        try
        {
            if (templateId != template.Id)
            {
                return BadRequest(new ApiResponse<ProjectTemplate>
                {
                    Success = false,
                    Error = "Template ID mismatch"
                });
            }

            // Validate template
            var validationResult = await _templateValidationService.ValidateTemplateAsync(template);
            if (!validationResult.IsValid)
            {
                return BadRequest(new ApiResponse<ProjectTemplate>
                {
                    Success = false,
                    Error = string.Join("; ", validationResult.Errors)
                });
            }

            var updatedTemplate = await _templateManagementService.UpdateTemplateAsync(template);
            return Ok(new ApiResponse<ProjectTemplate>
            {
                Success = true,
                Data = updatedTemplate
            });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = "An error occurred while updating the template"
            });
        }
    }

    [HttpDelete("{templateId}")]
    public async Task<ActionResult<ApiResponse<bool>>> DeleteTemplate(string templateId)
    {
        try
        {
            var result = await _templateManagementService.DeleteTemplateAsync(templateId);
            if (!result)
            {
                return NotFound(new ApiResponse<bool>
                {
                    Success = false,
                    Error = $"Template '{templateId}' not found"
                });
            }

            return Ok(new ApiResponse<bool>
            {
                Success = true,
                Data = true
            });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new ApiResponse<bool>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<bool>
            {
                Success = false,
                Error = "An error occurred while deleting the template"
            });
        }
    }

    [HttpPost("{templateId}/clone")]
    public async Task<ActionResult<ApiResponse<ProjectTemplate>>> CloneTemplate(
        string templateId, 
        [FromBody] CloneTemplateRequest request)
    {
        try
        {
            var clonedTemplate = await _templateManagementService.CloneTemplateAsync(
                templateId, 
                request.NewTemplateId, 
                request.NewTemplateName);

            return CreatedAtAction(nameof(GetTemplate), new { templateId = clonedTemplate.Id }, 
                new ApiResponse<ProjectTemplate>
                {
                    Success = true,
                    Data = clonedTemplate
                });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (InvalidOperationException ex)
        {
            return Conflict(new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error cloning template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = "An error occurred while cloning the template"
            });
        }
    }

    [HttpGet("{templateId}/usage")]
    public async Task<ActionResult<ApiResponse<TemplateUsageInfo>>> GetTemplateUsage(string templateId)
    {
        try
        {
            var inUse = await _templateManagementService.IsTemplateInUseAsync(templateId);
            var usageCount = await _templateManagementService.GetTemplateUsageCountAsync(templateId);

            return Ok(new ApiResponse<TemplateUsageInfo>
            {
                Success = true,
                Data = new TemplateUsageInfo
                {
                    TemplateId = templateId,
                    InUse = inUse,
                    UsageCount = usageCount
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking template usage for {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<TemplateUsageInfo>
            {
                Success = false,
                Error = "An error occurred while checking template usage"
            });
        }
    }

    [HttpPost("{templateId}/validate")]
    public async Task<ActionResult<ApiResponse<TemplateValidationResult>>> ValidateTemplate(string templateId)
    {
        try
        {
            var template = await _templateManagementService.GetTemplateAsync(templateId);
            if (template == null)
            {
                return NotFound(new ApiResponse<TemplateValidationResult>
                {
                    Success = false,
                    Error = $"Template '{templateId}' not found"
                });
            }

            var validationResult = await _templateValidationService.ValidateTemplateAsync(template);
            return Ok(new ApiResponse<TemplateValidationResult>
            {
                Success = true,
                Data = validationResult
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<TemplateValidationResult>
            {
                Success = false,
                Error = "An error occurred while validating the template"
            });
        }
    }

    [HttpPost("generate/{templateType}")]
    public async Task<ActionResult<ApiResponse<TemplateGenerationResult>>> GenerateTemplate(
        string templateType,
        [FromBody] TemplateGenerationOptions options)
    {
        try
        {
            TemplateGenerationResult result;
            var outputPath = Path.Combine(Path.GetTempPath(), "ByteForge", "Templates", Guid.NewGuid().ToString());

            switch (templateType.ToLower())
            {
                case "crm":
                    result = await _templateGenerator.GenerateCRMTemplateAsync(outputPath, options);
                    break;
                case "ecommerce":
                case "e-commerce":
                    result = await _templateGenerator.GenerateEcommerceTemplateAsync(outputPath, options);
                    break;
                default:
                    return BadRequest(new ApiResponse<TemplateGenerationResult>
                    {
                        Success = false,
                        Error = $"Unknown template type: {templateType}"
                    });
            }

            if (!result.Success)
            {
                return BadRequest(new ApiResponse<TemplateGenerationResult>
                {
                    Success = false,
                    Error = string.Join("; ", result.Errors)
                });
            }

            result.Metadata["outputPath"] = outputPath;
            return Ok(new ApiResponse<TemplateGenerationResult>
            {
                Success = true,
                Data = result
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating {TemplateType} template", templateType);
            return StatusCode(500, new ApiResponse<TemplateGenerationResult>
            {
                Success = false,
                Error = "An error occurred while generating the template"
            });
        }
    }

    [HttpGet("{templateId}/export")]
    public async Task<IActionResult> ExportTemplate(string templateId, [FromQuery] string format = "json")
    {
        try
        {
            var stream = await _templateManagementService.ExportTemplateAsync(templateId, format);
            var fileName = $"{templateId}.{format}";
            
            return File(stream, "application/octet-stream", fileName);
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new ApiResponse<object>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (NotSupportedException ex)
        {
            return BadRequest(new ApiResponse<object>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error exporting template {TemplateId}", templateId);
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Error = "An error occurred while exporting the template"
            });
        }
    }

    [HttpPost("import")]
    public async Task<ActionResult<ApiResponse<ProjectTemplate>>> ImportTemplate(IFormFile file, [FromQuery] string format = "json")
    {
        try
        {
            if (file == null || file.Length == 0)
            {
                return BadRequest(new ApiResponse<ProjectTemplate>
                {
                    Success = false,
                    Error = "No file uploaded"
                });
            }

            using var stream = file.OpenReadStream();
            var template = await _templateManagementService.ImportTemplateAsync(stream, format);

            return CreatedAtAction(nameof(GetTemplate), new { templateId = template.Id }, 
                new ApiResponse<ProjectTemplate>
                {
                    Success = true,
                    Data = template
                });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error importing template");
            return StatusCode(500, new ApiResponse<ProjectTemplate>
            {
                Success = false,
                Error = "An error occurred while importing the template"
            });
        }
    }

    [HttpGet("search")]
    public async Task<ActionResult<Models.Api.ApiResponse<IEnumerable<ProjectTemplate>>>> SearchTemplates(
        [FromQuery] string? q,
        [FromQuery] string? category,
        [FromQuery] TemplateSortBy sortBy = TemplateSortBy.Name)
    {
        try
        {
            var options = new TemplateSearchOptions
            {
                Category = category,
                SortBy = sortBy
            };

            var templates = await _templateManagementService.SearchTemplatesAsync(q ?? "", options);
            return Ok(new ApiResponse<IEnumerable<ProjectTemplate>>
            {
                Success = true,
                Data = templates
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching templates");
            return StatusCode(500, new ApiResponse<IEnumerable<ProjectTemplate>>
            {
                Success = false,
                Error = "An error occurred while searching templates"
            });
        }
    }

    [HttpGet("categories")]
    public async Task<ActionResult<Models.Api.ApiResponse<IEnumerable<string>>>> GetValidCategories()
    {
        try
        {
            var categories = await _templateValidationService.GetValidCategoriesAsync();
            return Ok(new ApiResponse<IEnumerable<string>>
            {
                Success = true,
                Data = categories
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving template categories");
            return StatusCode(500, new ApiResponse<IEnumerable<string>>
            {
                Success = false,
                Error = "An error occurred while retrieving categories"
            });
        }
    }

    [HttpGet("document-types")]
    public async Task<ActionResult<Models.Api.ApiResponse<IEnumerable<string>>>> GetValidDocumentTypes()
    {
        try
        {
            var documentTypes = await _templateValidationService.GetValidDocumentTypesAsync();
            return Ok(new ApiResponse<IEnumerable<string>>
            {
                Success = true,
                Data = documentTypes
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving document types");
            return StatusCode(500, new ApiResponse<IEnumerable<string>>
            {
                Success = false,
                Error = "An error occurred while retrieving document types"
            });
        }
    }
}

public class CloneTemplateRequest
{
    public string NewTemplateId { get; set; } = string.Empty;
    public string NewTemplateName { get; set; } = string.Empty;
}

public class TemplateUsageInfo
{
    public string TemplateId { get; set; } = string.Empty;
    public bool InUse { get; set; }
    public int UsageCount { get; set; }
}