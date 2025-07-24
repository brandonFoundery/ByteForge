using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Models.Api;

using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[ApiController]
[Route("api/infrastructure/llm")]
[Authorize]
public class InfrastructureLLMApiController : ControllerBase
{
    private readonly ILLMService _llmService;
    private readonly ILLMProviderFactory _providerFactory;
    private readonly ILogger<InfrastructureLLMApiController> _logger;

    public InfrastructureLLMApiController(
        ILLMService llmService,
        ILLMProviderFactory providerFactory,
        ILogger<InfrastructureLLMApiController> logger)
    {
        _llmService = llmService;
        _providerFactory = providerFactory;
        _logger = logger;
    }

    [HttpGet("providers")]
    public IActionResult GetAvailableProviders()
    {
        try
        {
            var providers = _providerFactory.GetAvailableProviders();
            return Ok(providers);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting available LLM providers");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to get available providers",
                Error = ex.Message
            });
        }
    }

    [HttpPost("generate")]
    public async Task<IActionResult> GenerateContent([FromBody] LLMGenerationRequest request)
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

            var response = await _llmService.GenerateAsync(request);
            
            return Ok(new ApiResponse<LLMGenerationResponse>
            {
                Success = response.Success,
                Data = response,
                Message = response.Success ? "Content generated successfully" : "Generation failed",
                Error = response.Error
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating content");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to generate content",
                Error = ex.Message
            });
        }
    }

    [HttpPost("generate/batch")]
    public async Task<IActionResult> GenerateBatch([FromBody] List<LLMGenerationRequest> requests)
    {
        try
        {
            if (!ModelState.IsValid || requests == null || !requests.Any())
            {
                return BadRequest(new ApiResponse<object>
                {
                    Success = false,
                    Message = "Invalid request",
                    Error = "Please provide valid generation requests"
                });
            }

            var responses = await _llmService.GenerateBatchAsync(requests);
            
            return Ok(new ApiResponse<IEnumerable<LLMGenerationResponse>>
            {
                Success = true,
                Data = responses,
                Message = "Batch generation completed"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in batch generation");
            return StatusCode(500, new ApiResponse<object>
            {
                Success = false,
                Message = "Failed to process batch generation",
                Error = ex.Message
            });
        }
    }
}