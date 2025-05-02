import time
from threading import Thread


class CacheItem:
    def __init__(self, value, ttl):
        self.value = value
        self.expiry_time = time.time() + ttl


class CacheMap:
    def __init__(self, default_ttl=60):
        self.cache = {}
        self.default_ttl = default_ttl
        self.cleanup_interval = 30  # seconds
        self._start_cleanup_task()

    def _cleanup(self):
        """Remove expired items from the cache."""
        current_time = time.time()
        keys_to_delete = [
            key for key, item in self.cache.items() if item.expiry_time <= current_time
        ]
        for key in keys_to_delete:
            del self.cache[key]

    def _start_cleanup_task(self):
        """Start a background thread that cleans up expired items at regular intervals."""

        def cleanup_task():
            while True:
                self._cleanup()
                time.sleep(self.cleanup_interval)

        Thread(target=cleanup_task, daemon=True).start()

    def set(self, key, value, ttl=None):
        """Add an item to the cache with an optional TTL."""
        if ttl is None:
            ttl = self.default_ttl
        self.cache[key] = CacheItem(value, ttl)

    def get(self, key):
        """Retrieve an item from the cache."""
        item = self.cache.get(key)
        if item and item.expiry_time > time.time():
            return item.value

        self.cache.pop(key, None)
        return None

    def invalidate(self, key):
        """Remove an item from the cache."""
        self.cache.pop(key, None)
