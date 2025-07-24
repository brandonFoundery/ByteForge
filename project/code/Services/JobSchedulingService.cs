using Hangfire;
using Microsoft.EntityFrameworkCore;
using ByteForgeFrontend.Models;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Jobs;

using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services;

public class JobSchedulingService : IJobSchedulingService
{
    private readonly IRecurringJobManager _recurringJobManager;
    private readonly ApplicationDbContext _context;
    private readonly ILogger<JobSchedulingService> _logger;

    public JobSchedulingService(
        IRecurringJobManager recurringJobManager,
        ApplicationDbContext context,
        ILogger<JobSchedulingService> logger)
    {
        _recurringJobManager = recurringJobManager;
        _context = context;
        _logger = logger;
    }

    public void ScheduleRecurringJobs()
    {
        try
        {
            _logger.LogInformation("Scheduling recurring jobs...");

            // TODO: Add ByteForge-specific recurring jobs here
            // Examples:
            // - Document cleanup jobs
            // - Project status monitoring
            // - AI agent maintenance tasks
            // - Cache cleanup
            
            _logger.LogInformation("No recurring jobs configured yet - ready for ByteForge job scheduling");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to schedule recurring jobs");
            throw;
        }
    }

    public async Task<List<JobScheduleViewModel>> GetJobSchedulesAsync()
    {
        try
        {
            var jobs = await _context.JobScheduleSettings
                .OrderBy(j => j.DisplayName)
                .ToListAsync();

            return jobs.Select(j => new JobScheduleViewModel
            {
                JobName = j.JobName,
                DisplayName = j.DisplayName,
                CronExpression = j.CronExpression,
                Description = j.Description,
                IsEnabled = j.IsEnabled,
                FriendlySchedule = GetFriendlyScheduleDescription(j.CronExpression),
                LastModified = j.ModifiedDate,
                ModifiedBy = j.ModifiedBy
            }).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get job schedules");
            throw;
        }
    }

    public async Task<JobScheduleViewModel?> GetJobScheduleAsync(string jobName)
    {
        try
        {
            var job = await _context.JobScheduleSettings
                .FirstOrDefaultAsync(j => j.JobName == jobName);

            if (job == null) return null;

            return new JobScheduleViewModel
            {
                JobName = job.JobName,
                DisplayName = job.DisplayName,
                CronExpression = job.CronExpression,
                Description = job.Description,
                IsEnabled = job.IsEnabled,
                FriendlySchedule = GetFriendlyScheduleDescription(job.CronExpression),
                LastModified = job.ModifiedDate,
                ModifiedBy = job.ModifiedBy
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get job schedule for {JobName}", jobName);
            throw;
        }
    }

    public async Task UpdateJobScheduleAsync(JobScheduleUpdateModel model, string modifiedBy)
    {
        try
        {
            var job = await _context.JobScheduleSettings
                .FirstOrDefaultAsync(j => j.JobName == model.JobName);

            if (job == null)
            {
                _logger.LogWarning("Job {JobName} not found for update", model.JobName);
                return;
            }

            // Update database record
            job.CronExpression = model.CronExpression;
            job.IsEnabled = model.IsEnabled;
            job.Notes = model.Notes;
            job.ModifiedBy = modifiedBy;
            job.ModifiedDate = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            // Update Hangfire schedule
            if (job.IsEnabled)
            {
                await UpdateHangfireJobScheduleAsync(job.JobName, job.CronExpression);
            }
            else
            {
                _recurringJobManager.RemoveIfExists(job.JobName);
            }

            _logger.LogInformation("Updated job schedule for {JobName} to {CronExpression}", 
                job.JobName, job.CronExpression);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update job schedule for {JobName}", model.JobName);
            throw;
        }
    }

    public async Task EnableJobAsync(string jobName, bool enabled, string modifiedBy)
    {
        try
        {
            var job = await _context.JobScheduleSettings
                .FirstOrDefaultAsync(j => j.JobName == jobName);

            if (job == null)
            {
                _logger.LogWarning("Job {JobName} not found for enable/disable", jobName);
                return;
            }

            job.IsEnabled = enabled;
            job.ModifiedBy = modifiedBy;
            job.ModifiedDate = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            if (enabled)
            {
                await UpdateHangfireJobScheduleAsync(job.JobName, job.CronExpression);
            }
            else
            {
                _recurringJobManager.RemoveIfExists(job.JobName);
            }

            _logger.LogInformation("{Action} job {JobName}", enabled ? "Enabled" : "Disabled", jobName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to {Action} job {JobName}", enabled ? "enable" : "disable", jobName);
            throw;
        }
    }

    public async Task InitializeDefaultJobSchedulesAsync()
    {
        try
        {
            _logger.LogInformation("Initializing default job schedules...");

            var defaultJobs = new List<JobScheduleSettings>
            {
                new()
                {
                    JobName = "google-leads",
                    DisplayName = "Google Leads",
                    CronExpression = "*/5 * * * * *",
                    Description = "Generates leads from Google every 5 seconds for testing",
                    IsEnabled = true,
                    ModifiedBy = "System"
                },
                new()
                {
                    JobName = "facebook-leads",
                    DisplayName = "Facebook Leads",
                    CronExpression = "30 */2 * * *",
                    Description = "Generates leads from Facebook every 2 hours",
                    IsEnabled = true,
                    ModifiedBy = "System"
                },
                new()
                {
                    JobName = "yellowpages-leads",
                    DisplayName = "YellowPages Leads",
                    CronExpression = "0 */3 * * *",
                    Description = "Generates leads from YellowPages every 3 hours",
                    IsEnabled = true,
                    ModifiedBy = "System"
                },
                new()
                {
                    JobName = "linkedin-leads",
                    DisplayName = "LinkedIn Leads",
                    CronExpression = "0 */6 * * *",
                    Description = "Generates leads from LinkedIn every 6 hours",
                    IsEnabled = true,
                    ModifiedBy = "System"
                },
                
                // NPPES Jobs
                new()
                {
                    JobName = "nppes-download-full",
                    DisplayName = "NPPES Full Download",
                    CronExpression = "0 0 1 * *",
                    Description = "Downloads full NPPES data file monthly",
                    IsEnabled = false, // Disabled by default due to large file size
                    ModifiedBy = "System"
                },
                new()
                {
                    JobName = "nppes-download-weekly",
                    DisplayName = "NPPES Weekly Download",
                    CronExpression = "0 2 * * 1",
                    Description = "Downloads weekly NPPES incremental data",
                    IsEnabled = false, // Disabled by default
                    ModifiedBy = "System"
                },
                new()
                {
                    JobName = "nppes-etl-process",
                    DisplayName = "NPPES ETL Processing",
                    CronExpression = "0 4 * * *",
                    Description = "Processes NPPES temp data into leads daily",
                    IsEnabled = false, // Disabled by default until configured
                    ModifiedBy = "System"
                },
                new()
                {
                    JobName = "nppes-update-leads",
                    DisplayName = "NPPES Lead Updates",
                    CronExpression = "0 6 * * 1",
                    Description = "Updates existing NPPES leads with fresh data",
                    IsEnabled = false, // Disabled by default
                    ModifiedBy = "System"
                },
                new()
                {
                    JobName = "nppes-cleanup",
                    DisplayName = "NPPES Data Cleanup",
                    CronExpression = "0 3 1 * *",
                    Description = "Cleans up old processed NPPES temp data",
                    IsEnabled = false, // Disabled by default
                    ModifiedBy = "System"
                }
            };

            foreach (var defaultJob in defaultJobs)
            {
                var existingJob = await _context.JobScheduleSettings
                    .FirstOrDefaultAsync(j => j.JobName == defaultJob.JobName);

                if (existingJob == null)
                {
                    _context.JobScheduleSettings.Add(defaultJob);
                    _logger.LogInformation("Added default job schedule for {JobName}", defaultJob.JobName);
                }
            }

            await _context.SaveChangesAsync();
            _logger.LogInformation("Default job schedules initialized successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize default job schedules");
            throw;
        }
    }

    public string GetFriendlyScheduleDescription(string cronExpression)
    {
        return cronExpression switch
        {
            "*/5 * * * * *" => "Every 5 seconds",
            "*/10 * * * * *" => "Every 10 seconds",
            "*/15 * * * * *" => "Every 15 seconds",
            "*/30 * * * * *" => "Every 30 seconds",
            "0 * * * *" => "Every minute",
            "0 */5 * * *" => "Every 5 minutes",
            "0 */10 * * *" => "Every 10 minutes",
            "0 */15 * * *" => "Every 15 minutes",
            "0 */30 * * *" => "Every 30 minutes",
            "0 0 * * *" => "Every hour",
            "30 */2 * * *" => "Every 2 hours (30min offset)",
            "0 */2 * * *" => "Every 2 hours",
            "0 */3 * * *" => "Every 3 hours",
            "0 */4 * * *" => "Every 4 hours",
            "0 */6 * * *" => "Every 6 hours",
            "0 */8 * * *" => "Every 8 hours",
            "0 */12 * * *" => "Every 12 hours",
            "0 0 0 * *" => "Daily at midnight",
            "0 0 12 * *" => "Daily at noon",
            "0 0 0 * * 0" => "Weekly (Sundays)",
            "0 0 0 1 * *" => "Monthly",
            "0 0 1 * *" => "Monthly (1st day at midnight)",
            "0 2 * * 1" => "Weekly (Mondays at 2 AM)",
            "0 4 * * *" => "Daily at 4 AM",
            "0 6 * * 1" => "Weekly (Mondays at 6 AM)",
            "0 3 1 * *" => "Monthly (1st day at 3 AM)",
            _ => $"Custom: {cronExpression}"
        };
    }

    private async Task UpdateHangfireJobScheduleAsync(string jobName, string cronExpression)
    {
        try
        {
            switch (jobName)
            {
                case "google-leads":
                    _recurringJobManager.AddOrUpdate<GoogleLeadJob>(jobName, job => job.Execute(), cronExpression);
                    break;
                case "facebook-leads":
                    _recurringJobManager.AddOrUpdate<FacebookLeadJob>(jobName, job => job.Execute(), cronExpression);
                    break;
                case "yellowpages-leads":
                    _recurringJobManager.AddOrUpdate<YellowPagesLeadJob>(jobName, job => job.Execute(), cronExpression);
                    break;
                case "linkedin-leads":
                    _recurringJobManager.AddOrUpdate<LinkedInLeadJob>(jobName, job => job.Execute(), cronExpression);
                    break;
                    
                // NPPES Jobs
                case "nppes-download-full":
                    _recurringJobManager.AddOrUpdate<NppesDownloadJob>(jobName, job => job.DownloadFullFileAsync(), cronExpression);
                    break;
                case "nppes-download-weekly":
                    _recurringJobManager.AddOrUpdate<NppesDownloadJob>(jobName, job => job.DownloadWeeklyFileAsync(), cronExpression);
                    break;
                case "nppes-etl-process":
                    _recurringJobManager.AddOrUpdate<NppesEtlJob>(jobName, job => job.ProcessAllActiveConfigurationsAsync(), cronExpression);
                    break;
                case "nppes-update-leads":
                    _recurringJobManager.AddOrUpdate<NppesEtlJob>(jobName, job => job.UpdateExistingNppesLeadsAsync(), cronExpression);
                    break;
                case "nppes-cleanup":
                    _recurringJobManager.AddOrUpdate<NppesEtlJob>(jobName, job => job.CleanupProcessedTempDataAsync(30), cronExpression);
                    break;
                    
                default:
                    _logger.LogWarning("Unknown job name for Hangfire update: {JobName}", jobName);
                    break;
            }

            _logger.LogInformation("Updated Hangfire schedule for {JobName} to {CronExpression}", jobName, cronExpression);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update Hangfire schedule for {JobName}", jobName);
            throw;
        }
    }
}