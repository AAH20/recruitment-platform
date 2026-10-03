import { test, expect, Page } from '@playwright/test';

/**
 * E2E tests for Dashboard navigation and stats.
 * Assumes the app is running and user is authenticated.
 */

async function navigateToDashboard(page: Page) {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
}

test.describe('Dashboard Flow', () => {
  test.beforeEach(async ({ page }) => {
    await navigateToDashboard(page);
  });

  test('should display dashboard page title', async ({ page }) => {
    await expect(page).toHaveTitle(/dashboard|recruitment/i);
  });

  test('should display main navigation links', async ({ page }) => {
    const nav = page.locator('nav, [role="navigation"]');
    await expect(nav).toBeVisible();

    const expectedLinks = ['Dashboard', 'Candidates', 'Jobs'];
    for (const linkText of expectedLinks) {
      await expect(
        nav.getByRole('link', { name: new RegExp(linkText, 'i') })
      ).toBeVisible();
    }
  });

  test('should display stats cards with numeric values', async ({ page }) => {
    const statsContainer = page.locator('[data-testid="stats-container"], .stats-grid, .dashboard-stats');
    await expect(statsContainer).toBeVisible();

    const statCards = page.locator('[data-testid="stat-card"], .stat-card, .stats-card');
    const count = await statCards.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < count; i++) {
      const card = statCards.nth(i);
      await expect(card).toBeVisible();

      const valueEl = card.locator('[data-testid="stat-value"], .stat-value, .value');
      await expect(valueEl).toBeVisible();
      const valueText = await valueEl.textContent();
      expect(valueText).toMatch(/\d+/);
    }
  });

  test('should display recent activity section', async ({ page }) => {
    const activitySection = page.locator(
      '[data-testid="recent-activity"], .recent-activity, .activity-feed'
    );
    await expect(activitySection).toBeVisible();
  });

  test('should navigate to Candidates page from dashboard', async ({ page }) => {
    const candidatesLink = page.getByRole('link', { name: /candidates/i }).first();
    await candidatesLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/candidates/);
  });

  test('should navigate to Jobs page from dashboard', async ({ page }) => {
    const jobsLink = page.getByRole('link', { name: /jobs/i }).first();
    await jobsLink.click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/jobs/);
  });

  test('should handle dashboard load errors gracefully', async ({ page }) => {
    // Intercept API calls to simulate failure
    await page.route('**/api/dashboard**', (route) =>
      route.fulfill({ status: 500, body: JSON.stringify({ error: 'Server error' }) })
    );

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    const errorEl = page.locator('[data-testid="error-message"], .error-message, .alert-error');
    const fallbackEl = page.locator('[data-testid="dashboard-fallback"], .dashboard-fallback');

    const hasError = await errorEl.isVisible().catch(() => false);
    const hasFallback = await fallbackEl.isVisible().catch(() => false);

    expect(hasError || hasFallback).toBeTruthy();
  });

  test('should display user profile or avatar', async ({ page }) => {
    const avatar = page.locator(
      '[data-testid="user-avatar"], .user-avatar, .avatar, [aria-label*="profile" i]'
    );
    await expect(avatar.first()).toBeVisible();
  });

  test('should have working search or filter input', async ({ page }) => {
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="search" i], [data-testid="search-input"]'
    );
    const count = await searchInput.count();

    if (count > 0) {
      await searchInput.first().fill('test query');
      await expect(searchInput.first()).toHaveValue('test query');
    }
  });
});
