import { defineConfig } from '@playwright/test';
import path from 'path';

const ARTIFACTS_DIR = path.resolve(process.env.TEST_RESULTS_DIR || '/tmp/playwright-artifacts');
const TEST_DIR = path.resolve(process.env.TEST_ROOT_DIR || './tests');
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://frontend:8501';

export default defineConfig({
  testDir: TEST_DIR,
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  fullyParallel: true,
  outputDir: path.join(ARTIFACTS_DIR, 'results'),
  reporter: [
    ['list'],
    ['html', { 
      outputFolder: path.join(ARTIFACTS_DIR, 'report'),
      open: 'never' 
    }]
  ],
  use: {
    baseURL: FRONTEND_URL,
    headless: process.env.HEADED !== 'true',
    viewport: { 
      width: 1280,
      height: 720
    },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    ignoreHTTPSErrors: true,
    bypassCSP: true,
  },
  projects: [{
    name: 'Chromium',
    use: { browserName: 'chromium' }
  }],
});
