const CACHE_NAME = 'resqmar-pwa-v1';
const ASSETS_TO_CACHE = [
  '/frontend/pwa/index.html',
  '/frontend/pwa/manifest.json',
  '/frontend/pwa/app.js',
  '/frontend/pwa/styles.css',
  '/data/edge_dataset.json'
];

self.addEventListener('install', event => {
  console.log('[SW] Install started');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Caching app shell');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => {
        console.log('[SW] Install complete');
        return self.skipWaiting();
      })
  );
});

self.addEventListener('activate', event => {
  console.log('[SW] Activate');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // API calls - Network first, fallback to cache
  if (url.pathname.startsWith('/edge/') || url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .catch(async () => {
          console.log('[SW] Network fetch failed, checking cache for', event.request.url);
          const cached = await caches.match(event.request);
          if (cached) return cached;
          
          return new Response(
            JSON.stringify({ error: "Offline mode active", source: "cache" }),
            { headers: { 'Content-Type': 'application/json' } }
          );
        })
    );
    return;
  }

  // App shell - Cache first, fallback to network
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          console.log('[SW] Serving from cache:', event.request.url);
          return response;
        }
        console.log('[SW] Fetching from network:', event.request.url);
        return fetch(event.request);
      })
  );
});

self.addEventListener('sync', event => {
  if (event.tag === 'sync-questions') {
    console.log('[SW] Background sync triggered');
    // Implement background queue logic here if needed
  }
});

self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
