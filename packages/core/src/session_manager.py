import json
import time
from pathlib import Path
import os

class SessionManager:
    """Zarządza trwałą sesją, ciasteczkami i podstawowymi statystykami w pliku JSON."""
    def __init__(self, plik: str = "data/session.json"):
        # Użyj ścieżki względnej do katalogu pracy aplikacji lub ścieżki bezwzględnej
        base_dir = os.getenv("DATA_DIR", ".") # Domyślnie bieżący katalog, w Dockerze będzie /app/data
        self._p = Path(base_dir) / plik
        self._p.parent.mkdir(parents=True, exist_ok=True)
        self._dane = self._read()
        # packages.utils.src.logger by się przydał tutaj do logowania operacji na sesji

    def _read(self):
        """Czyta dane sesji z pliku."""
        try:
            if self._p.exists():
                return json.loads(self._p.read_text(encoding='utf-8'))
            else:
                # print(f"INFO: Plik sesji nie istnieje: {self._p}. Tworzę nowy.")
                return {"cookies": {}, "last": 0, "req": 0, "err": [], "start_time": time.time()}
        except Exception as e:
            # print(f"BŁĄD: Nie udało się odczytać pliku sesji {self._p}: {e}. Używam domyślnych danych.")
            return {"cookies": {}, "last": 0, "req": 0, "err": [], "start_time": time.time()}

    def _write(self):
        """Zapisuje dane sesji do pliku."""
        try:
            self._p.write_text(json.dumps(self._dane, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
             # print(f"BŁĄD: Nie udało się zapisać pliku sesji {self._p}: {e}")
             pass # Ignoruj błędy zapisu

    def cookie(self):
        """Zwraca ciasteczko p_token."""
        # Sprawdź, czy ciasteczko nie jest zbyt stare, jeśli chcesz logikę odświeżania
        # Obecnie po prostu zwraca, jeśli istnieje
        return self._dane["cookies"].get("p_token")

    def update_cookie(self, c: str):
        """Aktualizuje ciasteczko p_token i czas ostatniej aktywności."""
        if c:
            self._dane["cookies"]["p_token"] = c
            self._dane["last"] = time.time()
            self._write()

    def log_req(self):
        """Loguje pomyślne zapytanie."""
        self._dane["req"] += 1
        self._dane["last"] = time.time()
        self._write()

    def log_err(self, e: str):
        """Loguje błąd zapytania (maksymalnie 100 ostatnich)."""
        # Ograniczamy historię błędów, aby plik nie rósł w nieskończoność
        self._dane["err"].append({"t": time.time(), "err": str(e)})
        self._dane["err"] = self._dane["err"][-100:]
        self._dane["last"] = time.time()
        self._write()

    def get_stats(self):
        """Zwraca podstawowe statystyki sesji."""
        now = time.time()
        uptime = now - self._dane.get("start_time", now)
        return {
            "całkowita_ilość_żądań": self._dane.get("req", 0),
            "ostatnia_aktywność_unix_timestamp": self._dane.get("last", 0),
            "czas_działania_sekundy": int(uptime),
            "ilość_zarejestrowanych_błędów": len(self._dane.get("err", []))
        }
