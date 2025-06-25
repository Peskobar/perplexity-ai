import asyncio
import time
import os

# Importowanie klas z pakietów lokalnych
from packages.config.src.settings import KONFIGURACJA
from packages.utils.src.logger import Logger
from packages.cache.src.memory_cache import PamięćLRU
from packages.core.src.session_manager import SessionManager
from packages.core.src.enhanced_client import EnhancedClient
from packages.monitoring.src.health_monitor import HealthMonitor, Status

logger = Logger().log # Użyj globalnej instancji Loggera

class PerplexityAIService:
    """Serwis fasady do klienta Perplexity AI, dodający cache i monitorowanie."""

    _inst = None

    def __new__(cls, cfg=None):
        if cls._inst is None:
            cls._inst = super(PerplexityAIService, cls).__new__(cls)
            # Użyj podanej konfiguracji lub globalnej instancji
            konf_do_uzycia = cfg if cfg else KONFIGURACJA
            cls._inst._inicjuj(konf_do_uzycia)
        return cls._inst

    def _inicjuj(self, cfg):
        self.cfg = cfg
        self.session_manager = SessionManager() # SessionManager zarządza plikiem sesji
        self.perplexity_client = EnhancedClient(self.cfg, self.session_manager.cookie()) # Przekazujemy ciasteczko

        # Inicjalizacja cache na podstawie konfiguracji
        cache_enabled = self.cfg.pobierz("cache.enabled", True)
        cache_max_entries = self.cfg.pobierz("cache.max_entries", 1000)
        cache_ttl = self.cfg.pobierz("cache.ttl", 3600)
        self.cache = PamięćLRU(cache_max_entries, cache_ttl) if cache_enabled else None
        if self.cache:
            logger.info(f"Cache włączony: max_entries={cache_max_entries}, ttl={cache_ttl}s")
        else:
            logger.info("Cache wyłączony.")

        # Inicjalizacja monitora zdrowia
        monitor_interval = self.cfg.pobierz("monitoring.interval_sek", 300) # Domyślny interwał 5 minut
        self.health_monitor = HealthMonitor(self.perplexity_client, monitor_interval)
        # Monitorowanie będzie uruchamiane przy starcie aplikacji (w main.py)

        logger.info("PerplexityAIService zainicjowany.")

    async def zapytaj(self, prompt: str) -> str:
        """Zadaje pytanie do Perplexity AI, wykorzystując cache i logując aktywność."""
        logger.info(f"Otrzymano zapytanie: '{prompt[:100]}...'") # Loguj początek zapytania

        if self.cache:
            cached_answer = self.cache.get(prompt)
            if cached_answer:
                logger.info("Odpowiedź znaleziona w cache.")
                # Zwracamy odpowiedź z cache - nie logujemy żądania do API
                return cached_answer

        logger.info("Odpowiedź nie w cache. Pytam API Perplexity.")
        try:
            start_time = time.time()
            # Wykonaj zapytanie za pomocą ulepszonego klienta
            # EnhancedClient zawiera logikę ponawiania i rate limiting
            api_response = await self.perplexity_client.request(prompt)
            end_time = time.time()
            czas_odpowiedzi_ms = int((end_time - start_time) * 1000)

            logger.info(f"Odpowiedź z API otrzymana (czas: {czas_odpowiedzi_ms}ms).")

            # Zapisz odpowiedź w cache, jeśli cache jest włączony
            if self.cache:
                self.cache.set(prompt, api_response)
                logger.debug("Odpowiedź zapisana w cache.")

            # Zaloguj pomyślne zapytanie w SessionManager
            self.session_manager.log_req()

            return api_response

        except Exception as e:
            logger.error(f"Błąd podczas zapytania do Perplexity AI: {e}")
            # Zaloguj błąd w SessionManager
            self.session_manager.log_err(str(e))
            # Zgłoś wyjątek dalej, aby obsłużył go endpoint API
            raise e

    async def status_zdrowia(self) -> Raport:
        """Zwraca ostatni raport zdrowia monitora."""
        raport = self.health_monitor.pobierz_ostatni_raport()
        if raport is None:
            # Jeśli monitor jeszcze nie wykonał próby, przeprowadź jedną natychmiast
            logger.warning("Monitor zdrowia nie ma jeszcze raportu. Przeprowadzam natychmiastową próbę.")
            raport = await self.health_monitor._przeprowadz_probe()
            self.health_monitor.historia_raportów.append(raport) # Dodaj do historii

        return raport

    def pobierz_metryki_prometheus(self) -> str:
        """Zwraca metryki w formacie Prometheus."""
        # Możemy dodać metryki specyficzne dla serwisu, np. ilość zapytań cache vs API
        cache_stats = self.cache.stat() if self.cache else {}
        session_stats = self.session_manager.get_stats()

        metrics = self.health_monitor.get_prometheus_metrics() # Metryki z monitora zdrowia

        metrics += f"# HELP perplexity_cache_hits_total Całkowita liczba trafień w cache.\n"
        metrics += f"# TYPE perplexity_cache_hits_total counter\n"
        metrics += f"perplexity_cache_hits_total {cache_stats.get('hits', 0)}\n"

        metrics += f"# HELP perplexity_cache_misses_total Całkowita liczba chybień w cache.\n"
        metrics += f"# TYPE perplexity_cache_misses_total counter\n"
        metrics += f"perplexity_cache_misses_total {cache_stats.get('misses', 0)}\n"

        metrics += f"# HELP perplexity_cache_entries_current Aktualna liczba wpisów w cache.\n"
        metrics += f"# TYPE perplexity_cache_entries_current gauge\n"
        metrics += f"perplexity_cache_entries_current {cache_stats.get('len', 0)}\n"

        metrics += f"# HELP perplexity_total_requests_count Całkowita liczba zapytań wysłanych do API Perplexity.\n"
        metrics += f"# TYPE perplexity_total_requests_count counter\n"
        metrics += f"perplexity_total_requests_count {session_stats.get('całkowita_ilość_żądań', 0)}\n"

        metrics += f"# HELP perplexity_service_uptime_seconds Czas działania serwisu w sekundach.\n"
        metrics += f"# TYPE perplexity_service_uptime_seconds gauge\n"
        metrics += f"perplexity_service_uptime_seconds {session_stats.get('czas_działania_sekundy', 0)}\n"


        return metrics

    async def start_monitoringu(self):
        """Uruchamia monitor zdrowia."""
        await self.health_monitor.start()

    async def stop_monitoringu(self):
        """Zatrzymuje monitor zdrowia."""
        await self.health_monitor.stop()

    async def zamknij(self):
        """Zamyka zasoby serwisu, np. sesję klienta."""
        logger.info("Zamykam PerplexityAIService...")
        await self.perplexity_client.close()
        # Zapisz sesję na koniec
        # self.session_manager._write() # _write jest wołane po każdej zmianie, więc to nie jest ściśle konieczne, ale można dodać na wszelki wypadek
        logger.info("PerplexityAIService zamknięty.")


# Globalna instancja serwisu do użycia w FastAPI
SERWIS_PERPLEXITY = PerplexityAIService()
