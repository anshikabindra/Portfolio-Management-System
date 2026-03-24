// CHANGED: Version updated to v2 to force a refresh
const CACHE_NAME = 'portfolio-hub-v2';

const ASSETS_TO_CACHE = [
  '/dashboard',
  '/static/manifest.json',
  // If you have a CSS file, add it here, e.g., '/static/css/style.css'
];

// Install event: Cache the essential files
self.addEventListener('install', (event) => {
  // ADDED: This forces the new service worker to become active immediately
  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

// Activate event: Clean up old caches (v1) and take control
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Deleting old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  // ADDED: Ensures the new code is used right away without needing a reload
  return self.clients.claim();
});

// Fetch event: Network first, fall back to cache if offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
