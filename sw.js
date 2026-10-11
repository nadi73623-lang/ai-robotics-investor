const CACHE = 'robotics-v3-update-1';
const APP_FILES = ['./', './index.html', './manifest.webmanifest', './assets/icon.svg'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(APP_FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith('robotics-') && key !== CACHE).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.endsWith('/data/scan.json')) {
    event.respondWith(fetch(request).catch(() => caches.match(request)));
    return;
  }
  if (request.mode === 'navigate' || url.pathname.endsWith('/index.html')) {
    event.respondWith((async () => {
      try {
        const response = await fetch(request, {cache:'no-store'});
        if (response.ok) { const cache = await caches.open(CACHE); await cache.put('./index.html', response.clone()); }
        return response;
      } catch (_) {
        return (await caches.match('./index.html')) || Response.error();
      }
    })());
    return;
  }
  event.respondWith(fetch(request).then(async response => {
    if (response.ok) { const cache = await caches.open(CACHE); await cache.put(request, response.clone()); }
    return response;
  }).catch(() => caches.match(request)));
});
