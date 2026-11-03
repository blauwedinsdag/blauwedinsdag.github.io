import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Third-party players are tested for a titled frame in the static checks.
// Block their network traffic here so third-party outages cannot fail a release.
test.beforeEach(async ({ context }) => {
  await context.route(/^https?:\/\//, route => {
    return new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort();
  });
});

const pages = ['/', '/leven.html', '/liedjes.html', '/podia.html', '/nieuws.html', '/museum.html', '/404.html', '/nieuws/2025/10/21/blauwe-dinsdag-vindt-amsterdam.html'];
for (const url of pages) {
  test(`accessible layout: ${url}`, async ({ page }, info) => {
    const runtimeErrors = [];
    page.on('pageerror', error => runtimeErrors.push(error.message));
    const response = await page.goto(url);
    expect(response.ok()).toBeTruthy();
    await expect(page.locator('main h1')).toHaveCount(1);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
    const audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
    expect(audit.violations.map(item => ({ rule: item.id, nodes: item.nodes.map(node => node.target) }))).toEqual([]);
    expect(runtimeErrors).toEqual([]);
    if (url === '/' || url.includes('vindt-amsterdam')) {
      await page.screenshot({ path: info.outputPath('layout.png'), fullPage: true });
    }
  });
}

test('keyboard navigation and responsive portraits', async ({ page }, info) => {
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Ga naar inhoud' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();
  if (info.project.name === 'mobile') {
    const menu = page.locator('#nav-trigger');
    await menu.focus();
    await page.keyboard.press('Space');
    await expect(page.getByRole('link', { name: 'Liedjes', exact: true })).toBeVisible();
    await page.keyboard.press('Space');
    await expect(page.locator('#navigation-links')).toBeHidden();
  }
  const columns = await page.locator('.portraits').evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length);
  expect(columns).toBe(info.project.name === 'mobile' ? 2 : 4);
  for (const image of await page.locator('.portraits img').all()) {
    await expect.poll(() => image.evaluate(el => el.complete && el.naturalWidth > 0)).toBeTruthy();
    expect(await image.evaluate(el => el.currentSrc)).toContain('/images/optimized/');
  }
});

test('cassette players and links are present without JavaScript', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  await context.route('https://**', route => route.abort());
  const page = await context.newPage();
  await page.goto(`${baseURL}/liedjes.html`);
  await expect(page.locator('audio[controls][preload="none"]')).toHaveCount(14);
  const link = page.getByRole('link', { name: 'Beluister Warm (MP3)', exact: true });
  const response = await page.request.get(`${baseURL}${await link.getAttribute('href')}`, { headers: { Range: 'bytes=0-15' } });
  expect(response.ok()).toBeTruthy();
  expect(response.headers()['content-type']).toContain('audio/mpeg');
  await context.close();
});
