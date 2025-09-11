import { test, expect } from '@playwright/test';

const fixture = 'tests/fixtures/ingest/aws_s3_inventory.csv';

test('upload and parse CSV', async ({ page }) => {
  await page.route('**/ingest/files', route => route.fulfill({ json: { upload_ids: { 'aws_s3_inventory.csv': '1' } } }));
  await page.route('**/ingest/parse', route => route.fulfill({ json: { ingested: 1 } }));
  await page.goto('/ingest');
  const input = page.locator('input[type="file"]');
  await input.setInputFiles(fixture);
  await page.getByText('Upload & Parse').click();
  await expect(page.getByText('Ingested 1 assets')).toBeVisible();
  await expect(page.getByText('1 files uploaded')).toBeVisible();
});

test('validate permissions shows missing', async ({ page }) => {
  await page.route('**/ingest/live/permissions?cloud=aws', route => route.fulfill({ json: { 's3:ListBuckets': true, 'ec2:Describe': false } }));
  await page.goto('/ingest');
  await page.getByText('Validate Permissions').click();
  await expect(page.getByText('ec2:Describe: missing')).toBeVisible();
});

test('start live ingestion', async ({ page }) => {
  await page.route('**/ingest/live?cloud=aws', route => route.fulfill({ json: { ingested: 12, errors: [] } }));
  await page.goto('/ingest');
  await page.getByText('Start Live Ingestion').click();
  await expect(page.getByText('Ingested 12 assets')).toBeVisible();
});

test('load demo assets', async ({ page }) => {
  await page.route('**/assets/load-demo', route => route.fulfill({ json: { ingested: 10 } }));
  await page.route('**/results', route => route.fulfill({ json: [{ id: '1', control: 'c1', status: 'PASS' }] }));
  await page.goto('/ingest');
  await page.getByText('Load Demo Assets').click();
  await page.waitForURL('**/results?env=demo');
  await expect(page.getByText('PASS')).toBeVisible();
});

test('keyboard accessibility triggers validate', async ({ page }) => {
  await page.route('**/ingest/live/permissions?cloud=aws', route => route.fulfill({ json: {} }));
  await page.goto('/ingest');
  const promise = page.waitForRequest('**/ingest/live/permissions?cloud=aws');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Enter');
  await promise;
});
