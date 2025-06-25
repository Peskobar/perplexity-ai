from pathlib import Path
from typing import Any, Dict, Optional
import tomllib, yaml
import os

# Upewnij się, że importujemy z odpowiedniego pakietu

DOMYŚLNY_YAML = {
    "api": {"base_url": "https://www.perplexity.ai/api", "timeout": 30, "max_retries": 3, "retry_delay": 1.0},
    "rate_limiting": {"requests_per_minute": 20, "burst_limit": 5},
    "proxy": {"enabled": False, "rotation": True, "proxy_list": []},
    "logging": {"level": "INFO", "file": "logs/perplexity.log", "max_size": "10MB", "backup_count": 5},
    "cache": {"enabled": True, "ttl": 3600, "max_entries": 1000},
    "security": {"jwt_algorithm": "HS256", "jwt_expire_minutes": 30},
    "database": {"url": os.getenv("DATABASE_URL", "postgresql://uzytkownik:haslo@localhost:5432/baza_danych")},
    "redis": {"url": os.getenv("REDIS_URL", "redis://localhost:6379/0")}
}

class Konfiguracja:
    _inst = None
    _dane: Dict[str, Any] = {}

    def __new__(cls, sciezka: Optional[str] = None):
        if cls._inst is None:
            cls._inst = super(Konfiguracja, cls).__new__(cls)
            cls._inst._inicjuj(sciezka)
        return cls._inst

    def _inicjuj(self, sciezka: Optional[str] = None):
        self._sciezka = Path(sciezka) if sciezka else Path(os.getenv("PERPLEXITY_CONFIG_PATH", Path.home() / ".perplexity_ai.yaml"))
        self._ladowanie()

    def _ladowanie(self):
        try:
            if self._sciezka.exists():
                self._dane = yaml.safe_load(self._sciezka.read_text())
            else:
                self._dane = DOMYŚLNY_YAML
                # Self-healing: stwórz domyślny plik jeśli nie istnieje
                self._zapis()
        except Exception as e:
            # Logowanie błędu ładowania konfiguracji
            # Należy użyć podstawowego loggera lub printować, jeśli logger wymaga konfiguracji
            print(f"BŁĄD: Nie udało się załadować konfiguracji z {self._sciezka}: {e}")
            self._dane = DOMYŚLNY_YAML # Użyj domyślnych jako fallback

    def _zapis(self):
        try:
            self._sciezka.parent.mkdir(parents=True, exist_ok=True)
            self._sciezka.write_text(yaml.dump(self._dane, allow_unicode=True))
        except Exception as e:
             print(f"BŁĄD: Nie udało się zapisać konfiguracji do {self._sciezka}: {e}")

    def pobierz(self, sciezka: str, domyslna: Any = None) -> Any:
        kursor = self._dane
        try:
            for segment in sciezka.split("."):
                if isinstance(kursor, dict) and segment in kursor:
                    kursor = kursor[segment]
                else:
                    # Sprawdź zmienne środowiskowe jako fallback
                    env_var_name = sciezka.replace('.', '_').upper()
                    env_val = os.getenv(env_var_name)
                    if env_val is not None:
                         # Spróbuj skonwertować zmienną środowiskową do odpowiedniego typu
                         try:
                             if isinstance(domyslna, int): return int(env_val)
                             if isinstance(domyslna, float): return float(env_val)
                             if isinstance(domyslna, bool): return env_val.lower() in ('true', '1', 'yes')
                             # Można dodać więcej konwersji (listy, dicty z JSONa?)
                         except ValueError:
                             pass # Ignoruj błędy konwersji, zwróć jako string lub domyślne
                         return env_val
                    return domyslna # Zwróć wartość domyślną jeśli brak w pliku i env
            return kursor # Zwróć wartość znalezioną w pliku
        except Exception as e:
            # Logowanie błędu dostępu do konfiguracji
            print(f"BŁĄD: Problem z pobraniem ścieżki konfiguracji '{sciezka}': {e}")
            return domyslna

# Globalna instancja konfiguracji
KONFIGURACJA = Konfiguracja()
