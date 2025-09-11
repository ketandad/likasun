import { test, expect } from '@playwright/test';

test('login redirects to dashboard', async ({ page }) => {
  await page.route('**/api/auth/login', (route) =>
    route.fulfill({
      status: 200,
      json: { token: 'test-token' }
    })
  );

  await page.route('**/api/auth/user', (route) =>
    route.fulfill({
      status: 200,
      json: { name: 'Test User' }
    })
  );

  await page.goto('/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password');
  await page.getByRole('button', { name: 'Login' }).click();
  
  await page.waitForURL('**/dashboard', { timeout: 45000 });
  await expect(page.getByText('Dashboard')).toBeVisible({ timeout: 15000 });
});
