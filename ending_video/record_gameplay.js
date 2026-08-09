/**
 * WordTacos のプレイ動画をたくさん録画する。
 *
 * 出力: ending_video/recordings/{scenario}.webm
 *
 * 起動前に http server が必要:
 *   python3 -m http.server 8794 --directory /tmp/vocab_sources_link
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT_DIR = path.join(__dirname, 'recordings');
const URL_BASE = process.env.WT_URL || 'http://localhost:8794';
// 縦長 440x780 = WordTacos の自然なサイズ。
// エンディング動画 (1080x1920) では中央配置するので、解像度はこれで十分。
const VP = { width: 440, height: 780 };

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function clickIfExists(page, selector, timeout = 1000) {
  try {
    const el = await page.waitForSelector(selector, { timeout, state: 'visible' });
    if (el) { await el.click(); return true; }
  } catch (_) {}
  return false;
}

async function newRecording(browser, name) {
  const context = await browser.newContext({
    viewport: VP,
    deviceScaleFactor: 2,
    recordVideo: { dir: OUT_DIR, size: VP },
  });
  const page = await context.newPage();
  await page.addInitScript(() => { try { localStorage.clear(); } catch (_) {} });
  return { context, page };
}

async function finishRecording(context, name) {
  await context.close();
  const files = fs.readdirSync(OUT_DIR).filter(f => f.endsWith('.webm'));
  if (!files.length) return;
  // 最新の .webm を name に rename
  const latest = files
    .map(f => ({ f, m: fs.statSync(path.join(OUT_DIR, f)).mtimeMs }))
    .sort((a, b) => b.m - a.m)[0].f;
  const target = path.join(OUT_DIR, `${name}.webm`);
  if (fs.existsSync(target)) fs.unlinkSync(target);
  fs.renameSync(path.join(OUT_DIR, latest), target);
  console.log(`  ✓ ${name}.webm`);
}

// === シナリオ群 ===

/** 1. タイトル → ステージ選択画面の遷移 */
async function recStageSelect(browser) {
  const { context, page } = await newRecording(browser, 'stage_select');
  await page.goto(`${URL_BASE}/app.html`, { waitUntil: 'networkidle' });
  await sleep(1500);
  await clickIfExists(page, '#start-btn');
  await sleep(3500);  // ステージ一覧をしっかり見せる
  await finishRecording(context, 'stage_select');
}

/** 2. 中1 ステージ → レッスン一覧 */
async function recLessonSelect(browser, stageIdx = 0, name = 'lesson_select_stage1') {
  const { context, page } = await newRecording(browser, name);
  await page.goto(`${URL_BASE}/app.html`, { waitUntil: 'networkidle' });
  await sleep(1000);
  await clickIfExists(page, '#start-btn');
  await sleep(800);
  const cards = await page.$$('.stage-card');
  await cards[stageIdx].click();
  await sleep(3000);
  await finishRecording(context, name);
}

/** 3. クイズプレイ (10問正解) */
async function recQuizCorrectStreak(browser, stageIdx, lessonIdx, count, name) {
  const { context, page } = await newRecording(browser, name);
  await page.goto(`${URL_BASE}/app.html`, { waitUntil: 'networkidle' });
  await sleep(1000);
  await clickIfExists(page, '#start-btn');
  await sleep(800);
  const stageCards = await page.$$('.stage-card');
  await stageCards[stageIdx].click();
  await sleep(800);
  const lessonCards = await page.$$('.lesson-card');
  await lessonCards[lessonIdx].click();
  await sleep(800);
  // モーダル: 「続きから学習」
  const btns = await page.$$('.modal .btn');
  let primary = null;
  for (const b of btns) {
    const t = (await b.innerText()).trim();
    if (t.includes('続きから学習') || t.includes('全単語復習')) { primary = b; break; }
  }
  if (!primary && btns.length) primary = btns[0];
  if (primary) await primary.click();
  await sleep(1500);

  // count 問を正解させる
  for (let i = 0; i < count; i++) {
    await sleep(700);
    const result = await page.evaluate(() => {
      if (typeof curQueue === 'undefined' || curIndex >= curQueue.length) return { done: true };
      const qid = curQueue[curIndex];
      const q = stageData.quizzes.find(x => x.id === qid);
      if (!q) return { done: false, err: 'no q' };
      const correctIdx = q.__displayCorrectIdx ?? q.correct_index;
      const btns = document.querySelectorAll('.choice');
      if (btns[correctIdx]) {
        btns[correctIdx].click();
        return { done: false, idx: correctIdx };
      }
      return { done: false, err: 'no btn' };
    });
    if (result.done) break;
    await sleep(1100); // 結果モーダル + 次へ
    // 「次へ」ボタンがあれば押す
    await clickIfExists(page, '#next-btn, .modal .btn', 500);
  }
  await sleep(1500);
  await finishRecording(context, name);
}

/** 4. クイズで間違える → 復習 */
async function recQuizWrongFlow(browser, name = 'quiz_wrong_retry') {
  const { context, page } = await newRecording(browser, name);
  await page.goto(`${URL_BASE}/app.html`, { waitUntil: 'networkidle' });
  await sleep(1000);
  await clickIfExists(page, '#start-btn');
  await sleep(800);
  const stageCards = await page.$$('.stage-card');
  await stageCards[0].click();
  await sleep(800);
  const lessonCards = await page.$$('.lesson-card');
  await lessonCards[0].click();
  await sleep(800);
  const btns = await page.$$('.modal .btn');
  if (btns.length) await btns[0].click();
  await sleep(1500);

  // 故意に間違える: correct_index と異なる選択肢を1つクリック
  await page.evaluate(() => {
    const qid = curQueue[curIndex];
    const q = stageData.quizzes.find(x => x.id === qid);
    const correctIdx = q.__displayCorrectIdx ?? q.correct_index;
    const wrongIdx = (correctIdx + 1) % 4;
    document.querySelectorAll('.choice')[wrongIdx].click();
  });
  await sleep(2200); // 結果モーダル
  await finishRecording(context, name);
}

/** 5. Kitchen Rush (鍵付きから昇級試験) */
async function recKitchenRushFromLocked(browser, name = 'kitchen_rush_unlock') {
  const { context, page } = await newRecording(browser, name);
  await page.goto(`${URL_BASE}/app.html`, { waitUntil: 'networkidle' });
  await sleep(1000);
  await clickIfExists(page, '#start-btn');
  await sleep(800);
  const stageCards = await page.$$('.stage-card');
  await stageCards[0].click();
  await sleep(800);
  const lessonCards = await page.$$('.lesson-card');
  if (lessonCards.length < 2) { await finishRecording(context, name); return; }
  await lessonCards[1].click();  // 鍵付き
  await sleep(1000);
  // 「L1 の昇級試験を受けて開放」
  const btns = await page.$$('.modal .btn');
  if (btns.length) await btns[0].click();
  await sleep(2500);
  // Kitchen Rush 起動
  await clickIfExists(page, '#btn-start');
  await sleep(1500);
  // 自動正解 5回
  for (let i = 0; i < 5; i++) {
    await sleep(900);
    await page.evaluate(() => {
      if (typeof curQ === 'undefined' || !curQ) return;
      const btns = document.querySelectorAll('.choice');
      btns[curQ.correctIdx]?.click();
    });
    await sleep(900);
  }
  await sleep(1000);
  await finishRecording(context, name);
}

/** 6. Kitchen Rush 失敗 → 復活 */
async function recKitchenRushMistake(browser, name = 'kitchen_rush_mistake') {
  const { context, page } = await newRecording(browser, name);
  await page.goto(`${URL_BASE}/kitchen_rush_prototype.html?stage=stage1&lesson=0`, { waitUntil: 'networkidle' });
  await sleep(1500);
  await clickIfExists(page, '#btn-start');
  await sleep(1500);
  // 2問正解 → 1問わざと間違える → 2問正解
  for (let i = 0; i < 5; i++) {
    await sleep(900);
    const mistake = (i === 2);
    await page.evaluate((wrong) => {
      if (typeof curQ === 'undefined' || !curQ) return;
      const btns = document.querySelectorAll('.choice');
      const idx = wrong ? (curQ.correctIdx + 1) % btns.length : curQ.correctIdx;
      btns[idx]?.click();
    }, mistake);
    await sleep(1100);
  }
  await sleep(800);
  await finishRecording(context, name);
}

/** 7. TOEIC ステージのレッスン */
async function recToeicStage(browser, name = 'toeic_basic') {
  const { context, page } = await newRecording(browser, name);
  await page.goto(`${URL_BASE}/app.html`, { waitUntil: 'networkidle' });
  await sleep(1000);
  await clickIfExists(page, '#start-btn');
  await sleep(800);
  // ステージ一覧をスクロールしてTOEICまで
  const stageCards = await page.$$('.stage-card');
  let toeicIdx = -1;
  for (let i = 0; i < stageCards.length; i++) {
    const txt = await stageCards[i].innerText();
    if (txt.includes('TOEIC')) { toeicIdx = i; break; }
  }
  if (toeicIdx < 0) { await finishRecording(context, name); return; }
  await stageCards[toeicIdx].scrollIntoViewIfNeeded();
  await sleep(800);
  await stageCards[toeicIdx].click();
  await sleep(1500);
  // 最初のレッスン
  const lessonCards = await page.$$('.lesson-card');
  if (lessonCards.length === 0) { await finishRecording(context, name); return; }
  await lessonCards[0].click();
  await sleep(800);
  const btns = await page.$$('.modal .btn');
  if (btns.length) await btns[0].click();
  await sleep(1200);

  // 3問正解
  for (let i = 0; i < 3; i++) {
    await sleep(700);
    await page.evaluate(() => {
      if (typeof curQueue === 'undefined' || curIndex >= curQueue.length) return;
      const qid = curQueue[curIndex];
      const q = stageData.quizzes.find(x => x.id === qid);
      if (!q) return;
      const correctIdx = q.__displayCorrectIdx ?? q.correct_index;
      document.querySelectorAll('.choice')[correctIdx]?.click();
    });
    await sleep(1100);
  }
  await sleep(800);
  await finishRecording(context, name);
}

// === Main ===
(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  console.log(`Recording to ${OUT_DIR}`);
  console.log(`URL: ${URL_BASE}`);

  const browser = await chromium.launch({ headless: true });

  const scenarios = [
    ['stage_select', () => recStageSelect(browser)],
    ['lesson_select_stage1', () => recLessonSelect(browser, 0, 'lesson_select_stage1')],
    ['lesson_select_stage4', () => recLessonSelect(browser, 3, 'lesson_select_stage4')],
    ['quiz_stage1_easy', () => recQuizCorrectStreak(browser, 0, 0, 4, 'quiz_stage1_easy')],
    ['quiz_stage4_intermediate', () => recQuizCorrectStreak(browser, 3, 0, 3, 'quiz_stage4_intermediate')],
    ['quiz_wrong_retry', () => recQuizWrongFlow(browser)],
    ['kitchen_rush_unlock', () => recKitchenRushFromLocked(browser)],
    ['kitchen_rush_mistake', () => recKitchenRushMistake(browser)],
    ['toeic_basic', () => recToeicStage(browser, 'toeic_basic')],
  ];

  for (const [name, fn] of scenarios) {
    console.log(`▶ ${name}`);
    try {
      await fn();
    } catch (e) {
      console.error(`  ✗ ${name} failed: ${e.message}`);
    }
  }

  await browser.close();
  console.log('done.');
})().catch(e => { console.error(e); process.exit(1); });
