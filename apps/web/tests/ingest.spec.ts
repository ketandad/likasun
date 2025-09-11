import { test, expect } from '@playwright/test';
import path from 'path';

const fixture = path.join(__dirname, 'fixtures/ingest/aws_s3_inventory.csv');

test('upload and parse CSV', async ({ page }) => {
  await page.route('**/api/ingest/files', (route) =>
    route.fulfill({ json: { id: 'test-1' } }),
  );
  await page.route('**/api/ingest/parse', (route) =>
    route.fulfill({
      json: { assets: 1, files: 1 },
    }),
  );

  await page.goto('/ingest');
  const input = page.locator('input[type="file"]');
  await input.setInputFiles(fixture);
  await page.getByText('Upload & Parse').click();
  await expect(page.getByText('Ingested 1 assets')).toBeVisible({ timeout: 15000 });
  await expect(page.getByText('1 files uploaded')).toBeVisible({ timeout: 15000 });
});

test('validate permissions shows missing', async ({ page }) => {
  await page.route('**/api/ingest/permissions', (route) =>
    route.fulfill({
      status: 200,
      json: { missing: ['ec2:Describe'] }
    }),
  );
  
  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  await page.getByText('Validate Permissions').click();
  await expect(page.getByText('ec2:Describe: missing')).toBeVisible({ timeout: 15000 });
});

test('start live ingestion', async ({ page }) => {
  await page.route('**/api/ingest/live', (route) =>
    route.fulfill({
      status: 200,
      json: { ingested: 12, status: 'success' }
    }),
  );
  
  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  await page.getByText('Start Live Ingestion').click();
  await expect(page.getByText('Ingested 12 assets')).toBeVisible({ timeout: 15000 });
});

test('load demo assets', async ({ page }) => {
  await page.route('**/assets/load-demo', (route) => route.fulfill({ json: { ingested: 10 } }));
  await page.route('**/results', (route) =>
    route.fulfill({ json: [{ id: '1', control: 'c1', status: 'PASS' }] }),
  );
  await page.goto('/ingest');
  await page.getByText('Load Demo Assets').click();
  await page.waitForURL('**/results?env=demo', { timeout: 45000 });
  await page.waitForLoadState('networkidle');
  await expect(page.getByText('PASS')).toBeVisible({ timeout: 15000 });
});

test('keyboard accessibility triggers validate', async ({ page }) => {
  const responsePromise = page.waitForResponse('**/api/ingest/live/permissions?cloud=aws');
  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  
  // Focus the validate button
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Enter');
  
  await responsePromise;
});

test('drop zone accessible via keyboard', async ({ page }) => {
  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  const dropZone = page.locator('[data-testid="drop-zone"]');
  await dropZone.focus();
  await expect(dropZone).toBeFocused({ timeout: 10000 });
});
