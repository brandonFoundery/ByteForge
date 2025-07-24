using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using ByteForgeFrontend.Data;
using ByteForgeFrontend.Models.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.LLM;
using ByteForgeFrontend.Services.Infrastructure.ProjectManagement;
using ByteForgeFrontend.Services.Infrastructure.RequirementsGeneration;
using ByteForgeFrontend.Services.Monitoring;
using ByteForgeFrontend.Tests.TestHelpers;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;
using Xunit.Abstractions;

namespace ByteForgeFrontend.Tests.Integration.Performance
{
    /// <summary>
    /// Performance benchmark tests for critical system operations
    /// </summary>
    public class PerformanceBenchmarkTests : IClassFixture<WebApplicationFactory<Program>>, IAsyncLifetime
    {
        private readonly WebApplicationFactory<Program> _factory;
        private readonly ITestOutputHelper _output;
        private IServiceScope _scope;
        private ApplicationDbContext _context;
        private IProjectService _projectService;
        private IRequirementsOrchestrationService _requirementsService;
        private IMonitoringService _monitoringService;
        private ILLMService _llmService;

        public PerformanceBenchmarkTests(WebApplicationFactory<Program> factory, ITestOutputHelper output)
        {
            _factory = factory;
            _output = output;
        }

        public async Task InitializeAsync()
        {
            var client = _factory.WithWebHostBuilder(builder =>
            {
                builder.ConfigureServices(services =>
                {
                    // Use in-memory database for performance testing
                    var descriptor = services.SingleOrDefault(
                        d => d.ServiceType == typeof(DbContextOptions<ApplicationDbContext>));
                    if (descriptor != null)
                    {
                        services.Remove(descriptor);
                    }

                    services.AddDbContext<ApplicationDbContext>(options =>
                    {
                        options.UseInMemoryDatabase($"PerfTest_{Guid.NewGuid()}");
                        options.EnableSensitiveDataLogging(false);
                        options.EnableServiceProviderCaching();
                    });

                    // Use mock LLM for consistent performance testing
                    services.AddSingleton<ILLMProvider, MockLLMProvider>();
                });
            }).CreateClient();

            _scope = _factory.Services.CreateScope();
            _context = _scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
            _projectService = _scope.ServiceProvider.GetRequiredService<IProjectService>();
            _requirementsService = _scope.ServiceProvider.GetRequiredService<IRequirementsOrchestrationService>();
            _monitoringService = _scope.ServiceProvider.GetRequiredService<IMonitoringService>();
            _llmService = _scope.ServiceProvider.GetRequiredService<ILLMService>();

            await _context.Database.EnsureCreatedAsync();
        }

        public async Task DisposeAsync()
        {
            _scope?.Dispose();
        }

        [Fact]
        public async Task Benchmark_DocumentGeneration_Performance()
        {
            // Arrange
            var iterations = 10;
            var documentTypes = new[] { "BRD", "PRD", "FRD", "TRD" };
            var results = new List<BenchmarkResult>();

            _output.WriteLine("=== Document Generation Performance Benchmark ===");
            _output.WriteLine($"Iterations: {iterations}");
            _output.WriteLine($"Document Types: {string.Join(", ", documentTypes)}");

            // Warm-up
            var warmupProject = await CreateTestProject("Warmup Project");
            await _requirementsService.GenerateDocumentAsync(warmupProject.Id, "BRD", new Dictionary<string, object>());

            // Act - Run benchmarks
            foreach (var docType in documentTypes)
            {
                var times = new List<long>();

                for (int i = 0; i < iterations; i++)
                {
                    var project = await CreateTestProject($"Perf Test {docType} {i}");
                    
                    var sw = Stopwatch.StartNew();
                    var result = await _requirementsService.GenerateDocumentAsync(
                        project.Id, 
                        docType, 
                        new Dictionary<string, object>
                        {
                            { "projectName", project.Name },
                            { "iteration", i }
                        });
                    sw.Stop();

                    Assert.True(result.Success);
                    times.Add(sw.ElapsedMilliseconds);
                }

                var benchmarkResult = new BenchmarkResult
                {
                    Operation = $"Generate {docType}",
                    AverageMs = times.Average(),
                    MinMs = times.Min(),
                    MaxMs = times.Max(),
                    MedianMs = GetMedian(times),
                    P95Ms = GetPercentile(times, 95),
                    P99Ms = GetPercentile(times, 99)
                };

                results.Add(benchmarkResult);
                _output.WriteLine($"\n{docType} Generation:");
                _output.WriteLine($"  Average: {benchmarkResult.AverageMs:F2}ms");
                _output.WriteLine($"  Median:  {benchmarkResult.MedianMs:F2}ms");
                _output.WriteLine($"  Min:     {benchmarkResult.MinMs}ms");
                _output.WriteLine($"  Max:     {benchmarkResult.MaxMs}ms");
                _output.WriteLine($"  P95:     {benchmarkResult.P95Ms:F2}ms");
                _output.WriteLine($"  P99:     {benchmarkResult.P99Ms:F2}ms");
            }

            // Assert - Performance thresholds
            foreach (var result in results)
            {
                Assert.True(result.AverageMs < 1000, $"{result.Operation} average time {result.AverageMs}ms exceeds 1000ms threshold");
                Assert.True(result.P95Ms < 2000, $"{result.Operation} P95 time {result.P95Ms}ms exceeds 2000ms threshold");
            }

            _output.WriteLine("\n=== All document generation benchmarks passed ===");
        }

        [Fact]
        public async Task Benchmark_DatabaseQuery_Performance()
        {
            // Arrange
            var tenantCount = 5;
            var projectsPerTenant = 20;
            var documentsPerProject = 10;

            _output.WriteLine("=== Database Query Performance Benchmark ===");
            _output.WriteLine($"Setting up: {tenantCount} tenants, {projectsPerTenant} projects each, {documentsPerProject} documents per project");

            // Seed test data
            var tenants = await SeedTestData(tenantCount, projectsPerTenant, documentsPerProject);
            
            // Act & Assert - Benchmark queries
            var queryBenchmarks = new List<BenchmarkResult>();

            // Benchmark 1: Get projects by tenant
            _output.WriteLine("\nBenchmark 1: Get projects by tenant");
            var getProjectsTimes = new List<long>();
            
            foreach (var tenantId in tenants)
            {
                var sw = Stopwatch.StartNew();
                var projects = await _projectService.GetProjectsByTenantAsync(tenantId);
                sw.Stop();
                
                Assert.Equal(projectsPerTenant, projects.Count());
                getProjectsTimes.Add(sw.ElapsedMilliseconds);
            }

            var getProjectsResult = CalculateBenchmarkResult("Get Projects by Tenant", getProjectsTimes);
            queryBenchmarks.Add(getProjectsResult);
            PrintBenchmarkResult(getProjectsResult);

            // Benchmark 2: Get project with documents
            _output.WriteLine("\nBenchmark 2: Get project with documents");
            var getProjectDetailsTimes = new List<long>();
            
            // Test random projects
            var random = new Random();
            for (int i = 0; i < 20; i++)
            {
                var tenantId = tenants[random.Next(tenants.Count)];
                var projects = await _projectService.GetProjectsByTenantAsync(tenantId);
                var project = projects.ElementAt(random.Next(projects.Count()));
                
                var sw = Stopwatch.StartNew();
                var details = await _projectService.GetProjectDetailsAsync(project.Id);
                sw.Stop();
                
                Assert.NotNull(details);
                getProjectDetailsTimes.Add(sw.ElapsedMilliseconds);
            }

            var getDetailsResult = CalculateBenchmarkResult("Get Project Details", getProjectDetailsTimes);
            queryBenchmarks.Add(getDetailsResult);
            PrintBenchmarkResult(getDetailsResult);

            // Benchmark 3: Search projects
            _output.WriteLine("\nBenchmark 3: Search projects");
            var searchTimes = new List<long>();
            var searchTerms = new[] { "Project", "Test", "10", "Tenant", "Description" };
            
            foreach (var term in searchTerms)
            {
                var sw = Stopwatch.StartNew();
                var results = await _projectService.SearchProjectsAsync(term);
                sw.Stop();
                
                Assert.NotNull(results);
                searchTimes.Add(sw.ElapsedMilliseconds);
            }

            var searchResult = CalculateBenchmarkResult("Search Projects", searchTimes);
            queryBenchmarks.Add(searchResult);
            PrintBenchmarkResult(searchResult);

            // Assert performance thresholds
            foreach (var result in queryBenchmarks)
            {
                Assert.True(result.AverageMs < 100, $"{result.Operation} average time {result.AverageMs}ms exceeds 100ms threshold");
                Assert.True(result.P95Ms < 200, $"{result.Operation} P95 time {result.P95Ms}ms exceeds 200ms threshold");
            }

            _output.WriteLine("\n=== All database query benchmarks passed ===");
        }

        [Fact]
        public async Task Benchmark_MonitoringService_Performance()
        {
            // Arrange
            var updateCount = 1000;
            var concurrentClients = 10;

            _output.WriteLine("=== Monitoring Service Performance Benchmark ===");
            _output.WriteLine($"Updates: {updateCount}, Concurrent clients: {concurrentClients}");

            // Act - Benchmark update operations
            var updateTimes = new List<long>();
            
            for (int i = 0; i < updateCount; i++)
            {
                var sw = Stopwatch.StartNew();
                
                await _monitoringService.UpdateDocumentProgressAsync(
                    Guid.NewGuid(), 
                    "BRD", 
                    i % 100, 
                    $"Update {i}");
                
                sw.Stop();
                updateTimes.Add(sw.ElapsedTicks);
            }

            var updateResult = CalculateBenchmarkResult("Monitoring Updates", updateTimes.Select(t => t * 1000 / Stopwatch.Frequency).ToList());
            PrintBenchmarkResult(updateResult);

            // Benchmark concurrent reads
            _output.WriteLine("\nBenchmarking concurrent reads...");
            var readTasks = new List<Task<long>>();
            
            for (int client = 0; client < concurrentClients; client++)
            {
                readTasks.Add(Task.Run(async () =>
                {
                    var sw = Stopwatch.StartNew();
                    
                    for (int i = 0; i < 100; i++)
                    {
                        var status = await _monitoringService.GetSystemStatusAsync();
                        Assert.NotNull(status);
                    }
                    
                    sw.Stop();
                    return sw.ElapsedMilliseconds;
                }));
            }

            var readTimes = await Task.WhenAll(readTasks);
            var readResult = CalculateBenchmarkResult("Concurrent Reads (100 per client)", readTimes.ToList());
            PrintBenchmarkResult(readResult);

            // Assert performance thresholds
            Assert.True(updateResult.AverageMs < 10, $"Update average time {updateResult.AverageMs}ms exceeds 10ms threshold");
            Assert.True(readResult.AverageMs < 500, $"Concurrent read average time {readResult.AverageMs}ms exceeds 500ms threshold");

            _output.WriteLine("\n=== Monitoring service benchmarks passed ===");
        }

        [Fact]
        public async Task Benchmark_LLMService_Failover_Performance()
        {
            // Arrange
            var requestCount = 50;
            var results = new List<BenchmarkResult>();

            _output.WriteLine("=== LLM Service Failover Performance Benchmark ===");
            _output.WriteLine($"Requests: {requestCount}");

            // Benchmark normal operation
            var normalTimes = new List<long>();
            
            for (int i = 0; i < requestCount; i++)
            {
                var sw = Stopwatch.StartNew();
                var result = await _llmService.GenerateContentAsync(new LLMRequest
                {
                    Prompt = $"Test prompt {i}",
                    MaxTokens = 100
                });
                sw.Stop();
                
                Assert.True(result.Success);
                normalTimes.Add(sw.ElapsedMilliseconds);
            }

            var normalResult = CalculateBenchmarkResult("Normal LLM Operation", normalTimes);
            results.Add(normalResult);
            PrintBenchmarkResult(normalResult);

            // Benchmark with simulated failures and retries
            _output.WriteLine("\nBenchmarking with failover simulation...");
            var failoverTimes = new List<long>();
            
            // Configure mock to fail intermittently
            var mockProvider = _scope.ServiceProvider.GetRequiredService<ILLMProvider>() as MockLLMProvider;
            if (mockProvider != null)
            {
                mockProvider.FailureRate = 0.3; // 30% failure rate
            }
            
            for (int i = 0; i < requestCount; i++)
            {
                var sw = Stopwatch.StartNew();
                var result = await _llmService.GenerateContentAsync(new LLMRequest
                {
                    Prompt = $"Failover test prompt {i}",
                    MaxTokens = 100
                });
                sw.Stop();
                
                // Should succeed due to retry logic
                Assert.True(result.Success);
                failoverTimes.Add(sw.ElapsedMilliseconds);
            }

            var failoverResult = CalculateBenchmarkResult("LLM with Failover", failoverTimes);
            results.Add(failoverResult);
            PrintBenchmarkResult(failoverResult);

            // Assert performance impact
            var overhead = (failoverResult.AverageMs - normalResult.AverageMs) / normalResult.AverageMs;
            _output.WriteLine($"\nFailover overhead: {overhead:P}");
            
            Assert.True(overhead < 0.5, $"Failover overhead {overhead:P} exceeds 50% threshold");
            Assert.True(failoverResult.P95Ms < normalResult.P95Ms * 2, "Failover P95 exceeds 2x normal operation");

            _output.WriteLine("\n=== LLM failover benchmarks passed ===");
        }

        [Fact]
        public async Task LoadTest_ConcurrentProjectGeneration()
        {
            // Arrange
            var concurrentProjects = 20;
            var tenantId = Guid.NewGuid().ToString();

            _output.WriteLine("=== Load Test: Concurrent Project Generation ===");
            _output.WriteLine($"Concurrent projects: {concurrentProjects}");

            // Act - Create projects concurrently
            var sw = Stopwatch.StartNew();
            var tasks = Enumerable.Range(1, concurrentProjects).Select(async i =>
            {
                var project = new Project
                {
                    Name = $"Load Test Project {i}",
                    Description = $"Load test project description {i}",
                    TenantId = tenantId,
                    CreatedBy = "loadtest@example.com",
                    Status = "Active"
                };

                var result = await _projectService.CreateProjectAsync(project);
                Assert.True(result.Success);

                // Generate a document for each project
                var docResult = await _requirementsService.GenerateDocumentAsync(
                    result.Data.Id, 
                    "BRD", 
                    new Dictionary<string, object>());
                
                Assert.True(docResult.Success);

                return result.Data.Id;
            }).ToList();

            var projectIds = await Task.WhenAll(tasks);
            sw.Stop();

            // Assert
            Assert.Equal(concurrentProjects, projectIds.Length);
            Assert.Equal(concurrentProjects, projectIds.Distinct().Count());

            var totalTimeMs = sw.ElapsedMilliseconds;
            var avgTimePerProject = totalTimeMs / concurrentProjects;

            _output.WriteLine($"\nResults:");
            _output.WriteLine($"  Total time: {totalTimeMs}ms");
            _output.WriteLine($"  Average per project: {avgTimePerProject}ms");
            _output.WriteLine($"  Throughput: {concurrentProjects * 1000.0 / totalTimeMs:F2} projects/second");

            // Performance assertions
            Assert.True(totalTimeMs < 30000, $"Total time {totalTimeMs}ms exceeds 30 second threshold");
            Assert.True(avgTimePerProject < 2000, $"Average time per project {avgTimePerProject}ms exceeds 2 second threshold");

            _output.WriteLine("\n=== Load test passed ===");
        }

        // Helper methods
        private async Task<Project> CreateTestProject(string name)
        {
            var result = await _projectService.CreateProjectAsync(new Project
            {
                Name = name,
                Description = $"Performance test project: {name}",
                TenantId = Guid.NewGuid().ToString(),
                CreatedBy = "perftest@example.com",
                Status = "Active"
            });
            
            Assert.True(result.Success);
            return result.Data;
        }

        private async Task<List<string>> SeedTestData(int tenantCount, int projectsPerTenant, int documentsPerProject)
        {
            var tenants = new List<string>();
            
            for (int t = 0; t < tenantCount; t++)
            {
                var tenantId = Guid.NewGuid().ToString();
                tenants.Add(tenantId);
                
                for (int p = 0; p < projectsPerTenant; p++)
                {
                    var project = await _projectService.CreateProjectAsync(new Project
                    {
                        Name = $"Tenant {t} Project {p}",
                        Description = $"Test project for performance benchmarking - Tenant {t}",
                        TenantId = tenantId,
                        CreatedBy = $"user{t}@tenant{t}.com",
                        Status = p % 3 == 0 ? "Completed" : "Active"
                    });
                    
                    Assert.True(project.Success);
                    
                    // Add some documents
                    for (int d = 0; d < documentsPerProject; d++)
                    {
                        var doc = new ProjectDocument
                        {
                            ProjectId = project.Data.Id,
                            Type = d % 4 == 0 ? "BRD" : d % 4 == 1 ? "PRD" : d % 4 == 2 ? "FRD" : "TRD",
                            Content = $"Document content for {project.Data.Name} - Doc {d}",
                            Version = "1.0",
                            CreatedAt = DateTime.UtcNow.AddDays(-d)
                        };
                        
                        _context.ProjectDocuments.Add(doc);
                    }
                }
            }
            
            await _context.SaveChangesAsync();
            return tenants;
        }

        private BenchmarkResult CalculateBenchmarkResult(string operation, List<long> times)
        {
            return new BenchmarkResult
            {
                Operation = operation,
                AverageMs = times.Average(),
                MinMs = times.Min(),
                MaxMs = times.Max(),
                MedianMs = GetMedian(times),
                P95Ms = GetPercentile(times, 95),
                P99Ms = GetPercentile(times, 99)
            };
        }

        private void PrintBenchmarkResult(BenchmarkResult result)
        {
            _output.WriteLine($"{result.Operation}:");
            _output.WriteLine($"  Average: {result.AverageMs:F2}ms");
            _output.WriteLine($"  Median:  {result.MedianMs:F2}ms");
            _output.WriteLine($"  Min:     {result.MinMs}ms");
            _output.WriteLine($"  Max:     {result.MaxMs}ms");
            _output.WriteLine($"  P95:     {result.P95Ms:F2}ms");
            _output.WriteLine($"  P99:     {result.P99Ms:F2}ms");
        }

        private double GetMedian(List<long> values)
        {
            var sorted = values.OrderBy(v => v).ToList();
            int n = sorted.Count;
            
            if (n % 2 == 0)
                return (sorted[n / 2 - 1] + sorted[n / 2]) / 2.0;
            else
                return sorted[n / 2];
        }

        private double GetPercentile(List<long> values, int percentile)
        {
            var sorted = values.OrderBy(v => v).ToList();
            int index = (int)Math.Ceiling(percentile / 100.0 * sorted.Count) - 1;
            return sorted[Math.Max(0, Math.Min(index, sorted.Count - 1))];
        }

        private class BenchmarkResult
        {
            public string Operation { get; set; }
            public double AverageMs { get; set; }
            public double MedianMs { get; set; }
            public long MinMs { get; set; }
            public long MaxMs { get; set; }
            public double P95Ms { get; set; }
            public double P99Ms { get; set; }
        }
    }

    /// <summary>
    /// Mock LLM provider for performance testing with configurable failure rate
    /// </summary>
    public class MockLLMProvider : ILLMProvider
    {
        private readonly Random _random = new Random();
        public double FailureRate { get; set; } = 0;

        public string Name => "Mock";
        public bool IsAvailable => true;

        public Task<LLMGenerationResponse> GenerateAsync(LLMGenerationRequest request, CancellationToken cancellationToken = default)
        {
            // Simulate processing time
            Task.Delay(_random.Next(10, 50)).Wait();

            // Simulate failures based on failure rate
            if (_random.NextDouble() < FailureRate)
            {
                return Task.FromResult(new LLMGenerationResponse
                {
                    Success = false,
                    Error = "Simulated failure for testing",
                    Provider = "Mock",
                    Model = "mock-model",
                    TokensUsed = 0,
                    ResponseTime = TimeSpan.FromMilliseconds(_random.Next(10, 50))
                });
            }

            return Task.FromResult(new LLMGenerationResponse
            {
                Success = true,
                Content = $"Mock response for: {request.Prompt}",
                Provider = "Mock",
                Model = "mock-model",
                TokensUsed = (request.MaxTokens ?? 100) / 2,
                ResponseTime = TimeSpan.FromMilliseconds(_random.Next(10, 50))
            });
        }

        public Task<bool> ValidateConnectionAsync()
        {
            return Task.FromResult(true);
        }
    }
}