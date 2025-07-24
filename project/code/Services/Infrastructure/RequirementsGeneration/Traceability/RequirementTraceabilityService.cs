using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.RegularExpressions;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.Traceability;

public class RequirementTraceabilityService : IRequirementTraceabilityService
{
    private readonly IProjectService _projectService;
    private readonly ILogger<RequirementTraceabilityService> _logger;

    // Regex patterns for requirement IDs and links
    private static readonly Regex RequirementIdPattern = new(@"\b(BR|PR|FR|TR|NFR)\d{3}\b", RegexOptions.Compiled);
    private static readonly Regex LinkPattern = new(@"\[(?:Implements|Traces to|Related to|Satisfies|Fulfills):?\s*([^]]+)\]", RegexOptions.Compiled | RegexOptions.IgnoreCase);
    private static readonly Regex InlineLinkPattern = new(@"\b(BR|PR|FR|TR|NFR)\d{3}(?:\s*,\s*(BR|PR|FR|TR|NFR)\d{3})*\b", RegexOptions.Compiled);

    // Document type hierarchy
    private static readonly Dictionary<string, int> DocumentHierarchy = new()
    {
        ["BRD"] = 0,
        ["PRD"] = 1,
        ["FRD"] = 2,
        ["TRD"] = 3,
        ["NFRD"] = 2 // Non-functional requirements at same level as FRD
    };

    public RequirementTraceabilityService(
        IProjectService projectService,
        ILogger<RequirementTraceabilityService> logger)
    {
        _projectService = projectService;
        _logger = logger;
    }

    public async Task<TraceabilityMatrixResponse> GenerateTraceabilityMatrixAsync(Guid projectId, CancellationToken cancellationToken = default)
    {
        var response = new TraceabilityMatrixResponse();

        try
        {
            var documents = await _projectService.GetProjectDocumentsAsync(projectId.ToString());
            var matrix = new RequirementTraceabilityMatrix();

            // First pass: Extract all requirements
            var requirementsByType = new Dictionary<string, List<RequirementData>>();
            
            foreach (var doc in documents)
            {
                var requirements = ExtractRequirements(doc);
                requirementsByType[doc.DocumentType] = requirements;

                foreach (var req in requirements)
                {
                    matrix.AddRequirement(req.Id, doc.DocumentType, req.Description);
                }
            }

            // Second pass: Extract links
            foreach (var doc in documents)
            {
                var links = ExtractLinks(doc);
                foreach (var link in links)
                {
                    matrix.AddLink(link.Source, link.Target, link.LinkType);
                }
            }

            // Calculate statistics
            response.Statistics["TotalRequirements"] = requirementsByType.Values.Sum(list => list.Count);
            response.Statistics["TotalLinks"] = CountAllLinks(matrix);
            response.Statistics["OrphanedRequirements"] = CountOrphanedRequirements(matrix);
            
            foreach (var kvp in requirementsByType)
            {
                response.Statistics[$"{kvp.Key}Count"] = kvp.Value.Count;
            }

            response.Success = true;
            response.Matrix = matrix;

            _logger.LogInformation("Generated traceability matrix for project {ProjectId} with {TotalReqs} requirements and {TotalLinks} links",
                projectId, response.Statistics["TotalRequirements"], response.Statistics["TotalLinks"]);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating traceability matrix for project {ProjectId}", projectId);
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    public async Task<ChangeImpactResponse> AnalyzeChangeImpactAsync(ChangeImpactRequest request, CancellationToken cancellationToken = default)
    {
        var response = new ChangeImpactResponse
        {
            SourceRequirement = request.ChangedRequirementId
        };

        try
        {
            var matrixResponse = await GenerateTraceabilityMatrixAsync(request.ProjectId, cancellationToken);
            if (!matrixResponse.Success)
            {
                response.Success = false;
                response.Error = matrixResponse.Error;
                return response;
            }

            var matrix = matrixResponse.Matrix;
            var visited = new HashSet<string>();

            // Find directly affected requirements (immediate downstream)
            var directlyAffected = matrix.GetLinksForRequirement(request.ChangedRequirementId).ToList();
            response.DirectlyAffectedRequirements.AddRange(directlyAffected);

            // Find indirectly affected requirements (transitive closure)
            var queue = new Queue<string>(directlyAffected);
            visited.Add(request.ChangedRequirementId);

            while (queue.Count > 0)
            {
                var current = queue.Dequeue();
                if (visited.Contains(current)) continue;
                visited.Add(current);

                var downstream = matrix.GetLinksForRequirement(current);
                foreach (var req in downstream)
                {
                    if (!visited.Contains(req))
                    {
                        response.IndirectlyAffectedRequirements.Add(req);
                        queue.Enqueue(req);
                    }
                }
            }

            // Determine severity based on impact scope and requirement type
            response.Severity = DetermineImpactSeverity(
                request.ChangedRequirementId,
                response.DirectlyAffectedRequirements.Count,
                response.IndirectlyAffectedRequirements.Count,
                matrix);

            // Identify affected documents
            var affectedDocs = new HashSet<string>();
            foreach (var req in visited)
            {
                var reqInfo = matrix.GetRequirement(req);
                if (reqInfo != null)
                {
                    affectedDocs.Add(reqInfo.Type);
                }
            }
            response.AffectedDocuments = affectedDocs.ToList();

            response.Success = true;

            _logger.LogInformation("Change impact analysis for {RequirementId}: {DirectCount} direct, {IndirectCount} indirect impacts",
                request.ChangedRequirementId, response.DirectlyAffectedRequirements.Count, response.IndirectlyAffectedRequirements.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing change impact for requirement {RequirementId}", request.ChangedRequirementId);
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    public async Task<TraceabilityValidationResponse> ValidateTraceabilityAsync(Guid projectId, CancellationToken cancellationToken = default)
    {
        var response = new TraceabilityValidationResponse { Success = true, IsValid = true };

        try
        {
            var matrixResponse = await GenerateTraceabilityMatrixAsync(projectId, cancellationToken);
            if (!matrixResponse.Success)
            {
                response.Success = false;
                response.Error = matrixResponse.Error;
                return response;
            }

            var matrix = matrixResponse.Matrix;
            var allRequirements = matrix.GetAllRequirements().ToList();

            // Check for orphaned requirements (no upstream links except for BRD)
            foreach (var req in allRequirements.Where(r => r.Type != "BRD"))
            {
                var sources = matrix.GetSourceRequirements(req.Id);
                if (!sources.Any())
                {
                    response.OrphanedRequirements.Add(req.Id);
                    response.ValidationMessages.Add($"{req.Id} has no upstream traceability");
                    response.IsValid = false;
                }
            }

            // Check for unimplemented requirements (no downstream links except for TRD)
            foreach (var req in allRequirements.Where(r => r.Type != "TRD" && r.Type != "NFRD"))
            {
                var targets = matrix.GetLinksForRequirement(req.Id);
                if (!targets.Any())
                {
                    response.UnimplementedRequirements.Add(req.Id);
                    response.ValidationMessages.Add($"{req.Id} has no downstream implementation");
                    response.IsValid = false;
                }
            }

            // Check for broken links
            var documents = await _projectService.GetProjectDocumentsAsync(projectId.ToString());
            foreach (var doc in documents)
            {
                var brokenLinks = FindBrokenLinks(doc, allRequirements.Select(r => r.Id).ToHashSet());
                response.BrokenLinks.AddRange(brokenLinks);
                if (brokenLinks.Any())
                {
                    response.IsValid = false;
                }
            }

            _logger.LogInformation("Traceability validation for project {ProjectId}: Valid={IsValid}, Orphaned={OrphanedCount}, Unimplemented={UnimplementedCount}",
                projectId, response.IsValid, response.OrphanedRequirements.Count, response.UnimplementedRequirements.Count);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating traceability for project {ProjectId}", projectId);
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    public async Task<RequirementDetailsResponse> GetRequirementDetailsAsync(Guid projectId, string requirementId, CancellationToken cancellationToken = default)
    {
        var response = new RequirementDetailsResponse { RequirementId = requirementId };

        try
        {
            var documents = await _projectService.GetProjectDocumentsAsync(projectId.ToString());
            
            // Find the requirement in documents
            foreach (var doc in documents)
            {
                var requirements = ExtractRequirements(doc);
                var requirement = requirements.FirstOrDefault(r => r.Id == requirementId);
                
                if (requirement != null)
                {
                    response.Description = requirement.Description;
                    response.DocumentType = doc.DocumentType;
                    response.Version = doc.Version;
                    response.CreatedAt = doc.CreatedAt;
                    
                    // Get traceability info
                    var matrixResponse = await GenerateTraceabilityMatrixAsync(projectId, cancellationToken);
                    if (matrixResponse.Success)
                    {
                        response.ImplementedBy = matrixResponse.Matrix.GetLinksForRequirement(requirementId).ToList();
                        response.Implements = matrixResponse.Matrix.GetSourceRequirements(requirementId).ToList();
                    }
                    
                    response.Success = true;
                    return response;
                }
            }

            response.Success = false;
            response.Error = $"Requirement {requirementId} not found in project";
            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting requirement details for {RequirementId}", requirementId);
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    public async Task<TraceabilityExportResponse> ExportTraceabilityMatrixAsync(Guid projectId, ExportFormat format, CancellationToken cancellationToken = default)
    {
        var response = new TraceabilityExportResponse
        {
            Format = format,
            FileName = $"RTM_{projectId}_{DateTime.UtcNow:yyyyMMdd_HHmmss}.{format.ToString().ToLower()}"
        };

        try
        {
            var matrixResponse = await GenerateTraceabilityMatrixAsync(projectId, cancellationToken);
            if (!matrixResponse.Success)
            {
                response.Success = false;
                response.Error = matrixResponse.Error;
                return response;
            }

            var matrix = matrixResponse.Matrix;
            
            response.Content = format switch
            {
                ExportFormat.CSV => ExportToCSV(matrix),
                ExportFormat.JSON => ExportToJSON(matrix),
                ExportFormat.HTML => ExportToHTML(matrix),
                ExportFormat.Markdown => ExportToMarkdown(matrix),
                _ => throw new NotSupportedException($"Export format {format} not supported")
            };

            response.Success = true;
            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error exporting traceability matrix for project {ProjectId}", projectId);
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    public async Task<TraceabilityGapAnalysisResponse> AnalyzeTraceabilityGapsAsync(Guid projectId, CancellationToken cancellationToken = default)
    {
        var response = new TraceabilityGapAnalysisResponse();

        try
        {
            var matrixResponse = await GenerateTraceabilityMatrixAsync(projectId, cancellationToken);
            if (!matrixResponse.Success)
            {
                response.Success = false;
                response.Error = matrixResponse.Error;
                return response;
            }

            var matrix = matrixResponse.Matrix;
            var allRequirements = matrix.GetAllRequirements().ToList();
            var requirementsByType = allRequirements.GroupBy(r => r.Type).ToDictionary(g => g.Key, g => g.ToList());

            // Find requirements without upstream links (except BRD)
            foreach (var req in allRequirements.Where(r => r.Type != "BRD"))
            {
                if (!matrix.GetSourceRequirements(req.Id).Any())
                {
                    response.RequirementsWithoutUpstreamLinks.Add(req.Id);
                }
            }

            // Find requirements without downstream links (except TRD/NFRD)
            foreach (var req in allRequirements.Where(r => r.Type != "TRD" && r.Type != "NFRD"))
            {
                if (!matrix.GetLinksForRequirement(req.Id).Any())
                {
                    response.RequirementsWithoutDownstreamLinks.Add(req.Id);
                }
            }

            // Calculate coverage percentages
            var totalRequiringUpstream = allRequirements.Count(r => r.Type != "BRD");
            var totalWithUpstream = totalRequiringUpstream - response.RequirementsWithoutUpstreamLinks.Count;
            response.UpstreamCoveragePercentage = totalRequiringUpstream > 0 
                ? (double)totalWithUpstream / totalRequiringUpstream * 100 
                : 100;

            var totalRequiringDownstream = allRequirements.Count(r => r.Type != "TRD" && r.Type != "NFRD");
            var totalWithDownstream = totalRequiringDownstream - response.RequirementsWithoutDownstreamLinks.Count;
            response.DownstreamCoveragePercentage = totalRequiringDownstream > 0 
                ? (double)totalWithDownstream / totalRequiringDownstream * 100 
                : 100;

            // Group gaps by document type
            response.GapsByDocumentType = response.RequirementsWithoutUpstreamLinks
                .Concat(response.RequirementsWithoutDownstreamLinks)
                .Distinct()
                .GroupBy(reqId => allRequirements.First(r => r.Id == reqId).Type)
                .ToDictionary(g => g.Key, g => g.ToList());

            response.Success = true;

            _logger.LogInformation("Traceability gap analysis for project {ProjectId}: Upstream coverage={UpstreamCoverage:F1}%, Downstream coverage={DownstreamCoverage:F1}%",
                projectId, response.UpstreamCoveragePercentage, response.DownstreamCoveragePercentage);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing traceability gaps for project {ProjectId}", projectId);
            response.Success = false;
            response.Error = ex.Message;
            return response;
        }
    }

    // Helper methods
    private List<RequirementData> ExtractRequirements(ProjectDocument document)
    {
        var requirements = new List<RequirementData>();
        var matches = RequirementIdPattern.Matches(document.Content);

        foreach (Match match in matches)
        {
            var id = match.Value;
            var description = ExtractRequirementDescription(document.Content, match.Index);
            
            requirements.Add(new RequirementData
            {
                Id = id,
                Description = description,
                DocumentType = document.DocumentType
            });
        }

        return requirements.DistinctBy(r => r.Id).ToList();
    }

    private string ExtractRequirementDescription(string content, int idPosition)
    {
        // Look for text after the ID until the next requirement or line break
        var afterId = content.Substring(idPosition);
        var descMatch = Regex.Match(afterId, @"^[A-Z]+\d{3}:?\s*(.+?)(?=\n|$|(?:[A-Z]+\d{3}))", RegexOptions.Singleline);
        
        return descMatch.Success ? descMatch.Groups[1].Value.Trim() : string.Empty;
    }

    private List<RequirementLink> ExtractLinks(ProjectDocument document)
    {
        var links = new List<RequirementLink>();
        var requirementMatches = RequirementIdPattern.Matches(document.Content);

        foreach (Match reqMatch in requirementMatches)
        {
            var sourceId = reqMatch.Value;
            var afterReq = document.Content.Substring(reqMatch.Index);
            var lineEnd = afterReq.IndexOf('\n');
            var reqLine = lineEnd > 0 ? afterReq.Substring(0, lineEnd) : afterReq;

            // Check for explicit link patterns [Implements BR001]
            var linkMatches = LinkPattern.Matches(reqLine);
            foreach (Match linkMatch in linkMatches)
            {
                var targetIds = RequirementIdPattern.Matches(linkMatch.Groups[1].Value);
                foreach (Match targetMatch in targetIds)
                {
                    links.Add(new RequirementLink
                    {
                        Source = sourceId,
                        Target = targetMatch.Value,
                        LinkType = ExtractLinkType(linkMatch.Value)
                    });
                }
            }

            // Check for inline references
            if (!linkMatches.Any())
            {
                var inlineMatches = InlineLinkPattern.Matches(reqLine);
                foreach (Match inlineMatch in inlineMatches.Skip(1)) // Skip the source ID itself
                {
                    links.Add(new RequirementLink
                    {
                        Source = sourceId,
                        Target = inlineMatch.Value,
                        LinkType = "Implements"
                    });
                }
            }
        }

        return links;
    }

    private string ExtractLinkType(string linkText)
    {
        if (linkText.Contains("Implements", StringComparison.OrdinalIgnoreCase))
            return "Implements";
        if (linkText.Contains("Traces to", StringComparison.OrdinalIgnoreCase))
            return "TracesTo";
        if (linkText.Contains("Related to", StringComparison.OrdinalIgnoreCase))
            return "RelatedTo";
        if (linkText.Contains("Satisfies", StringComparison.OrdinalIgnoreCase))
            return "Satisfies";
        if (linkText.Contains("Fulfills", StringComparison.OrdinalIgnoreCase))
            return "Fulfills";
        
        return "Implements"; // Default
    }

    private List<BrokenLink> FindBrokenLinks(ProjectDocument document, HashSet<string> validRequirementIds)
    {
        var brokenLinks = new List<BrokenLink>();
        var links = ExtractLinks(document);

        foreach (var link in links)
        {
            if (!validRequirementIds.Contains(link.Target))
            {
                brokenLinks.Add(new BrokenLink
                {
                    From = link.Source,
                    To = link.Target,
                    Reason = "Target requirement does not exist"
                });
            }
        }

        return brokenLinks;
    }

    private ImpactSeverity DetermineImpactSeverity(string requirementId, int directCount, int indirectCount, RequirementTraceabilityMatrix matrix)
    {
        var requirement = matrix.GetRequirement(requirementId);
        if (requirement == null) return ImpactSeverity.Low;

        // Critical requirements (authentication, security, data integrity)
        var criticalKeywords = new[] { "auth", "security", "encrypt", "password", "access", "permission", "audit" };
        if (criticalKeywords.Any(k => requirement.Description.Contains(k, StringComparison.OrdinalIgnoreCase)))
        {
            return ImpactSeverity.High;
        }

        // Based on impact scope
        var totalImpact = directCount + indirectCount;
        if (totalImpact > 10) return ImpactSeverity.Critical;
        if (totalImpact > 5) return ImpactSeverity.High;
        if (totalImpact > 2) return ImpactSeverity.Medium;
        
        return ImpactSeverity.Low;
    }

    private int CountAllLinks(RequirementTraceabilityMatrix matrix)
    {
        return matrix.GetAllRequirements()
            .Sum(req => matrix.GetLinksForRequirement(req.Id).Count());
    }

    private int CountOrphanedRequirements(RequirementTraceabilityMatrix matrix)
    {
        return matrix.GetAllRequirements()
            .Count(req => req.Type != "BRD" && 
                         !matrix.GetSourceRequirements(req.Id).Any() && 
                         !matrix.GetLinksForRequirement(req.Id).Any());
    }

    private string ExportToCSV(RequirementTraceabilityMatrix matrix)
    {
        var csv = new StringBuilder();
        csv.AppendLine("Source,Target,Link Type");

        foreach (var req in matrix.GetAllRequirements())
        {
            foreach (var target in matrix.GetLinksForRequirement(req.Id))
            {
                csv.AppendLine($"{req.Id},{target},Implements");
            }
        }

        return csv.ToString();
    }

    private string ExportToJSON(RequirementTraceabilityMatrix matrix)
    {
        var data = new
        {
            requirements = matrix.GetAllRequirements().Select(r => new
            {
                id = r.Id,
                type = r.Type,
                description = r.Description,
                implements = matrix.GetSourceRequirements(r.Id).ToList(),
                implementedBy = matrix.GetLinksForRequirement(r.Id).ToList()
            })
        };

        return System.Text.Json.JsonSerializer.Serialize(data, new System.Text.Json.JsonSerializerOptions 
        { 
            WriteIndented = true 
        });
    }

    private string ExportToHTML(RequirementTraceabilityMatrix matrix)
    {
        var html = new StringBuilder();
        html.AppendLine("<!DOCTYPE html>");
        html.AppendLine("<html><head><title>Requirements Traceability Matrix</title>");
        html.AppendLine("<style>table { border-collapse: collapse; } th, td { border: 1px solid black; padding: 8px; }</style>");
        html.AppendLine("</head><body>");
        html.AppendLine("<h1>Requirements Traceability Matrix</h1>");
        html.AppendLine("<table>");
        html.AppendLine("<tr><th>ID</th><th>Type</th><th>Description</th><th>Implements</th><th>Implemented By</th></tr>");

        foreach (var req in matrix.GetAllRequirements().OrderBy(r => r.Type).ThenBy(r => r.Id))
        {
            html.AppendLine("<tr>");
            html.AppendLine($"<td>{req.Id}</td>");
            html.AppendLine($"<td>{req.Type}</td>");
            html.AppendLine($"<td>{req.Description}</td>");
            html.AppendLine($"<td>{string.Join(", ", matrix.GetSourceRequirements(req.Id))}</td>");
            html.AppendLine($"<td>{string.Join(", ", matrix.GetLinksForRequirement(req.Id))}</td>");
            html.AppendLine("</tr>");
        }

        html.AppendLine("</table></body></html>");
        return html.ToString();
    }

    private string ExportToMarkdown(RequirementTraceabilityMatrix matrix)
    {
        var md = new StringBuilder();
        md.AppendLine("# Requirements Traceability Matrix");
        md.AppendLine();
        md.AppendLine("| ID | Type | Description | Implements | Implemented By |");
        md.AppendLine("|---|---|---|---|---|");

        foreach (var req in matrix.GetAllRequirements().OrderBy(r => r.Type).ThenBy(r => r.Id))
        {
            var implements = string.Join(", ", matrix.GetSourceRequirements(req.Id));
            var implementedBy = string.Join(", ", matrix.GetLinksForRequirement(req.Id));
            md.AppendLine($"| {req.Id} | {req.Type} | {req.Description} | {implements} | {implementedBy} |");
        }

        return md.ToString();
    }

    // Internal data structures
    private class RequirementData
    {
        public string Id { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string DocumentType { get; set; } = string.Empty;
    }

    private class RequirementLink
    {
        public string Source { get; set; } = string.Empty;
        public string Target { get; set; } = string.Empty;
        public string LinkType { get; set; } = string.Empty;
    }
}