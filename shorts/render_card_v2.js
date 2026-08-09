// quiz_card_v2.html / cm_card_v2.html を 1080x1920 でPNG化。
// usage: node render_card_v2.js "<file-url-with-query>" out.png
const { chromium } = require('/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/node_modules/playwright');
(async () => {
  const url = process.argv[2], out = process.argv[3];
  const b = await chromium.launch({ headless: true });
  const ctx = await b.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForTimeout(350);
  await p.screenshot({ path: out, clip: { x: 0, y: 0, width: 1080, height: 1920 }, omitBackground: true });
  await b.close();
  console.log('✓ ' + out);
})();
