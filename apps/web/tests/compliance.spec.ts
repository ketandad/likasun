import { test, expect } from '@playwright/test';

test('compliance matrix and exports', async ({ page }) => {
  await page.goto('/compliance');
  await page.selectOption('select', { label: 'FedRAMP M' });
  await expect(page.getByText('Coverage matrix for FedRAMP M')).toBeVisible();
  await expect(page.getByText('Evidence Pack')).toBeVisible();
  await expect(page.getByText('Export CSV')).toBeVisible();
});
