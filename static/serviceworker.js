const CACHE_NAME = 'munter-v1';
const OFFLINE_URL = '/';
const FILES_TO_CACHE = [
  '/',
  '/static/style.css',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/chart.js',
  '/static/js/chart.min.js',

];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(FILES_TO_CACHE);
    })
  );
});

self.addEventListener('fetch', function (event) {
  event.respondWith(
    caches.match(event.request).then(function (response) {
      return response || fetch(event.request).catch(() => caches.match(OFFLINE_URL));
    })
  );
});
