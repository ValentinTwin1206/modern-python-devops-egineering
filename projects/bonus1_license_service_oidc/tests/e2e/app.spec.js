import { test, expect } from '@playwright/test';

test('signs in through Keycloak', async ({ page }) => {
  // get login credentials
  const username = process.env.KEYCLOAK_TEST_USERNAME;
  const password = process.env.KEYCLOAK_TEST_PASSWORD;

  if (!username || !password) {
    throw new Error('Set KEYCLOAK_TEST_USERNAME and KEYCLOAK_TEST_PASSWORD in .env');
  }

  // navigate to the app and confirm it is not logged in
  await page.goto('/');

  await expect(page.getByText('🔑 License Service')).toBeVisible();
  await expect(page.getByText('You are not logged in.')).toBeVisible();
  await page.getByRole('button', { name: 'Log in with Keycloak' }).click();

  // Confirm the app handed sign-in off to Keycloak.
  await expect(page).toHaveURL(
    /keycloak\.localhost:8081\/realms\/license-service\/protocol\/openid-connect\/auth/,
  );

  // sign in through Keycloak and confirm the app is logged in
  await page.locator('#username').fill(username);
  await page.locator('#password').fill(password);
  await page.locator('#kc-login').click();

  await expect(page.getByText(`Signed in as: ${username}`)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Get license' })).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'License Key' })).toBeVisible();
});