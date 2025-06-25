from prometheus_client import generate_latest, REGISTRY, Counter, Gauge, Histogram
import time
from packages.core.src.session_manager import SessionManager
from packages.monitoring.src.health_monitor import HealthMonitor, Status
from packages.utils.src.logger import Logger
from packages.backend.app.services.perplexity_service import SERWIS_PERPLEXITY # Importuj serwis

logger = Logger().log # Użyj globalnej instancji Loggera

# Definicje metryk Prometheus
# Metryki żądań HTTP do FastAPI
REQUEST_COUNT = Counter('http_requests_total', 'Całkowita liczba żądań HTTP', ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Czas trwania żądań HTTP', ['method', 'endpoint'])

# Metryki specyficzne dla serwisu Perplexity
PERPLEXITY_API_REQUEST_COUNT = Counter('perplexity_api_requests_total', 'Całkowita liczba żądań wysłanych do API Perplexity')
PERPLEXITY_API_LATENCY = Histogram('perplexity_api_request_duration_seconds', 'Czas trwania żądań do API Perplexity')
PERPLEXITY_CACHE_HITS = Counter('perplexity_cache_hits_total', 'Całkowita liczba trafień w cache Perplexity')
PERPLEXITY_CACHE_MISSES = Counter('perplexity_cache_misses_total', 'Całkowita liczba chybień w cache Perplexity')
PERPLEXITY_CACHE_ENTRIES = Gauge('perplexity_cache_entries_current', 'Aktualna liczba wpisów w cache Perplexity')
PERPLEXITY_HEALTH_STATUS = Gauge('perplexity_health_status', 'Stan zdrowia klienta Perplexity AI (1=OK, 0.5=DEGRADACJA, 0=ZLY)')
PERPLEXITY_HEALTH_LAST_TEST_DURATION = Gauge('perplexity_health_last_test_duration_seconds', 'Czas wykonania ostatniego testu zdrowia Perplexity AI')
PERPLEXITY_HEALTH_SUCCESSFUL_TESTS = Gauge('perplexity_health_successful_tests_count', 'Liczba udanych testów w ostatniej probie zdrowia Perplexity AI')
PERPLEXITY_HEALTH_FAILED_TESTS = Gauge('perplexity_health_failed_tests_count', 'Liczba nieudanych testów w ostatniej probie zdrowia Perplexity AI')

# Metryki systemu/aplikacji
SERVICE_UPTIME = Gauge('service_uptime_seconds', 'Czas działania serwisu w sekundach')

# Monitor wątków? Pamięci? Zależności od systemu

def prometheus_metrics():
    """Generuje metryki w formacie Prometheus."""
    # Aktualizuj metryki, które muszą być aktualizowane w momencie żądania metryk
    # Metryki z cache i sesji są już zarządzane przez SessionManager i Cache (choć Cachetools ma wbudowane hits/misses)
    # Statystyki sesji
    ses_mgr = SessionManager() # Użyj globalnej instancji
    ses_stats = ses_mgr.get_stats()
    SERVICE_UPTIME.set(ses_stats.get('czas_działania_sekundy', 0))

    # Statystyki cache
    if SERWIS_PERPLEXITY.cache:
        cache_stats = SERWIS_PERPLEXITY.cache.stat()
        # Hits i misses są wbudowane w TTLCache od wersji 5+, ale my używamy własnych liczników w serwisie
        # lub pobieramy te z cachetools jeśli dostępne.
        # Poniżej pobieramy metryki bezpośrednio z serwisu, który je agreguje.
        # Te metryki powinny być aktualizowane w serwisie przy każdym trafieniu/chybieniu/żądaniu
        # lub możemy je aktualizować tutaj, ale wtedy mogą być nieaktualne między odczytami.
        # Najlepiej, aby serwis sam aktualizował swoje liczniki metryk.
        PERPLEXITY_CACHE_ENTRIES.set(cache_stats.get('len', 0))
        # PERPLEXITY_CACHE_HITS i PERPLEXITY_CACHE_MISSES powinny być inkrementowane w PerplexityAIService.zapytaj()

    # Statystyki monitora zdrowia
    ostatni_raport_zdrowia = SERWIS_PERPLEXITY.health_monitor.pobierz_ostatni_raport()
    if ostatni_raport_zdrowia:
        status_value = 1.0 if ostatni_raport_zdrowia.stan == Status.OK else \
                       (0.5 if ostatni_raport_zdrowia.stan == Status.DEG else 0.0)
        PERPLEXITY_HEALTH_STATUS.set(status_value)
        PERPLEXITY_HEALTH_LAST_TEST_DURATION.set(ostatni_raport_zdrowia.czas_testu_sek)
        PERPLEXITY_HEALTH_SUCCESSFUL_TESTS.set(ostatni_raport_zdrowia.udane_testy)
        PERPLEXITY_HEALTH_FAILED_TESTS.set(ostatni_raport_zdrowia.nieudane_testy)
    else:
        PERPLEXITY_HEALTH_STATUS.set(0.0) # Brak danych o zdrowiu = status nieznany/zły

    # Generuj metryki z globalnego rejestru Prometheus
    return generate_latest(REGISTRY)

# Middleware do zbierania metryk żądań HTTP
async def metrics_middleware(request, call_next):
    """Middleware do zliczania żądań i mierzenia czasu trwania."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code

    # Zliczaj tylko żądania do API (nie np. do /metrics samego w sobie)
    if endpoint.startswith("/api/"):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)
        logger.debug(f"Metryki HTTP dla {method} {endpoint} {status_code} zebrane ({process_time:.4f}s).")
    elif endpoint == "/stats":
        # Nie zliczaj żądań do endpointu metryk w metrykach HTTP, aby uniknąć rekurencji/szumu
        pass
    else:
         # Możesz zliczać żądania do frontendu, ale zazwyczaj robi to webserver (nginx)
         pass


    return response

# Uwaga: Metryki specyficzne dla Perplexity (API_REQUEST_COUNT, API_LATENCY, CACHE_HITS, CACHE_MISSES)
# Powinny być inkrementowane bezpośrednio w PerplexityAIService.zapytaj()
# lub w metodach EnhancedClient.request()
