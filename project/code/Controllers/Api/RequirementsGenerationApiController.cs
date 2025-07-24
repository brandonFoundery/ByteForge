using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.Traceability;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[Authorize]
[ApiController]
[Route("api/projects/{projectId}/requirements")]
public class RequirementsGenerationApiController : ControllerBase
{
    private readonly IRequirementsOrchestrationService _orchestrationService;
    private readonly IRequirementTraceabilityService _traceabilityService;
    private readonly ILogger<RequirementsGenerationApiController> _logger;

    public RequirementsGenerationApiController(
        IRequirementsOrchestrationService orchestrationService,
        IRequirementTraceabilityService traceabilityService,
        ILogger<RequirementsGenerationApiController> logger)
    {
        _orchestrationService = orchestrationService;
        _traceabilityService = traceabilityService;
        _logger = logger;
    }

    [HttpPost("generate")]
    public async Task<IActionResult> GenerateRequirements(Guid projectId, [FromBody] GenerateRequirementsRequest request)
    {
        try
        {
            request.ProjectId = projectId; // Ensure project ID matches route
            var result = await _orchestrationService.GenerateRequirementsAsync(request);
            
            if (result.Success)
            {
                return Ok(new
                {
                    success = true,
                    data = result,
                    message = $"Successfully generated {result.GeneratedDocuments.Count} documents"
                });
            }

            return BadRequest(new
            {
                success = false,
                errors = result.Errors,
                warnings = result.Warnings
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating requirements for project {ProjectId}", projectId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while generating requirements"
            });
        }
    }

    [HttpGet("progress")]
    public async Task<IActionResult> GetGenerationProgress(Guid projectId)
    {
        try
        {
            var progress = await _orchestrationService.GetGenerationProgressAsync(projectId);
            return Ok(new
            {
                success = true,
                data = progress
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting generation progress for project {ProjectId}", projectId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while retrieving progress"
            });
        }
    }

    [HttpGet("traceability/matrix")]
    public async Task<IActionResult> GetTraceabilityMatrix(Guid projectId)
    {
        try
        {
            var result = await _traceabilityService.GenerateTraceabilityMatrixAsync(projectId);
            
            if (result.Success)
            {
                return Ok(new
                {
                    success = true,
                    data = result
                });
            }

            return BadRequest(new
            {
                success = false,
                error = result.Error
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating traceability matrix for project {ProjectId}", projectId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while generating traceability matrix"
            });
        }
    }

    [HttpPost("traceability/impact")]
    public async Task<IActionResult> AnalyzeChangeImpact(Guid projectId, [FromBody] ChangeImpactRequest request)
    {
        try
        {
            request.ProjectId = projectId;
            var result = await _traceabilityService.AnalyzeChangeImpactAsync(request);
            
            if (result.Success)
            {
                return Ok(new
                {
                    success = true,
                    data = result
                });
            }

            return BadRequest(new
            {
                success = false,
                error = result.Error
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing change impact for requirement {RequirementId}", request.ChangedRequirementId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while analyzing change impact"
            });
        }
    }

    [HttpGet("traceability/validate")]
    public async Task<IActionResult> ValidateTraceability(Guid projectId)
    {
        try
        {
            var result = await _traceabilityService.ValidateTraceabilityAsync(projectId);
            
            if (result.Success)
            {
                return Ok(new
                {
                    success = true,
                    data = result
                });
            }

            return BadRequest(new
            {
                success = false,
                error = result.Error
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating traceability for project {ProjectId}", projectId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while validating traceability"
            });
        }
    }

    [HttpGet("traceability/export")]
    public async Task<IActionResult> ExportTraceabilityMatrix(Guid projectId, [FromQuery] ExportFormat format = ExportFormat.CSV)
    {
        try
        {
            var result = await _traceabilityService.ExportTraceabilityMatrixAsync(projectId, format);
            
            if (result.Success)
            {
                var contentType = format switch
                {
                    ExportFormat.CSV => "text/csv",
                    ExportFormat.JSON => "application/json",
                    ExportFormat.HTML => "text/html",
                    ExportFormat.Markdown => "text/markdown",
                    _ => "text/plain"
                };

                return File(
                    System.Text.Encoding.UTF8.GetBytes(result.Content),
                    contentType,
                    result.FileName
                );
            }

            return BadRequest(new
            {
                success = false,
                error = result.Error
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error exporting traceability matrix for project {ProjectId}", projectId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while exporting traceability matrix"
            });
        }
    }

    [HttpGet("traceability/gaps")]
    public async Task<IActionResult> AnalyzeTraceabilityGaps(Guid projectId)
    {
        try
        {
            var result = await _traceabilityService.AnalyzeTraceabilityGapsAsync(projectId);
            
            if (result.Success)
            {
                return Ok(new
                {
                    success = true,
                    data = result
                });
            }

            return BadRequest(new
            {
                success = false,
                error = result.Error
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing traceability gaps for project {ProjectId}", projectId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while analyzing traceability gaps"
            });
        }
    }

    [HttpGet("{requirementId}")]
    public async Task<IActionResult> GetRequirementDetails(Guid projectId, string requirementId)
    {
        try
        {
            var result = await _traceabilityService.GetRequirementDetailsAsync(projectId, requirementId);
            
            if (result.Success)
            {
                return Ok(new
                {
                    success = true,
                    data = result
                });
            }

            return NotFound(new
            {
                success = false,
                error = result.Error ?? $"Requirement {requirementId} not found"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting requirement details for {RequirementId}", requirementId);
            return StatusCode(500, new
            {
                success = false,
                error = "An error occurred while retrieving requirement details"
            });
        }
    }
}