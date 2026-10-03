import { test, expect } from '@playwright/test';

test('creates and verifies a license', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('🔑 License Service')).toBeVisible();

  await page.getByRole('textbox', { name: 'Benutzer' }).fill('playwright-user');
  await page.getByRole('button', { name: 'License erzeugen' }).click();

  await expect(page.getByText('License erzeugt')).toBeVisible();

  const licenseKey = (await page.locator('code').last().innerText()).trim();
  expect(licenseKey).not.toBe('');

  await page.getByRole('textbox', { name: 'License Key' }).fill(licenseKey);
  await page.getByRole('button', { name: 'Überprüfen' }).click();

  await expect(page.getByText('Gültig für playwright-user')).toBeVisible();
});