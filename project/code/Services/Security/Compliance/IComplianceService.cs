using System;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.Security;

namespace ByteForgeFrontend.Services.Security.Compliance
{
    public interface IComplianceService
    {
        Task<ComplianceValidationResult> ValidateGDPRComplianceAsync(string tenantId, string userId = null);
        
        Task<SOC2ComplianceResult> ValidateSOC2ComplianceAsync(string tenantId);
        
        Task<DataPortabilityResult> HandleDataPortabilityRequestAsync(string tenantId, string userId);
        
        Task<DataErasureResult> HandleDataErasureRequestAsync(string tenantId, string userId);
        
        Task<ComplianceDashboard> GenerateComplianceDashboardAsync(string tenantId);
        
        Task<ComplianceReviewResult> ScheduleComplianceReviewAsync(
            string tenantId,
            ComplianceReviewType reviewType,
            DateTime scheduledDate);
            
        Task<ComplianceExportReport> ExportComplianceReportAsync(
            string tenantId,
            ComplianceReportType reportType,
            int year,
            int? month = null,
            int? quarter = null);
            
        Task<bool> UpdateConsentAsync(
            string tenantId,
            string userId,
            bool dataProcessingConsent,
            bool marketingConsent);
            
        Task<bool> AcceptPrivacyPolicyAsync(string tenantId, string userId, string policyVersion);
    }
}