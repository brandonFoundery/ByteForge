using Microsoft.AspNetCore.Mvc;
using ByteForgeFrontend.Services;
using ByteForgeFrontend.Models;

using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Controllers.Api;

[ApiController]
[Route("api/v1/jobscheduling")]
public class JobSchedulingApiController : ControllerBase
{
    private readonly IJobSchedulingService _jobSchedulingService;
    private readonly ILogger<JobSchedulingApiController> _logger;

    public JobSchedulingApiController(
        IJobSchedulingService jobSchedulingService,
        ILogger<JobSchedulingApiController> logger)
    {
        _jobSchedulingService = jobSchedulingService;
        _logger = logger;
    }

    /// <summary>
    /// Get all job schedules
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<JobScheduleViewModel>>> GetJobSchedules()
    {
        try
        {
            _logger.LogInformation("JobSchedulingApiController: Getting all job schedules");
            var schedules = await _jobSchedulingService.GetJobSchedulesAsync();
            _logger.LogInformation("JobSchedulingApiController: Found {Count} job schedules", schedules.Count);
            return Ok(schedules);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get job schedules");
            return StatusCode(500, new { error = "Failed to retrieve job schedules", message = ex.Message });
        }
    }

    /// <summary>
    /// Get specific job schedule by name
    /// </summary>
    [HttpGet("{jobName}")]
    public async Task<ActionResult<JobScheduleViewModel>> GetJobSchedule(string jobName)
    {
        try
        {
            _logger.LogDebug("Getting job schedule for {JobName}", jobName);
            var schedule = await _jobSchedulingService.GetJobScheduleAsync(jobName);
            
            if (schedule == null)
            {
                return NotFound(new { error = "Job not found", jobName });
            }

            return Ok(schedule);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get job schedule for {JobName}", jobName);
            return StatusCode(500, new { error = "Failed to retrieve job schedule", message = ex.Message });
        }
    }

    /// <summary>
    /// Update job schedule
    /// </summary>
    [HttpPut("{jobName}")]
    public async Task<IActionResult> UpdateJobSchedule(string jobName, [FromBody] JobScheduleUpdateRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.CronExpression))
            {
                return BadRequest(new { error = "CronExpression is required" });
            }

            _logger.LogInformation("Updating job schedule for {JobName} to {CronExpression}", jobName, request.CronExpression);

            var updateModel = new JobScheduleUpdateModel
            {
                JobName = jobName,
                CronExpression = request.CronExpression,
                IsEnabled = request.IsEnabled,
                Notes = request.Notes
            };

            await _jobSchedulingService.UpdateJobScheduleAsync(updateModel, request.ModifiedBy ?? "API");

            return Ok(new { message = "Job schedule updated successfully", jobName });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update job schedule for {JobName}", jobName);
            return StatusCode(500, new { error = "Failed to update job schedule", message = ex.Message });
        }
    }

    /// <summary>
    /// Enable or disable a job
    /// </summary>
    [HttpPatch("{jobName}/enabled")]
    public async Task<IActionResult> SetJobEnabled(string jobName, [FromBody] SetJobEnabledRequest request)
    {
        try
        {
            _logger.LogInformation("{Action} job {JobName}", request.Enabled ? "Enabling" : "Disabling", jobName);

            await _jobSchedulingService.EnableJobAsync(jobName, request.Enabled, request.ModifiedBy ?? "API");

            return Ok(new { 
                message = $"Job {(request.Enabled ? "enabled" : "disabled")} successfully", 
                jobName,
                enabled = request.Enabled 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to {Action} job {JobName}", request.Enabled ? "enable" : "disable", jobName);
            return StatusCode(500, new { error = $"Failed to {(request.Enabled ? "enable" : "disable")} job", message = ex.Message });
        }
    }

    /// <summary>
    /// Get friendly description for a cron expression
    /// </summary>
    [HttpGet("cron/{expression}/description")]
    public IActionResult GetCronDescription(string expression)
    {
        try
        {
            var description = _jobSchedulingService.GetFriendlyScheduleDescription(expression);
            return Ok(new { expression, description });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get cron description for {Expression}", expression);
            return StatusCode(500, new { error = "Failed to get cron description", message = ex.Message });
        }
    }

    /// <summary>
    /// Get available preset frequencies
    /// </summary>
    [HttpGet("presets")]
    public IActionResult GetPresetFrequencies()
    {
        _logger.LogInformation("JobSchedulingApiController: Getting preset frequencies");
        var presets = new
        {
            testing = new[]
            {
                new { label = "Every 5 seconds", cron = "*/5 * * * * *", category = "Testing" },
                new { label = "Every 10 seconds", cron = "*/10 * * * * *", category = "Testing" },
                new { label = "Every 15 seconds", cron = "*/15 * * * * *", category = "Testing" },
                new { label = "Every 30 seconds", cron = "*/30 * * * * *", category = "Testing" }
            },
            minutes = new[]
            {
                new { label = "Every minute", cron = "0 * * * *", category = "Minutes" },
                new { label = "Every 2 minutes", cron = "*/2 * * * *", category = "Minutes" },
                new { label = "Every 5 minutes", cron = "0 */5 * * *", category = "Minutes" },
                new { label = "Every 10 minutes", cron = "0 */10 * * *", category = "Minutes" },
                new { label = "Every 15 minutes", cron = "0 */15 * * *", category = "Minutes" },
                new { label = "Every 30 minutes", cron = "0 */30 * * *", category = "Minutes" }
            },
            hours = new[]
            {
                new { label = "Every hour", cron = "0 0 * * *", category = "Hours" },
                new { label = "Every 2 hours", cron = "0 */2 * * *", category = "Hours" },
                new { label = "Every 3 hours", cron = "0 */3 * * *", category = "Hours" },
                new { label = "Every 4 hours", cron = "0 */4 * * *", category = "Hours" },
                new { label = "Every 6 hours", cron = "0 */6 * * *", category = "Hours" },
                new { label = "Every 8 hours", cron = "0 */8 * * *", category = "Hours" },
                new { label = "Every 12 hours", cron = "0 */12 * * *", category = "Hours" }
            },
            daily = new[]
            {
                new { label = "Daily at midnight", cron = "0 0 0 * *", category = "Daily" },
                new { label = "Daily at noon", cron = "0 0 12 * *", category = "Daily" },
                new { label = "Daily at 6 AM", cron = "0 0 6 * *", category = "Daily" },
                new { label = "Daily at 6 PM", cron = "0 0 18 * *", category = "Daily" }
            },
            weekly = new[]
            {
                new { label = "Weekly (Sundays)", cron = "0 0 0 * * 0", category = "Weekly" },
                new { label = "Weekly (Mondays)", cron = "0 0 0 * * 1", category = "Weekly" },
                new { label = "Weekdays only", cron = "0 0 8 * * 1-5", category = "Weekly" }
            }
        };

        return Ok(presets);
    }
}

/// <summary>
/// Request model for updating job schedules
/// </summary>
public class JobScheduleUpdateRequest
{
    public string CronExpression { get; set; } = string.Empty;
    public bool IsEnabled { get; set; } = true;
    public string? Notes { get; set; }
    public string? ModifiedBy { get; set; }
}

/// <summary>
/// Request model for enabling/disabling jobs
/// </summary>
public class SetJobEnabledRequest
{
    public bool Enabled { get; set; }
    public string? ModifiedBy { get; set; }
}