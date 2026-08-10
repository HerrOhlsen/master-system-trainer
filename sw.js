/* Offline support. Bump CACHE when the app changes so phones pick it up. */
const CACHE = "master-system-v9";
const ASSETS = [
  ".",
  "index.html",
  "manifest.webmanifest",
  "icon-192.png",
  "icon-512.png",
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

/* Cache first, refresh in the background. A phone waking up is rarely cleanly
   offline: the network is half up, fetch() hangs instead of failing, and a
   network first worker would leave the app on a white screen until iOS gives
   up. Out of the cache the start is instant, online or not. The price is that
   a new version shows on the next launch instead of this one. */
self.addEventListener("fetch", event => {
  const request = event.request;
  if(request.method !== "GET") return;
  if(new URL(request.url).origin !== self.location.origin) return;
  event.respondWith(serve(event));
});

async function serve(event){
  const request = event.request;
  const cache = await caches.open(CACHE);
  const cached = await cache.match(request, {ignoreSearch: true});
  /* A 404 from a half finished deploy or the login page of some hotspot must
     never replace a working app, so only clean same origin answers are kept. */
  const network = fetch(request).then(response => {
    if(response && response.ok && response.type === "basic"){
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => null);

  if(cached){
    event.waitUntil(network);
    return cached;
  }
  const response = await network;
  if(response) return response;
  return (await cache.match("index.html")) || new Response("Offline", {
    status: 503,
    headers: {"Content-Type": "text/plain; charset=utf-8"},
  });
}
