import { test, expect } from '@playwright/test';

test('compliance matrix and exports', async ({ page }) => {
  await page.route('**/api/compliance/frameworks', route =>
    route.fulfill({
      json: [{
        id: 'fedramp_moderate',
        name: 'FedRAMP M',
        controls: ['AC-1', 'AC-2']
      }]
    })
  );

  await page.goto('/compliance');
  await page.selectOption('[data-testid="framework-select"]', 'fedramp_moderate');
  await expect(page.getByTestId('matrix-title')).toContainText('FedRAMP M');
});
  await expect(page.getByRole('heading', { name: /Coverage matrix for FedRAMP M/i }))
    .toBeVisible({ timeout: 15000 });
});
