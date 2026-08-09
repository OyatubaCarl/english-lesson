/**
 * quiz_card_render.html を Playwright でレンダリングして PNG 化。
 *
 * Usage:
 *   node render_quiz_card.js <html_url_or_path> <out_png> [--reveal]
 *
 * 例:
 *   node render_quiz_card.js file:///.../quiz_card_render.html?body=...&choices=...&correct=2 default.png
 *   node render_quiz_card.js file:///.../quiz_card_render.html?body=...&choices=...&correct=2&reveal=1 answered.png
 */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const url = process.argv[2];
  const out = process.argv[3];
  if (!url || !out) {
    console.error('usage: node render_quiz_card.js <url> <out.png>');
    process.exit(1);
  }
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1080, height: 1300 },
    deviceScaleFactor: 2,  // 2160x2600 で書き出してから 1080 にダウンサンプル → くっきり
  });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(300);
  await page.screenshot({
    path: out,
    omitBackground: true,
    clip: { x: 0, y: 0, width: 1080, height: 1300 },
  });
  await browser.close();
  console.log(`✓ saved: ${out}`);
})();
