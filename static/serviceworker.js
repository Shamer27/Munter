// static/service-worker.js

// 🔁 Bump this to force an update when you change cached files
const CACHE_NAME = 'munter-v3';

// ✅ Add every route & static file your app needs to work offline
// Include your key pages, CSS, JS, images, manifest, icons, rank badges, etc.
const ASSETS = [
  '/',                // home
  '/stats',
  '/ranks',
  '/add',

  // CSS
  '/static/css/style.css',

  // JS (use your local copy if you need offline)
  '/static/js/chart.min.js',   // make sure this file exists if you reference it

  // Manifest & icons (adjust filenames to yours)
  '/static/manifest.json',
  '/static/images/favicon.png',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',

  // Rank images
  '/static/images/ranks/bronze.png',
  '/static/images/ranks/silver.png',
  '/static/images/ranks/gold.png',
  '/static/images/ranks/platinum.png',
  '/static/images/ranks/diamond.png',
  '/static/images/ranks/monster.png',



];

// Install: precache app shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting(); // activate immediately
});

// Activate: clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) return caches.delete(key);
      }))
    )
  );
  self.clients.claim();
});

// Fetch: offline-first for navigations & static assets
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // For navigation requests (HTML pages), try cache, else network, else fallback
  if (req.mode === 'navigate') {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req)
          .then((res) => {
            // Clone & cache a copy of successful responses
            const resClone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
            return res;
          })
          .catch(() => caches.match('/static/offline.html'));
      })
    );
    return;
  }

  // For static assets: cache-first, then network, then no-op
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        // Cache successful GET responses
        if (req.method === 'GET' && res && res.status === 200) {
          const resClone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
        }
        return res;
      });
    })
  );
});
