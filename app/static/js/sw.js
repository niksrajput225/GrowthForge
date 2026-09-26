/**
 * GrowthForge PWA Offline Service Worker
 * Ensures offline resiliency for Android WebView & Play Store compliance
 */

const CACHE_NAME = 'growthforge-v1.0.0';
const STATIC_ASSETS = [
    '/',
    '/dashboard',
    '/static/css/app.css',
    '/static/js/app.js',
    '/static/icons/icon.svg',
    '/static/manifest.json'
];

// Install Event
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Pre-caching static app shell');
            return cache.addAll(STATIC_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// Activate Event
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(
                keyList.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[SW] Purging old cache:', key);
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch Event (Network first for API, Stale-while-revalidate for static)
self.addEventListener('fetch', (event) => {
    const request = event.request;
    
    // Ignore non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // API calls: Network first, fall back to offline JSON if failed
    if (request.url.includes('/api/')) {
        event.respondWith(
            fetch(request).catch(() => {
                return new Response(JSON.stringify({
                    success: false,
                    offline: true,
                    message: 'You are currently offline. Local cache active.'
                }), {
                    headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }

    // Static Assets & Navigation: Stale-While-Revalidate
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            const fetchPromise = fetch(request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, responseClone);
                    });
                }
                return networkResponse;
            }).catch(() => {
                // If network fails and we have a cached version, return cached
                return cachedResponse;
            });

            return cachedResponse || fetchPromise;
        })
    );
});
