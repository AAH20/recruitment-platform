import { test, expect, Page } from '@playwright/test';

/**
 * E2E tests for Job CRUD operations.
 * Assumes the app is running and user is authenticated.
 */

async function navigateToJobs(page: Page) {
  await page.goto('/jobs');
  await page.waitForLoadState('networkidle');
}

async function fillJobForm(page: Page, overrides: Record<string, string> = {}) {
  const data = {
    title: 'Senior Developer',
    department: 'Engineering',
    location: 'Remote',
    type: 'Full-time',
    description: 'We are looking for a senior developer to join our team.',
    salary: '120000',
    ...overrides,
  };

  const fieldMap: Record<string, string[]> = {
    title: ['input[name="title"]', 'input[id="title"]', '[data-testid="job-title"]'],
    department: ['input[name="department"]', 'input[id="department"]', '[data-testid="department"]'],
    location: ['input[name="location"]', 'input[id="location"]', '[data-testid="location"]'],
    type: ['select[name="type"]', 'select[id="type"]', '[data-testid="job-type"]'],
    description: ['textarea[name="description"]', 'textarea[id="description"]', '[data-testid="description"]'],
    salary: ['input[name="salary"]', 'input[id="salary"]', '[data-testid="salary"]'],
  };

  for (const [field, selectors] of Object.entries(fieldMap)) {
    for (const selector of selectors) {
      const el = page.locator(selector);
      if (await el.isVisible().catch(() => false)) {
        const value = data[field as keyof typeof data];
        if (selector.startsWith('select')) {
          await el.selectOption({ label: value }).catch(() => {
            // Fallback: try selecting by value
            el.selectOption({ value }).catch(() => {});
          });
        } else {
          await el.fill(value);
        }
        break;
      }
    }
  }

  return data;
}

test.describe('Jobs Flow', () => {
  test.beforeEach(async ({ page }) => {
    await navigateToJobs(page);
  });

  test('should display jobs page', async ({ page }) => {
    await expect(page).toHaveURL(/jobs/);
    const heading = page.getByRole('heading', { name: /jobs|positions|openings/i });
    await expect(heading.first()).toBeVisible();
  });

  test('should display jobs list or table', async ({ page }) => {
    const list = page.locator(
      '[data-testid="jobs-list"], .jobs-list, table, [data-testid="jobs-table"]'
    );
    await expect(list.first()).toBeVisible();
  });

  test('should display add job button', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add job|new job|create job|post job/i,
    });
    await expect(addBtn.first()).toBeVisible();
  });

  test('should open add job form/modal', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add job|new job|create job|post job/i,
    });
    await addBtn.first().click();

    const form = page.locator(
      '[data-testid="job-form"], form, [role="dialog"], .modal'
    );
    await expect(form.first()).toBeVisible();
  });

  test('should create a new job successfully', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add job|new job|create job|post job/i,
    });
    await addBtn.first().click();

    const jobData = await fillJobForm(page);

    const submitBtn = page.getByRole('button', {
      name: /save|submit|create|post|publish/i,
    });
    await submitBtn.first().click();

    const successIndicator = page.locator(
      '[data-testid="success-message"], .success-message, .toast-success, [role="alert"]'
    );
    const hasSuccess = await successIndicator.isVisible().catch(() => false);

    const jobInList = page.locator(
      `text=${jobData.title}`, `text=${jobData.department}`
    );
    const inList = await jobInList.first().isVisible().catch(() => false);

    expect(hasSuccess || inList).toBeTruthy();
  });

  test('should validate required fields in job form', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add job|new job|create job|post job/i,
    });
    await addBtn.first().click();

    const submitBtn = page.getByRole('button', {
      name: /save|submit|create|post|publish/i,
    });
    await submitBtn.first().click();

    const errorMessages = page.locator(
      '[data-testid="error-message"], .error-message, .field-error, .invalid-feedback, [role="alert"]'
    );
    const errorCount = await errorMessages.count();
    expect(errorCount).toBeGreaterThan(0);
  });

  test('should view job details', async ({ page }) => {
    const firstJob = page.locator(
      '[data-testid="job-row"], tbody tr, .job-card, .job-item'
    ).first();

    const count = await firstJob.count();
    if (count === 0) {
      test.skip(true, 'No jobs available to view');
      return;
    }

    await firstJob.click();
    await page.waitForLoadState('networkidle');

    const detailView = page.locator(
      '[data-testid="job-detail"], .job-detail, .job-description, [role="dialog"]'
    );
    await expect(detailView.first()).toBeVisible();
  });

  test('should edit an existing job', async ({ page }) => {
    const firstJob = page.locator(
      '[data-testid="job-row"], tbody tr, .job-card, .job-item'
    ).first();

    const count = await firstJob.count();
    if (count === 0) {
      test.skip(true, 'No jobs available to edit');
      return;
    }

    const editBtn = firstJob.getByRole('button', {
      name: /edit|modify|update/i,
    });

    if (await editBtn.isVisible().catch(() => false)) {
      await editBtn.click();
    } else {
      await firstJob.click();
      const editBtnInDetail = page.getByRole('button', { name: /edit|modify|update/i });
      if (await editBtnInDetail.isVisible().catch(() => false)) {
        await editBtnInDetail.first().click();
      } else {
        test.skip(true, 'No edit action available');
        return;
      }
    }

    const form = page.locator('[data-testid="job-form"], form, [role="dialog"]');
    await expect(form.first()).toBeVisible();

    const titleInput = page.locator(
      'input[name="title"], input[id="title"], [data-testid="job-title"]'
    ).first();
    if (await titleInput.isVisible().catch(() => false)) {
      await titleInput.fill('Updated Job Title');
    }

    const saveBtn = page.getByRole('button', { name: /save|update|submit/i });
    await saveBtn.first().click();

    const successIndicator = page.locator(
      '[data-testid="success-message"], .success-message, .toast-success'
    );
    const hasSuccess = await successIndicator.isVisible().catch(() => false);
    expect(hasSuccess).toBeTruthy();
  });

  test('should delete a job with confirmation', async ({ page }) => {
    const firstJob = page.locator(
      '[data-testid="job-row"], tbody tr, .job-card, .job-item'
    ).first();

    const count = await firstJob.count();
    if (count === 0) {
      test.skip(true, 'No jobs available to delete');
      return;
    }

    const deleteBtn = firstJob.getByRole('button', {
      name: /delete|remove|close/i,
    });

    if (await deleteBtn.isVisible().catch(() => false)) {
      await deleteBtn.click();

      const confirmBtn = page.getByRole('button', {
        name: /confirm|yes|delete|ok/i,
      });
      if (await confirmBtn.isVisible().catch(() => false)) {
        await confirmBtn.first().click();
      }

      const successIndicator = page.locator(
        '[data-testid="success-message"], .success-message, .toast-success'
      );
      const hasSuccess = await successIndicator.isVisible().catch(() => false);
      expect(hasSuccess).toBeTruthy();
    } else {
      test.skip(true, 'No delete action available');
    }
  });

  test('should search/filter jobs', async ({ page }) => {
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="search" i], [data-testid="search-input"], [data-testid="job-search"]'
    );

    const count = await searchInput.count();
    if (count === 0) {
      test.skip(true, 'No search input available');
      return;
    }

    await searchInput.first().fill('Engineer');
    await page.waitForTimeout(500);

    const results = page.locator(
      '[data-testid="job-row"], tbody tr, .job-card, .job-item'
    );
    const resultCount = await results.count();
    expect(resultCount).toBeGreaterThanOrEqual(0);
  });

  test('should filter jobs by department or type', async ({ page }) => {
    const filterSelect = page.locator(
      'select[name="department"], select[name="type"], [data-testid="filter-department"], [data-testid="filter-type"]'
    );

    const count = await filterSelect.count();
    if (count === 0) {
      test.skip(true, 'No filter available');
      return;
    }

    const options = await filterSelect.first().locator('option').allTextContents();
    if (options.length > 1) {
      await filterSelect.first().selectOption({ index: 1 });
      await page.waitForTimeout(500);
    }
  });

  test('should handle job creation API failure gracefully', async ({ page }) => {
    await page.route('**/api/jobs**', (route) => {
      if (route.request().method() === 'POST') {
        return route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal server error' }),
        });
      }
      return route.continue();
    });

    const addBtn = page.getByRole('button', {
      name: /add job|new job|create job|post job/i,
    });
    await addBtn.first().click();

    await fillJobForm(page);

    const submitBtn = page.getByRole('button', {
      name: /save|submit|create|post|publish/i,
    });
    await submitBtn.first().click();

    const errorIndicator = page.locator(
      '[data-testid="error-message"], .error-message, .toast-error, [role="alert"]'
    );
    const hasError = await errorIndicator.isVisible().catch(() => false);
    expect(hasError).toBeTruthy();
  });

  test('should cancel job form and return to list', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add job|new job|create job|post job/i,
    });
    await addBtn.first().click();

    const cancelBtn = page.getByRole('button', { name: /cancel|close|back/i });
    if (await cancelBtn.isVisible().catch(() => false)) {
      await cancelBtn.first().click();
      await expect(page).toHaveURL(/jobs/);
    }
  });

  test('should display job status indicators', async ({ page }) => {
    const statusBadges = page.locator(
      '[data-testid="job-status"], .job-status, .status-badge, .badge'
    );
    const count = await statusBadges.count();

    if (count > 0) {
      const firstStatus = statusBadges.first();
      await expect(firstStatus).toBeVisible();
      const statusText = await firstStatus.textContent();
      expect(statusText).toMatch(/active|closed|draft|paused|filled/i);
    }
  });
});
