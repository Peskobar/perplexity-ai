import asyncio
import time
from enum import Enum
from dataclasses import dataclass
from typing import List

# Upewnij się, że importujesz z odpowiednich pakietów
from packages.core.src.enhanced_client import EnhancedClient
from packages.utils.src.logger import Logger
from packages.config.src.settings import KONFIGURACJA

# Użyj Loggera
logger = Logger().log

class Status(Enum):
    OK="ok" # Wszystko działa poprawnie
    DEG="degradacja" # Działa częściowo lub z problemami
    BAD="zły" # Nie działa lub poważne problemy

@dataclass
class Raport:
    stan: Status # Ogólny stan usługi (OK, DEGRADACJA, ZŁY)
    czas_testu_sek: float # Czas wykonania wszystkich testów
    udane_testy: int # Liczba udanych testów (pingów)
    nieudane_testy: int # Liczba nieudanych testów (pingów)
    timestamp: float # Czas utworzenia raportu (epoch)

class HealthMonitor:
    """Monitoruje stan zdrowia (dostępność i czas odpowiedzi) klienta Perplexity AI."""
    def __init__(self, client: EnhancedClient, interwał_sek: int = 300):
        if not isinstance(client, EnhancedClient):
             raise TypeError("Client musi być instancją EnhancedClient")
        if interwał_sek <= 0:
             raise ValueError("Interwał monitorowania musi być > 0")
        self.client = client
        self.interwał_sek = interwał_sek # Jak często uruchamiać testy
        self.historia_raportów: List[Raport] = [] # Przechowuje historię raportów
        self._monitoring_task: Optional[asyncio.Task] = None # Zadanie asyncio dla monitorowania w tle

    async def start(self):
        """Uruchamia zadanie monitorowania w tle."""
        if self._monitoring_task is None or self._monitoring_task.done():
            logger.info(f"Uruchamiam monitorowanie zdrowia z interwałem {self.interwał_sek}s...")
            self._monitoring_task = asyncio.create_task(self._pętla_monitorowania())
        else:
            logger.warning("Monitorowanie zdrowia już działa.")

    async def stop(self):
        """Zatrzymuje zadanie monitorowania w tle."""
        if self._monitoring_task and not self._monitoring_task.done():
            logger.info("Zatrzymuję monitorowanie zdrowia...")
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                logger.info("Monitorowanie zdrowia zostało zatrzymane.")
            self._monitoring_task = None

    async def _pętla_monitorowania(self):
        """Główna pętla monitorowania."""
        while True:
            try:
                raport = await self._przeprowadz_probe()
                self.historia_raportów.append(raport)
                # Ograniczamy historię, np. do ostatnich 100 raportów
                self.historia_raportów = self.historia_raportów[-100:]
                logger.info(f"Raport monitorowania: Stan={raport.stan.value}, Czas={raport.czas_testu_sek:.2f}s, Udane={raport.udane_testy}, Nieudane={raport.nieudane_testy}")
            except Exception as e:
                logger.error(f"Wystąpił błąd podczas monitorowania zdrowia: {e}")

            # Czekaj przed kolejną próbą
            await asyncio.sleep(self.interwał_sek)

    async def _przeprowadz_probe(self) -> Raport:
        """Wykonuje serię testowych zapytań do API."""
        logger.debug("Przeprowadzam próbę monitorowania zdrowia API...")
        start_time = time.time()
        udane_testy = 0
        nieudane_testy = 0

        # Lista prostych zapytań testowych
        testowe_zapytania = ["Jaki jest dzisiaj dzień?", "Test ping", "2 + 2"]

        # Wykonaj testy asynchronicznie
        async def wykonaj_test(q):
            try:
                # Użyj timeoutu na poziomie pojedynczego zapytania testowego, niezależnie od timeoutu klienta
                # aby próba monitorowania nie trwała zbyt długo w przypadku problemów.
                # Możesz dostosować ten timeout.
                await asyncio.wait_for(self.client.request(q), timeout=10) # Timeout 10 sekund na pojedynczy test
                return True
            except Exception as e:
                logger.debug(f"Test zapytania '{q}' nie powiódł się: {e}")
                return False

        tasks = [wykonaj_test(q) for q in testowe_zapytania]
        wyniki = await asyncio.gather(*tasks, return_exceptions=True)

        for wynik in wyniki:
            if wynik is True:
                udane_testy += 1
            else:
                nieudane_testy += 1

        czas_testu_sek = time.time() - start_time

        # Określenie ogólnego stanu
        # Kryteria można dostosować: np. OK jeśli wszystkie udane, DEGRADACJA jeśli część udana, ZŁY jeśli wszystkie nieudane
        if udane_testy == len(testowe_zapytania):
            stan = Status.OK
        elif udane_testy > 0:
            stan = Status.DEG
        else:
            stan = Status.BAD

        logger.debug(f"Próba zakończona: Stan={stan.value}, Udane={udane_testy}, Nieudane={nieudane_testy}")

        return Raport(stan, czas_testu_sek, udane_testy, nieudane_testy, time.time())

    def pobierz_ostatni_raport(self) -> Optional[Raport]:
        """Zwraca ostatni raport monitorowania."""
        if self.historia_raportów:
            return self.historia_raportów[-1]
        return None

    def pobierz_historie_raportów(self) -> List[Raport]:
        """Zwraca kopię historii raportów."""
        return list(self.historia_raportów) # Zwróć kopię, aby uniknąć modyfikacji z zewnątrz

    def get_prometheus_metrics(self):
        """Generuje metryki w formacie Prometheus."""
        ostatni_raport = self.pobierz_ostatni_raport()
        metrics = []

        # Metryka stanu ogólnego (Gauge)
        # 1 dla OK, 0.5 dla DEGRADACJA, 0 dla ZŁY
        status_value = 1.0 if ostatni_raport and ostatni_raport.stan == Status.OK else \
                       (0.5 if ostatni_raport and ostatni_raport.stan == Status.DEG else 0.0)
        metrics.append(f"# HELP perplexity_health_status Stan zdrowia klienta Perplexity AI (1=OK, 0.5=DEGRADACJA, 0=ZLY).\n")
        metrics.append(f"# TYPE perplexity_health_status gauge\n")
        metrics.append(f"perplexity_health_status {status_value}\n")

        if ostatni_raport:
            # Metryka czasu ostatniego testu (Gauge)
            metrics.append(f"# HELP perplexity_health_last_test_duration_seconds Czas wykonania ostatniego testu zdrowia Perplexity AI.\n")
            metrics.append(f"# TYPE perplexity_health_last_test_duration_seconds gauge\n")
            metrics.append(f"perplexity_health_last_test_duration_seconds {ostatni_raport.czas_testu_sek}\n")

            # Metryki liczby udanych/nieudanych testów (Gauge lub Counter - Gauge lepszy dla pojedynczego testu)
            metrics.append(f"# HELP perplexity_health_successful_tests_count Liczba udanych testów w ostatniej probie zdrowia Perplexity AI.\n")
            metrics.append(f"# TYPE perplexity_health_successful_tests_count gauge\n")
            metrics.append(f"perplexity_health_successful_tests_count {ostatni_raport.udane_testy}\n")

            metrics.append(f"# HELP perplexity_health_failed_tests_count Liczba nieudanych testów w ostatniej probie zdrowia Perplexity AI.\n")
            metrics.append(f"# TYPE perplexity_health_failed_tests_count gauge\n")
            metrics.append(f"perplexity_health_failed_tests_count {ostatni_raport.nieudane_testy}\n")

        # Dodaj metryki globalne z SessionManager (ilość zapytań, uptime)
        # Zakładamy, że SessionManager jest dostępny
        # from packages.core.src.session_manager import SessionManager # Import tutaj, żeby uniknąć cyklicznych zależności jeśli HealthMonitor jest importowany gdzieś w SessionManager
        # ses_mgr = SessionManager()
        # ses_stats = ses_mgr.get_stats()

        # metrics.append(f"# HELP perplexity_total_requests_count Całkowita liczba zapytań wykonanych przez klienta Perplexity AI.\n")
        # metrics.append(f"# TYPE perplexity_total_requests_count counter\n")
        # metrics.append(f"perplexity_total_requests_count {ses_stats.get('całkowita_ilość_żądań', 0)}\n")

        # metrics.append(f"# HELP perplexity_service_uptime_seconds Czas działania serwisu klienta Perplexity AI w sekundach.\n")
        # metrics.append(f"# TYPE perplexity_service_uptime_seconds gauge\n")
        # metrics.append(f"perplexity_service_uptime_seconds {ses_stats.get('czas_działania_sekundy', 0)}\n")


        return "".join(metrics)
