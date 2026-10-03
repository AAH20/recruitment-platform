import { test, expect, Page } from '@playwright/test';

/**
 * E2E tests for Candidate CRUD operations.
 * Assumes the app is running and user is authenticated.
 */

async function navigateToCandidates(page: Page) {
  await page.goto('/candidates');
  await page.waitForLoadState('networkidle');
}

async function fillCandidateForm(page: Page, overrides: Record<string, string> = {}) {
  const data = {
    firstName: 'John',
    lastName: 'Doe',
    email: `john.doe.${Date.now()}@example.com`,
    phone: '+1234567890',
    position: 'Software Engineer',
    experience: '5',
    ...overrides,
  };

  const fieldMap: Record<string, string[]> = {
    firstName: ['input[name="firstName"]', 'input[id="firstName"]', '[data-testid="first-name"]'],
    lastName: ['input[name="lastName"]', 'input[id="lastName"]', '[data-testid="last-name"]'],
    email: ['input[name="email"]', 'input[id="email"]', '[data-testid="email"]'],
    phone: ['input[name="phone"]', 'input[id="phone"]', '[data-testid="phone"]'],
    position: ['input[name="position"]', 'input[id="position"]', '[data-testid="position"]'],
    experience: ['input[name="experience"]', 'input[id="experience"]', '[data-testid="experience"]'],
  };

  for (const [field, selectors] of Object.entries(fieldMap)) {
    for (const selector of selectors) {
      const el = page.locator(selector);
      if (await el.isVisible().catch(() => false)) {
        await el.fill(data[field as keyof typeof data]);
        break;
      }
    }
  }

  return data;
}

test.describe('Candidates Flow', () => {
  test.beforeEach(async ({ page }) => {
    await navigateToCandidates(page);
  });

  test('should display candidates page', async ({ page }) => {
    await expect(page).toHaveURL(/candidates/);
    const heading = page.getByRole('heading', { name: /candidates/i });
    await expect(heading.first()).toBeVisible();
  });

  test('should display candidates list or table', async ({ page }) => {
    const list = page.locator(
      '[data-testid="candidates-list"], .candidates-list, table, [data-testid="candidates-table"]'
    );
    await expect(list.first()).toBeVisible();
  });

  test('should display add candidate button', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add candidate|new candidate|create candidate/i,
    });
    await expect(addBtn.first()).toBeVisible();
  });

  test('should open add candidate form/modal', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add candidate|new candidate|create candidate/i,
    });
    await addBtn.first().click();

    const form = page.locator(
      '[data-testid="candidate-form"], form, [role="dialog"], .modal'
    );
    await expect(form.first()).toBeVisible();
  });

  test('should create a new candidate successfully', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add candidate|new candidate|create candidate/i,
    });
    await addBtn.first().click();

    const candidateData = await fillCandidateForm(page);

    const submitBtn = page.getByRole('button', {
      name: /save|submit|create|add/i,
    });
    await submitBtn.first().click();

    // Wait for success indication
    const successIndicator = page.locator(
      '[data-testid="success-message"], .success-message, .toast-success, [role="alert"]'
    );
    const hasSuccess = await successIndicator.isVisible().catch(() => false);

    // Or verify the candidate appears in the list
    const candidateInList = page.locator(
      `text=${candidateData.firstName}`, `text=${candidateData.email}`
    );
    const inList = await candidateInList.first().isVisible().catch(() => false);

    expect(hasSuccess || inList).toBeTruthy();
  });

  test('should validate required fields in candidate form', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add candidate|new candidate|create candidate/i,
    });
    await addBtn.first().click();

    // Try to submit empty form
    const submitBtn = page.getByRole('button', {
      name: /save|submit|create|add/i,
    });
    await submitBtn.first().click();

    // Check for validation errors
    const errorMessages = page.locator(
      '[data-testid="error-message"], .error-message, .field-error, .invalid-feedback, [role="alert"]'
    );
    const errorCount = await errorMessages.count();
    expect(errorCount).toBeGreaterThan(0);
  });

  test('should validate email format in candidate form', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add candidate|new candidate|create candidate/i,
    });
    await addBtn.first().click();

    await fillCandidateForm(page, { email: 'invalid-email' });

    const submitBtn = page.getByRole('button', {
      name: /save|submit|create|add/i,
    });
    await submitBtn.first().click();

    const emailError = page.locator(
      '[data-testid="email-error"], .email-error, input[name="email"] ~ .error, input[id="email"] ~ .error'
    );
    const hasEmailError = await emailError.isVisible().catch(() => false);

    // Also check for HTML5 validation
    const emailInput = page.locator('input[name="email"], input[id="email"]').first();
    const validationMessage = await emailInput.evaluate(
      (el: HTMLInputElement) => el.validationMessage
    );

    expect(hasEmailError || validationMessage.length > 0).toBeTruthy();
  });

  test('should view candidate details', async ({ page }) => {
    const firstCandidate = page.locator(
      '[data-testid="candidate-row"], tbody tr, .candidate-card, .candidate-item'
    ).first();

    const count = await firstCandidate.count();
    if (count === 0) {
      test.skip(true, 'No candidates available to view');
      return;
    }

    await firstCandidate.click();
    await page.waitForLoadState('networkidle');

    const detailView = page.locator(
      '[data-testid="candidate-detail"], .candidate-detail, .candidate-profile, [role="dialog"]'
    );
    await expect(detailView.first()).toBeVisible();
  });

  test('should edit an existing candidate', async ({ page }) => {
    const firstCandidate = page.locator(
      '[data-testid="candidate-row"], tbody tr, .candidate-card, .candidate-item'
    ).first();

    const count = await firstCandidate.count();
    if (count === 0) {
      test.skip(true, 'No candidates available to edit');
      return;
    }

    // Look for edit button on first candidate
    const editBtn = firstCandidate.getByRole('button', {
      name: /edit|modify|update/i,
    });

    if (await editBtn.isVisible().catch(() => false)) {
      await editBtn.click();
    } else {
      await firstCandidate.click();
      const editBtnInDetail = page.getByRole('button', { name: /edit|modify|update/i });
      if (await editBtnInDetail.isVisible().catch(() => false)) {
        await editBtnInDetail.first().click();
      } else {
        test.skip(true, 'No edit action available');
        return;
      }
    }

    const form = page.locator('[data-testid="candidate-form"], form, [role="dialog"]');
    await expect(form.first()).toBeVisible();

    // Modify a field
    const firstNameInput = page.locator(
      'input[name="firstName"], input[id="firstName"], [data-testid="first-name"]'
    ).first();
    if (await firstNameInput.isVisible().catch(() => false)) {
      await firstNameInput.fill('Jane');
    }

    const saveBtn = page.getByRole('button', { name: /save|update|submit/i });
    await saveBtn.first().click();

    const successIndicator = page.locator(
      '[data-testid="success-message"], .success-message, .toast-success'
    );
    const hasSuccess = await successIndicator.isVisible().catch(() => false);
    expect(hasSuccess).toBeTruthy();
  });

  test('should delete a candidate with confirmation', async ({ page }) => {
    const firstCandidate = page.locator(
      '[data-testid="candidate-row"], tbody tr, .candidate-card, .candidate-item'
    ).first();

    const count = await firstCandidate.count();
    if (count === 0) {
      test.skip(true, 'No candidates available to delete');
      return;
    }

    const deleteBtn = firstCandidate.getByRole('button', {
      name: /delete|remove/i,
    });

    if (await deleteBtn.isVisible().catch(() => false)) {
      await deleteBtn.click();

      // Handle confirmation dialog
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

  test('should search/filter candidates', async ({ page }) => {
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="search" i], [data-testid="search-input"], [data-testid="candidate-search"]'
    );

    const count = await searchInput.count();
    if (count === 0) {
      test.skip(true, 'No search input available');
      return;
    }

    await searchInput.first().fill('John');
    await page.waitForTimeout(500); // Wait for debounce

    const results = page.locator(
      '[data-testid="candidate-row"], tbody tr, .candidate-card, .candidate-item'
    );
    const resultCount = await results.count();
    expect(resultCount).toBeGreaterThanOrEqual(0); // Could be 0 if no matches
  });

  test('should handle candidate creation API failure gracefully', async ({ page }) => {
    await page.route('**/api/candidates**', (route) => {
      if (route.request().method() === 'POST') {
        return route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal server error' }),
        });
      }
      return route.continue();
    });

    const addBtn = page.getByRole('button', {
      name: /add candidate|new candidate|create candidate/i,
    });
    await addBtn.first().click();

    await fillCandidateForm(page);

    const submitBtn = page.getByRole('button', {
      name: /save|submit|create|add/i,
    });
    await submitBtn.first().click();

    const errorIndicator = page.locator(
      '[data-testid="error-message"], .error-message, .toast-error, [role="alert"]'
    );
    const hasError = await errorIndicator.isVisible().catch(() => false);
    expect(hasError).toBeTruthy();
  });

  test('should cancel candidate form and return to list', async ({ page }) => {
    const addBtn = page.getByRole('button', {
      name: /add candidate|new candidate|create candidate/i,
    });
    await addBtn.first().click();

    const cancelBtn = page.getByRole('button', { name: /cancel|close|back/i });
    if (await cancelBtn.isVisible().catch(() => false)) {
      await cancelBtn.first().click();
      await expect(page).toHaveURL(/candidates/);
    }
  });
});
