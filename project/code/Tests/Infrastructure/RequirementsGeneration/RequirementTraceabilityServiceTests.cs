using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration.Traceability;
using ByteForgeFrontend.Models.ProjectManagement;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
namespace ByteForgeFrontend.Tests.Infrastructure.RequirementsGeneration;

public class RequirementTraceabilityServiceTests
{
    private readonly Mock<IProjectService> _mockProjectService;
    private readonly Mock<ILogger<RequirementTraceabilityService>> _mockLogger;
    private readonly RequirementTraceabilityService _service;

    public RequirementTraceabilityServiceTests()
    {
        _mockProjectService = new Mock<IProjectService>();
        _mockLogger = new Mock<ILogger<RequirementTraceabilityService>>();
        _service = new RequirementTraceabilityService(_mockProjectService.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task GenerateTraceabilityMatrixAsync_ShouldCreateRTMFromProjectDocuments()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var documents = new List<ProjectDocument>
        {
            new ProjectDocument
            {
                DocumentType = "BRD",
                Content = @"Business Requirements:
- BR001: System shall support user authentication
- BR002: System shall process payments
- BR003: System shall generate reports"
            },
            new ProjectDocument
            {
                DocumentType = "PRD",
                Content = @"Product Requirements:
- PR001: Login screen with username/password [Implements BR001]
- PR002: OAuth integration [Implements BR001]  
- PR003: Payment gateway integration [Implements BR002]
- PR004: Report builder feature [Implements BR003]"
            },
            new ProjectDocument
            {
                DocumentType = "FRD",
                Content = @"Functional Requirements:
- FR001: User login validation [Implements PR001]
- FR002: Session management [Implements PR001, PR002]
- FR003: Payment processing workflow [Implements PR003]
- FR004: Report generation engine [Implements PR004]"
            },
            new ProjectDocument
            {
                DocumentType = "TRD",
                Content = @"Technical Requirements:
- TR001: JWT token implementation [Implements FR001, FR002]
- TR002: Stripe API integration [Implements FR003]
- TR003: SQL reporting queries [Implements FR004]"
            }
        };

        _mockProjectService.Setup(x => x.GetProjectDocumentsAsync(projectId))
            .ReturnsAsync(documents);

        // Act
        var result = await _service.GenerateTraceabilityMatrixAsync(projectId);

        // Assert
        Assert.True(result.Success);
        Assert.NotNull(result.Matrix);
        
        // Verify BR001 traces through the system
        var br001Links = result.Matrix.GetLinksForRequirement("BR001");
        Assert.Contains("PR001", br001Links);
        Assert.Contains("PR002", br001Links);
        
        // Verify reverse traceability
        var tr001Sources = result.Matrix.GetSourceRequirements("TR001");
        Assert.Contains("FR001", tr001Sources);
        Assert.Contains("FR002", tr001Sources);
    }

    [Fact]
    public async Task AnalyzeChangeImpactAsync_ShouldIdentifyAffectedRequirements()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var request = new ChangeImpactRequest
        {
            ProjectId = projectId,
            ChangedRequirementId = "BR001",
            ChangeDescription = "Modified authentication to require 2FA"
        };

        var documents = new List<ProjectDocument>
        {
            new ProjectDocument
            {
                DocumentType = "BRD",
                Content = "BR001: System shall support user authentication"
            },
            new ProjectDocument
            {
                DocumentType = "PRD",
                Content = @"PR001: Login screen [Implements BR001]
PR002: OAuth integration [Implements BR001]"
            },
            new ProjectDocument
            {
                DocumentType = "FRD",
                Content = @"FR001: User login [Implements PR001]
FR002: Session management [Implements PR001, PR002]"
            },
            new ProjectDocument
            {
                DocumentType = "TRD",
                Content = "TR001: JWT tokens [Implements FR001, FR002]"
            }
        };

        _mockProjectService.Setup(x => x.GetProjectDocumentsAsync(projectId))
            .ReturnsAsync(documents);

        // Act
        var result = await _service.AnalyzeChangeImpactAsync(request);

        // Assert
        Assert.True(result.Success);
        Assert.Equal("BR001", result.SourceRequirement);
        
        // Should identify all downstream requirements
        Assert.Contains("PR001", result.DirectlyAffectedRequirements);
        Assert.Contains("PR002", result.DirectlyAffectedRequirements);
        Assert.Contains("FR001", result.IndirectlyAffectedRequirements);
        Assert.Contains("FR002", result.IndirectlyAffectedRequirements);
        Assert.Contains("TR001", result.IndirectlyAffectedRequirements);
        
        Assert.Equal(ImpactSeverity.High, result.Severity); // Authentication changes are high impact
    }

    [Fact]
    public async Task ValidateTraceabilityAsync_ShouldIdentifyOrphanedRequirements()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var documents = new List<ProjectDocument>
        {
            new ProjectDocument
            {
                DocumentType = "BRD",
                Content = @"BR001: Requirement 1
BR002: Requirement 2
BR003: Requirement 3"
            },
            new ProjectDocument
            {
                DocumentType = "PRD",
                Content = @"PR001: Feature 1 [Implements BR001]
PR002: Feature 2 [Implements BR001]
PR003: Feature 3" // Orphaned - no BR link
            },
            new ProjectDocument
            {
                DocumentType = "FRD",
                Content = @"FR001: Function 1 [Implements PR001]
FR002: Function 2 [Implements PR004]" // PR004 doesn't exist
            }
        };

        _mockProjectService.Setup(x => x.GetProjectDocumentsAsync(projectId))
            .ReturnsAsync(documents);

        // Act
        var result = await _service.ValidateTraceabilityAsync(projectId);

        // Assert
        Assert.False(result.IsValid); // Should fail due to issues
        
        // Should identify orphaned requirements
        Assert.Contains("PR003", result.OrphanedRequirements);
        
        // Should identify requirements with no implementation
        Assert.Contains("BR002", result.UnimplementedRequirements);
        Assert.Contains("BR003", result.UnimplementedRequirements);
        
        // Should identify broken links
        Assert.Contains("FR002 -> PR004", result.BrokenLinks.Select(l => $"{l.From} -> {l.To}"));
    }

    [Fact]
    public async Task GenerateTraceabilityMatrixAsync_ShouldParseComplexLinkFormats()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var documents = new List<ProjectDocument>
        {
            new ProjectDocument
            {
                DocumentType = "PRD",
                Content = @"PR001: Feature [Traces to: BR001, BR002]
PR002: Another feature [Implements BR003] [Related to BR004]
PR003: Complex feature [BR005, BR006]"
            }
        };

        _mockProjectService.Setup(x => x.GetProjectDocumentsAsync(projectId))
            .ReturnsAsync(documents);

        // Act
        var result = await _service.GenerateTraceabilityMatrixAsync(projectId);

        // Assert
        Assert.True(result.Success);
        
        // Should parse various link formats
        var pr001Links = result.Matrix.GetSourceRequirements("PR001");
        Assert.Contains("BR001", pr001Links);
        Assert.Contains("BR002", pr001Links);
        
        var pr002Links = result.Matrix.GetSourceRequirements("PR002");
        Assert.Contains("BR003", pr002Links);
        Assert.Contains("BR004", pr002Links);
        
        var pr003Links = result.Matrix.GetSourceRequirements("PR003");
        Assert.Contains("BR005", pr003Links);
        Assert.Contains("BR006", pr003Links);
    }

    [Fact]
    public async Task ExportTraceabilityMatrixAsync_ShouldGenerateCSVFormat()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var documents = new List<ProjectDocument>
        {
            new ProjectDocument
            {
                DocumentType = "BRD",
                Content = "BR001: Business requirement"
            },
            new ProjectDocument
            {
                DocumentType = "PRD",
                Content = "PR001: Product requirement [Implements BR001]"
            }
        };

        _mockProjectService.Setup(x => x.GetProjectDocumentsAsync(projectId))
            .ReturnsAsync(documents);

        // Act
        var matrixResult = await _service.GenerateTraceabilityMatrixAsync(projectId);
        var exportResult = await _service.ExportTraceabilityMatrixAsync(projectId, ExportFormat.CSV);

        // Assert
        Assert.True(exportResult.Success);
        Assert.Equal(ExportFormat.CSV, exportResult.Format);
        Assert.Contains("Source,Target,Link Type", exportResult.Content);
        Assert.Contains("BR001,PR001,Implements", exportResult.Content);
    }

    [Fact]
    public async Task GetRequirementDetailsAsync_ShouldReturnFullRequirementInfo()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var requirementId = "BR001";
        
        var documents = new List<ProjectDocument>
        {
            new ProjectDocument
            {
                DocumentType = "BRD",
                Content = "BR001: System shall support multi-factor authentication",
                Version = "1.0.0",
                CreatedAt = DateTime.UtcNow.AddDays(-5)
            },
            new ProjectDocument
            {
                DocumentType = "PRD",
                Content = "PR001: MFA login screen [Implements BR001]"
            }
        };

        _mockProjectService.Setup(x => x.GetProjectDocumentsAsync(projectId))
            .ReturnsAsync(documents);

        // Act
        var result = await _service.GetRequirementDetailsAsync(projectId, requirementId);

        // Assert
        Assert.True(result.Success);
        Assert.Equal("BR001", result.RequirementId);
        Assert.Equal("System shall support multi-factor authentication", result.Description);
        Assert.Equal("BRD", result.DocumentType);
        Assert.Equal("1.0.0", result.Version);
        Assert.Contains("PR001", result.ImplementedBy);
    }

    [Fact] 
    public async Task AnalyzeTraceabilityGapsAsync_ShouldIdentifyMissingLinks()
    {
        // Arrange
        var projectId = Guid.NewGuid();
        var documents = new List<ProjectDocument>
        {
            new ProjectDocument
            {
                DocumentType = "BRD",
                Content = @"BR001: Requirement 1
BR002: Requirement 2"
            },
            new ProjectDocument
            {
                DocumentType = "PRD",
                Content = @"PR001: Feature 1 [Implements BR001]
PR002: Feature 2
PR003: Feature 3 [Implements BR002]"
            },
            new ProjectDocument
            {
                DocumentType = "FRD",
                Content = @"FR001: Function 1 [Implements PR001]
FR002: Function 2 [Implements PR003]"
            },
            new ProjectDocument
            {
                DocumentType = "TRD",
                Content = "TR001: Technical req 1"
            }
        };

        _mockProjectService.Setup(x => x.GetProjectDocumentsAsync(projectId))
            .ReturnsAsync(documents);

        // Act
        var result = await _service.AnalyzeTraceabilityGapsAsync(projectId);

        // Assert
        Assert.True(result.Success);
        
        // PR002 has no upstream link to BRD
        Assert.Contains("PR002", result.RequirementsWithoutUpstreamLinks);
        
        // PR002 has no downstream implementation in FRD
        Assert.Contains("PR002", result.RequirementsWithoutDownstreamLinks);
        
        // TR001 is completely disconnected
        Assert.Contains("TR001", result.RequirementsWithoutUpstreamLinks);
        Assert.Contains("TR001", result.RequirementsWithoutDownstreamLinks);
        
        // Should calculate coverage metrics
        Assert.True(result.UpstreamCoveragePercentage < 100);
        Assert.True(result.DownstreamCoveragePercentage < 100);
    }
}