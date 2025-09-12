import { test, expect } from '@playwright/test';
import path from 'path';

const licensePath = path.join(__dirname, 'fixtures/license/license.json');

test('upload license shows details', async ({ page }) => {
  // Log unexpected requests
  page.on('request', (request) => {
    if (!request.url().includes('/api/settings/license')) {
      console.log('Unexpected request:', request.url());
    }
  });
  await page.route('**/api/settings/license', (route) =>
    route.fulfill({
      json: {
        org: 'Acme',
        edition: 'enterprise',
        valid: true,
      },
    }),
  );
  await page.goto('/settings/license');
  await expect(page.getByText('Org: Acme')).toBeVisible({ timeout: 10000 });
  const input = page.locator('input[type="file"]');
  await expect(input).toBeEnabled({ timeout: 5000 });
  await input.setInputFiles(licensePath);
  await expect(page.getByText('License uploaded')).toBeVisible();
});
