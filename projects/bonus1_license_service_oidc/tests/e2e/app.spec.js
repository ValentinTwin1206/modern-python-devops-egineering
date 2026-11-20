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

  await expect(page.getByText('IrisLab Analysis Platform')).toBeVisible();
  await page.getByRole('button', { name: 'Continue with Keycloak' }).click();

  // Confirm the app handed sign-in off to Keycloak.
  await expect(page).toHaveURL(
    /keycloak\.localhost:8081\/realms\/iris-analysis\/protocol\/openid-connect\/auth/,
  );

  // sign in through Keycloak and confirm the app is logged in
  await page.locator('#username').fill(username);
  await page.locator('#password').fill(password);
  await page.locator('#kc-login').click();

  await expect(page.getByText('Discover the details of the iris.')).toBeVisible();
  await expect(page.getByRole('button', { name: /Start a new analysis/ })).toBeVisible();
});