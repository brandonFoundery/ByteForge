# Fix Build Errors for ByteForgeFrontend/project/code/Tests/Integration/E2E/FullWorkflowIntegrationTests.cs

## Instructions

You need to fix the following build errors in the file `ByteForgeFrontend/project/code/Tests/Integration/E2E/FullWorkflowIntegrationTests.cs`. Follow these steps:

1. Read the file to understand the current code
2. Fix each error listed below
3. Run `dotnet build` to verify all errors are fixed
4. If there are still errors, fix them and build again
5. Once the build succeeds with no errors for this file, stop

## Errors to Fix

### Error 1
- **Location**: Line 72, Column 57
- **Error Code**: CS0246
- **Message**: The type or namespace name 'MockLLMProvider' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 2
- **Location**: Line 114, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 3
- **Location**: Line 115, Column 17
- **Error Code**: CS0117
- **Message**: 'Project' does not contain a definition for 'CurrentPhase' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 4
- **Location**: Line 125, Column 52
- **Error Code**: CS1061
- **Message**: 'ITemplateManagementService' does not contain a definition for 'GetTemplatesAsync' and no accessible extension method 'GetTemplatesAsync' accepting a first argument of type 'ITemplateManagementService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 5
- **Location**: Line 129, Column 54
- **Error Code**: CS1061
- **Message**: 'ITemplateManagementService' does not contain a definition for 'ApplyTemplateAsync' and no accessible extension method 'ApplyTemplateAsync' accepting a first argument of type 'ITemplateManagementService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 6
- **Location**: Line 143, Column 60
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'GenerateDocumentAsync' and no accessible extension method 'GenerateDocumentAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 7
- **Location**: Line 157, Column 91
- **Error Code**: CS0234
- **Message**: The type or namespace name 'AuditLogQuery' does not exist in the namespace 'ByteForgeFrontend.Models.Security' (are you missing an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 8
- **Location**: Line 169, Column 65
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'ValidateTraceabilityAsync' and no accessible extension method 'ValidateTraceabilityAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 9
- **Location**: Line 182, Column 49
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentContext' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 10
- **Location**: Line 182, Column 29
- **Error Code**: CS1061
- **Message**: 'IAgent' does not contain a definition for 'InitializeAsync' and no accessible extension method 'InitializeAsync' accepting a first argument of type 'IAgent' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 11
- **Location**: Line 206, Column 36
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'StartAgentMonitoring' and no accessible extension method 'StartAgentMonitoring' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 12
- **Location**: Line 208, Column 68
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 13
- **Location**: Line 221, Column 60
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'GetAgentStatusAsync' and no accessible extension method 'GetAgentStatusAsync' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 14
- **Location**: Line 232, Column 54
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectFilesAsync' and no accessible extension method 'GetProjectFilesAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 15
- **Location**: Line 261, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 16
- **Location**: Line 267, Column 56
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectsByTenantAsync' and no accessible extension method 'GetProjectsByTenantAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 17
- **Location**: Line 287, Column 54
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'ExportProjectAsync' and no accessible extension method 'ExportProjectAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 18
- **Location**: Line 320, Column 34
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 19
- **Location**: Line 323, Column 75
- **Error Code**: CS1503
- **Message**: Argument 1: cannot convert from 'ByteForgeFrontend.Models.ProjectManagement.Project' to 'ByteForgeFrontend.Services.Infrastructure.ProjectManagement.CreateProjectRequest' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 20
- **Location**: Line 332, Column 48
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'GenerateDocumentAsync' and no accessible extension method 'GenerateDocumentAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 21
- **Location**: Line 346, Column 60
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectsByTenantAsync' and no accessible extension method 'GetProjectsByTenantAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 22
- **Location**: Line 358, Column 91
- **Error Code**: CS0234
- **Message**: The type or namespace name 'AuditLogQuery' does not exist in the namespace 'ByteForgeFrontend.Models.Security' (are you missing an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 23
- **Location**: Line 389, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 24
- **Location**: Line 398, Column 47
- **Error Code**: CS1061
- **Message**: 'IAgentRegistry' does not contain a definition for 'GetAgent' and no accessible extension method 'GetAgent' accepting a first argument of type 'IAgentRegistry' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 25
- **Location**: Line 401, Column 62
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 26
- **Location**: Line 413, Column 38
- **Error Code**: CS0117
- **Message**: 'AgentStatus' does not contain a definition for 'Error' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 27
- **Location**: Line 416, Column 61
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'GetAgentStatusAsync' and no accessible extension method 'GetAgentStatusAsync' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 28
- **Location**: Line 420, Column 87
- **Error Code**: CS0234
- **Message**: The type or namespace name 'AuditLogQuery' does not exist in the namespace 'ByteForgeFrontend.Models.Security' (are you missing an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 29
- **Location**: Line 433, Column 67
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 30
- **Location**: Line 458, Column 17
- **Error Code**: CS0117
- **Message**: 'ProjectTemplate' does not contain a definition for 'TenantId' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 31
- **Location**: Line 459, Column 17
- **Error Code**: CS0117
- **Message**: 'ProjectTemplate' does not contain a definition for 'Metadata' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 32
- **Location**: Line 471, Column 40
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Success' and no accessible extension method 'Success' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 33
- **Location**: Line 472, Column 45
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Data' and no accessible extension method 'Data' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 34
- **Location**: Line 480, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 35
- **Location**: Line 487, Column 54
- **Error Code**: CS1061
- **Message**: 'ITemplateManagementService' does not contain a definition for 'ApplyTemplateAsync' and no accessible extension method 'ApplyTemplateAsync' accepting a first argument of type 'ITemplateManagementService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 36
- **Location**: Line 491, Column 111
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Metadata' and no accessible extension method 'Metadata' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 37
- **Location**: Line 491, Column 56
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'GenerateDocumentAsync' and no accessible extension method 'GenerateDocumentAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 38
- **Location**: Line 495, Column 50
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectDocumentAsync' and no accessible extension method 'GetProjectDocumentAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 39
- **Location**: Line 510, Column 44
- **Error Code**: CS1061
- **Message**: 'IAgentRegistry' does not contain a definition for 'GetAgent' and no accessible extension method 'GetAgent' accepting a first argument of type 'IAgentRegistry' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 40
- **Location**: Line 511, Column 64
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 41
- **Location**: Line 517, Column 62
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Metadata' and no accessible extension method 'Metadata' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 42
- **Location**: Line 541, Column 32
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'SubscribeToUpdates' and no accessible extension method 'SubscribeToUpdates' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 43
- **Location**: Line 549, Column 66
- **Error Code**: CS1503
- **Message**: Argument 1: cannot convert from 'System.Guid' to 'string' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 44
- **Location**: Line 550, Column 38
- **Error Code**: CS1501
- **Message**: No overload for method 'UpdateAgentStatusAsync' takes 5 arguments [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 45
- **Location**: Line 551, Column 38
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'UpdateProjectStatusAsync' and no accessible extension method 'UpdateProjectStatusAsync' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 46
- **Location**: Line 561, Column 32
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'UnsubscribeFromUpdates' and no accessible extension method 'UnsubscribeFromUpdates' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 47
- **Location**: Line 72, Column 57
- **Error Code**: CS0246
- **Message**: The type or namespace name 'MockLLMProvider' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 48
- **Location**: Line 114, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 49
- **Location**: Line 115, Column 17
- **Error Code**: CS0117
- **Message**: 'Project' does not contain a definition for 'CurrentPhase' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 50
- **Location**: Line 125, Column 52
- **Error Code**: CS1061
- **Message**: 'ITemplateManagementService' does not contain a definition for 'GetTemplatesAsync' and no accessible extension method 'GetTemplatesAsync' accepting a first argument of type 'ITemplateManagementService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 51
- **Location**: Line 129, Column 54
- **Error Code**: CS1061
- **Message**: 'ITemplateManagementService' does not contain a definition for 'ApplyTemplateAsync' and no accessible extension method 'ApplyTemplateAsync' accepting a first argument of type 'ITemplateManagementService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 52
- **Location**: Line 143, Column 60
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'GenerateDocumentAsync' and no accessible extension method 'GenerateDocumentAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 53
- **Location**: Line 157, Column 91
- **Error Code**: CS0234
- **Message**: The type or namespace name 'AuditLogQuery' does not exist in the namespace 'ByteForgeFrontend.Models.Security' (are you missing an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 54
- **Location**: Line 169, Column 65
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'ValidateTraceabilityAsync' and no accessible extension method 'ValidateTraceabilityAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 55
- **Location**: Line 182, Column 49
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentContext' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 56
- **Location**: Line 182, Column 29
- **Error Code**: CS1061
- **Message**: 'IAgent' does not contain a definition for 'InitializeAsync' and no accessible extension method 'InitializeAsync' accepting a first argument of type 'IAgent' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 57
- **Location**: Line 206, Column 36
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'StartAgentMonitoring' and no accessible extension method 'StartAgentMonitoring' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 58
- **Location**: Line 208, Column 68
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 59
- **Location**: Line 221, Column 60
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'GetAgentStatusAsync' and no accessible extension method 'GetAgentStatusAsync' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 60
- **Location**: Line 232, Column 54
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectFilesAsync' and no accessible extension method 'GetProjectFilesAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 61
- **Location**: Line 261, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 62
- **Location**: Line 267, Column 56
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectsByTenantAsync' and no accessible extension method 'GetProjectsByTenantAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 63
- **Location**: Line 287, Column 54
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'ExportProjectAsync' and no accessible extension method 'ExportProjectAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 64
- **Location**: Line 320, Column 34
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 65
- **Location**: Line 323, Column 75
- **Error Code**: CS1503
- **Message**: Argument 1: cannot convert from 'ByteForgeFrontend.Models.ProjectManagement.Project' to 'ByteForgeFrontend.Services.Infrastructure.ProjectManagement.CreateProjectRequest' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 66
- **Location**: Line 332, Column 48
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'GenerateDocumentAsync' and no accessible extension method 'GenerateDocumentAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 67
- **Location**: Line 346, Column 60
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectsByTenantAsync' and no accessible extension method 'GetProjectsByTenantAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 68
- **Location**: Line 358, Column 91
- **Error Code**: CS0234
- **Message**: The type or namespace name 'AuditLogQuery' does not exist in the namespace 'ByteForgeFrontend.Models.Security' (are you missing an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 69
- **Location**: Line 389, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 70
- **Location**: Line 398, Column 47
- **Error Code**: CS1061
- **Message**: 'IAgentRegistry' does not contain a definition for 'GetAgent' and no accessible extension method 'GetAgent' accepting a first argument of type 'IAgentRegistry' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 71
- **Location**: Line 401, Column 62
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 72
- **Location**: Line 413, Column 38
- **Error Code**: CS0117
- **Message**: 'AgentStatus' does not contain a definition for 'Error' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 73
- **Location**: Line 416, Column 61
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'GetAgentStatusAsync' and no accessible extension method 'GetAgentStatusAsync' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 74
- **Location**: Line 420, Column 87
- **Error Code**: CS0234
- **Message**: The type or namespace name 'AuditLogQuery' does not exist in the namespace 'ByteForgeFrontend.Models.Security' (are you missing an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 75
- **Location**: Line 433, Column 67
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 76
- **Location**: Line 458, Column 17
- **Error Code**: CS0117
- **Message**: 'ProjectTemplate' does not contain a definition for 'TenantId' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 77
- **Location**: Line 459, Column 17
- **Error Code**: CS0117
- **Message**: 'ProjectTemplate' does not contain a definition for 'Metadata' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 78
- **Location**: Line 471, Column 40
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Success' and no accessible extension method 'Success' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 79
- **Location**: Line 472, Column 45
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Data' and no accessible extension method 'Data' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 80
- **Location**: Line 480, Column 26
- **Error Code**: CS0029
- **Message**: Cannot implicitly convert type 'string' to 'ByteForgeFrontend.Models.ProjectManagement.ProjectStatus' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 81
- **Location**: Line 487, Column 54
- **Error Code**: CS1061
- **Message**: 'ITemplateManagementService' does not contain a definition for 'ApplyTemplateAsync' and no accessible extension method 'ApplyTemplateAsync' accepting a first argument of type 'ITemplateManagementService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 82
- **Location**: Line 491, Column 111
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Metadata' and no accessible extension method 'Metadata' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 83
- **Location**: Line 491, Column 56
- **Error Code**: CS1061
- **Message**: 'IRequirementsOrchestrationService' does not contain a definition for 'GenerateDocumentAsync' and no accessible extension method 'GenerateDocumentAsync' accepting a first argument of type 'IRequirementsOrchestrationService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 84
- **Location**: Line 495, Column 50
- **Error Code**: CS1061
- **Message**: 'IProjectService' does not contain a definition for 'GetProjectDocumentAsync' and no accessible extension method 'GetProjectDocumentAsync' accepting a first argument of type 'IProjectService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 85
- **Location**: Line 510, Column 44
- **Error Code**: CS1061
- **Message**: 'IAgentRegistry' does not contain a definition for 'GetAgent' and no accessible extension method 'GetAgent' accepting a first argument of type 'IAgentRegistry' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 86
- **Location**: Line 511, Column 64
- **Error Code**: CS0246
- **Message**: The type or namespace name 'AgentTaskRequest' could not be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 87
- **Location**: Line 517, Column 62
- **Error Code**: CS1061
- **Message**: 'ProjectTemplate' does not contain a definition for 'Metadata' and no accessible extension method 'Metadata' accepting a first argument of type 'ProjectTemplate' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 88
- **Location**: Line 541, Column 32
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'SubscribeToUpdates' and no accessible extension method 'SubscribeToUpdates' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 89
- **Location**: Line 549, Column 66
- **Error Code**: CS1503
- **Message**: Argument 1: cannot convert from 'System.Guid' to 'string' [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 90
- **Location**: Line 550, Column 38
- **Error Code**: CS1501
- **Message**: No overload for method 'UpdateAgentStatusAsync' takes 5 arguments [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 91
- **Location**: Line 551, Column 38
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'UpdateProjectStatusAsync' and no accessible extension method 'UpdateProjectStatusAsync' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

### Error 92
- **Location**: Line 561, Column 32
- **Error Code**: CS1061
- **Message**: 'IMonitoringService' does not contain a definition for 'UnsubscribeFromUpdates' and no accessible extension method 'UnsubscribeFromUpdates' accepting a first argument of type 'IMonitoringService' could be found (are you missing a using directive or an assembly reference?) [D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Tests\ByteForgeFrontend.Tests.csproj]

## Important Notes

- Focus ONLY on fixing the errors listed above
- Do not make unnecessary changes to the code
- Preserve the existing functionality while fixing the errors
- Common fixes include:
  - Adding missing using statements
  - Fixing type mismatches
  - Adding null checks for nullable reference types
  - Correcting method signatures
  - Fixing namespace issues

After fixing all errors, run the build command to verify:
```bash
cd /mnt/d/Repository/@Founder-y/ByteForgeFrontend/project/code && cmd.exe /c "dotnet build"
```

Only stop when the build succeeds with no errors for this specific file.
