import aiohttp
import asyncio
import uuid
import json
import random
import time  # Dodany import time
import os  # Dodany import os
from typing import Optional, Dict

# Upewnij się, że importujesz z odpowiednich pakietów
from packages.utils.src.async_rate_limiter import AsyncRateLimiter
from packages.utils.src.async_retry import async_retry
from packages.config.src.settings import KONFIGURACJA
# packages.utils.src.logger by się przydał tutaj do logowania operacji klienta

class ProxyManager:
    """Zarządza listą proxy, obsługuje rotację i oznaczanie niedziałających."""
    def __init__(self, lista: list, rotacja: bool = True):
        # Filtruj puste lub None wpisy z listy proxy
        self.lista = [p for p in lista if p and isinstance(p, str)]
        self.rotacja, self.idx = rotacja, 0
        self.bad = set() # Zestaw adresów proxy, które ostatnio zawiodły

    def wybierz(self) -> Optional[str]:
        """Wybiera proxy z listy. Zwraca None jeśli lista pusta lub wszystkie oznaczone jako złe."""
        dostępne_proxy = [p for p in self.lista if p not in self.bad]
        if not dostępne_proxy:
            # Opcjonalnie: zresetuj listę złych proxy po czasie lub liczbie prób
            # print("OSTRZEŻENIE: Brak dostępnych proxy. Resetuję listę złych.")
            self.bad.clear()
            dostępne_proxy = list(self.lista) # Spróbuj ponownie z całą listą

        if not dostępne_proxy:
             # print("OSTRZEŻENIE: Brak jakichkolwiek proxy do użycia.")
             return None # Całkowity brak proxy

        if self.rotacja:
            # Logika rotacji, upewnij się, że nie utkniesz w pętli nieskończonej
            start_idx = self.idx
            while True:
                p = self.lista[self.idx]
                self.idx = (self.idx + 1) % len(self.lista)
                if p in dostępne_proxy: # Wybierz tylko z listy dostępnych
                    # print(f"INFO: Wybrano proxy (rotacja): {p}")
                    return p
                if self.idx == start_idx: # Sprawdź czy wróciliśmy do punktu wyjścia po przejrzeniu całej listy
                    # print("OSTRZEŻENIE: Rotacja nie znalazła dostępnego proxy po pełnym obrocie.")
                    break # Wyjdź z pętli, jeśli rotacja nie działa poprawnie z dostępnymi proxy

        # Jeśli brak rotacji lub rotacja zawiodła, wybierz losowo z dostępnych
        wybrane = random.choice(dostępne_proxy)
        # print(f"INFO: Wybrano proxy (losowo/fallback): {wybrane}")
        return wybrane

    def oznacz_blad(self, p: str):
        """Oznacza dane proxy jako niedziałające."""
        if p:
            # print(f"OSTRZEŻENIE: Oznaczam proxy jako błędne: {p}")
            self.bad.add(p)
            # Opcjonalnie: dodaj logikę usuwania z "bad" po pewnym czasie lub zdarzeniu

class EnhancedClient:
    """Klient HTTP/S z zaawansowanymi funkcjami: limitowanie zapytań, ponawianie, proxy, zarządzanie ciasteczkami."""
    def __init__(self, cfg=None, cookie: Optional[str] = None):
        # Użyj podanej konfiguracji lub globalnej instancji
        self.cfg = cfg if cfg else KONFIGURACJA
        self.cookie = cookie or os.getenv("PERPLEXITY_COOKIE")
        if not self.cookie:
             # print("KRYTYCZNY BŁĄD: PERPLEXITY_COOKIE nie znaleziono w konfiguracji ani zmiennych środowiskowych.")
             raise ValueError("Brak PERPLEXITY_COOKIE. Proszę ustaw zmienną środowiskową lub wartość w pliku konfiguracyjnym.")

        # Inicjalizacja limitera z konfiguracji
        rps = self.cfg.pobierz("rate_limiting.requests_per_minute", 20)
        burst = self.cfg.pobierz("rate_limiting.burst_limit", 5)
        self.rate = AsyncRateLimiter(rps, burst)

        # Inicjalizacja ProxyManager z konfiguracji
        proxy_enabled = self.cfg.pobierz("proxy.enabled", False)
        proxy_list = self.cfg.pobierz("proxy.proxy_list", [])
        proxy_rotation = self.cfg.pobierz("proxy.rotation", True)
        self.proxy_mgr = ProxyManager(proxy_list, proxy_rotation) if proxy_enabled else None
        if proxy_enabled and not proxy_list:
            # print("OSTRZEŻENIE: Proxy włączone w konfiguracji, ale lista proxy jest pusta.")
            pass

        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock() # Blokada dla inicjalizacji sesji

    async def _sess(self) -> aiohttp.ClientSession:
        """Zwraca lub tworzy asynchroniczną sesję klienta aiohttp."""
        async with self._session_lock:
            if self.session is None or self.session.closed:
                timeout_sec = self.cfg.pobierz("api.timeout", 30)
                timeout = aiohttp.ClientTimeout(total=timeout_sec)
                self.session = aiohttp.ClientSession(timeout=timeout)
                # print("INFO: Utworzono nową sesję klienta aiohttp.")
        return self.session

    def _hdr(self) -> Dict[str, str]:
        """Generuje nagłówki HTTP, w tym User-Agent i Cookie."""
        # Lista często używanych User-Agentów przeglądarek
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
        ]
        ua = random.choice(ua_list)
        headers = {
            "User-Agent": ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "Origin": "https://www.perplexity.ai",
            "Referer": "https://www.perplexity.ai/",
            "X-PPH-Pro-Entitlement": "false", # Zmienić na true jeśli używasz konta Pro
        }
        if self.cookie:
            headers["Cookie"] = f"p_token={self.cookie}"
        return headers

    @async_retry(max_retries=KONFIGURACJA.pobierz("api.max_retries", 3), base_delay=KONFIGURACJA.pobierz("api.retry_delay", 1.0))
    async def request(self, q: str) -> str:
        """Wykonuje zapytanie do API Perplexity AI."""
        # Czekaj na możliwość wykonania żądania (rate limiting)
        await self.rate.acquire()

        ses = await self._sess()
        proxy_uzyte = None
        if self.proxy_mgr:
            proxy_uzyte = self.proxy_mgr.wybierz()
            # print(f"INFO: Używam proxy: {proxy_uzyte}")

        api_url = self.cfg.pobierz("api.base_url", "https://www.perplexity.ai/api")
        endpoint = f"{api_url}/chat/async" # Używamy async endpoint dla lepszej zgodności

        payload = {
            "id": str(uuid.uuid4()),
            "version": "0.0", # Wersja API, może wymagać aktualizacji
            "source": "user",
            "text": q,
            "timestamp": int(time.time() * 1000),
            "previous_messages": [], # Można dodać kontekst konwersacji
            "attachments": [] # Obsługa załączników jeśli potrzebna
        }

        start_time = time.time()
        try:
            # Użyj ses.post wewnątrz bloku async with
            async with ses.post(endpoint, json=payload, headers=self._hdr(), proxy=proxy_uzyte) as r:
                czas_odpowiedzi_ms = int((time.time() - start_time) * 1000)
                status_kodu = r.status

                # print(f"INFO: Zapytanie do API: Status {status_kodu}, Czas {czas_odpowiedzi_ms}ms")

                if status_kodu != 200:
                    # print(f"BŁĄD: API zwróciło status {status_kodu}")
                    if proxy_uzyte and status_kodu in [403, 407, 408, 502, 503, 504]: # Typowe kody błędów związanych z proxy
                        self.proxy_mgr.oznacz_blad(proxy_uzyte)
                        # print(f"INFO: Proxy {proxy_uzyte} oznaczone jako błędne.")
                    raise RuntimeError(f"Błąd API: Status {status_kodu}")

                # API /chat/async zwraca obiekt JSON z polem "answer" i innymi danymi
                try:
                    odpowiedz_json = await r.json()
                    # Sprawdź strukturę odpowiedzi
                    if not isinstance(odpowiedz_json, dict) or "answer" not in odpowiedz_json:
                        # print(f"BŁĄD: Nieoczekiwana struktura odpowiedzi API: {odpowiedz_json}")
                        raise ValueError("Nieoczekiwana struktura odpowiedzi API")

                    odpowiedz = odpowiedz_json.get("answer", "").strip()
                    if not odpowiedz:
                         # print("OSTRZEŻENIE: API zwróciło pustą odpowiedź.")
                         # W zależności od wymagań, można podnieść wyjątek lub zwrócić pusty string
                         # Dla prostoty zwracamy pusty string, ale logujemy ostrzeżenie
                         pass # Kontynuuj, zwracając pusty string

                    # Tutaj można by zalogować sukces zapytania
                    # packages.core.src.session_manager by mógł log_req()
                    return odpowiedz

                except json.JSONDecodeError:
                    # print(f"BŁĄD: Nie udało się zdekodować odpowiedzi JSON od API.")
                    raise ValueError("Niepoprawna odpowiedź JSON od API")
                except Exception as e:
                    # print(f"BŁĄD: Wystąpił błąd podczas przetwarzania odpowiedzi API: {e}")
                    raise e

        except aiohttp.ClientConnectorError as e:
            # print(f"BŁĄD: Błąd połączenia z API/Proxy {proxy_uzyte if proxy_uzyte else 'bez proxy'}: {e}")
            if proxy_uzyte:
                self.proxy_mgr.oznacz_blad(proxy_uzyte)
                # print(f"INFO: Proxy {proxy_uzyte} oznaczone jako błędne z powodu błędu połączenia.")
            raise RuntimeError(f"Błąd połączenia: {e}")
        except asyncio.TimeoutError:
            # print(f"BŁĄD: Przekroczono czas oczekiwania na odpowiedź z API/Proxy {proxy_uzyte if proxy_uzyte else 'bez proxy'}.")
            if proxy_uzyte:
                self.proxy_mgr.oznacz_blad(proxy_uzyte)
                # print(f"INFO: Proxy {proxy_uzyte} oznaczone jako błędne z powodu timeoutu.")
            raise TimeoutError("Przekroczono czas oczekiwania na odpowiedź API")
        except Exception as e:
            # Logowanie innych nieobsłużonych błędów
            # print(f"BŁĄD: Nieoczekiwany błąd podczas żądania API: {e}")
            if proxy_uzyte:
                 # Oznacz proxy jako błędne również w przypadku innych błędów, być może jest niestabilne
                 self.proxy_mgr.oznacz_blad(proxy_uzyte)
                 # print(f"INFO: Proxy {proxy_uzyte} oznaczone jako błędne z powodu nieoczekiwanego błędu.")
            raise e # Ponowne zgłoszenie błędu

    async def close(self):
        """Zamyka sesję klienta aiohttp."""
        async with self._session_lock:
            if self.session and not self.session.closed:
                await self.session.close()
                # print("INFO: Sesja klienta aiohttp została zamknięta.")
            self.session = None # Ustaw na None po zamknięciu
