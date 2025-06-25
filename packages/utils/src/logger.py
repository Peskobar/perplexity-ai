import atexit, logging, logging.handlers
from pathlib import Path
import os

KONFIGURACJA = None

class Logger:
    _inst = None

    # Przyjmujemy konfigurację jako argument, ale możemy użyć też globalnej KONFIGURACJA
    # Definicja __new__ dla singletona
    def __new__(cls, cfg=None):
        if not cls._inst:
            cls._inst = super().__new__(cls)
            if cfg is None:
                global KONFIGURACJA
                if KONFIGURACJA is None:
                    from packages.config.src.settings import KONFIGURACJA as K
                    KONFIGURACJA = K
                konf_do_uzycia = KONFIGURACJA
            else:
                konf_do_uzycia = cfg
            cls._inst._init(konf_do_uzycia)
        return cls._inst

    def _init(self, cfg):
        # Poziom logowania z konfiguracji lub zmiennej środowiskowej
        lvl_str = cfg.pobierz("logging.level", os.getenv("LOG_LEVEL", "INFO"))
        lvl = getattr(logging, lvl_str.upper(), logging.INFO)

        # Ścieżka pliku logów
        plik_sciezka_str = cfg.pobierz("logging.file", "logs/perplexity.log")
        plik = Path(plik_sciezka_str)
        plik.parent.mkdir(parents=True, exist_ok=True)

        # Format logowania
        fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

        self.log = logging.getLogger("perplexity")
        self.log.setLevel(lvl)

        # Unikaj dodawania wielu handlerów, jeśli instancja Logger jest używana wielokrotnie
        if not self.log.handlers:
            # Handler plikowy z rotacją
            try:
                max_bytes_str = cfg.pobierz("logging.max_size", "10MB")
                max_bytes = self._parse_size(max_bytes_str)
                backup_count = cfg.pobierz("logging.backup_count", 5)

                fh = logging.handlers.RotatingFileHandler(
                    plik, maxBytes=max_bytes,
                    backupCount=backup_count
                )
                fh.setFormatter(fmt)
                self.log.addHandler(fh)
            except Exception as e:
                print(f"BŁĄD: Nie udało się skonfigurować handlera plikowego logów: {e}")
                # Fallback na handler strumieniowy jeśli plikowy zawiedzie

            # Handler strumieniowy (konsola)
            ch = logging.StreamHandler()
            ch.setFormatter(fmt)
            self.log.addHandler(ch)

        # Zarejestruj funkcję zamykającą handlery przy wyjściu
        atexit.register(self._shutdown)

    def _parse_size(self, s: str) -> int:
        """Parsuje rozmiar pliku logów w formacie np. '10MB', '500KB'."""
        s = s.upper()
        if s.endswith("KB"):
            return int(s[:-2]) * 1024
        elif s.endswith("MB"):
            return int(s[:-2]) * 1024 * 1024
        else:
            try:
                return int(s) # Domyślnie bajty
            except ValueError:
                print(f"OSTRZEŻENIE: Nieprawidłowy format rozmiaru logów: '{s}'. Używam domyślnie 10MB.")
                return 10 * 1024 * 1024 # Domyślna wartość w bajtach

    def _shutdown(self):
        """Zamyka handlery logowania."""
        for h in self.log.handlers:
            try:
                h.flush()
                h.close()
            except Exception as e:
                print(f"BŁĄD: Nie udało się zamknąć handlera logów: {e}")

# Użyj globalnej instancji Loggera powiązanej z globalną konfiguracją
# Logowanie można uzyskać poprzez `Logger().log`
