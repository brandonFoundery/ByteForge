using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using ByteForgeFrontend.Models.ProjectManagement;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Newtonsoft.Json;
using Xunit;
using Xunit.Abstractions;

namespace ByteForgeFrontend.Tests.Integration.Performance
{
    /// <summary>
    /// Comprehensive load testing suite for realistic usage scenarios
    /// </summary>
    public class LoadTestingSuite : IClassFixture<WebApplicationFactory<Program>>
    {
        private readonly WebApplicationFactory<Program> _factory;
        private readonly ITestOutputHelper _output;
        private readonly HttpClient _client;
        private readonly Random _random = new Random();

        public LoadTestingSuite(WebApplicationFactory<Program> factory, ITestOutputHelper output)
        {
            _factory = factory;
            _output = output;
            _client = _factory.CreateClient();
        }

        [Fact]
        public async Task LoadTest_RealisticMixedWorkload()
        {
            // Arrange
            var testDuration = TimeSpan.FromMinutes(2);
            var userCount = 50;
            var metrics = new LoadTestMetrics();

            _output.WriteLine("=== Realistic Mixed Workload Load Test ===");
            _output.WriteLine($"Duration: {testDuration.TotalMinutes} minutes");
            _output.WriteLine($"Virtual Users: {userCount}");

            // Define workload distribution (based on typical usage patterns)
            var workloadDistribution = new Dictionary<string, int>
            {
                { "ViewDashboard", 40 },      // 40% - Most common action
                { "CreateProject", 5 },        // 5% - Less frequent
                { "GenerateDocument", 15 },    // 15% - Regular usage
                { "CheckStatus", 25 },         // 25% - Frequent monitoring
                { "UpdateSettings", 5 },       // 5% - Occasional
                { "ExportData", 10 }          // 10% - Periodic exports
            };

            // Create test users and authenticate
            var users = await CreateTestUsers(userCount);

            // Act - Run load test
            var cts = new CancellationTokenSource(testDuration);
            var tasks = users.Select(user => RunUserSimulation(user, workloadDistribution, metrics, cts.Token)).ToList();

            await Task.WhenAll(tasks);

            // Assert and Report
            GenerateLoadTestReport(metrics, testDuration, userCount);

            // Performance assertions
            Assert.True(metrics.SuccessRate > 0.95, $"Success rate {metrics.SuccessRate:P} below 95% threshold");
            Assert.True(metrics.AverageResponseTime < 500, $"Average response time {metrics.AverageResponseTime}ms exceeds 500ms");
            Assert.True(metrics.P95ResponseTime < 2000, $"P95 response time {metrics.P95ResponseTime}ms exceeds 2000ms");
        }

        [Fact]
        public async Task LoadTest_SpikeTest()
        {
            // Arrange
            var normalUsers = 10;
            var spikeUsers = 100;
            var normalDuration = TimeSpan.FromMinutes(1);
            var spikeDuration = TimeSpan.FromSeconds(30);
            var metrics = new LoadTestMetrics();

            _output.WriteLine("=== Spike Test ===");
            _output.WriteLine($"Normal Load: {normalUsers} users for {normalDuration.TotalMinutes} minutes");
            _output.WriteLine($"Spike Load: {spikeUsers} users for {spikeDuration.TotalSeconds} seconds");

            // Act - Normal load phase
            _output.WriteLine("\nPhase 1: Normal Load");
            var normalCts = new CancellationTokenSource(normalDuration);
            var normalTasks = new List<Task>();
            
            for (int i = 0; i < normalUsers; i++)
            {
                var user = await CreateTestUser($"normal-{i}@test.com");
                normalTasks.Add(RunContinuousRequests(user, metrics, normalCts.Token));
            }

            // Wait for normal phase to complete
            await Task.WhenAll(normalTasks);
            
            var normalMetrics = metrics.GetSnapshot();
            _output.WriteLine($"Normal phase - Avg Response: {normalMetrics.avgResponseTime:F0}ms, Success Rate: {normalMetrics.successRate:P}");

            // Spike phase
            _output.WriteLine("\nPhase 2: Spike Load");
            var spikeCts = new CancellationTokenSource(spikeDuration);
            var spikeTasks = new List<Task>();
            
            var spikeStartTime = DateTime.UtcNow;
            for (int i = 0; i < spikeUsers; i++)
            {
                var user = await CreateTestUser($"spike-{i}@test.com");
                spikeTasks.Add(RunContinuousRequests(user, metrics, spikeCts.Token));
                
                // Stagger user arrivals slightly
                if (i % 10 == 0) await Task.Delay(100);
            }

            await Task.WhenAll(spikeTasks);
            
            var spikeMetrics = metrics.GetSnapshotSince(spikeStartTime);
            _output.WriteLine($"Spike phase - Avg Response: {spikeMetrics.avgResponseTime:F0}ms, Success Rate: {spikeMetrics.successRate:P}");

            // Recovery phase
            _output.WriteLine("\nPhase 3: Recovery");
            await Task.Delay(TimeSpan.FromSeconds(10));
            
            var recoveryCts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
            var recoveryTasks = new List<Task>();
            
            for (int i = 0; i < normalUsers; i++)
            {
                var user = await CreateTestUser($"recovery-{i}@test.com");
                recoveryTasks.Add(RunContinuousRequests(user, metrics, recoveryCts.Token));
            }

            await Task.WhenAll(recoveryTasks);
            
            // Assert
            Assert.True(spikeMetrics.successRate > 0.90, $"Spike phase success rate {spikeMetrics.successRate:P} below 90%");
            Assert.True(spikeMetrics.avgResponseTime < normalMetrics.avgResponseTime * 3, "Spike response time exceeded 3x normal");
            
            _output.WriteLine("\n=== Spike test completed successfully ===");
        }

        [Fact]
        public async Task LoadTest_StressTest_FindBreakingPoint()
        {
            // Arrange
            var initialUsers = 10;
            var userIncrement = 10;
            var maxUsers = 200;
            var stepDuration = TimeSpan.FromSeconds(30);
            var metrics = new LoadTestMetrics();
            var breakingPoint = 0;

            _output.WriteLine("=== Stress Test - Finding Breaking Point ===");
            _output.WriteLine($"Starting with {initialUsers} users, incrementing by {userIncrement} every {stepDuration.TotalSeconds}s");

            // Act - Gradually increase load until system breaks
            for (int currentUsers = initialUsers; currentUsers <= maxUsers; currentUsers += userIncrement)
            {
                _output.WriteLine($"\nTesting with {currentUsers} concurrent users...");
                
                var stepMetrics = new LoadTestMetrics();
                var cts = new CancellationTokenSource(stepDuration);
                var tasks = new List<Task>();

                // Create users for this step
                for (int i = 0; i < currentUsers; i++)
                {
                    var user = await CreateTestUser($"stress-{currentUsers}-{i}@test.com");
                    tasks.Add(RunContinuousRequests(user, stepMetrics, cts.Token));
                }

                await Task.WhenAll(tasks);

                var snapshot = stepMetrics.GetSnapshot();
                _output.WriteLine($"  Requests: {snapshot.totalRequests}, Success Rate: {snapshot.successRate:P}, Avg Response: {snapshot.avgResponseTime:F0}ms");

                // Check if system is breaking down
                if (snapshot.successRate < 0.95 || snapshot.avgResponseTime > 5000 || snapshot.errorRate > 0.10)
                {
                    breakingPoint = currentUsers;
                    _output.WriteLine($"\n!!! Breaking point detected at {breakingPoint} concurrent users !!!");
                    break;
                }

                // Small delay between steps
                await Task.Delay(TimeSpan.FromSeconds(5));
            }

            // Assert
            Assert.True(breakingPoint >= 50, $"System broke at only {breakingPoint} users, expected at least 50");
            
            _output.WriteLine($"\n=== Stress test completed. System can handle up to {breakingPoint - userIncrement} concurrent users reliably ===");
        }

        [Fact]
        public async Task LoadTest_EnduranceTest()
        {
            // Arrange
            var userCount = 25;
            var testDuration = TimeSpan.FromMinutes(5); // Shortened for testing, production would be hours
            var checkInterval = TimeSpan.FromMinutes(1);
            var metrics = new LoadTestMetrics();

            _output.WriteLine("=== Endurance Test ===");
            _output.WriteLine($"Duration: {testDuration.TotalMinutes} minutes");
            _output.WriteLine($"Concurrent Users: {userCount}");
            _output.WriteLine($"Check Interval: {checkInterval.TotalMinutes} minutes");

            // Create test users
            var users = await CreateTestUsers(userCount);

            // Act - Run sustained load
            var cts = new CancellationTokenSource(testDuration);
            var tasks = users.Select(user => RunContinuousRequests(user, metrics, cts.Token)).ToList();

            // Monitor performance over time
            var checkpoints = new List<(DateTime time, LoadTestSnapshot snapshot)>();
            var monitoringTask = Task.Run(async () =>
            {
                while (!cts.Token.IsCancellationRequested)
                {
                    await Task.Delay(checkInterval);
                    var snapshot = metrics.GetSnapshot();
                    checkpoints.Add((DateTime.UtcNow, snapshot));
                    
                    _output.WriteLine($"\nCheckpoint at {DateTime.UtcNow:HH:mm:ss}:");
                    _output.WriteLine($"  Total Requests: {snapshot.totalRequests:N0}");
                    _output.WriteLine($"  Success Rate: {snapshot.successRate:P}");
                    _output.WriteLine($"  Avg Response: {snapshot.avgResponseTime:F0}ms");
                    _output.WriteLine($"  Memory Usage: {GC.GetTotalMemory(false) / 1024 / 1024}MB");
                }
            });

            await Task.WhenAll(tasks.Concat(new[] { monitoringTask }));

            // Analyze performance degradation
            if (checkpoints.Count >= 2)
            {
                var firstCheckpoint = checkpoints.First().snapshot;
                var lastCheckpoint = checkpoints.Last().snapshot;
                
                var performanceDegradation = (lastCheckpoint.avgResponseTime - firstCheckpoint.avgResponseTime) / firstCheckpoint.avgResponseTime;
                _output.WriteLine($"\nPerformance degradation: {performanceDegradation:P}");
                
                // Assert no significant degradation
                Assert.True(performanceDegradation < 0.20, $"Performance degraded by {performanceDegradation:P}, exceeding 20% threshold");
                Assert.True(lastCheckpoint.successRate > 0.95, $"Success rate dropped to {lastCheckpoint.successRate:P}");
            }

            _output.WriteLine("\n=== Endurance test completed successfully ===");
        }

        // Helper methods
        private async Task<TestUser> CreateTestUser(string email)
        {
            var registerData = new
            {
                email = email,
                password = "Test123!",
                confirmPassword = "Test123!"
            };

            var response = await _client.PostAsync("/api/auth/register",
                new StringContent(JsonConvert.SerializeObject(registerData), Encoding.UTF8, "application/json"));

            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<dynamic>(content);
                return new TestUser
                {
                    Email = email,
                    Token = result.data.token.ToString(),
                    TenantId = Guid.NewGuid().ToString()
                };
            }

            // If registration fails (user might exist), try login
            var loginData = new { email = email, password = "Test123!" };
            response = await _client.PostAsync("/api/auth/login",
                new StringContent(JsonConvert.SerializeObject(loginData), Encoding.UTF8, "application/json"));

            var loginContent = await response.Content.ReadAsStringAsync();
            var loginResult = JsonConvert.DeserializeObject<dynamic>(loginContent);
            
            return new TestUser
            {
                Email = email,
                Token = loginResult.data.token.ToString(),
                TenantId = Guid.NewGuid().ToString()
            };
        }

        private async Task<List<TestUser>> CreateTestUsers(int count)
        {
            var tasks = Enumerable.Range(0, count)
                .Select(i => CreateTestUser($"loadtest-{Guid.NewGuid():N}@test.com"))
                .ToList();
            
            return (await Task.WhenAll(tasks)).ToList();
        }

        private async Task RunUserSimulation(
            TestUser user, 
            Dictionary<string, int> workloadDistribution, 
            LoadTestMetrics metrics,
            CancellationToken cancellationToken)
        {
            var client = _factory.CreateClient();
            client.DefaultRequestHeaders.Add("Authorization", $"Bearer {user.Token}");

            while (!cancellationToken.IsCancellationRequested)
            {
                // Select action based on distribution
                var action = SelectRandomAction(workloadDistribution);
                
                // Execute action and record metrics
                var sw = Stopwatch.StartNew();
                var success = false;
                string error = null;

                try
                {
                    switch (action)
                    {
                        case "ViewDashboard":
                            success = await ViewDashboard(client);
                            break;
                        case "CreateProject":
                            success = await CreateProject(client, user);
                            break;
                        case "GenerateDocument":
                            success = await GenerateDocument(client, user);
                            break;
                        case "CheckStatus":
                            success = await CheckStatus(client);
                            break;
                        case "UpdateSettings":
                            success = await UpdateSettings(client);
                            break;
                        case "ExportData":
                            success = await ExportData(client);
                            break;
                    }
                }
                catch (Exception ex)
                {
                    error = ex.Message;
                }

                sw.Stop();
                metrics.RecordRequest(action, sw.ElapsedMilliseconds, success, error);

                // Random think time between actions (1-5 seconds)
                await Task.Delay(_random.Next(1000, 5000), cancellationToken);
            }
        }

        private async Task RunContinuousRequests(
            TestUser user,
            LoadTestMetrics metrics,
            CancellationToken cancellationToken)
        {
            var client = _factory.CreateClient();
            client.DefaultRequestHeaders.Add("Authorization", $"Bearer {user.Token}");

            while (!cancellationToken.IsCancellationRequested)
            {
                var sw = Stopwatch.StartNew();
                var success = false;
                string error = null;

                try
                {
                    var response = await client.GetAsync("/api/monitoring/status");
                    success = response.IsSuccessStatusCode;
                    if (!success)
                    {
                        error = $"Status: {response.StatusCode}";
                    }
                }
                catch (Exception ex)
                {
                    error = ex.Message;
                }

                sw.Stop();
                metrics.RecordRequest("GetStatus", sw.ElapsedMilliseconds, success, error);

                // Small delay between requests
                await Task.Delay(100, cancellationToken);
            }
        }

        private string SelectRandomAction(Dictionary<string, int> distribution)
        {
            var totalWeight = distribution.Values.Sum();
            var randomValue = _random.Next(totalWeight);
            var currentWeight = 0;

            foreach (var kvp in distribution)
            {
                currentWeight += kvp.Value;
                if (randomValue < currentWeight)
                {
                    return kvp.Key;
                }
            }

            return distribution.Keys.First();
        }

        // Simulated user actions
        private async Task<bool> ViewDashboard(HttpClient client)
        {
            var response = await client.GetAsync("/api/monitoring/dashboard");
            return response.IsSuccessStatusCode;
        }

        private async Task<bool> CreateProject(HttpClient client, TestUser user)
        {
            var projectData = new
            {
                name = $"Load Test Project {Guid.NewGuid():N}",
                description = "Created during load testing",
                tenantId = user.TenantId
            };

            var response = await client.PostAsync("/api/infrastructure/projects",
                new StringContent(JsonConvert.SerializeObject(projectData), Encoding.UTF8, "application/json"));
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<dynamic>(content);
                user.LastProjectId = result.data.id.ToString();
            }

            return response.IsSuccessStatusCode;
        }

        private async Task<bool> GenerateDocument(HttpClient client, TestUser user)
        {
            if (string.IsNullOrEmpty(user.LastProjectId))
            {
                // Create a project first if none exists
                await CreateProject(client, user);
            }

            var docData = new
            {
                projectId = user.LastProjectId,
                documentType = "BRD"
            };

            var response = await client.PostAsync("/api/requirements/generate",
                new StringContent(JsonConvert.SerializeObject(docData), Encoding.UTF8, "application/json"));
            
            return response.IsSuccessStatusCode;
        }

        private async Task<bool> CheckStatus(HttpClient client)
        {
            var response = await client.GetAsync("/api/monitoring/status");
            return response.IsSuccessStatusCode;
        }

        private async Task<bool> UpdateSettings(HttpClient client)
        {
            var settings = new
            {
                enableNotifications = _random.Next(2) == 1,
                autoSave = true,
                theme = "dark"
            };

            var response = await client.PutAsync("/api/settings/user",
                new StringContent(JsonConvert.SerializeObject(settings), Encoding.UTF8, "application/json"));
            
            return response.IsSuccessStatusCode;
        }

        private async Task<bool> ExportData(HttpClient client)
        {
            var response = await client.GetAsync("/api/monitoring/analytics/export?format=json");
            return response.IsSuccessStatusCode;
        }

        private void GenerateLoadTestReport(LoadTestMetrics metrics, TimeSpan duration, int userCount)
        {
            var snapshot = metrics.GetSnapshot();
            
            _output.WriteLine("\n=== Load Test Report ===");
            _output.WriteLine($"\nTest Summary:");
            _output.WriteLine($"  Duration: {duration.TotalMinutes:F1} minutes");
            _output.WriteLine($"  Virtual Users: {userCount}");
            _output.WriteLine($"  Total Requests: {snapshot.totalRequests:N0}");
            _output.WriteLine($"  Successful Requests: {snapshot.successfulRequests:N0}");
            _output.WriteLine($"  Failed Requests: {snapshot.failedRequests:N0}");
            _output.WriteLine($"  Success Rate: {snapshot.successRate:P}");
            
            _output.WriteLine($"\nPerformance Metrics:");
            _output.WriteLine($"  Average Response Time: {snapshot.avgResponseTime:F0}ms");
            _output.WriteLine($"  Median Response Time: {snapshot.medianResponseTime:F0}ms");
            _output.WriteLine($"  95th Percentile: {snapshot.p95ResponseTime:F0}ms");
            _output.WriteLine($"  99th Percentile: {snapshot.p99ResponseTime:F0}ms");
            _output.WriteLine($"  Min Response Time: {snapshot.minResponseTime}ms");
            _output.WriteLine($"  Max Response Time: {snapshot.maxResponseTime}ms");
            
            _output.WriteLine($"\nThroughput:");
            _output.WriteLine($"  Requests per Second: {snapshot.totalRequests / duration.TotalSeconds:F1}");
            _output.WriteLine($"  Requests per Minute: {snapshot.totalRequests / duration.TotalMinutes:F1}");
            
            _output.WriteLine($"\nBreakdown by Action:");
            foreach (var action in metrics.GetActionBreakdown())
            {
                _output.WriteLine($"  {action.Action}:");
                _output.WriteLine($"    Count: {action.Count:N0}");
                _output.WriteLine($"    Success Rate: {action.SuccessRate:P}");
                _output.WriteLine($"    Avg Response: {action.AverageResponseTime:F0}ms");
            }
            
            if (metrics.GetErrors().Any())
            {
                _output.WriteLine($"\nTop Errors:");
                foreach (var error in metrics.GetErrors().Take(5))
                {
                    _output.WriteLine($"  {error.Error} (Count: {error.Count})");
                }
            }
        }

        // Supporting classes
        private class TestUser
        {
            public string Email { get; set; }
            public string Token { get; set; }
            public string TenantId { get; set; }
            public string LastProjectId { get; set; }
        }

        private class LoadTestMetrics
        {
            private readonly ConcurrentBag<RequestMetric> _metrics = new ConcurrentBag<RequestMetric>();

            public double SuccessRate => GetSnapshot().successRate;
            public double AverageResponseTime => GetSnapshot().avgResponseTime;
            public double P95ResponseTime => GetSnapshot().p95ResponseTime;

            public void RecordRequest(string action, long responseTime, bool success, string error = null)
            {
                _metrics.Add(new RequestMetric
                {
                    Action = action,
                    ResponseTime = responseTime,
                    Success = success,
                    Error = error,
                    Timestamp = DateTime.UtcNow
                });
            }

            public LoadTestSnapshot GetSnapshot()
            {
                var allMetrics = _metrics.ToList();
                return CalculateSnapshot(allMetrics);
            }

            public LoadTestSnapshot GetSnapshotSince(DateTime since)
            {
                var recentMetrics = _metrics.Where(m => m.Timestamp >= since).ToList();
                return CalculateSnapshot(recentMetrics);
            }

            private LoadTestSnapshot CalculateSnapshot(List<RequestMetric> metrics)
            {
                if (!metrics.Any())
                {
                    return new LoadTestSnapshot();
                }

                var responseTimes = metrics.Select(m => m.ResponseTime).OrderBy(t => t).ToList();
                
                return new LoadTestSnapshot
                {
                    totalRequests = metrics.Count,
                    successfulRequests = metrics.Count(m => m.Success),
                    failedRequests = metrics.Count(m => !m.Success),
                    successRate = metrics.Count(m => m.Success) / (double)metrics.Count,
                    errorRate = metrics.Count(m => !m.Success) / (double)metrics.Count,
                    avgResponseTime = responseTimes.Average(),
                    medianResponseTime = GetPercentile(responseTimes, 50),
                    p95ResponseTime = GetPercentile(responseTimes, 95),
                    p99ResponseTime = GetPercentile(responseTimes, 99),
                    minResponseTime = responseTimes.Min(),
                    maxResponseTime = responseTimes.Max()
                };
            }

            public List<ActionBreakdown> GetActionBreakdown()
            {
                return _metrics
                    .GroupBy(m => m.Action)
                    .Select(g => new ActionBreakdown
                    {
                        Action = g.Key,
                        Count = g.Count(),
                        SuccessRate = g.Count(m => m.Success) / (double)g.Count(),
                        AverageResponseTime = g.Average(m => m.ResponseTime)
                    })
                    .OrderByDescending(a => a.Count)
                    .ToList();
            }

            public List<ErrorBreakdown> GetErrors()
            {
                return _metrics
                    .Where(m => !string.IsNullOrEmpty(m.Error))
                    .GroupBy(m => m.Error)
                    .Select(g => new ErrorBreakdown
                    {
                        Error = g.Key,
                        Count = g.Count()
                    })
                    .OrderByDescending(e => e.Count)
                    .ToList();
            }

            private double GetPercentile(List<long> sortedValues, int percentile)
            {
                if (!sortedValues.Any()) return 0;
                
                int index = (int)Math.Ceiling(percentile / 100.0 * sortedValues.Count) - 1;
                return sortedValues[Math.Max(0, Math.Min(index, sortedValues.Count - 1))];
            }
        }

        private class RequestMetric
        {
            public string Action { get; set; }
            public long ResponseTime { get; set; }
            public bool Success { get; set; }
            public string Error { get; set; }
            public DateTime Timestamp { get; set; }
        }

        private class LoadTestSnapshot
        {
            public int totalRequests { get; set; }
            public int successfulRequests { get; set; }
            public int failedRequests { get; set; }
            public double successRate { get; set; }
            public double errorRate { get; set; }
            public double avgResponseTime { get; set; }
            public double medianResponseTime { get; set; }
            public double p95ResponseTime { get; set; }
            public double p99ResponseTime { get; set; }
            public long minResponseTime { get; set; }
            public long maxResponseTime { get; set; }
        }

        private class ActionBreakdown
        {
            public string Action { get; set; }
            public int Count { get; set; }
            public double SuccessRate { get; set; }
            public double AverageResponseTime { get; set; }
        }

        private class ErrorBreakdown
        {
            public string Error { get; set; }
            public int Count { get; set; }
        }

    }
}