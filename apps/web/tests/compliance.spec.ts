import { test, expect } from '@playwright/test';

test('compliance matrix and exports', async ({ page }) => {
  await page.route('**/api/compliance/matrix', route =>
    route.fulfill({
      json: {
        framework: 'FedRAMP M',
        controls: [
          { id: 'AC-1', status: 'PASS' }
        ]
      }
    })
  );

  await page.goto('/compliance');
  await page.waitForLoadState('networkidle');
  await page.selectOption('select', { label: 'FedRAMP M' });
  await expect(page.getByRole('heading', { name: /Coverage matrix for FedRAMP M/i }))
    .toBeVisible({ timeout: 15000 });
});
