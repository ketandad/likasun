import { test, expect } from '@playwright/test';
import path from 'path';

const fixture = path.join(__dirname, 'fixtures/ingest/aws_s3_inventory.csv');

test('upload and parse CSV', async ({ page }) => {
  // Log unexpected requests
  page.on('request', request => {
    if (!request.url().includes('/api/ingest/upload') && !request.url().includes('/api/ingest/parse')) {
      console.log('Unexpected request:', request.url());
    }
  });
  await page.route('**/api/ingest/upload', route => 
    route.fulfill({ json: { id: 'test-1', message: 'Upload successful' }}));
  await page.route('**/api/ingest/parse', route =>
    route.fulfill({ json: { assets: 1, files: 1, message: 'Parse complete' }}));

  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  const input = page.locator('input[type="file"]');
  await input.setInputFiles(fixture);
  const uploadBtn = page.getByText('Upload & Parse');
  await expect(uploadBtn).toBeEnabled({ timeout: 5000 });
  await uploadBtn.click();
  await expect(page.getByText('Ingested 1 assets')).toBeVisible({ timeout: 15000 });
  await expect(page.getByText('1 files uploaded')).toBeVisible({ timeout: 15000 });
});

test('validate permissions shows missing', async ({ page }) => {
  page.on('request', request => {
    if (!request.url().includes('/api/ingest/validate')) {
      console.log('Unexpected request:', request.url());
    }
  });
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
  const validateBtn = page.getByText('Validate Permissions');
  await expect(validateBtn).toBeEnabled({ timeout: 5000 });
  await validateBtn.click();
  await expect(page.getByText('ec2:Describe: missing')).toBeVisible({ timeout: 15000 });
});

test('start live ingestion', async ({ page }) => {
  page.on('request', request => {
    if (!request.url().includes('/api/ingest/start')) {
      console.log('Unexpected request:', request.url());
    }
  });
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
  const liveBtn = page.getByText('Start Live Ingestion');
  await expect(liveBtn).toBeEnabled({ timeout: 5000 });
  await liveBtn.click();
  await expect(page.getByText('Ingested 12 assets')).toBeVisible({ timeout: 15000 });
});

test('load demo assets', async ({ page }) => {
  page.on('request', request => {
    if (!request.url().includes('/assets/load-demo') && !request.url().includes('/results')) {
      console.log('Unexpected request:', request.url());
    }
  });
  await page.route('**/assets/load-demo', (route) => route.fulfill({ json: { ingested: 10 } }));
  await page.route('**/results', (route) =>
    route.fulfill({ json: [{ id: '1', control: 'c1', status: 'PASS' }] }),
  );
  await page.goto('/ingest');
  const demoBtn = page.getByText('Load Demo Assets');
  await expect(demoBtn).toBeEnabled({ timeout: 5000 });
  await demoBtn.click();
  await page.waitForURL('**/results?env=demo', { timeout: 45000 });
  await page.waitForLoadState('networkidle');
  await expect(page.getByText('PASS')).toBeVisible({ timeout: 15000 });
});

test('keyboard accessibility triggers validate', async ({ page }) => {
  page.on('request', request => {
    if (!request.url().includes('/api/ingest/validate')) {
      console.log('Unexpected request:', request.url());
    }
  });
  await page.route('**/api/ingest/validate', route =>
    route.fulfill({ json: { missing: [], message: 'Validation complete' }})
  );
  await page.goto('/ingest');
  const validateBtn2 = page.getByRole('button', { name: /validate/i });
  await expect(validateBtn2).toBeEnabled({ timeout: 5000 });
  await validateBtn2.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByText('Validation complete')).toBeVisible();
});

test('drop zone accessible via keyboard', async ({ page }) => {
  await page.goto('/ingest');
  await page.waitForLoadState('networkidle');
  const dropZone = page.getByRole('button', { name: 'Drop files here' });
  await expect(dropZone).toBeEnabled({ timeout: 5000 });
  await dropZone.focus();
  await expect(dropZone).toBeFocused();
});

