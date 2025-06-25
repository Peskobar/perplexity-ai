from cachetools import TTLCache

class PamięćLRU:
    """Cache w pamięci z TTL i ograniczeniem liczby wpisów."""
    def __init__(self, max_entries: int = 1000, ttl: int = 3600):
        if max_entries < 0 or ttl < 0:
             raise ValueError("max_entries i ttl muszą być >= 0")
        # maxsize=0 oznacza brak limitu rozmiaru, ttl=0 oznacza brak limitu czasu
        self.cache = TTLCache(maxsize=max_entries if max_entries > 0 else float('inf'),
                              ttl=ttl if ttl > 0 else float('inf'))

    def get(self, k):
        """Pobiera wartość z cache po kluczu."""
        try:
            return self.cache.get(k)
        except Exception:
            # Ignoruj błędy cache, np. podczas iteracji lub czyszczenia w tle
            return None

    def set(self, k, v):
        """Ustawia wartość w cache dla danego klucza."""
        try:
            self.cache[k] = v
        except Exception:
            # Ignoruj błędy ustawiania w cache
            pass

    def stat(self):
        """Zwraca statystyki cache."""
        try:
            return dict(
                len=len(self.cache),
                max_size=self.cache.maxsize,
                ttl=self.cache.ttl,
                hits=getattr(self.cache, 'hits', 0), # cachetools 5+ ma hits/misses
                misses=getattr(self.cache, 'misses', 0)
            )
        except Exception:
            return dict(len=len(self.cache), error="Błąd statystyk cache")

    def clear(self):
        """Czyści cały cache."""
        try:
            self.cache.clear()
        except Exception:
            pass # Ignoruj błędy czyszczenia
