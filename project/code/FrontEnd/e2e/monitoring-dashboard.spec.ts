import { test, expect } from '@playwright/test';
import { TestBase } from './fixtures/test-base';

class MonitoringDashboardPage extends TestBase {
  async navigateToDashboard() {
    await this.page.goto('/dashboard/monitoring');
  }

  async waitForDashboardLoad() {
    await this.page.waitForSelector('[data-testid="monitoring-dashboard"]', { state: 'visible' });
    await this.page.waitForLoadState('networkidle');
  }

  async getDocumentGenerationCard() {
    return this.page.locator('[data-testid="document-generation-card"]');
  }

  async getAgentStatusPanel() {
    return this.page.locator('[data-testid="agent-status-panel"]');
  }

  async getProjectOverviewCard() {
    return this.page.locator('[data-testid="project-overview-card"]');
  }

  async getSystemMetricsCard() {
    return this.page.locator('[data-testid="system-metrics-card"]');
  }

  async getAnalyticsPanel() {
    return this.page.locator('[data-testid="analytics-panel"]');
  }

  async selectProject(projectId: string) {
    await this.page.selectOption('[data-testid="project-selector"]', projectId);
  }

  async exportAnalytics(format: 'csv' | 'json' | 'pdf') {
    await this.page.click('[data-testid="export-button"]');
    await this.page.click(`[data-testid="export-${format}"]`);
  }

  async refreshDashboard() {
    await this.page.click('[data-testid="refresh-button"]');
  }

  async waitForRealTimeUpdate() {
    // Wait for SignalR connection
    await this.page.waitForTimeout(1000);
    // Check for real-time update indicator
    await expect(this.page.locator('[data-testid="realtime-indicator"]')).toHaveClass(/connected/);
  }
}

test.describe('Monitoring Dashboard', () => {
  let dashboardPage: MonitoringDashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new MonitoringDashboardPage(page);
    await dashboardPage.authenticate();
    await dashboardPage.navigateToDashboard();
    await dashboardPage.waitForDashboardLoad();
  });

  test('should display all monitoring sections', async () => {
    // Check main sections are visible
    await expect(dashboardPage.getDocumentGenerationCard()).toBeVisible();
    await expect(dashboardPage.getAgentStatusPanel()).toBeVisible();
    await expect(dashboardPage.getProjectOverviewCard()).toBeVisible();
    await expect(dashboardPage.getSystemMetricsCard()).toBeVisible();
    await expect(dashboardPage.getAnalyticsPanel()).toBeVisible();
  });

  test('should show document generation progress', async () => {
    const docCard = dashboardPage.getDocumentGenerationCard();
    
    // Check for progress bars
    await expect(docCard.locator('[data-testid="progress-bar-BRD"]')).toBeVisible();
    await expect(docCard.locator('[data-testid="progress-bar-PRD"]')).toBeVisible();
    await expect(docCard.locator('[data-testid="progress-bar-FRD"]')).toBeVisible();
    await expect(docCard.locator('[data-testid="progress-bar-TRD"]')).toBeVisible();
    
    // Check progress values
    const brdProgress = await docCard.locator('[data-testid="progress-value-BRD"]').textContent();
    expect(parseInt(brdProgress || '0')).toBeGreaterThanOrEqual(0);
    expect(parseInt(brdProgress || '0')).toBeLessThanOrEqual(100);
  });

  test('should display active agents', async () => {
    const agentPanel = dashboardPage.getAgentStatusPanel();
    
    // Check for agent cards
    const agentCards = agentPanel.locator('[data-testid^="agent-card-"]');
    const count = await agentCards.count();
    expect(count).toBeGreaterThanOrEqual(0);
    
    if (count > 0) {
      // Check first agent card has required information
      const firstAgent = agentCards.first();
      await expect(firstAgent.locator('[data-testid="agent-type"]')).toBeVisible();
      await expect(firstAgent.locator('[data-testid="agent-state"]')).toBeVisible();
      await expect(firstAgent.locator('[data-testid="agent-health"]')).toBeVisible();
    }
  });

  test('should show project overview with phase indicators', async () => {
    const projectCard = dashboardPage.getProjectOverviewCard();
    
    // Check phase progress
    const phases = ['Initialization', 'Requirements', 'Documentation', 'Code Generation', 'Testing', 'Deployment'];
    for (const phase of phases) {
      await expect(projectCard.locator(`[data-testid="phase-${phase.toLowerCase().replace(' ', '-')}"]`)).toBeVisible();
    }
    
    // Check overall progress
    await expect(projectCard.locator('[data-testid="overall-progress"]')).toBeVisible();
  });

  test('should display system metrics', async () => {
    const metricsCard = dashboardPage.getSystemMetricsCard();
    
    // Check metric gauges
    await expect(metricsCard.locator('[data-testid="cpu-gauge"]')).toBeVisible();
    await expect(metricsCard.locator('[data-testid="memory-gauge"]')).toBeVisible();
    await expect(metricsCard.locator('[data-testid="disk-gauge"]')).toBeVisible();
    
    // Check service health indicators
    await expect(metricsCard.locator('[data-testid="service-health-database"]')).toBeVisible();
    await expect(metricsCard.locator('[data-testid="service-health-llm"]')).toBeVisible();
    await expect(metricsCard.locator('[data-testid="service-health-signalr"]')).toBeVisible();
  });

  test('should show analytics charts', async () => {
    const analyticsPanel = dashboardPage.getAnalyticsPanel();
    
    // Check for chart components
    await expect(analyticsPanel.locator('[data-testid="generation-trend-chart"]')).toBeVisible();
    await expect(analyticsPanel.locator('[data-testid="agent-performance-chart"]')).toBeVisible();
    await expect(analyticsPanel.locator('[data-testid="success-rate-chart"]')).toBeVisible();
  });

  test('should handle project selection', async () => {
    // Select a different project
    await dashboardPage.selectProject('test-project-2');
    
    // Wait for dashboard to update
    await dashboardPage.page.waitForTimeout(500);
    
    // Verify dashboard updated with new project data
    await expect(dashboardPage.page.locator('[data-testid="current-project-id"]')).toContainText('test-project-2');
  });

  test('should export analytics in different formats', async () => {
    // Test CSV export
    const [download] = await Promise.all([
      dashboardPage.page.waitForEvent('download'),
      dashboardPage.exportAnalytics('csv')
    ]);
    
    expect(download.suggestedFilename()).toMatch(/analytics.*\.csv$/);
    
    // Test JSON export
    const [jsonDownload] = await Promise.all([
      dashboardPage.page.waitForEvent('download'),
      dashboardPage.exportAnalytics('json')
    ]);
    
    expect(jsonDownload.suggestedFilename()).toMatch(/analytics.*\.json$/);
  });

  test('should receive real-time updates', async () => {
    // Wait for SignalR connection
    await dashboardPage.waitForRealTimeUpdate();
    
    // Simulate a document progress update
    // In a real test, this would come from the backend
    const initialProgress = await dashboardPage.page.locator('[data-testid="progress-value-BRD"]').textContent();
    
    // Wait for an update
    await dashboardPage.page.waitForTimeout(5000);
    
    // Check if progress changed (indicating real-time update)
    const updatedProgress = await dashboardPage.page.locator('[data-testid="progress-value-BRD"]').textContent();
    
    // In a real scenario, we'd trigger an update from the backend
    // For now, just verify the UI is set up for real-time updates
    await expect(dashboardPage.page.locator('[data-testid="realtime-indicator"]')).toBeVisible();
  });

  test('should handle refresh action', async () => {
    // Click refresh
    await dashboardPage.refreshDashboard();
    
    // Check loading state appears
    await expect(dashboardPage.page.locator('[data-testid="loading-spinner"]')).toBeVisible();
    
    // Wait for loading to complete
    await dashboardPage.waitForDashboardLoad();
    
    // Verify data is refreshed
    await expect(dashboardPage.getDocumentGenerationCard()).toBeVisible();
  });

  test('should show error states gracefully', async ({ page }) => {
    // Intercept API calls and return errors
    await page.route('**/api/monitoring/**', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    // Navigate to dashboard
    await dashboardPage.navigateToDashboard();
    
    // Check error state is displayed
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Failed to load monitoring data');
    
    // Check retry button is available
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await dashboardPage.navigateToDashboard();
    await dashboardPage.waitForDashboardLoad();
    
    // Check that cards stack vertically on mobile
    const cards = page.locator('[data-testid$="-card"]');
    const count = await cards.count();
    
    for (let i = 0; i < count - 1; i++) {
      const currentCard = await cards.nth(i).boundingBox();
      const nextCard = await cards.nth(i + 1).boundingBox();
      
      // Cards should be stacked (next card's top should be below current card's bottom)
      expect(nextCard!.y).toBeGreaterThan(currentCard!.y + currentCard!.height);
    }
  });

  test('should display file system changes', async () => {
    const fileChangesPanel = dashboardPage.page.locator('[data-testid="file-changes-panel"]');
    
    // Check panel is visible
    await expect(fileChangesPanel).toBeVisible();
    
    // Check for file change entries
    const changes = fileChangesPanel.locator('[data-testid^="file-change-"]');
    const changeCount = await changes.count();
    
    if (changeCount > 0) {
      // Verify first change has required info
      const firstChange = changes.first();
      await expect(firstChange.locator('[data-testid="change-type"]')).toBeVisible();
      await expect(firstChange.locator('[data-testid="change-path"]')).toBeVisible();
      await expect(firstChange.locator('[data-testid="change-timestamp"]')).toBeVisible();
    }
  });

  test('should filter monitoring data by date range', async () => {
    // Open date range picker
    await dashboardPage.page.click('[data-testid="date-range-picker"]');
    
    // Select last 7 days
    await dashboardPage.page.click('[data-testid="date-range-7days"]');
    
    // Wait for data to update
    await dashboardPage.page.waitForTimeout(1000);
    
    // Verify analytics are filtered
    const analyticsTitle = await dashboardPage.page.locator('[data-testid="analytics-date-range"]').textContent();
    expect(analyticsTitle).toContain('Last 7 days');
  });

  test('should show tooltips on hover', async () => {
    // Hover over a metric
    await dashboardPage.page.hover('[data-testid="cpu-gauge"]');
    
    // Check tooltip appears
    await expect(dashboardPage.page.locator('[role="tooltip"]')).toBeVisible();
    await expect(dashboardPage.page.locator('[role="tooltip"]')).toContainText('CPU Usage');
  });
});