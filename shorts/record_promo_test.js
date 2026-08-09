/**
 * 昇級試験(Kitchen Rush)のプレイ録画
 *
 * 流れ:
 *  1. WordTacos スタート
 *  2. 中1 ステージ
 *  3. Lesson 2 (鍵付き) をタップ → モーダル
 *  4. 「L1 の昇級試験を受けて開放」 → kitchen_rush_prototype に遷移
 *  5. ゲーム開始 → 自動正解で約8秒分プレイ
 *
 * 出力: recordings/promo_test_<timestamp>.webm (1080x1920)
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT_DIR = path.join(__dirname, 'recordings');
const URL_BASE = process.env.WT_URL || 'http://localhost:8794';
// 440x780 = WordTacos アプリの自然な縦長サイズ (max-width:440px、min-height:100svh)
const VP = { width: 440, height: 780 };

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  console.log(`→ launching ${URL_BASE}/app.html @ ${VP.width}x${VP.height}`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: VP,
    deviceScaleFactor: 1,
    recordVideo: { dir: OUT_DIR, size: VP },
  });
  const page = await context.newPage();
  await page.addInitScript(() => { try { localStorage.clear(); } catch (_) {} });

  await page.goto(`${URL_BASE}/app.html`, { waitUntil: 'networkidle' });
  await sleep(1500);

  // 1. Start
  console.log('▶ click start');
  await page.click('#start-btn');
  await sleep(1200);

  // 2. 中1 ステージ
  console.log('▶ enter 中1');
  await page.click('.stage-card:first-of-type');
  await sleep(1200);

  // 3. Lesson 2 (鍵付き)
  console.log('▶ click Lesson 2 (locked)');
  const lessons = await page.$$('.lesson-card');
  if (lessons.length < 2) throw new Error('Lesson 2 not found');
  await lessons[1].click();
  await sleep(1500);

  // 4. 「L1 の昇級試験を受けて開放」
  console.log('▶ open promo test');
  await page.click('#modal-actions .btn:first-of-type');
  await sleep(2500);

  // ---- ここで kitchen_rush_prototype に遷移しているはず ----
  const url = page.url();
  console.log('  current url:', url);
  if (!url.includes('kitchen_rush_prototype')) {
    throw new Error('did not navigate to kitchen rush');
  }

  // 5. ゲーム開始
  console.log('▶ start kitchen rush');
  await page.click('#btn-start');
  await sleep(1500);

  // 6. 自動正解で 6 回 (約 8 秒)
  for (let i = 0; i < 6; i++) {
    // 問題が出るのを少し待つ
    await sleep(900);
    // 正解の選択肢をクリック
    const result = await page.evaluate(() => {
      if (typeof curQ === 'undefined' || !curQ) return { ok: false, msg: 'no curQ' };
      const choices = document.querySelectorAll('.choice');
      const idx = curQ.correctIdx;
      if (choices[idx]) { choices[idx].click(); return { ok: true, idx, n: choices.length }; }
      return { ok: false, msg: 'choice not found', idx, n: choices.length };
    });
    console.log(`  round ${i + 1}: ${JSON.stringify(result)}`);
    await sleep(900);
  }

  await sleep(600);

  console.log('⏹ close');
  await context.close();
  await browser.close();

  // 出力ファイル名を整える
  const files = fs.readdirSync(OUT_DIR).filter(f => f.endsWith('.webm'));
  if (files.length) {
    const latest = files
      .map(f => ({ f, m: fs.statSync(path.join(OUT_DIR, f)).mtimeMs }))
      .sort((a, b) => b.m - a.m)[0].f;
    const target = path.join(OUT_DIR, 'promo_test_kitchen_rush.webm');
    fs.renameSync(path.join(OUT_DIR, latest), target);
    console.log(`✓ saved: ${target}`);
  }
})().catch(e => { console.error(e); process.exit(1); });
