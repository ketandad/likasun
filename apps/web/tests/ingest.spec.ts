import { test, expect } from '@playwright/test';
import path from 'path';

const fixture = path.join(__dirname, 'fixtures/ingest/aws_s3_inventory.csv');

test('upload and parse CSV', async ({ page }) => {
  await page.route('**/api/ingest/upload', route => 
    route.fulfill({ json: { id: 'test-1', message: 'Upload successful' }}));
  
  await page.route('**/api/ingest/parse', route =>
    route.fulfill({ json: { assets: 1, files: 1, message: 'Parse complete' }}));

  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  const input = page.locator('input[type="file"]');
  await input.setInputFiles(fixture);
  await page.getByText('Upload & Parse').click();
  await expect(page.getByText('Ingested 1 assets')).toBeVisible({ timeout: 15000 });
  await expect(page.getByText('1 files uploaded')).toBeVisible({ timeout: 15000 });
});

test('validate permissions shows missing', async ({ page }) => {
  await page.route('**/api/ingest/validate', route =>
    route.fulfill({
      json: { 
        missing: ['ec2:Describe'],
        message: 'Permission check complete'
      }
    })
  );
  
  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  await page.getByText('Validate Permissions').click();
  await expect(page.getByText('ec2:Describe: missing')).toBeVisible({ timeout: 15000 });
});

test('start live ingestion', async ({ page }) => {
  await page.route('**/api/ingest/start', route =>
    route.fulfill({
      json: { 
        status: 'running',
        ingested: 12,
        message: 'Ingestion started'
      }
    })
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
  await page.route('**/api/ingest/validate', route =>
    route.fulfill({ json: { missing: [], message: 'Validation complete' }})
  );

  await page.goto('/ingest');
  await page.getByRole('button', { name: /validate/i }).focus();
  await page.keyboard.press('Enter');
  
  // Wait for validation response
  await expect(page.getByText('Validation complete')).toBeVisible();
});

test('drop zone accessible via keyboard', async ({ page }) => {
  await page.goto('/ingest');
  await page.getByTestId('drop-zone').focus();
  await expect(page.getByTestId('drop-zone')).toBeFocused();
});
  const dropZone = page.getByRole('button', { name: 'Drop files here' });
  await dropZone.focus();
  await expect(dropZone).toBeFocused();
});
