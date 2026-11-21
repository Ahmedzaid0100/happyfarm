const CACHE_NAME = 'crazy-farm-static-v1';
const STATIC_ASSETS = [
  './',
  'index.html',
  'assets/libs/telegram-web-app.js',
  'assets/libs/supabase.min.js',
  'assets/libs/tonconnect-ui.min.js',
  'assets/libs/three.r128.min.js',
  'assets/libs/GLTFLoader.js',
  'assets/libs/tailwindcss.min.js',
  'assets/fonts/fonts.css',
  'assets/fonts/fredoka-variable.woff2',
  'assets/fonts/tajawal-500-arabic.woff2',
  'assets/fonts/tajawal-700-arabic.woff2',
  'assets/fonts/tajawal-800-arabic.woff2',
  'assets/fonts/tajawal-900-arabic.woff2'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[SW] Pre-caching warning:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Bypass caching for APIs, Ads, Supabase, and non-GET requests
  if (
    event.request.method !== 'GET' ||
    url.hostname.includes('supabase.co') ||
    url.hostname.includes('telegram.org') ||
    url.hostname.includes('adsgram') ||
    url.hostname.includes('libtl.com') ||
    url.hostname.includes('tads.me') ||
    url.pathname.startsWith('/rest/v1')
  ) {
    return;
  }

  // Cache-first for local static assets (libs, fonts, images)
  if (url.origin === self.location.origin && (url.pathname.includes('/assets/') || STATIC_ASSETS.includes(url.pathname))) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const clone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // Network-first for other requests
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
