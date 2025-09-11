import { test, expect } from '@playwright/test';

const licensePath = 'tests/fixtures/licenses/dev.json';

test('upload license shows details', async ({ page }) => {
  await page.route('**/settings/license', (route) =>
    route.fulfill({ json: { org: 'Acme', edition: 'enterprise', expiry: '2099-01-01' } }),
  );
  await page.route('**/settings/license/upload', (route) => route.fulfill({ json: {} }));
  await page.goto('/settings/license');
  await expect(page.getByText('Org: Acme')).toBeVisible();
  const input = page.locator('input[type="file"]');
  await input.setInputFiles(licensePath);
  await expect(page.getByText('License uploaded')).toBeVisible();
});
