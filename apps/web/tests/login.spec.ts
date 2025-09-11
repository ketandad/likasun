import { test, expect } from '@playwright/test';

test('login redirects to dashboard', async ({ page }) => {
  await page.route('**/api/auth/login', route =>
    route.fulfill({
      json: { 
        token: 'test-token',
        redirect: '/dashboard'
      }
    })
  );

  await page.goto('/login');
  await page.fill('[data-testid="email-input"]', 'test@example.com');
  await page.fill('[data-testid="password-input"]', 'password');
  await page.getByRole('button', { name: 'Login' }).click();

  await page.waitForResponse('**/api/auth/login');
  await page.waitForURL('**/dashboard', { timeout: 30000 });
  await expect(page.getByText('Dashboard')).toBeVisible({ timeout: 15000 });
});
  
  await page.waitForURL('**/dashboard', { timeout: 45000 });
  await expect(page.getByText('Dashboard')).toBeVisible({ timeout: 15000 });
});
