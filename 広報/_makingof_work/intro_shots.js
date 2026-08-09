// アプリ紹介ショート用スクショ2枚 (iPhoneサイズ 390x800 @2x)
const { chromium } = require('/private/tmp/claude-501/-Users-masaki-Documents-ClaudeCode---------/89f2ecb1-81e6-417f-af25-15e752cdafba/scratchpad/node_modules/playwright');
const WORK = '/Users/masaki/Documents/ClaudeCode/英語学習教材作成/広報/_makingof_work';

(async () => {
  const b = await chromium.launch({ headless: true });
  const ctx = await b.newContext({ viewport: { width: 390, height: 800 }, deviceScaleFactor: 2 });

  // 1) タコビート トップ
  let p = await ctx.newPage();
  await p.goto('https://taco-beat.pages.dev', { waitUntil: 'networkidle' });
  await p.waitForTimeout(1000);
  await p.screenshot({ path: `${WORK}/intro_shot_tacobeat.png` });
  console.log('ok intro_shot_tacobeat.png');

  // 2) レタスデモ 正解！x6 → 1秒待ちでスクショ
  p = await ctx.newPage();
  await p.goto('https://taco-course.pages.dev/lettuce_demo.html', { waitUntil: 'networkidle' });
  await p.waitForTimeout(800);
  const okBtn = p.locator('button:has-text("正解")').first();
  const useOk = (await okBtn.count()) > 0;
  for (let i = 0; i < 6; i++) {
    if (useOk) { await okBtn.click(); } else { await p.click('#ok'); }
    await p.waitForTimeout(350);
  }
  await p.waitForTimeout(1000);
  await p.screenshot({ path: `${WORK}/intro_shot_lettuce.png` });
  console.log('ok intro_shot_lettuce.png');

  await b.close();
})();
