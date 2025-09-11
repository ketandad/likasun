import { test, expect } from '@playwright/test';

test('login redirects to dashboard', async ({ page }) => {
  await page.route('**/auth/login', (route) => route.fulfill({ json: { access_token: 't' } }));
  await page.goto('/login');
  await page.fill('input[type="email"]', 'a@b.com');
  await page.fill('input[type="password"]', 'x');
  await page.getByRole('button', { name: 'Login' }).click();
  await page.waitForURL('**/dashboard');
  await expect(page.getByText('Dashboard')).toBeVisible();
});
