using ByteForgeFrontend.Models;

using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services;

public interface IJobSchedulingService
{
    void ScheduleRecurringJobs();
    Task<List<JobScheduleViewModel>> GetJobSchedulesAsync();
    Task<JobScheduleViewModel?> GetJobScheduleAsync(string jobName);
    Task UpdateJobScheduleAsync(JobScheduleUpdateModel model, string modifiedBy);
    Task EnableJobAsync(string jobName, bool enabled, string modifiedBy);
    Task InitializeDefaultJobSchedulesAsync();
    string GetFriendlyScheduleDescription(string cronExpression);
}