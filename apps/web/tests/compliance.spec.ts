import { test, expect } from '@playwright/test';

test('compliance matrix and exports', async ({ page }) => {
  await page.route('**/api/compliance/matrix', (route) =>
    route.fulfill({
      status: 200,
      json: {
        framework: 'FedRAMP M',
        controls: []
      }
    })
  );

  await page.goto('/compliance');
  await page.waitForLoadState('networkidle');
  await page.selectOption('select', { label: 'FedRAMP M' });
  await expect(page.getByText('Coverage matrix for FedRAMP M')).toBeVisible({ timeout: 15000 });
});
