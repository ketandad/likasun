import { test, expect } from '@playwright/test';

test('compliance matrix and exports', async ({ page }) => {
  // Log unexpected requests
  page.on('request', request => {
    if (!request.url().includes('/api/compliance/matrix')) {
      console.log('Unexpected request:', request.url());
    }
  });
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
  const select = page.locator('select');
  await expect(select).toBeEnabled({ timeout: 5000 });
  await select.selectOption({ label: 'FedRAMP M' });
  const heading = page.getByRole('heading', { name: /Coverage matrix for FedRAMP M/i });
  await expect(heading).toBeVisible({ timeout: 15000 });
});
