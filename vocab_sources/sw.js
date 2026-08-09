// WordTacos Service Worker
// 静的アセットはキャッシュ優先、クイズ JSON / 音声は network-first → cache fallback。
// バージョンを上げると古いキャッシュは activate 時にすべて消える。
//
// ★重要: Cloudflare Pages の「クリーンURL」は /app.html → /app (308) のように
//   .html リクエストをリダイレクトする。リダイレクト済み(redirected=true)の
//   レスポンスをナビゲーションに返すと
//   "response served by service worker has redirections" が出て PWA が開けない。
//   → 起点は非リダイレクトの './'(=index.html) にし、保険で redirected を必ず剥がす。

const CACHE = 'wt-v53';
const SHELL = [
  './',                 // ルート = index.html を 200 で返す(リダイレクトなし)。PWA の起点。
  './manifest.json',
  './app_assets/icon-192.png',
  './app_assets/icon-512.png',
  './app_assets/icon-maskable-512.png',
];

// redirected フラグ付きのレスポンスを、中身そのままの 200 レスポンスに作り直して剥がす
async function cleanRedirect(res) {
  try {
    if (!res || !res.redirected) return res;
    const body = await res.blob();
    return new Response(body, { status: 200, statusText: 'OK', headers: new Headers(res.headers) });
  } catch (e) {
    return res;
  }
}

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // addAll は使わず、リダイレクトを追って(follow)→剥がして(clean)から保存する
    await Promise.allSettled(SHELL.map(async (u) => {
      try {
        const res = await fetch(new Request(u, { redirect: 'follow', cache: 'reload' }));
        if (res && res.ok) await cache.put(u, await cleanRedirect(res));
      } catch (e) {}
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // 外部(CDN)はネット直

  // クイズデータ・音声: network-first (新規問題追加に追従)
  const isData = /_quizzes_clean\.json$|app_audio\//.test(url.pathname);
  if (isData) {
    event.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match(req))
    );
    return;
  }

  // それ以外 (HTML/CSS/JS/画像): cache-first。redirected は必ず剥がして返す。
  event.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached.redirected ? cleanRedirect(cached) : cached;
    try {
      const res = await fetch(req, { redirect: 'follow' });
      const clean = (res && res.redirected) ? await cleanRedirect(res) : res;
      if (clean && clean.ok) {
        const c = await caches.open(CACHE);
        c.put(req, clean.clone()).catch(() => {});
      }
      return clean;
    } catch (e) {
      // オフライン等はシェル(ルート)を返す
      return (await caches.match('./')) || Response.error();
    }
  })());
});
