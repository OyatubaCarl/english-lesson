/**
 * GASflare — 汎用バックエンド（全アプリ共通・このファイル1枚で完結）
 *
 *   どのアプリ（WordTacos / タコスパーティー / CalTacos / …）でも、GAS側は**完全に同一**。
 *   違いは2つだけで、どちらもコードの外にある:
 *     - サイトURL      … スプレッドシートの「設定」シートのセル（コピーすると一緒に引き継がれる）
 *     - タイトル・集計項目 … アプリが初回接続時に名乗る（マニフェスト）
 *
 * ■ 先生の手順はこれだけ（3手）
 *   1. このスプレッドシートを**自分のドライブにコピー**する
 *   2. 拡張機能 → Apps Script → デプロイ → 新しいデプロイ → ウェブアプリ
 *        次のユーザーとして実行 : **自分**        （シートは先生の権限で書く。生徒に編集権限は不要）
 *        アクセスできるユーザー : **全員**        （※下の「なぜ全員か」を参照）
 *   3. デプロイで出てきたURLを生徒に配る（メニュー「🌮 …」→「生徒に配るURLを表示」でも確認できる）
 *   → そのURLを踏んだ生徒のデータだけが、このスプレッドシートに溜まる。先生ごとの独立DBになる。
 *
 * ■ しくみ
 *   生徒 → 先生のGAS URL（ブラウザで開く。Googleのセッションがある）
 *        → Session.getActiveUser().getEmail() で本人を特定
 *          ※ getActiveUser はスクリプト所有者と**同じドメイン**の利用者にしかメールを返さない。
 *            この性質だけで「学校のアカウントのみ」が自動的に成立する（設定不要・自動追随）。
 *        → メールを students シートで不透明ID(stu_xxxx)に変換
 *        → {sid, url, exp} を HMAC 署名したトークンを作り、ゲーム本体へ ?tt=<token> で転送
 *   ゲーム → 進捗が変わるたび、トークンに書かれた**このGASのURL**へ記録をPOST
 *        → GAS が署名を検証して sid を確定 → 進捗シートへ書き込む
 *
 *   **メールはアプリ（Cloudflare側）へ一切渡さない**。アプリが持つのは不透明IDだけ。
 *   メール↔ID の対応表は students シート（このスプレッドシート内）にしかない。
 *   先生が見る「進捗」シートには、照合済みのメールを表示する。
 *
 * ■ なぜ「アクセス＝全員」なのか
 *   ゲーム(別オリジン)から fetch でPOSTするため。Cookieを使わないCORSでは「ドメイン内限定」だと
 *   そもそも呼べない（GASは Access-Control-Allow-Credentials を返せない）。
 *   代わりに **HMAC署名トークン**で本人確認する。署名が無い/壊れているPOSTは全て捨てるので、
 *   URLを知られても他人になりすまして書き込むことはできない。
 *   （ブラウザで直接URLを開いたときは Cookie が効くので、getActiveUser でドメイン判定できる）
 *
 * ■ シート（すべて自動生成。手で作らない）
 *   進捗        … 生徒 × 項目 の一覧。**先生が見るのはここ**
 *   ログ        … 1行1イベントの生データ（クリア等）
 *   students   … メール ↔ 不透明ID の対応表（メールはここだけ）
 *   _data      … 集計用（非表示）。触らない
 *   _wallet    … 生徒ごとの連続ログイン・アイテム（非表示）。触らない
 *   デプロイ管理 … 日時 / URL / Ver。デプロイし直すと追記される
 */

/* =========================================================
 *  設定 — コードの中にアプリ固有の値は置かない。
 *
 *  ■ サイトURL（生徒が遊ぶアプリのURL）
 *    「設定」シートの B2 に置く。**シートをコピーすると設定も一緒に引き継がれる**ので、
 *    テンプレートに一度書いておけば、コピーした先生は何もしなくていい。
 *    （スクリプトプロパティはコピーで引き継がれないため、シートに置くのが正しい）
 *
 *  ■ マニフェスト（アプリが名乗る自己紹介）
 *    アプリは起動時の load に manifest:{ title, stats:[{key,label},…], headers:{student,plays,done,rate} } を添えてくる。
 *    GASはそれを覚え、メニューの名前・ダッシュボードの集計列に使う。
 *    アプリ側を更新すれば、全先生のGASに自動で行き渡る（GASのコードは凍結されたままでいい）。
 * ========================================================= */
var TOKEN_TTL_DAYS = 120;      // トークンの有効期間。切れたら先生のURLを開き直す
var SH_SETTINGS = '設定';

function manifest_() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('MANIFEST');
    var m = raw ? JSON.parse(raw) : null;
    if (m && typeof m === 'object') return m;
  } catch (e) { }
  return {};
}
function appTitle_() { return String(manifest_().title || 'GASflare'); }
function tokenTtlDays_() { return TOKEN_TTL_DAYS; }

/** アプリが名乗ってきたマニフェストを覚える（不正値は捨てる。ラベルは表示にしか使わない） */
function registerManifest_(m) {
  try {
    if (!m || typeof m !== 'object') return;
    var out = { title: String(m.title || '').slice(0, 40) };
    var stats = [];
    (Array.isArray(m.stats) ? m.stats : []).slice(0, 10).forEach(function (d) {
      var key = String((d && d.key) || '').trim();
      if (!/^[a-zA-Z0-9_]{1,24}$/.test(key)) return;
      stats.push({ key: key, label: String((d && d.label) || key).slice(0, 20) });
    });
    out.stats = stats;
    // 進捗シートのサマリー列（総プレイ/達成数/到達率）は、アプリが名乗れる。
    //   文字列 → その名前に変える ／ false・空 → その列ごと非表示（意味を持たないアプリ用）
    if (m.headers && typeof m.headers === 'object') {
      var hh = {};
      ['student', 'plays', 'done', 'rate'].forEach(function (k) {
        if (!(k in m.headers)) return;
        var raw = m.headers[k];
        if (k !== 'student' && (raw === false || raw === null || raw === '')) { hh[k] = ''; return; }
        var v = String(raw || '').trim().slice(0, 16);
        if (v) hh[k] = v;
      });
      if (Object.keys(hh).length) out.headers = hh;
    }
    var json = JSON.stringify(out);
    var props = PropertiesService.getScriptProperties();
    if (props.getProperty('MANIFEST') !== json) {
      props.setProperty('MANIFEST', json);
      applyHeaders_();               // 既に進捗シートがあれば、見出しをその場で貼り替える
    }
  } catch (e) { }
}

/** サマリー列の見出し（マニフェスト → 既定値）。'' はその列を使わない＝非表示の意味 */
function headers_() {
  var d = { student: '生徒（メール）', plays: '総プレイ', done: '達成数', rate: '到達率' };
  var h = manifest_().headers || {};
  var out = {};
  ['student', 'plays', 'done', 'rate'].forEach(function (k) {
    out[k] = (k !== 'student' && h[k] === '') ? '' : (h[k] || d[k]);
  });
  return out;
}

/**
 * 進捗シートのサマリー列をマニフェストに合わせる。
 * 見出し（2行目）を貼り替え、使わない列は非表示にする。
 * 列そのものは消さない（列の並びを固定しておかないと、既存データがずれるため）。
 */
function applyHeaders_() {
  try {
    var sh = ss_().getSheetByName(SH_PROGRESS);
    if (!sh) return;
    var h = headers_();
    sh.getRange(2, 1, 1, 4).setValues([[h.student, h.plays || '—', h.done || '—', h.rate || '—']]);
    var cols = { 2: h.plays, 3: h.done, 4: h.rate };
    for (var c in cols) {
      if (cols[c] === '') sh.hideColumns(Number(c));
      else sh.showColumns(Number(c));
    }
  } catch (e) { }
}

/** 「設定」シート。無ければ作る */
function settingsSheet_() {
  var ss = ss_();
  var sh = ss.getSheetByName(SH_SETTINGS);
  if (sh) return sh;
  sh = ss.insertSheet(SH_SETTINGS);
  sh.getRange(1, 1, 1, 2).setValues([['項目', '値']]).setFontWeight('bold').setBackground('#F4A26A');
  sh.getRange(2, 1).setValue('サイトURL');
  sh.getRange(3, 1).setValue('※ 生徒が遊ぶアプリのURL。シートをコピーしても引き継がれます');
  sh.setColumnWidth(1, 180); sh.setColumnWidth(2, 460);
  return sh;
}

/** 生徒を送り込むアプリのURL。設定シート → プロパティ（保険）の順で読む */
function appUrl_() {
  try {
    var sh = ss_().getSheetByName(SH_SETTINGS);
    if (sh) {
      var v = String(sh.getRange(2, 2).getValue() || '').trim();
      if (/^https:\/\//.test(v)) return v;
    }
  } catch (e) { }
  try {
    var p = String(PropertiesService.getScriptProperties().getProperty('APP_URL') || '');
    if (/^https:\/\//.test(p)) return p;
  } catch (e) { }
  return '';
}

function setAppUrl_(url) {
  url = String(url || '').trim();
  if (!/^https:\/\//.test(url)) return false;
  settingsSheet_().getRange(2, 2).setValue(url);
  return true;
}

function ownerEmail_() {
  try { return String(Session.getEffectiveUser().getEmail() || '').toLowerCase(); } catch (e) { return ''; }
}
function isOwner_() {
  var a = activeEmail_();
  return !!a && a === ownerEmail_();
}

/** 所有者だけが使える、Webからの初期設定（設定シートを開かなくてもURLを入れられる） */
function webSetAppUrl(url) {
  if (!isOwner_()) throw new Error('所有者のみ設定できます');
  if (!setAppUrl_(url)) throw new Error('https:// で始まるURLを入れてください');
  return appUrl_();
}

var SH_PROGRESS = '進捗';
var SH_LOG = 'ログ';
var SH_STUDENTS = 'students';
var SH_DATA = '_data';
var SH_WALLET = '_wallet';
var SH_DEPLOY = 'デプロイ管理';

/* =========================================================
 *  入口
 * ========================================================= */

function doGet(e) {
  recordAccess();
  var p = (e && e.parameter) || {};


  if (p.action === 'me') return json_(apiMe_(p));      // 自分の記録を見る（JSONP不使用・素のJSON）

  // 動作診断（サポート用）。既知シートの有無とプロパティの有無を boolean で返すだけ。
  // 中身（生徒名・記録・鍵・URL）は一切含まない。
  if (p.action === 'diag') {
    var d = { ok: true, sheets: {}, props: {} };
    try {
      var names = ss_().getSheets().map(function (x) { return x.getName(); });
      [SH_PROGRESS, SH_LOG, SH_STUDENTS, SH_DATA, SH_WALLET, SH_DEPLOY, SH_SETTINGS].forEach(function (n) {
        d.sheets[n] = names.indexOf(n) >= 0;
      });
      d.sheetCount = names.length;
    } catch (err) { d.ssError = String((err && err.message) || err); }
    var pr = PropertiesService.getScriptProperties();
    ['lastDeployUrl', 'instanceId', 'SIGNING_KEY', 'MANIFEST', 'SHEET_ID'].forEach(function (k) {
      d.props[k] = !!pr.getProperty(k);
    });
    d.appUrlSet = !!appUrl_();
    // 所有者本人がブラウザで開いたときだけ、実際に書き込んでいるシートの場所を出す
    // （「見ているシートと書き込み先が別だった」を自力で発見できるように）
    if (isOwner_()) {
      try { d.sheetName = ss_().getName(); d.sheetUrl = ss_().getUrl(); } catch (err) { }
      d.owner = true;
    }
    return json_(d);
  }

  var email = activeEmail_();
  if (!email) {
    // ここに来るのは「未ログイン」か「別のアカウントで見ている」のどちらか。
    // マルチアカウント環境では後者が起きる（Googleが既定アカウントで解決してしまう）。
    // 行き止まりにせず、**学校のアカウントで開き直す導線**を出す。
    var dom = ownerDomain_() || '学校ドメイン';
    var entry = webAppUrl_();
    var chooser = 'https://accounts.google.com/AccountChooser?continue=' + encodeURIComponent(entry);
    return html_(
      '学校のGoogleアカウントで開き直してください。',
      '<p class="sub">複数のGoogleアカウントでログインしていると、<br>'
      + '別のアカウントで開いてしまうことがあります。</p>'
      + '<a class="go" href="' + escapeHtml_(chooser) + '" target="_top">アカウントを選んで開き直す</a>'
      + '<p class="sub">学校で配られたアカウント（' + escapeHtml_(dom) + '）を選んでください。</p>');
  }

  var game = appUrl_();
  if (!game) {
    // サイトURLが未設定。所有者ならその場で設定できるフォームを出す（初回セットアップ用）
    if (isOwner_()) {
      return html_('サイトURLを設定してください。',
        '<p class="sub">生徒が遊ぶアプリのURL（https://…）を貼り付けてください。<br>'
        + 'スプレッドシートの「設定」シートに保存され、コピーにも引き継がれます。</p>'
        + '<input id="u" type="url" placeholder="https://…" style="width:90%;max-width:420px;'
        + 'padding:12px;font-size:14px;border:1px solid #DCCDB4;border-radius:8px">'
        + '<br><button class="go" style="border:none;cursor:pointer;font-family:inherit" '
        + 'onclick="var b=this;b.disabled=true;google.script.run'
        + '.withSuccessHandler(function(){location.reload()})'
        + '.withFailureHandler(function(e){alert(e.message);b.disabled=false})'
        + '.webSetAppUrl(document.getElementById(\'u\').value)">設定する</button>');
    }
    return html_('準備中です。', '<p class="sub">先生が設定を完了すると使えるようになります。</p>');
  }

  var sid = resolveStudentId_(email);
  var token = signToken_({ sid: sid, url: webAppUrl_(), exp: Date.now() + tokenTtlDays_() * 86400000 });
  var target = game + (game.indexOf('?') >= 0 ? '&' : '?') + 'tt=' + encodeURIComponent(token);

  // GASのHtmlServiceはサンドボックスiframeで動くので、window.top へ抜ける3段構えで遷移する
  var safe = target.replace(/"/g, '%22');
  return html_(
    '準備ができました。',
    '<a id="go" class="go" href="' + safe + '" target="_top">🌮 はじめる</a>'
    + '<p class="sub">自動で切り替わらないときは上のボタンを押してください</p>'
    + '<script>(function(){var a=document.getElementById("go");var u=a.href;'
    + 'setTimeout(function(){try{a.click()}catch(e){}},400);'
    + 'setTimeout(function(){try{window.top.location.href=u}catch(e){'
    + 'try{window.parent.location.href=u}catch(e2){}}},1200);})();</script>'
  ).setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/** ゲーム本体からの記録。CORS のプリフライトを避けるため Content-Type: text/plain で受ける */
function doPost(e) {
  var req = {};
  try { req = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { req = {}; }

  var res;
  try {
    var claims = verifyToken_(String(req.tt || ''));
    if (!claims) return json_({ ok: false, error: 'bad_token' });   // 署名なし/改ざん/期限切れ → 捨てる

    // アプリの自己紹介（タイトル・集計項目）。起動時の load に添えられてくる
    if (req.manifest) registerManifest_(req.manifest);

    if (req.action === 'load') res = apiLoad_(claims.sid, req);
    else if (req.action === 'record') res = apiRecord_(claims.sid, req);
    else if (req.action === 'wallet') res = apiWallet_(claims.sid, req.wallet || {});
    else res = { ok: false, error: 'unknown_action' };
  } catch (err) {
    res = { ok: false, error: String((err && err.message) || err) };
  }
  return json_(res);
}

/* =========================================================
 *  API
 * ========================================================= */

/** 生徒の記録を返す（別端末から入っても続きが引き継がれる） */
function apiLoad_(sid, req) {
  var out = { ok: true, sid: sid, progress: getProgress_(sid), serverDate: walletToday_() };
  if (req && req.wallet) {
    var wr = apiWallet_(sid, req.wallet);
    out.wallet = wr.wallet;
    out.walletResult = wr.result;
  }
  return out;
}

/**
 * 記録する。
 *   entries: [{ item, label, cell, detail, plays, clears, best, perfect }]
 *     item   … 項目ID（レッスンID・ステージID・工程IDなど。アプリが決める）
 *     label  … 列見出しに出す名前
 *     cell   … 進捗シートのセルに出す短い文字列（表示はアプリ側が決める）
 *     detail … 復元用の生データ（_dataにだけ入る。先生の目に触れる進捗シートには出さない）
 *   log:     [{ item, label, text }]  … 任意。ログシートに1行ずつ追記
 */
function apiRecord_(sid, req) {
  var entries = (req.entries || []).slice(0, 400);
  var logs = (req.log || []).slice(0, 50);
  if (!entries.length && !logs.length) return { ok: true, skipped: true };

  var lock = LockService.getScriptLock();
  lock.waitLock(25000);
  var progress;
  try {
    var email = emailBySid_(sid);
    var now = new Date();

    if (logs.length) {
      var lg = sheet_(SH_LOG, ['日時', '生徒', '項目ID', '項目', '内容']);
      logs.forEach(function (l) {
        lg.appendRow([now, email, String(l.item || ''), String(l.label || ''), String(l.text || '')]);
      });
    }

    var d = readData_();
    writeData_(d, sid, entries, now);
    progress = progressFrom_(d, sid);
    rebuildProgressRow_(email, entries, progress);
  } finally {
    lock.releaseLock();
  }
  return { ok: true, progress: progress };
}

/* =========================================================
 *  生徒ウォレット（サーバー日付を正本にしたログイン・アイテム）
 *
 *  タコスパーティーが wallet を送ったときだけ使う任意API。
 *  既存アプリの load / record 形式は変えないため、他アプリには影響しない。
 *  全操作を ScriptLock 内で処理し、別端末から同時に開いても二重配布・二重消費を防ぐ。
 * ========================================================= */
var WALLET_HEADERS = ['sid', 'json', 'updatedAt'];
var WALLET_LIME_MAX = 2;
var WALLET_AWARD_DAYS = [3, 7, 14, 30, 60, 100];

function walletSheet_() {
  var sh = sheet_(SH_WALLET, WALLET_HEADERS);
  if (sh.getLastColumn() < WALLET_HEADERS.length) {
    sh.getRange(1, 1, 1, WALLET_HEADERS.length).setValues([WALLET_HEADERS])
      .setFontWeight('bold').setBackground('#F4A26A');
  }
  if (!sh.isSheetHidden()) sh.hideSheet();
  return sh;
}

function walletToday_() {
  return Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd');
}

function walletDayOrdinal_(key) {
  var m = String(key || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
  return m ? Math.floor(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3])) / 86400000) : NaN;
}

function walletDefault_() {
  return { v: 1, loginBonusDate: '', loginStreak: 0, loginBestStreak: 0,
    specialTacos: 0, freezeLimes: 0, limeRewardedLessons: [], spentOps: [] };
}

function walletInt_(v, lo, hi) {
  var n = Math.floor(Number(v));
  return isFinite(n) ? Math.max(lo, Math.min(hi, n)) : lo;
}

function walletSanitize_(raw) {
  raw = raw && typeof raw === 'object' ? raw : {};
  var out = walletDefault_();
  var date = String(raw.loginBonusDate || '');
  out.loginBonusDate = /^\d{4}-\d{2}-\d{2}$/.test(date) ? date : '';
  out.loginStreak = walletInt_(raw.loginStreak, out.loginBonusDate ? 1 : 0, 100000);
  out.loginBestStreak = Math.max(out.loginStreak, walletInt_(raw.loginBestStreak, 0, 100000));
  out.specialTacos = walletInt_(raw.specialTacos, 0, 9999);
  out.freezeLimes = walletInt_(raw.freezeLimes, 0, WALLET_LIME_MAX);

  var lessons = Array.isArray(raw.limeRewardedLessons)
    ? raw.limeRewardedLessons
    : Object.keys(raw.limeRewardedLessons && typeof raw.limeRewardedLessons === 'object' ? raw.limeRewardedLessons : {})
      .filter(function (k) { return !!raw.limeRewardedLessons[k]; });
  var seenLessons = {};
  lessons.slice(0, 500).forEach(function (k) {
    k = String(k || '').toLowerCase();
    if (/^[bmh]\d{1,3}$/.test(k)) seenLessons[k] = 1;
  });
  out.limeRewardedLessons = Object.keys(seenLessons);

  var seenOps = {};
  (Array.isArray(raw.spentOps) ? raw.spentOps : []).slice(-100).forEach(function (id) {
    id = String(id || '').slice(0, 120);
    if (/^[a-zA-Z0-9:_.-]+$/.test(id)) seenOps[id] = 1;
  });
  out.spentOps = Object.keys(seenOps).slice(-100);
  return out;
}

function walletRecord_(sid) {
  var sh = walletSheet_();
  var last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, WALLET_HEADERS.length).getValues() : [];
  for (var i = 0; i < rows.length; i++) {
    if (String(rows[i][0]) !== String(sid)) continue;
    var raw = {};
    try { raw = JSON.parse(String(rows[i][1] || '{}')); } catch (e) { raw = {}; }
    return { sh: sh, row: i + 2, exists: true, wallet: walletSanitize_(raw) };
  }
  return { sh: sh, row: Math.max(2, last + 1), exists: false, wallet: walletDefault_() };
}

function walletWrite_(rec, sid, wallet) {
  rec.sh.getRange(rec.row, 1, 1, WALLET_HEADERS.length)
    .setValues([[String(sid), JSON.stringify(walletSanitize_(wallet)), new Date()]]);
}

function walletPublic_(wallet) {
  var w = walletSanitize_(wallet);
  return { v: 1, serverDate: walletToday_(), loginBonusDate: w.loginBonusDate,
    loginStreak: w.loginStreak, loginBestStreak: w.loginBestStreak,
    specialTacos: w.specialTacos, freezeLimes: w.freezeLimes,
    limeRewardedLessons: w.limeRewardedLessons.slice() };
}

function walletLogin_(wallet) {
  var today = walletToday_();
  var previous = Math.max(1, walletInt_(wallet.loginStreak, 1, 100000));
  var bestBefore = Math.max(previous, walletInt_(wallet.loginBestStreak, 0, 100000));
  if (wallet.loginBonusDate === today) {
    return { ok: true, op: 'login', amount: 0, previousStreak: previous, streak: previous,
      bestStreak: bestBefore, gap: 0, missedDays: 0, usedFreeze: 0,
      freezeLeft: wallet.freezeLimes, awardDays: 0, reset: false, alreadyClaimed: true };
  }

  var gap = walletDayOrdinal_(today) - walletDayOrdinal_(wallet.loginBonusDate);
  var missedDays = isFinite(gap) && gap > 1 ? gap - 1 : 0;
  var canFreeze = missedDays > 0 && missedDays <= wallet.freezeLimes;
  var usedFreeze = canFreeze ? missedDays : 0;
  var reset = !(gap === 1 || canFreeze);
  var streak = gap === 1 ? previous + 1 : (canFreeze ? previous + gap : 1);
  streak = Math.min(100000, streak);
  var bestStreak = Math.max(bestBefore, streak);
  var awardDays = 0;
  WALLET_AWARD_DAYS.forEach(function (days) {
    if (days > bestBefore && days <= bestStreak) awardDays = days;
  });
  var amount = Math.min(3, streak);

  wallet.loginBonusDate = today;
  wallet.loginStreak = streak;
  wallet.loginBestStreak = bestStreak;
  wallet.freezeLimes -= usedFreeze;
  wallet.specialTacos = Math.min(9999, wallet.specialTacos + amount);
  return { ok: true, op: 'login', amount: amount, previousStreak: previous, streak: streak,
    bestStreak: bestStreak, gap: isFinite(gap) ? gap : 0, missedDays: missedDays,
    usedFreeze: usedFreeze, freezeLeft: wallet.freezeLimes, awardDays: awardDays,
    reset: reset, alreadyClaimed: false };
}

function walletGrantLime_(wallet, op) {
  var lesson = String(op.lesson || '').toLowerCase();
  if (!/^[bmh]\d{1,3}$/.test(lesson)) {
    return { ok: false, op: 'grant_lime', error: 'bad_lesson', earned: false, count: wallet.freezeLimes };
  }
  if (wallet.limeRewardedLessons.indexOf(lesson) >= 0) {
    return { ok: true, op: 'grant_lime', lesson: lesson, earned: false, already: true,
      full: wallet.freezeLimes >= WALLET_LIME_MAX, count: wallet.freezeLimes };
  }
  wallet.limeRewardedLessons.push(lesson);
  var before = wallet.freezeLimes;
  wallet.freezeLimes = Math.min(WALLET_LIME_MAX, before + 1);
  return { ok: true, op: 'grant_lime', lesson: lesson, earned: wallet.freezeLimes > before,
    already: false, full: wallet.freezeLimes >= WALLET_LIME_MAX, count: wallet.freezeLimes };
}

function walletSpendSpecial_(wallet, op) {
  var id = String(op.requestId || '').slice(0, 120);
  if (!/^[a-zA-Z0-9:_.-]+$/.test(id)) {
    return { ok: false, op: 'spend_special', error: 'bad_request', spent: false, count: wallet.specialTacos };
  }
  if (wallet.spentOps.indexOf(id) >= 0) {
    return { ok: true, op: 'spend_special', spent: true, duplicate: true, count: wallet.specialTacos };
  }
  if (wallet.specialTacos < 1) {
    return { ok: false, op: 'spend_special', error: 'empty', spent: false, count: wallet.specialTacos };
  }
  wallet.specialTacos--;
  wallet.spentOps.push(id);
  wallet.spentOps = wallet.spentOps.slice(-100);
  return { ok: true, op: 'spend_special', spent: true, duplicate: false, count: wallet.specialTacos };
}

function walletApplyOp_(wallet, op) {
  var name = String((op && op.op) || 'sync');
  if (name === 'login') return walletLogin_(wallet);
  if (name === 'grant_lime') return walletGrantLime_(wallet, op || {});
  if (name === 'spend_special') return walletSpendSpecial_(wallet, op || {});
  if (name === 'sync') return { ok: true, op: 'sync' };
  return { ok: false, op: name, error: 'unknown_wallet_op' };
}

function apiWallet_(sid, op) {
  op = op && typeof op === 'object' ? op : {};
  var lock = LockService.getScriptLock();
  lock.waitLock(25000);
  try {
    var rec = walletRecord_(sid);
    var wallet = rec.exists ? rec.wallet : walletSanitize_(op.seed || {});
    var result = walletApplyOp_(wallet, op);
    walletWrite_(rec, sid, wallet);
    return { ok: true, sid: sid, serverDate: walletToday_(), wallet: walletPublic_(wallet), result: result };
  } finally {
    lock.releaseLock();
  }
}

/** 自分の記録をブラウザから見る（?action=me）。ログイン済みの本人にだけ返す */
function apiMe_() {
  var email = activeEmail_();
  if (!email) return { ok: false, error: 'not_signed_in' };
  var sid = resolveStudentId_(email);
  return { ok: true, email: email, sid: sid, progress: getProgress_(sid) };
}

/* =========================================================
 *  本人確認（メールはここから外に出さない）
 * ========================================================= */

function activeEmail_() {
  // 同一ドメインの利用者にしかメールを返さない（＝学校アカウント限定が自動で成立）
  try { return String(Session.getActiveUser().getEmail() || '').toLowerCase(); } catch (e) { return ''; }
}

function ownerDomain_() {
  var owner = '';
  try { owner = String(Session.getEffectiveUser().getEmail() || ''); } catch (e) { }
  return owner ? owner.slice(owner.indexOf('@') + 1) : '';
}

function webAppUrl_() {
  try { return ScriptApp.getService().getUrl() || ''; } catch (e) { return ''; }
}

/** メール → 不透明ID。対応表は students シートにだけ置く */
function resolveStudentId_(email) {
  var sh = sheet_(SH_STUDENTS, ['メール', '生徒ID', '初回']);
  var v = sh.getDataRange().getValues();
  for (var i = 1; i < v.length; i++) if (String(v[i][0]).toLowerCase() === email) return String(v[i][1]);
  var sid = 'stu_' + Utilities.getUuid().replace(/-/g, '').slice(0, 12);
  sh.appendRow([email, sid, new Date()]);
  return sid;
}

function emailBySid_(sid) {
  var sh = sheet_(SH_STUDENTS, ['メール', '生徒ID', '初回']);
  var v = sh.getDataRange().getValues();
  for (var i = 1; i < v.length; i++) if (String(v[i][1]) === sid) return String(v[i][0]);
  return sid;   // 見つからなければIDのまま出す
}

/* ---- 署名トークン（この先生のGASの鍵でしか作れない） ---- */

function signingKey_() {
  var props = PropertiesService.getScriptProperties();
  var k = props.getProperty('SIGNING_KEY');
  if (!k) { k = Utilities.getUuid() + Utilities.getUuid(); props.setProperty('SIGNING_KEY', k); }
  return k;
}

function b64url_(x) { return Utilities.base64EncodeWebSafe(x).replace(/=+$/, ''); }

function signToken_(payload) {
  var p = b64url_(JSON.stringify(payload));
  return p + '.' + b64url_(Utilities.computeHmacSha256Signature(p, signingKey_()));
}

/** 正しければ payload を返す。ダメなら null */
function verifyToken_(token) {
  try {
    var i = token.indexOf('.');
    if (i < 0) return null;
    var p = token.slice(0, i), sig = token.slice(i + 1);
    if (b64url_(Utilities.computeHmacSha256Signature(p, signingKey_())) !== sig) return null;
    var payload = JSON.parse(Utilities.newBlob(Utilities.base64DecodeWebSafe(p)).getDataAsString());
    if (!payload.sid || Number(payload.exp) <= Date.now()) return null;
    return payload;
  } catch (e) { return null; }
}

/* =========================================================
 *  シート
 * ========================================================= */

function ss_() {
  var id = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  if (id) { try { return SpreadsheetApp.openById(id); } catch (e) { } }
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) throw new Error('スプレッドシートが見つかりません（シートを一度開いてください）');
  return ss;
}

function sheet_(name, headers) {
  var ss = ss_();
  var sh = ss.getSheetByName(name);
  if (sh) return sh;
  sh = ss.insertSheet(name);
  if (headers) {
    sh.getRange(1, 1, 1, headers.length).setValues([headers])
      .setFontWeight('bold').setBackground('#F4A26A');
    sh.setFrozenRows(1);
    sh.setColumnWidth(1, 240);
  }
  return sh;
}

/* _data の列
 *   detail … アプリが復元に使う生データ（例: タコスパーティー='11010'、WordTacos='0,1,3'）。
 *            集計値だけでは端末をまたいだ復元が正確にできないので、原本をここに置く。
 *   stats  … アプリ固有の集計値のJSON（例: {"words":120,"tacos":40,"excellent":31}）。
 *            何を出すかはアプリのマニフェスト（manifest.stats）が決める。ダッシュボードで合計して表示する。
 *   ※ 列を足すときは必ず**末尾**に足すこと。途中に挿すと既存シートの列がずれる。 */
var DATA_COLS = ['sid', 'item', 'plays', 'clears', 'best', 'perfect', 'cell', 'detail', 'lastAt', 'stats'];
var C_STATS = 9;   // stats の 0 始まり列番号

function dataSheet_() {
  var sh = sheet_(SH_DATA, DATA_COLS);
  if (!sh.isSheetHidden()) sh.hideSheet();
  // 古いシート（stats 列が無い）を開いたときに見出しを足す
  if (sh.getLastColumn() < DATA_COLS.length) {
    sh.getRange(1, 1, 1, DATA_COLS.length).setValues([DATA_COLS]).setFontWeight('bold').setBackground('#F4A26A');
  }
  return sh;
}

/** アプリが出したい集計項目 [{key,label}]。アプリのマニフェストが決める */
function statDefs_() {
  var v = manifest_().stats;
  return Array.isArray(v) ? v : [];
}

function parseStats_(v) {
  if (!v) return {};
  try { var o = JSON.parse(v); return (o && typeof o === 'object') ? o : {}; } catch (e) { return {}; }
}

/** 集計値は「増える一方」なので大きい方を採る（送信が前後しても減らない） */
function mergeStats_(a, b) {
  var out = {}, k;
  for (k in a) out[k] = Number(a[k]) || 0;
  for (k in b) out[k] = Math.max(out[k] || 0, Number(b[k]) || 0);
  return out;
}

/** _data を丸ごと1回だけ読む（項目ごとに読み直すとシートI/Oが項目数ぶん増えて遅い） */
function readData_() {
  var sh = dataSheet_();
  var last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, DATA_COLS.length).getValues() : [];
  var idx = {};
  for (var i = 0; i < rows.length; i++) idx[rows[i][0] + ' ' + rows[i][1]] = i;
  return { sh: sh, rows: rows, idx: idx };
}

function truthy_(v) { return v === true || String(v).toUpperCase() === 'TRUE'; }

/**
 * entries をまとめて upsert（回数は多い方・タイムは速い方・perfect と cell/detail は最新を採用）。
 * 書き込みは**最後に1回だけ**。項目ごとに setValues すると、まとめ送り（前回送れなかった分を
 * 起動時に全部送る等）のときにシートI/Oが項目数ぶん増え、GASの実行時間制限に当たる。
 */
function writeData_(d, sid, entries, now) {
  var dirty = false;
  entries.forEach(function (en) {
    var item = String(en.item || '').trim();
    if (!item) return;
    var plays = Number(en.plays) || 0;
    var clears = Number(en.clears) || 0;
    var best = Number(en.best) || 0;
    var stats = (en.stats && typeof en.stats === 'object') ? en.stats : {};
    var row = [sid, item, plays, clears, best > 0 ? best : '', !!en.perfect,
      String(en.cell == null ? '' : en.cell), String(en.detail == null ? '' : en.detail).slice(0, 4000),
      now, JSON.stringify(stats)];

    var i = d.idx[sid + ' ' + item];
    if (i === undefined) { d.idx[sid + ' ' + item] = d.rows.length; d.rows.push(row); dirty = true; return; }

    var cur = d.rows[i];
    var prevBest = Number(cur[4]);
    row[2] = Math.max(Number(cur[2]) || 0, plays);
    row[3] = Math.max(Number(cur[3]) || 0, clears);
    row[4] = (best > 0) ? (prevBest > 0 ? Math.min(prevBest, best) : best) : (prevBest > 0 ? prevBest : '');
    row[5] = truthy_(cur[5]) || !!en.perfect;
    if (!row[6]) row[6] = cur[6];
    if (!row[7]) row[7] = cur[7];
    row[C_STATS] = JSON.stringify(mergeStats_(parseStats_(cur[C_STATS]), stats));
    d.rows[i] = row;
    dirty = true;
  });
  if (dirty && d.rows.length) d.sh.getRange(2, 1, d.rows.length, DATA_COLS.length).setValues(d.rows);
}

function progressFrom_(d, sid) {
  var out = {};
  d.rows.forEach(function (r) {
    if (String(r[0]) !== sid) return;
    var b = Number(r[4]);
    out[String(r[1])] = {
      plays: Number(r[2]) || 0,
      clears: Number(r[3]) || 0,
      best: b > 0 ? b : null,
      perfect: truthy_(r[5]),
      cell: String(r[6] || ''),
      detail: String(r[7] || ''),
      stats: parseStats_(r[C_STATS]),
    };
  });
  return out;
}

function getProgress_(sid) { return progressFrom_(readData_(), sid); }

/* ---- 進捗シート（先生が見る一覧）
 *      1行目 = 項目ID（非表示・機械用） / 2行目 = 見出し / 3行目〜 = 生徒 ---- */

function progressSheet_() {
  var ss = ss_();
  var sh = ss.getSheetByName(SH_PROGRESS);
  if (sh) return sh;
  sh = ss.insertSheet(SH_PROGRESS, 0);
  sh.getRange(1, 1, 1, 4).setValues([['_id', '_plays', '_done', '_rate']]);
  sh.getRange(2, 1, 1, 4).setValues([['生徒（メール）', '総プレイ', '達成数', '到達率']])
    .setFontWeight('bold').setBackground('#F4A26A');
  sh.setFrozenRows(2);
  sh.setFrozenColumns(1);
  sh.hideRows(1);
  sh.setColumnWidth(1, 240);
  applyHeaders_();                       // マニフェストの見出し・非表示設定を反映
  return sh;
}

/**
 * 進捗シートの1行を更新する。シートI/Oは「読み1 + 列追加 + 値1 + 色1」に固定してある。
 * （項目ごとに setValue すると、まとめ送りのときに実行時間制限に当たる）
 */
function rebuildProgressRow_(email, entries, p) {
  var sh = progressSheet_();

  // --- 列（1行目=項目ID / 2行目=見出し）。無い項目は右端に足す。レッスンが増えても自動追随する
  var lastCol = sh.getLastColumn();
  var ids = sh.getRange(1, 1, 1, lastCol).getValues()[0];
  var colOf = {};
  for (var c = 4; c < ids.length; c++) if (ids[c]) colOf[String(ids[c])] = c + 1;

  var newIds = [], newLabels = [];
  entries.forEach(function (en) {
    var item = String(en.item || '');
    if (!item || colOf[item]) return;
    colOf[item] = lastCol + newIds.length + 1;
    newIds.push(item);
    newLabels.push(String(en.label || item));
  });
  if (newIds.length) {
    sh.getRange(1, lastCol + 1, 1, newIds.length).setValues([newIds]);
    sh.getRange(2, lastCol + 1, 1, newLabels.length).setValues([newLabels])
      .setFontWeight('bold').setBackground('#F4A26A').setWrap(true);
    for (var k = 0; k < newIds.length; k++) sh.setColumnWidth(lastCol + 1 + k, 96);
    lastCol += newIds.length;
    ids = sh.getRange(1, 1, 1, lastCol).getValues()[0];
  }

  // --- 生徒の行（3行目以降）。表示はメール
  var row = -1;
  var last = sh.getLastRow();
  if (last >= 3) {
    var names = sh.getRange(3, 1, last - 2, 1).getValues();
    for (var i = 0; i < names.length; i++) {
      if (String(names[i][0]).toLowerCase() === String(email).toLowerCase()) { row = i + 3; break; }
    }
  }
  if (row < 0) row = Math.max(3, sh.getLastRow() + 1);

  // --- 行を丸ごと組み立てて、値と色をそれぞれ1回で書く
  var vals = sh.getRange(row, 1, 1, lastCol).getValues()[0];
  var bgs = new Array(lastCol);
  vals[0] = email;

  var plays = 0, done = 0, total = 0;
  for (var j = 4; j < lastCol; j++) {
    var id = String(ids[j] || '');
    bgs[j] = null;                                   // 触らない列は色を変えない
    if (!id) continue;
    total++;
    var q = p[id];
    if (!q) continue;
    plays += q.plays;
    if (q.clears > 0) done++;
    vals[j] = q.cell || '';
    bgs[j] = q.perfect ? '#D9EAD3' : (q.clears > 0 ? '#EAF4EC' : '#FFF8EE');
  }
  vals[1] = plays;
  vals[2] = done;
  vals[3] = total ? Math.round(done * 100 / total) + '%' : '0%';
  for (var b = 0; b < 4; b++) bgs[b] = null;

  sh.getRange(row, 1, 1, lastCol).setValues([vals]).setWrap(true);
  sh.getRange(row, 1, 1, lastCol).setBackgrounds([bgs]);
}

/* =========================================================
 *  デプロイ管理（makehtmlslide-viewer-dev / MINERALIA と同方式）
 *   URLが変わったときだけシートに触る（通常のPOSTではシートI/Oゼロ）
 * ========================================================= */

function recordAccess() {
  var url = webAppUrl_();
  if (!url || url.slice(-4) === '/dev') return url;

  var props = PropertiesService.getScriptProperties();
  if (props.getProperty('lastDeployUrl') === url) return url;    // 通常はここで終わる

  var ss = ss_();
  var sheet = getOrCreateDeploySheet_(ss);

  if (!props.getProperty('instanceId')) {          // コピー直後 → 前の先生のデータを消す
    if (hasExistingData_(ss)) clearAllData_(ss);
    props.setProperty('instanceId', '1');
    props.deleteProperty('SIGNING_KEY');           // 鍵も作り直す（前の先生のトークンを無効化）
  }

  var lastUrl = sheet.getRange(3, 2).getValue();
  if (lastUrl !== url) {
    var lastVersion = sheet.getRange(3, 3).getValue();
    var newVersion = (typeof lastVersion === 'number') ? lastVersion + 1 : 1;
    sheet.insertRowAfter(2);
    sheet.getRange(3, 1, 1, 3).setValues([[new Date(), url, newVersion]]);
    sheet.getRange(3, 1).setNumberFormat('yyyy/MM/dd HH:mm:ss');
  }
  props.setProperty('lastDeployUrl', url);
  return url;
}

function hasExistingData_(ss) {
  return ss.getSheets().some(function (sh) {
    var n = sh.getName();
    if ((n === SH_PROGRESS || n === SH_LOG || n === SH_STUDENTS || n === SH_DATA || n === SH_WALLET) && sh.getLastRow() > 1) return true;
    if (n === SH_DEPLOY && sh.getRange(3, 2).getValue()) return true;
    return false;
  });
}

function clearAllData_(ss) {
  PropertiesService.getScriptProperties().deleteProperty('instanceId');
  ss.getSheets().forEach(function (sh) {
    var n = sh.getName();
    if (n === SH_LOG || n === SH_STUDENTS || n === SH_DATA || n === SH_WALLET) {
      if (sh.getLastRow() > 1) sh.deleteRows(2, sh.getLastRow() - 1);
    } else if (n === SH_PROGRESS) {
      if (sh.getLastRow() > 2) sh.deleteRows(3, sh.getLastRow() - 2);
    } else if (n === SH_DEPLOY) {
      sh.clear(); setupDeployHeader_(sh);
    }
  });
}

function getOrCreateDeploySheet_(ss) {
  var sh = ss.getSheetByName(SH_DEPLOY);
  if (!sh) { sh = ss.insertSheet(SH_DEPLOY); setupDeployHeader_(sh); }
  else if (!sh.getRange(2, 1).getValue()) setupDeployHeader_(sh);
  return sh;
}

function setupDeployHeader_(sh) {
  sh.getRange('A1').setValue('⚠ 他の先生に配るときは、メニュー「🌮 … → 🎁 配布用に初期化」を実行してから「コピーを作成」で渡してください')
    .setFontColor('#cc0000').setFontWeight('bold');
  sh.getRange(2, 1, 1, 3).setValues([['日時', 'URL', 'Ver']])
    .setBackground('#4a86e8').setFontColor('#ffffff').setFontWeight('bold');
  sh.setColumnWidth(1, 150); sh.setColumnWidth(2, 460); sh.setColumnWidth(3, 50);
  sh.setFrozenRows(2);
}

/* =========================================================
 *  表示・メニュー
 * ========================================================= */

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function escapeHtml_(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function html_(lead, body) {
  return HtmlService.createHtmlOutput(
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><base target="_top">'
    + '<meta name="viewport" content="width=device-width,initial-scale=1">'
    + '<title>' + escapeHtml_(appTitle_()) + '</title><style>'
    + 'body{font-family:"Hiragino Sans","Yu Gothic",sans-serif;background:#FFF8EE;color:#2A1F14;'
    + 'text-align:center;padding:56px 20px;margin:0}'
    + 'h2{color:#C73E1D;margin:0 0 12px;font-size:1.3rem}'
    + 'p{color:#6B5A47;font-size:14px;line-height:1.8}.sub{font-size:12px;color:#8B7355;margin-top:18px}'
    + 'a.go{display:inline-block;margin-top:8px;padding:16px 44px;font-size:17px;font-weight:700;'
    + 'background:#C73E1D;color:#fff;text-decoration:none;border-radius:999px;'
    + 'box-shadow:0 6px 16px rgba(199,62,29,.35)}'
    + '</style></head><body><h2>🌮 ' + escapeHtml_(appTitle_()) + '</h2><p>' + lead + '</p>'
    + body + '</body></html>');
}

/** スプレッドシートを開いたとき: SHEET_ID を保存し、メニューを出す */
function onOpen() {
  try { PropertiesService.getScriptProperties().setProperty('SHEET_ID', SpreadsheetApp.getActiveSpreadsheet().getId()); } catch (e) { }
  SpreadsheetApp.getUi().createMenu('🌮 ' + appTitle_())
    .addItem('📊 クラスの進捗を見る', 'showDashboard')
    .addItem('📎 サイドバーで見る', 'showDashboardSidebar')
    .addSeparator()
    .addItem('🔗 生徒に配るURLを表示', 'showUrl')
    .addItem('⚙️ サイトURLを設定', 'setAppUrlPrompt')
    .addItem('🎮 自分でプレイする（記録あり）', 'playAsTeacher')
    .addSeparator()
    .addItem('シートを初期化（この先生の分を全消去）', 'resetAll')
    .addItem('🎁 配布用に初期化（設定だけ残して全削除）', 'resetForHandoff')
    .addToUi();
}

function setAppUrlPrompt() {
  var ui = SpreadsheetApp.getUi();
  var res = ui.prompt('サイトURLを設定',
    '生徒が遊ぶアプリのURL（https://…）を貼り付けてください。\n現在: ' + (appUrl_() || '未設定'),
    ui.ButtonSet.OK_CANCEL);
  if (res.getSelectedButton() !== ui.Button.OK) return;
  if (!setAppUrl_(res.getResponseText())) { ui.alert('https:// で始まるURLを入れてください'); return; }
  ui.alert('設定しました:\n' + appUrl_());
}

function showUrl() {
  var entry = webAppUrl_();
  SpreadsheetApp.getUi().alert(
    '生徒に配るURL\n\n' + (entry || '（まだデプロイされていません）')
    + (appUrl_() ? '' : '\n\n⚠ サイトURLが未設定です。メニュー「⚙️ サイトURLを設定」から設定してください。')
    + '\n\nClassroom や QR で配ってください。'
    + '\n生徒が学校のGoogleアカウントで開くと、そのまま ' + appTitle_() + ' が始まり、'
    + '\nここから先の学習がこのスプレッドシートに記録されます。'
);
}

function resetAll() {
  var ui = SpreadsheetApp.getUi();
  if (ui.alert('この先生の記録をすべて消します。よろしいですか？', ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
  clearAllData_(ss_());
  PropertiesService.getScriptProperties().setProperty('instanceId', '1');
  ui.alert('消去しました。');
}

/** 配布用に初期化: 「設定」だけ残して他のシートを全部削除し、記録・署名鍵を白紙に戻す。
 *  他の先生がこのスプレッドシートをコピーすれば、まっさらな自分専用DBとして使える。
 *  ・サイトURL（設定シートB2）は残す ── コピーに引き継ぐための設定なので消さない。
 *  ・データ系シート（進捗/ログ/students/_data/_wallet/デプロイ管理 と手作りシート）は削除。次回アクセスで自動再生成される。
 *  ・鍵などのスクリプトプロパティは元々コピーで引き継がれないが、原本も白紙にしておく。 */
function resetForHandoff() {
  var ui = SpreadsheetApp.getUi();
  if (ui.alert('配布用に初期化',
      '「設定」以外のシート（進捗 / ログ / students / _data / _wallet / デプロイ管理 など）を\n'
      + 'すべて削除し、記録と署名鍵を白紙に戻します。\n'
      + 'サイトURL（設定シートのB2）は残します。\n\n'
      + '※ 元に戻せません。他の先生に配る直前にだけ実行してください。\n\n実行しますか？',
      ui.ButtonSet.YES_NO) !== ui.Button.YES) return;

  var ss = ss_();
  var keep = settingsSheet_();                 // 「設定」は必ず残す（無ければ作る）
  ss.getSheets().forEach(function (sh) {
    if (sh.getSheetId() !== keep.getSheetId()) ss.deleteSheet(sh);
  });

  // インスタンス固有の値を白紙化（コピーには元々引き継がれないが、原本もきれいにする）
  var props = PropertiesService.getScriptProperties();
  ['SIGNING_KEY', 'instanceId', 'lastDeployUrl'].forEach(function (k) { props.deleteProperty(k); });

  ui.alert('配布用の初期化が完了しました。\n\n'
    + 'このスプレッドシートを「ファイル → コピーを作成」で配ってください。\n'
    + 'コピーした先生は、デプロイして出たURLを生徒に配るだけで使えます。');
}

/* =========================================================
 *  先生用ダッシュボード（シートの上に出す。表を目で追わなくていいように）
 * ========================================================= */

function showDashboard() {
  var html = HtmlService.createHtmlOutputFromFile('Dashboard')
    .setWidth(1180).setHeight(760).setTitle(appTitle_() + ' ・ クラスの進捗');
  SpreadsheetApp.getUi().showModalDialog(html, appTitle_() + ' ・ クラスの進捗');
}

function showDashboardSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Dashboard').setTitle('クラスの進捗');
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * 先生自身がプレイして、その記録もこのシートに残すための入口。
 *
 * 先生も「生徒に配るURL」を踏めば、生徒とまったく同じ経路で記録される（先生だけの特別扱いは無い）。
 * ただし先生は普段ブックマークやホーム画面からアプリを直接開くはずで、その経路には
 * トークンが付かないので記録されない。だからここから開いてもらう。
 * 一度ここから開けば端末にトークンが残るので、次からは直接開いても記録され続ける。
 */
function playAsTeacher() {
  var url = webAppUrl_();
  if (!url) { SpreadsheetApp.getUi().alert('先にウェブアプリとしてデプロイしてください。'); return; }
  var safe = url.replace(/"/g, '%22');
  var html = HtmlService.createHtmlOutput(
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><base target="_blank"><style>'
    + 'body{font-family:"Hiragino Sans","Yu Gothic",sans-serif;background:#FFF8EE;color:#2A1F14;'
    + 'text-align:center;padding:26px 22px;margin:0;font-size:13px;line-height:1.8}'
    + 'p{color:#6B5A47;margin:0 0 6px}.sub{font-size:11.5px;color:#8B7355;margin-top:16px}'
    + 'a.go{display:inline-block;margin-top:12px;padding:14px 40px;font-size:15px;font-weight:800;'
    + 'background:#C73E1D;color:#fff;text-decoration:none;border-radius:999px;'
    + 'box-shadow:0 6px 16px rgba(199,62,29,.3)}</style></head><body>'
    + '<p>先生自身のプレイも、このシートに記録されます。<br>下のボタンから開いてください。</p>'
    + '<a class="go" href="' + safe + '">🎮 ' + escapeHtml_(appTitle_()) + ' を開く</a>'
    + '<p class="sub">一度ここから開けば、その端末にはログイン情報が残ります。<br>'
    + '次からはブックマークやホーム画面から開いても記録され続けます。<br>'
    + 'ダッシュボードでは先生の行に「先生」と表示され、初期状態ではクラスの集計から外れます。</p>'
    + '</body></html>').setWidth(460).setHeight(300);
  SpreadsheetApp.getUi().showModalDialog(html, '自分でプレイする');
}

/**
 * ダッシュボードへ渡すデータ。
 *   項目の並びは「進捗」シートの列順（＝生徒が実際に触った順に増える）に合わせる。
 *   _data と students を1回ずつ読むだけで組み立てる。
 */
function dashData() {
  var d = readData_();

  // 生徒ID → メール
  var st = sheet_(SH_STUDENTS, ['メール', '生徒ID', '初回']).getDataRange().getValues();
  var mail = {};
  for (var i = 1; i < st.length; i++) mail[String(st[i][1])] = String(st[i][0]);

  // 項目（ID → 見出し）。進捗シートの列順を正とする
  var ps = progressSheet_();
  var lastCol = ps.getLastColumn();
  var head = lastCol >= 5 ? ps.getRange(1, 1, 2, lastCol).getValues() : [[], []];
  var items = [], seen = {};
  for (var c = 4; c < lastCol; c++) {
    var id = String(head[0][c] || '');
    if (!id || seen[id]) continue;
    seen[id] = 1;
    items.push({ id: id, label: String(head[1][c] || id) });
  }

  // 生徒ごとに集計。stats（学習済み単語・Tacos など）は項目をまたいで足し合わせる
  var defs = statDefs_();
  var by = {};
  d.rows.forEach(function (r) {
    var sid = String(r[0]), item = String(r[1]);
    if (!sid || !item) return;
    var s = by[sid] || (by[sid] = { email: mail[sid] || sid, plays: 0, done: 0, last: 0, cells: {}, stats: {} });
    var clears = Number(r[3]) || 0;
    s.plays += Number(r[2]) || 0;
    if (clears > 0) s.done++;
    var t = r[8] instanceof Date ? r[8].getTime() : 0;
    if (t > s.last) s.last = t;
    s.cells[item] = { cell: String(r[6] || ''), clears: clears, perfect: truthy_(r[5]) };

    var st = parseStats_(r[C_STATS]);
    defs.forEach(function (def) { s.stats[def.key] = (s.stats[def.key] || 0) + (Number(st[def.key]) || 0); });
  });

  // 先生自身のプレイも同じように記録される。行は出すが、印を付けて区別できるようにする
  var owner = '';
  try { owner = String(Session.getEffectiveUser().getEmail() || '').toLowerCase(); } catch (e) { }

  var students = Object.keys(by).map(function (sid) {
    var s = by[sid];
    s.rate = items.length ? (s.done * 100 / items.length) : 0;
    s.me = !!owner && String(s.email).toLowerCase() === owner;
    return s;
  });

  return { app: appTitle_(), now: Date.now(), items: items, students: students, statDefs: defs, headers: headers_() };
}

/** 初期設定（1度だけ実行。シートを作り、鍵を用意する） */
function setup() {
  settingsSheet_();
  sheet_(SH_STUDENTS, ['メール', '生徒ID', '初回']);
  sheet_(SH_LOG, ['日時', '生徒', '項目ID', '項目', '内容']);
  dataSheet_();
  walletSheet_();
  progressSheet_();
  getOrCreateDeploySheet_(ss_());
  signingKey_();
  try { PropertiesService.getScriptProperties().setProperty('SHEET_ID', ss_().getId()); } catch (e) { }
  return 'OK: ' + appTitle_() + ' / ドメイン=' + (ownerDomain_() || '不明') + ' / URL=' + (webAppUrl_() || '未デプロイ');
}
