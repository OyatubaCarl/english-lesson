/**
 * GASflare クライアント — Teacher Tacos 共通
 *   （WordTacos / タコスパーティー / CalTacos で同じファイル）
 *
 * ■ 何が起きるか
 *   生徒は「先生が配ったURL（先生のGASウェブアプリ）」を踏む
 *     → GASが学校アカウントを確認し、署名付きトークンを付けてゲーム本体へ転送する
 *     → ゲームは ?tt=<token> を受け取り localStorage に保存する
 *     → 以降、進捗が変わるたび、トークンの中に書かれた**その先生のGAS**へ記録を送る
 *   つまり **踏んだURLの先生のスプレッドシートにだけ**データが溜まる。先生ごとに独立したDBになる。
 *
 * ■ 大原則
 *   GASが落ちていても、ネットが切れていても、**ゲームは絶対に止まらない**。
 *   進捗の正本はあくまで localStorage。クラウドはその写しにすぎない。
 *
 * ■ アプリ側の設定（このスクリプトを読み込む前に window.TT_GASFLARE を定義する）
 *   window.TT_GASFLARE = {
 *     app:     'tacosparty',              // localStorage のキー接頭辞
 *     manifest:{ title:'タコスパーティー', stats:[{key:'words',label:'学習済み単語'}] },
 *                                          // GASへの自己紹介。起動時のloadに添えて送られ、
 *                                          // メニュー名・ダッシュボードの集計列になる
 *     mount:   () => document.getElementById('...'),   // 状態表示を差し込む要素（省略可）
 *     collect: () => ([                    // 送る記録
 *       { item:'b1', label:'B1 ぼくのなまえ', cell:'🌮 完成', plays:3, clears:1, best:0, perfect:true },
 *     ]),
 *     apply:   (progress) => {...},        // クラウドの記録をローカルへ反映（マージはアプリ側の責任）
 *     onSynced:() => {},                   // 反映後に画面を描き直したいとき
 *   };
 */
(function () {
  'use strict';
  var CFG = window.TT_GASFLARE;
  if (!CFG || !CFG.app) return;

  var K_TOKEN = CFG.app + '_gf_token';
  var K_OWNER = CFG.app + '_gf_owner';   // この端末に入っている進捗は「誰のもの」か（sid）
  var K_BAK = CFG.app + '_gf_bak_';      // 別の生徒がログインしたとき、前の持ち主の進捗をここへ退避する
  var K_LOGQ = CFG.app + '_gf_logq';     // GASのログシートへ送る「出来事」の待ち行列
  var token = '';
  var claims = null;     // { sid, url, exp }

  /* ---------- トークン ---------- */

  function decode(t) {
    try {
      var p = t.split('.')[0].replace(/-/g, '+').replace(/_/g, '/');
      var o = JSON.parse(decodeURIComponent(escape(atob(p + '==='.slice((p.length + 3) % 4)))));
      if (!o.sid || !o.url || Number(o.exp) <= Date.now()) return null;   // 署名はGAS側で検証する
      return o;
    } catch (e) { return null; }
  }

  function adopt(t) {
    var c = decode(t);
    if (!c) return false;
    token = t; claims = c;
    try { localStorage.setItem(K_TOKEN, t); } catch (e) { }
    return true;
  }

  // 1) URLに ?tt= が付いていれば取り込み、アドレスバーからは消す（他人に見せない）
  try {
    var u = new URL(location.href);
    var tt = u.searchParams.get('tt');
    if (tt && adopt(tt)) {
      u.searchParams.delete('tt');
      history.replaceState(null, '', u.pathname + (u.search || '') + (u.hash || ''));
    }
  } catch (e) { }
  // 2) 無ければ前回のものを使う
  if (!token) { try { adopt(localStorage.getItem(K_TOKEN) || ''); } catch (e) { } }

  var on = function () { return !!(token && claims); };

  /* ---------- 端末の進捗の「持ち主」 ----------
   *
   * 【原則】**記録に残るのは、先生のURLから入って学習した分だけ。**
   *         端末に元からあった進捗が、あとからアカウントへ合流することは無い。
   *
   * localStorage は **Googleアカウントには紐づかない**（Chromeの同期対象外。オリジン×プロファイルに属する）。
   * だから「端末に進捗がある」ことは「その人がやった」ことを意味しない。友人の端末かもしれないし、
   * ログイン前に誰かが遊んだ分かもしれない。**端末の進捗は、誰のものか分からない。**
   *
   * そこで進捗に「持ち主(sid)」を刻み、
   *
   *   持ち主 == いまログインしている生徒  → 学校モードで貯めた分。そのまま送る（オフラインの分も届く）
   *   持ち主 != いまログインしている生徒  → **アカウント側の記録が正**。端末の進捗は捨て、サーバから読み直す。
   *                                        **端末の分は絶対に送らない。**
   *
   * 捨てるといっても消しはしない。K_BAK へ退避する。ただし **アカウントへ書き戻すことはしない**。
   * 書き戻すのは、ログアウトして端末が「個人モード（記録なし）」に戻ったときの匿名分だけ。
   */

  function appKeys() {
    try { return (CFG.keys && CFG.keys()) || []; } catch (e) { return []; }
  }
  function snapshot() {
    var o = {};
    appKeys().forEach(function (k) { var v = localStorage.getItem(k); if (v != null) o[k] = v; });
    return o;
  }
  function wipe() {
    appKeys().forEach(function (k) { try { localStorage.removeItem(k); } catch (e) { } });
  }
  function stashTo(owner) {
    try { localStorage.setItem(K_BAK + owner, JSON.stringify(snapshot())); } catch (e) { }
  }
  function restoreFrom(owner) {
    var raw = null;
    try { raw = localStorage.getItem(K_BAK + owner); } catch (e) { }
    if (!raw) return false;
    try {
      var o = JSON.parse(raw);
      Object.keys(o).forEach(function (k) { localStorage.setItem(k, o[k]); });
      localStorage.removeItem(K_BAK + owner);
      return true;
    } catch (e) { return false; }
  }

  /**
   * 持ち主が違う（＝他人の端末、または誰のものか分からない進捗）なら、端末側を捨ててアカウント側を正とする。
   * **端末の進捗をアカウントへ書き戻す経路は用意しない。** これがこの設計の一線。
   */
  function takeover() {
    // 鍵一覧が取れない＝端末の進捗を掃除できない。その場合は「送らない」側に倒す（安全側）
    if (!appKeys().length) return { switched: true };

    var owner = '';
    try { owner = localStorage.getItem(K_OWNER) || ''; } catch (e) { }
    if (owner === claims.sid) return { switched: false };   // 同じ生徒 → 学校モードの続き

    stashTo(owner || 'anon');        // 消しはしない（個人モードに戻ったときのために取っておく）
    wipe();                          // が、アカウントへは持ち込まない
    try { localStorage.setItem(K_OWNER, claims.sid); } catch (e) { }
    if (CFG.reload) { try { CFG.reload(); } catch (e) { } }   // メモリ上の状態も読み直す
    return { switched: true };
  }

  /* ---------- 通信 ---------- */

  function api(payload, keepalive) {
    if (!on()) return Promise.resolve(null);
    payload.tt = token;
    return fetch(claims.url, {
      method: 'POST',
      // text/plain = 「単純リクエスト」→ プリフライト(OPTIONS)が飛ばない。
      // GASはOPTIONSに応答できないので、これが唯一の通し方。
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload),
      redirect: 'follow',
      // 離脱時の送信は keepalive を付ける。付けないとページが消えた時点で fetch が中断される
      keepalive: !!keepalive,
    })
      .then(function (r) { return r.json(); })
      .catch(function () { return null; });     // つながらなくてもゲームは続く
  }

  function pull() {
    if (!on()) return Promise.resolve();
    // manifest = アプリの自己紹介（タイトル・集計項目）。GASはこれを覚えて表示に使う。
    // アプリを更新すれば全先生のGASに自動で行き渡る（GAS側のコードは全アプリ共通のまま）
    return api({ action: 'load', manifest: CFG.manifest || null }).then(function (r) {
      if (!r) return;                            // 通信失敗 → 何もしない（ローカルのまま遊ぶ）
      if (!r.ok) { if (r.error === 'bad_token') signOut(); return; }
      if (CFG.apply && r.progress) CFG.apply(r.progress);
      if (CFG.onSynced) CFG.onSynced();
      note('');
    });
  }

  function push(keepalive) {
    if (!on() || !CFG.collect) return Promise.resolve();
    clearTimeout(timer); timer = null;
    var entries;
    try { entries = CFG.collect() || []; } catch (e) { return Promise.resolve(); }
    var q = logq();
    var logs = q.slice(0, 50);
    if (!entries.length && !logs.length) return Promise.resolve();   // 送るものが無い
    var payload = { action: 'record', entries: entries };
    if (logs.length) payload.log = logs.map(function (l) { return { item: l.item, label: l.label, text: l.text }; });
    return api(payload, keepalive).then(function (r) {
      var ok = !!(r && r.ok);
      note(ok ? '' : 'あとで保存します');
      // 送れた**ときだけ**「送信済み」にする。失敗分は残り、次のpushで必ず送り直される。
      if (ok && CFG.onPushed) { try { CFG.onPushed(entries); } catch (e) { } }
      if (ok && logs.length) {
        var sent = {}; logs.forEach(function (l) { sent[l.ts] = 1; });
        var rest = logq().filter(function (l) { return !sent[l.ts]; });
        try { localStorage.setItem(K_LOGQ, JSON.stringify(rest)); } catch (e) { }
      }
      return r;
    });
  }

  var timer = null;
  function pushLater() {                    // 進捗が動くたび呼ぶ。まとめて1回だけ送る
    if (!on()) return;
    clearTimeout(timer);
    timer = setTimeout(function () { push(); }, 2500);
  }

  /* ---------- 出来事ログ ----------
   * アプリが「レッスン合格」「タコス完成」のような出来事を1行ずつ残す。
   * GASのログシートに時系列で溜まり、先生が生データとして追える。
   * 送信に失敗しても待ち行列に残り、次のpushで必ず届く（進捗と同じ考え方）。 */
  function logq() {
    try { return JSON.parse(localStorage.getItem(K_LOGQ) || '[]'); } catch (e) { return []; }
  }
  function logEvent(item, label, text) {
    if (!on()) return;                       // 個人モードでは出来事を残さない（記録先が無い）
    var q = logq();
    q.push({ item: String(item || ''), label: String(label || ''), text: String(text || ''),
             ts: Date.now() + '_' + Math.floor(Math.random() * 1e6) });
    try { localStorage.setItem(K_LOGQ, JSON.stringify(q.slice(-200))); } catch (e) { }
    pushLater();
  }

  /** 記録をやめる。いまの持ち主のぶんを退避し、この端末で匿名で遊んでいた分があれば書き戻す */
  function signOut() {
    var sid = claims && claims.sid;
    if (sid) {
      stashTo(sid);
      wipe();
      restoreFrom('anon');
      try { localStorage.removeItem(K_OWNER); } catch (e) { }
      if (CFG.reload) { try { CFG.reload(); } catch (e) { } }
    }
    token = ''; claims = null;
    try { localStorage.removeItem(K_TOKEN); } catch (e) { }
    render();
    if (CFG.onSynced) { try { CFG.onSynced(); } catch (e) { } }
  }

  // 離脱時に取りこぼさない（keepalive付き。付けないとページが消えた時点で送信が中断される）
  window.addEventListener('pagehide', function () { if (timer) push(true); });
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden' && timer) push(true);
  });

  /* ---------- 表示 ---------- */

  var msg = null;
  function note(t) { if (msg) { msg.textContent = t || ''; msg.style.display = t ? 'block' : 'none'; } }

  function render() {
    var mount = CFG.mount && CFG.mount();
    if (!mount) return;
    mount.innerHTML = '';
    if (!on()) return;                     // 先生のURL経由でなければ何も出さない（普通に遊べる）
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'gf-badge';
    b.textContent = '☁️ 記録中';
    b.title = '先生のクラスに記録されています（タップで詳細）';
    b.onclick = function () {
      if (confirm('学習の記録が先生のシートに保存されています。\n\n記録をやめますか？\n（進捗そのものは端末に残ります。先生のURLをもう一度開けば再開します）')) signOut();
    };
    msg = document.createElement('div');
    msg.className = 'gf-note';
    msg.style.display = 'none';
    mount.appendChild(b);
    mount.appendChild(msg);
  }

  /* 起動時
   *   1) 端末の進捗の持ち主を確かめる（違えば、アカウント側を正として端末側を捨てる）
   *   2) クラウドの記録を取り込む
   *   3) 未送信分を送り直す ＝ 取りこぼしの修復
   *      ただし「持ち主が入れ替わって、自分の記録がこの端末に無かった」場合は送らない。
   *      端末に残っていたのは他人の進捗なので、自分のアカウントへ足してはいけない。
   */
  function boot() {
    render();
    if (!on()) return;
    var t = takeover();
    pull().then(function () {
      if (t.switched) {
        // 端末の進捗は捨てた。いまローカルにあるのはサーバの写しそのもの。
        // 送り返す必要はないので「送信済み」として覚え、**何も送らない**。
        if (CFG.onPushed && CFG.collect) { try { CFG.onPushed(CFG.collect()); } catch (e) { } }
        return;
      }
      return push();   // 同じ生徒の続き → 未送信分（オフラインで進めた分）を送る
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  window.gasflare = {
    get on() { return on(); },
    get sid() { return claims && claims.sid; },
    push: push, pushLater: pushLater, pull: pull, render: render, signOut: signOut,
    log: logEvent,
  };
})();
