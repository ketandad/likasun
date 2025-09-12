import { test, expect } from '@playwright/test';

test('login redirects to dashboard', async ({ page }) => {
  // Log unexpected requests
  page.on('request', (request) => {
    if (!request.url().includes('/api/auth/login')) {
      console.log('Unexpected request:', request.url());
    }
  });
  await page.route('**/api/auth/login', (route) =>
    route.fulfill({
      json: {
        token: 'test-token',
        redirect: '/dashboard',
      },
    }),
  );
  await page.goto('/login');
  const emailInput = page.locator('[data-testid="email-input"]');
  const passwordInput = page.locator('[data-testid="password-input"]');
  await expect(emailInput).toBeEnabled({ timeout: 5000 });
  await expect(passwordInput).toBeEnabled({ timeout: 5000 });
  await emailInput.fill('test@example.com');
  await passwordInput.fill('password');
  const loginBtn = page.getByRole('button', { name: 'Login' });
  await expect(loginBtn).toBeEnabled({ timeout: 5000 });
  await loginBtn.click();
  await page.waitForResponse('**/api/auth/login');
  await page.waitForURL('**/dashboard', { timeout: 30000 });
  await expect(page.getByText('Dashboard')).toBeVisible({ timeout: 15000 });
  await page.waitForURL('**/dashboard', { timeout: 45000 });
  await expect(page.getByText('Dashboard')).toBeVisible({ timeout: 15000 });
});

