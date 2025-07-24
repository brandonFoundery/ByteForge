using ByteForgeFrontend.Models;

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services;

public interface IWorkflowMonitoringService
{
    Task<WorkflowHealthStatus> GetWorkflowHealthAsync();
    Task<List<WorkflowExecution>> GetRecentWorkflowExecutionsAsync(int count = 50);
    Task RecordWorkflowStartAsync(int leadId, string workflowType);
    Task RecordWorkflowCompletionAsync(int leadId, string workflowType, bool successful, TimeSpan duration);
    Task RecordActivityStartAsync(int leadId, string activityName);
    Task RecordActivityCompletionAsync(int leadId, string activityName, bool successful, TimeSpan duration, string? errorMessage = null);
}