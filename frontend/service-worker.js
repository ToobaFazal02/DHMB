const CACHE_NAME = "dhmb-pwa-v3";
const APP_SHELL = [
  "/",
  "/admin",
  "/artisan",
  "/buyer",
  "/offline.html",
  "/manifest.webmanifest",
  "/icon.svg",
];

async function putInCache(request, response) {
  if (!response || (!response.ok && response.type !== "opaque")) {
    return response;
  }
  const cache = await caches.open(CACHE_NAME);
  cache.put(request, response.clone());
  return response;
}

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }

  const url = new URL(event.request.url);

  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request)
        .then((response) => putInCache(event.request, response))
        .catch(async () => {
          const cachedRoute = await caches.match(url.pathname);
          return cachedRoute || caches.match("/offline.html");
        })
    );
    return;
  }

  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(event.request)
        .then((response) => putInCache(event.request, response))
        .catch(async () => {
          const cached = await caches.match(event.request);
          return (
            cached ||
            new Response(JSON.stringify({ error: "offline" }), {
              status: 503,
              headers: { "Content-Type": "application/json" },
            })
          );
        })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) {
        fetch(event.request).then((response) => putInCache(event.request, response)).catch(() => {});
        return cached;
      }

      return fetch(event.request)
        .then((response) => putInCache(event.request, response))
        .catch(() => caches.match("/offline.html"));
    })
  );
});
