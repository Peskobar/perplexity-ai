Zrozumiałem.

```
# Stuktura Katalogów
# .github/
#   workflows/
#     ci.yml
# apps/
#   backend/
#     Dockerfile
#     requirements.txt
#     app/
#       __init__.py
#       main.py
#       auth.py
#       deps.py
#       stats.py
#       services/
#         __init__.py
#         perplexity_service.py
#   frontend/
#     index.html
#     package.json
#     postcss.config.js
#     tailwind.config.js
#     tsconfig.json
#     vite.config.ts
#     public/
#       logo.svg
#     src/
#       main.tsx
#       App.tsx
#       index.css
#       components/
#         ui/
#           button.tsx
#           dialog.tsx
#           input.tsx
#           label.tsx
#           progress.tsx
#           tooltip.tsx
#           # ... inne komponenty shadcn/ui
#         onboarding/
#           Krok1.tsx
#           Krok2.tsx
#           Krok3.tsx
#           OnboardingDialog.tsx
#         command-palette/
#           PaletaPolecen.tsx
#         layout/
#           Naglowek.tsx
#           Stopka.tsx
#           GlownaZawartosc.tsx
#         chat/
#           OknoCzatu.tsx
#           WiadomoscCzatu.tsx
#           PoleWprowadzania.tsx
#         three/
#           Tlo3D.tsx
#       lib/
#         api.ts
#         utils.ts
#         hooks.ts
#         theme.ts
#       context/
#         ThemeContext.tsx
#         AuthContext.tsx
#         OnboardingContext.tsx
# packages/
#   config/
#     package.json
#     src/
#       __init__.py
#       settings.py
#   utils/
#     package.json
#     src/
#       __init__.py
#       logger.py
#       async_rate_limiter.py
#       async_retry.py
#   cache/
#     package.json
#     src/
#       __init__.py
#       memory_cache.py
#   core/
#     package.json
#     src/
#       __init__.py
#       session_manager.py
#       enhanced_client.py
#   monitoring/
#     package.json
#     src/
#       __init__.py
#       health_monitor.py
# .gitignore
# package.json # Główny monorepo package.json
# turbo.json
# README.md
# infra/
#   docker-compose.yml
#   nginx/
#     nginx.conf
#   postgres/
#     init.sql
#   redis/
#     redis.conf
```

```json
// package.json (root)
{
  "name": "perplexity-ai-optymalizacja",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev --parallel",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "clean": "turbo run clean && rm -rf node_modules",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,md}\""
  },
  "devDependencies": {
    "prettier": "^3.2.5",
    "turbo": "^1.13.3"
  },
  "packageManager": "pnpm@8.15.6",
  "workspaces": [
    "apps/*",
    "packages/*"
  ]
}
```

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [
    "**/.env"
  ],
  "pipeline": {
    "build": {
      "outputs": [
        "dist/**",
        ".next/**",
        "build/**"
      ],
      "dependsOn": [
        "^build"
      ]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    }
  }
}
```

```yaml
# infra/docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_USER: użytkownik
      POSTGRES_PASSWORD: hasło
      POSTGRES_DB: baza_danych
    volumes:
      - db_dane:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - redis_dane:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"

  backend:
    build:
      context: ../apps/backend
      dockerfile: Dockerfile
    restart: always
    environment:
      DATABASE_URL: postgresql://użytkownik:hasło@db:5432/baza_danych
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: klucz_sekretny_jwt_bardzo_dlugi_i_losowy
      PERPLEXITY_COOKIE: ciasteczko_perplexity_ai_wymagane
      LOG_LEVEL: INFO
      # PERPLEXITY_CONFIG_PATH: /app/config.yaml # Jeśli chcesz używać pliku zamiast zmiennych env
    volumes:
      - backend_dane:/app/data # Na sesje, logi itp.
      # - ../config.yaml:/app/config.yaml # Mapowanie zewnętrznego pliku konfiguracyjnego
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ../apps/frontend
      dockerfile: Dockerfile
    restart: always
    volumes:
      - frontend_dane:/app/build
    # Frontend będzie serwowany przez Nginx w produkcji, port tylko dla developmentu
    # ports:
    #   - "3000:80"

  nginx:
    image: nginx:stable-alpine
    restart: always
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - frontend_dane:/usr/share/nginx/html:ro # Serwowanie plików frontend
      - backend_dane/logs:/var/log/nginx # Opcjonalnie logi nginx do tego samego wolumenu
    ports:
      - "80:80"
      - "443:443" # Dla HTTPS
    depends_on:
      - backend
      - frontend # Upewnij się, że frontend zbudował swoje pliki

volumes:
  db_dane:
  redis_dane:
  backend_dane:
  frontend_dane:
```

```nginx
# infra/nginx/nginx.conf
worker_processes 1;

events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  sendfile on;
  keepalive_timeout 65;

  server {
    listen 80;
    server_name localhost; # Zmień na swoją domenę w produkcji

    location / {
      root /usr/share/nginx/html;
      index index.html;
      try_files $uri $uri/ /index.html; # Obsługa routingu po stronie klienta
    }

    location /api/ {
      proxy_pass http://backend:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
      proxy_pass http://backend:8000;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $websocket_upgrade;
      proxy_set_header Connection "Upgrade";
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /stats {
      proxy_pass http://backend:8000;
      proxy_set_header Host $host;
    }

    # Opcjonalnie: Konfiguracja SSL/TLS
    # listen 443 ssl;
    # ssl_certificate /etc/nginx/certs/fullchain.pem; # Ścieżka do certyfikatu
    # ssl_certificate_key /etc/nginx/certs/privkey.pem; # Ścieżka do klucza prywatnego
    # include /etc/nginx/options-ssl-nginx.conf; # Standardowe opcje bezpieczeństwa
    # ssl_dhparam /etc/nginx/ssl-dhparams.pem; # Parametry Diffie-Hellmana
  }
}
```

```sql
-- infra/postgres/init.sql
CREATE TABLE IF NOT EXISTS użytkownicy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hasło_hash VARCHAR(255) NOT NULL,
    utworzono_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logi_zapytań (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    użytkownik_id UUID REFERENCES użytkownicy(id),
    zapytanie TEXT NOT NULL,
    odpowiedź TEXT,
    czas_odpowiedzi_ms INTEGER,
    status_kodu INTEGER,
    utworzono_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Dodaj indeksy dla lepszej wydajności
CREATE INDEX IF NOT EXISTS idx_logi_uzytkownik_utworzono ON logi_zapytań (użytkownik_id, utworzono_at);
CREATE INDEX IF NOT EXISTS idx_logi_utworzono ON logi_zapytań (utworzono_at);
CREATE INDEX IF NOT EXISTS idx_uzytkownicy_email ON użytkownicy (email);

-- Opcjonalnie: Tabela na sesje JWT lub odświeżające tokeny
-- CREATE TABLE IF NOT EXISTS tokeny_odświeżające (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     użytkownik_id UUID REFERENCES użytkownicy(id),
--     token VARCHAR(255) UNIQUE NOT NULL,
--     wygasa_at TIMESTAMP WITH TIME ZONE NOT NULL,
--     utworzono_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );
```

```conf
# infra/redis/redis.conf
# Standardowy plik konfiguracyjny Redis, z włączonym AOF dla trwałości danych
appendonly yes
```

```dockerfile
# apps/backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalacja zależności systemowych potrzebnych przez niektóre biblioteki Pythona
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików projektu
# Użyj warstwy buforowania - kopiuj tylko pliki zależności najpierw
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj resztę kodu aplikacji i pakietów lokalnych
COPY ./app /app/app
COPY ../../packages/config/src /app/packages/config/src
COPY ../../packages/utils/src /app/packages/utils/src
COPY ../../packages/cache/src /app/packages/cache/src
COPY ../../packages/core/src /app/packages/core/src
COPY ../../packages/monitoring/src /app/packages/monitoring/src

# Ustawienie PYTHONPATH, aby umożliwić importowanie pakietów lokalnych
ENV PYTHONPATH=/app:/app/packages/config/src:/app/packages/utils/src:/app/packages/cache/src:/app/packages/core/src:/app/packages/monitoring/src

# Tworzenie katalogu na dane sesji i logi
RUN mkdir -p /app/data /app/logs

# Ustawienie zmiennych środowiskowych domyślnie lub użyj tych z docker-compose
ENV DATABASE_URL="postgresql://uzytkownik:haslo@db:5432/baza_danych"
ENV REDIS_URL="redis://redis:6379/0"
ENV JWT_SECRET_KEY="klucz_sekretny_jwt_bardzo_dlugi_i_losowy"
ENV PERPLEXITY_COOKIE="ciasteczko_perplexity_ai_wymagane"
ENV LOG_LEVEL="INFO"
ENV PERPLEXITY_CONFIG_PATH="/app/config.yaml" # Ścieżka do pliku konfiguracyjnego w kontenerze

# Użycie uvicorn jako serwera ASGI z workerami
# Możesz dostosować liczbę workerów w zależności od zasobów (np. --workers 4)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

```txt
# apps/backend/requirements.txt
fastapi==0.111.0
uvicorn==0.29.0
SQLAlchemy==2.0.29
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
websockets==12.0
prometheus_client==0.20.0
redis==5.0.4
aiohttp==3.9.5
asyncio==3.4.3
cachetools==5.3.3
curl_cffi==0.6.3
httpx==0.27.0
playwright==1.44.0 # Może wymagać dodatkowych zależności systemowych
PyYAML==6.0.1
tomli==2.0.1 # Wbudowane w Python 3.11+, ale dodane dla starszych
llama-cpp-python==0.2.75 # Potrzebuje dodatkowych zależności systemowych i kompilacji
python-dotenv==1.0.0
```

```python
# packages/config/src/settings.py
from pathlib import Path
from typing import Any, Dict, Optional
import tomllib, yaml
import os

# Upewnij się, że importujemy z odpowiedniego pakietu
from packages.utils.src.logger import Logger

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

```

```python
# packages/config/src/__init__.py
from .settings import KONFIGURACJA
```

```python
# packages/utils/src/logger.py
import atexit, logging, logging.handlers
from pathlib import Path
import os
from packages.config.src.settings import KONFIGURACJA # Import globalnej konfiguracji

class Logger:
    _inst = None

    # Przyjmujemy konfigurację jako argument, ale możemy użyć też globalnej KONFIGURACJA
    # Definicja __new__ dla singletona
    def __new__(cls, cfg=None):
        if not cls._inst:
            cls._inst = super().__new__(cls)
            # Użyj podanej konfiguracji lub globalnej instancji
            konf_do_uzycia = cfg if cfg else KONFIGURACJA
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
```

```python
# packages/utils/src/async_rate_limiter.py
import asyncio, time

class AsyncRateLimiter:
    """Asynchroniczny limiter liczby żądań na sekundę z możliwością burstu."""
    def __init__(self, rps: int = 20, burst: int = 5):
        if rps <= 0 or burst < 0:
             raise ValueError("RPS musi być > 0, a burst >= 0")
        self.rps, self.burst = rps, burst
        # Początkowo mamy tokensów równych burst, aby umożliwić natychmiastowe żądania
        self.tokens = float(burst)
        self.last = time.monotonic()
        self.lock = asyncio.Lock() # Blokada do synchronizacji dostępu do tokenów

    async def acquire(self):
        """Pozyskuje jeden token. Czeka, jeśli brak tokenów."""
        async with self.lock:
            now = time.monotonic()
            # Oblicz nowe tokeny, które "napłynęły" od ostatniego sprawdzenia
            elapsed = now - self.last
            self.last = now
            self.tokens = min(float(self.burst), self.tokens + elapsed * self.rps)

            # Jeśli mamy tokeny, zużyj jeden i zwróć
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return

            # Jeśli brak tokenów, oblicz czas oczekiwania na następny token
            # Czas oczekiwania na 1 token = 1 / rps
            # Aby mieć 1 token, potrzebujemy (1 - self.tokens) tokenów więcej
            # Czas oczekiwania = (1 - self.tokens) / rps
            czas_oczekiwania = (1.0 - self.tokens) / self.rps
            self.tokens = 0.0 # Ustawiamy tokeny na zero, bo musimy czekać

        # Zwolniliśmy blokadę, teraz czekamy poza nią
        await asyncio.sleep(czas_oczekiwania)
        # Po czekaniu, tokeny "napłynęły", możemy ponowić próbę (choć zwykle wystarczy jedno czekanie)
        # W tym prostym limiterze, po czekaniu możemy od razu "uzyskać" token,
        # ale dla precyzji można by ponowić acquire(). W tym przypadku proste czekanie jest wystarczające.
        # Można też zmodyfikować logikę, by acquire czekało i od razu odejmowało token po czekaniu.
        # Poniższa linia jest logicznie poprawniejsza po czekaniu, aby faktycznie "zużyć" token, który "przyszedł"
        # w trakcie snu, ale dla prostoty często pomija się rekurencję.
        # Ponowimy acquire, ale w większości przypadków zadziała od razu dzięki "napływowi" tokenów podczas snu.
        # W praktyce, po `await asyncio.sleep(czas_oczekiwania)`, przy następnym `acquire`, tokeny będą >= 0,
        # więc odjęcie 1.0 będzie możliwe (lub prawie możliwe, uwzględniając zmiennoprzecinkowe).
        # Prostszą logiką jest po prostu wyjść po spaniu, zakładając, że token jest już dostępny.
        # Implementacja poniżej jest bardziej defensywna/precyzyjna:
        await self.acquire() # Upewnij się, że faktycznie pozyskasz token po czekaniu.
```

```python
# packages/utils/src/async_retry.py
import asyncio
import functools
import random
from typing import Callable, Awaitable, TypeVar, ParamSpec

T = TypeVar('T')
P = ParamSpec('P')

def async_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Dekorator do asynchronicznych funkcji, dodający logikę ponawiania prób z wykładniczym backoffem i jitterem."""
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for i in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # packages.utils.src.logger by się przydał tutaj do logowania prób
                    # print(f"Próba {i+1}/{max_retries+1} nie powiodła się dla {func.__name__}: {e}")
                    if i == max_retries:
                        # print(f"Wszystkie {max_retries+1} próby dla {func.__name__} zakończone niepowodzeniem. Podnoszę wyjątek.")
                        raise e
                    # Oblicz opóźnienie: base_delay * (2 ** i) * (0.5 + random.random())
                    delay = base_delay * (2 ** i) * (0.5 + random.random() * 0.5) # Jitter między 0.5 a 1.0 * base_delay * 2^i
                    # print(f"Następna próba dla {func.__name__} za {delay:.2f}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

```

```python
# packages/utils/src/__init__.py
from .logger import Logger
from .async_rate_limiter import AsyncRateLimiter
from .async_retry import async_retry
```

```python
# packages/cache/src/memory_cache.py
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
```

```python
# packages/cache/src/__init__.py
from .memory_cache import PamięćLRU
```

```python
# packages/core/src/session_manager.py
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
```

```python
# packages/core/src/enhanced_client.py
import aiohttp
import asyncio
import uuid
import json
import random
import time # Dodany import time
import os # Dodany import os

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

```

```python
# packages/core/src/__init__.py
from .session_manager import SessionManager
from .enhanced_client import EnhancedClient
```

```python
# packages/monitoring/src/health_monitor.py
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

```

```python
# packages/monitoring/src/__init__.py
from .health_monitor import HealthMonitor, Status, Raport
```

```python
# apps/backend/app/services/perplexity_service.py
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

```

```python
# apps/backend/app/services/__init__.py
from .perplexity_service import SERWIS_PERPLEXITY
```

```python
# apps/backend/app/auth.py
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from packages.config.src.settings import KONFIGURACJA
from packages.utils.src.logger import Logger

logger = Logger().log

# Ustawienia z globalnej konfiguracji
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = KONFIGURACJA.pobierz("security.jwt_algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = KONFIGURACJA.pobierz("security.jwt_expire_minutes", 30)

if not JWT_SECRET_KEY:
    logger.error("KRYTYCZNY BŁĄD: Zmienna środowiskowa JWT_SECRET_KEY nie jest ustawiona!")
    # Można podnieść wyjątek lub zakończyć aplikację tutaj, w zależności od polityki startu
    # raise EnvironmentError("JWT_SECRET_KEY nie jest ustawione.")
    # Dla kontynuacji w developmentcie można ustawić domyślną, ale to NIEBEZPIECZNE W PRODUKCJI
    logger.warning("Używam domyślnego, niebezpiecznego klucza JWT_SECRET_KEY. USTAW GO W ZMIENNYCH ŚRODOWISKOWYCH!")
    JWT_SECRET_KEY = "domyslny_niebezpieczny_klucz_secretny_jwt_zmien_to_natychmiast"

# Kontekst hashowania haseł
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemat OAuth2PasswordBearer do użycia w zależnościach FastAPI
# tokenUrl='/token' wskazuje endpoint, gdzie klient może uzyskać token (u nas /api/token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Weryfikuje hasło."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashuje hasło."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Tworzy token dostępu JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Dodaj pole 'iat' (Issued At) dla lepszego zarządzania sesją
    to_encode.update({"iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Dekoduje token dostępu JWT."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        # Sprawdź, czy token nie wygasł - choć jwt.decode z "exp" to robi, explicite jest bezpieczniejsze
        expire_ts = payload.get("exp")
        if expire_ts and datetime.fromtimestamp(expire_ts, tz=timezone.utc) < datetime.now(timezone.utc):
             logger.warning("Próba użycia wygasłego tokenu JWT.")
             return None # Token wygasł
        return payload
    except JWTError as e:
        logger.error(f"Błąd dekodowania tokenu JWT: {e}")
        return None # Błąd dekodowania lub weryfikacji

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Zależność FastAPI do pobierania aktualnego użytkownika na podstawie tokenu."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Niepoprawne dane logowania",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    # Tutaj zazwyczaj sprawdzasz payload (np. email, user_id) z bazą danych
    # W tym uproszczonym przykładzie zakładamy, że payload wystarczy
    user_email = payload.get("sub") # 'sub' to standardowe pole subject w JWT
    if user_email is None:
        raise credentials_exception
    # Możesz tu pobrać obiekt użytkownika z bazy danych na podstawie emaila/ID
    # from app.deps import get_db # Zakładamy, że masz taką zależność
    # db = next(get_db())
    # user = db.query(models.User).filter(models.User.email == user_email).first()
    # if user is None:
    #     raise credentials_exception
    # Zwracamy uproszczony obiekt użytkownika lub słownik z danymi z tokenu
    logger.debug(f"Użytkownik uwierzytelniony: {user_email}")
    return {"email": user_email} # Zwracamy dane użytkownika z tokenu
```

```python
# apps/backend/app/deps.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeBase
from sqlalchemy.orm import sessionmaker
import os

# Importuj globalną konfigurację
from packages.config.src.settings import KONFIGURACJA
from packages.utils.src.logger import Logger

logger = Logger().log

# Ustawienia bazy danych z konfiguracji lub zmiennych środowiskowych
DATABASE_URL = KONFIGURACJA.pobierz("database.url")

# Sprawdź, czy URL bazy danych jest poprawnie skonfigurowany
if not DATABASE_URL or DATABASE_URL == DOMYŚLNY_YAML["database"]["url"]:
     logger.warning(f"DATABASE_URL nie ustawiony lub używa domyślnej wartości: {DATABASE_URL}. Upewnij się, że jest poprawnie skonfigurowany w zmiennych środowiskowych lub pliku konfiguracyjnym.")


# Utwórz silnik SQLAlchemy
# echo=True włącza logowanie zapytań SQL (przydatne do debugowania)
engine = create_engine(DATABASE_URL, echo=KONFIGURACJA.pobierz("database.echo_sql", False))

# Utwórz obiekt sesji lokalnej
# autocommit=False oznacza, że zmiany muszą być jawnie zatwierdzone (session.commit())
# autoflush=False zapobiega automatycznemu flushowaniu sesji
# bind=engine wiąże sesję z utworzonym silnikiem
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Bazowa klasa dla modeli danych (deklaratywna)
class BazowyModel(DeclarativeBase):
    pass

# Ta klasa jest potrzebna do definiowania modeli ORM w SQLAlchemy
# Przykład użycia:
# from app.deps import BazowyModel
# class Użytkownik(BazowyModel):
#     __tablename__ = "użytkownicy"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
#     email = Column(String, unique=True, index=True)
#     hasło_hash = Column(String)

def get_db() -> Generator:
    """Zależność FastAPI dostarczająca sesję bazy danych."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modele danych dla bazy danych (przykładowe, można przenieść do osobnego pliku models.py)
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UUID, Text
from sqlalchemy.sql import func
from uuid import uuid4

class DbUżytkownik(BazowyModel):
    __tablename__ = "użytkownicy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hasło_hash = Column(String, nullable=False)
    utworzono_at = Column(DateTime(timezone=True), server_default=func.now())

class DbLogZapytania(BazowyModel):
    __tablename__ = "logi_zapytań"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    użytkownik_id = Column(UUID(as_uuid=True), ForeignKey("użytkownicy.id"), nullable=True) # Możliwe zapytania anonimowe
    zapytanie = Column(Text, nullable=False)
    odpowiedź = Column(Text, nullable=True)
    czas_odpowiedzi_ms = Column(Integer, nullable=True)
    status_kodu = Column(Integer, nullable=True) # Status API
    utworzono_at = Column(DateTime(timezone=True), server_default=func.now())

# Funkcja do tworzenia wszystkich tabel w bazie danych
def utwórz_tabele():
    """Tworzy wszystkie tabele zdefiniowane przez BazowyModel."""
    logger.info("Tworzę tabele w bazie danych...")
    try:
        BazowyModel.metadata.create_all(bind=engine)
        logger.info("Tabele utworzone pomyślnie (lub już istniały).")
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia tabel w bazie danych: {e}")
        # Można podnieść wyjątek, aby przerwać start aplikacji, jeśli baza jest krytyczna
        # raise ConnectionError("Nie można utworzyć tabel w bazie danych.") from e

```

```python
# apps/backend/app/stats.py
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
```

```python
# apps/backend/app/main.py
import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Annotated
import time # Importowanie czasu

# Importuj pakiety lokalne
# packages.config.src
from packages.config.src.settings import KONFIGURACJA
# packages.utils.src
from packages.utils.src.logger import Logger
# packages.core.src
from packages.core.src.session_manager import SessionManager
# packages.monitoring.src
from packages.monitoring.src.health_monitor import Status
# packages.backend.app.services
from apps.backend.app.services.perplexity_service import SERWIS_PERPLEXITY
# packages.backend.app
from apps.backend.app.deps import get_db, utwórz_tabele, DbUżytkownik
from apps.backend.app.auth import create_access_token, verify_password, get_password_hash, get_current_user
from apps.backend.app.stats import prometheus_metrics, metrics_middleware # Import metryk i middleware

# Użyj globalnej instancji Loggera
logger = Logger().log

# Inicjalizacja FastAPI
app = FastAPI(
    title="Perplexity AI Optymalizacja API",
    description="API do optymalizowanego dostępu do Perplexity AI z cache i monitorowaniem.",
    version="1.0.0"
)

# Konfiguracja CORS
# Pozwól na żądania z frontendu uruchomionego lokalnie lub w Vercel/inne domenę
origins = [
    "http://localhost:3000",  # Frontend lokalny
    "http://localhost",       # Dostęp przez Nginx lokalnie
    "http://localhost:80",
    "http://localhost:443",
    "http://127.0.0.1:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:443",
    "https://twoja-domena-frontend.com", # Zmień na domenę produkcyjną frontendu
    "https://*.vercel.app", # Jeśli używasz Vercel (uwaga na bezpieczeństwo wildcard)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Pozwól na wszystkie metody (GET, POST, itp.)
    allow_headers=["*"], # Pozwól na wszystkie nagłówki
)

# Dodaj middleware do zbierania metryk HTTP
app.middleware("http")(metrics_middleware)


# --- Zdarzenia startu i zamknięcia aplikacji ---
@app.on_event("startup")
async def startup_event():
    """Zdarzenia uruchamiane przy starcie aplikacji."""
    logger.info("Aplikacja FastAPI startuje...")
    # Utwórz tabele w bazie danych przy starcie
    # Upewnij się, że baza danych jest dostępna, zanim to zrobisz
    # Można dodać logikę ponawiania prób połączenia z bazą
    try:
        utwórz_tabele()
        logger.info("Tabele bazy danych sprawdzone/utworzone.")
    except Exception as e:
        logger.error(f"Nie udało się połączyć z bazą danych lub utworzyć tabel: {e}")
        # Zdecyduj, czy aplikacja powinna wystartować bez bazy danych
        # W przypadku krytycznej zależności, można zakończyć proces: sys.exit(1)

    # Uruchom monitor zdrowia Perplexity AI w tle
    try:
        await SERWIS_PERPLEXITY.start_monitoringu()
        logger.info("Monitor zdrowia Perplexity AI uruchomiony.")
    except Exception as e:
        logger.error(f"Nie udało się uruchomić monitora zdrowia Perplexity AI: {e}")
        # Aplikacja może działać dalej, ale bez monitoringu

    logger.info("Aplikacja FastAPI wystartowała pomyślnie.")


@app.on_event("shutdown")
async def shutdown_event():
    """Zdarzenia uruchamiane przy zamknięciu aplikacji."""
    logger.info("Aplikacja FastAPI zamyka się...")

    # Zatrzymaj monitor zdrowia
    try:
        await SERWIS_PERPLEXITY.stop_monitoringu()
        logger.info("Monitor zdrowia Perplexity AI zatrzymany.")
    except Exception as e:
        logger.error(f"Błąd podczas zatrzymywania monitora zdrowia: {e}")

    # Zamknij serwis Perplexity AI (np. sesję aiohttp)
    try:
        await SERWIS_PERPLEXITY.zamknij()
        logger.info("Serwis Perplexity AI zamknięty.")
    except Exception as e:
        logger.error(f"Błąd podczas zamykania serwisu Perplexity AI: {e}")

    logger.info("Aplikacja FastAPI zamknięta.")

# --- Endpointy API ---

# Endpoint do testowania połączenia i zdrowia serwisu
@app.get("/api/health", summary="Sprawdza stan zdrowia serwisu Perplexity AI")
async def get_health_status():
    """
    Zwraca aktualny raport o stanie zdrowia klienta Perplexity AI.
    Informuje, czy serwis jest dostępny (OK), działa z problemami (DEGRADACJA),
    czy jest niedostępny (ZŁY).
    """
    try:
        raport = await SERWIS_PERPLEXITY.status_zdrowia()
        # Przekształć raport do formy czytelnej w JSON
        return {
            "stan": raport.stan.value,
            "czas_testu_sek": raport.czas_testu_sek,
            "udane_testy": raport.udane_testy,
            "nieudane_testy": raport.nieudane_testy,
            "timestamp": raport.timestamp
        }
    except Exception as e:
        logger.error(f"Błąd podczas pobierania statusu zdrowia: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Błąd serwisu podczas pobierania statusu zdrowia: {e}")


# Endpoint POST do zadawania pytań (synchronicznie)
@app.post("/api/ask", summary="Zadaj pytanie do Perplexity AI")
async def ask_perplexity(
    zapytanie: Annotated[str, Body(..., description="Treść zapytania do Perplexity AI")],
    current_user: Annotated[dict, Depends(get_current_user)] # Wymaga uwierzytelnienia JWT
):
    """
    Przyjmuje zapytanie tekstowe i zwraca odpowiedź z Perplexity AI.
    Wykorzystuje wewnętrzny cache i obsługuje limitowanie zapytań.
    Wymaga tokenu autoryzacji JWT.
    """
    logger.info(f"Endpoint /api/ask wywołany przez użytkownika: {current_user['email']}")
    try:
        odpowiedz = await SERWIS_PERPLEXITY.zapytaj(zapytanie)
        # Tutaj możesz opcjonalnie logować zapytanie do bazy danych
        # db: Session = Depends(get_db) # Trzeba by wstrzyknąć db tutaj lub użyć innej metody logowania
        # log_zapytania(db, current_user['email'], zapytanie, odpowiedz)
        return {"odpowiedz": odpowiedz}
    except ValueError as e:
         # Przykładowa obsługa konkretnego błędu z serwisu
         logger.error(f"Błąd walidacji zapytania: {e}")
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
         # Błędy związane z API (np. status 400/500)
         logger.error(f"Błąd wykonania zapytania do Perplexity AI: {e}")
         raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Błąd komunikacji z Perplexity AI: {e}")
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd podczas przetwarzania zapytania: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Wewnętrzny błąd serwisu: {e}")

# Endpoint WebSocket do strumieniowania odpowiedzi (wymaga adaptacji klienta Perplexity AI)
# Uwaga: Implementacja strumieniowania wymaga, aby EnhancedClient i serwis obsługiwały strumienie
# Perplexity API /chat/async zwraca pełną odpowiedź, a nie strumień.
# Aby zaimplementować strumieniowanie, trzeba by:
# 1. Znaleźć Perplexity API, które wspiera strumieniowanie lub
# 2. Użyć Playwright/Selenium w EnhancedClient do symulacji interakcji na stronie web (bardziej złożone)
# Poniższy kod jest szkieletem dla WS, zakłada, że serwis potrafi "streamować" lub wysyłać odpowiedzi kawałkami.
# Na potrzeby tego zadania, symulujemy strumieniowanie wysyłając pełną odpowiedź kawałkami.
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket do strumieniowania odpowiedzi z Perplexity AI.
    Wymaga, aby klient połączył się i opcjonalnie przesłał token JWT.
    """
    await websocket.accept()
    logger.info("Klient WebSocket połączony.")
    # Możesz wymagać uwierzytelnienia po nawiązaniu połączenia, wysyłając token
    # jako pierwszą wiadomość lub parametr połączenia.
    # W tym przykładzie zakładamy uproszczony model - brak wymagania uwierzytelnienia na poziomie WS
    # ale w prawdziwej aplikacji należy to dodać.

    try:
        while True:
            # Odbieraj wiadomość od klienta (oczekujemy tekstowego zapytania)
            data = await websocket.receive_text()
            logger.info(f"Otrzymano wiadomość przez WS: '{data[:100]}...'")

            # W prawdziwej aplikacji:
            # 1. Uwierzytelnij użytkownika, jeśli token był przesłany
            # 2. Przetwórz zapytanie (np. przez serwis PerplexityAIService)
            # 3. Strumieniuj odpowiedź z powrotem do klienta WebSocket

            # --- Symulacja strumieniowania odpowiedzi ---
            try:
                # Wywołaj serwis Perplexity AI (synchroniczne zapytanie jak na /api/ask)
                # SERWIS_PERPLEXITY.zapytaj() jest async, więc wywołaj go z await
                # Tutaj brak logiki cache hit/miss per user, logowanie req/err jest w serwisie
                # Jeśli serwis PerplexityAI nie obsługuje strumieniowania, musimy zasymulować
                # rozbicie pełnej odpowiedzi na kawałki.
                pelna_odpowiedz = await SERWIS_PERPLEXITY.zapytaj(data) # To może potrwać
                logger.info("Symuluję strumieniowanie pełnej odpowiedzi przez WS.")

                # Rozbij odpowiedź na kawałki i wysyłaj z opóźnieniem
                # To jest tylko symulacja, nie prawdziwe strumieniowanie tokenów z API
                kawałki = [pelna_odpowiedz[i:i+50] for i in range(0, len(pelna_odpowiedz), 50)] # Rozbij na kawałki po 50 znaków
                for kawałek in kawałki:
                    if kawałek: # Upewnij się, że kawałek nie jest pusty
                        await websocket.send_text(kawałek)
                        await asyncio.sleep(0.05) # Małe opóźnienie między kawałkami (np. 50 ms)

                # Wyślij specjalną wiadomość oznaczającą koniec strumienia (opcjonalnie)
                await websocket.send_text("[KONIEC_STRUMIENIA]")
                logger.info("Symulacja strumieniowania zakończona.")

            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania zapytania przez WS: {e}")
                # Wyślij komunikat o błędzie do klienta WebSocket
                await websocket.send_text(f"[BŁĄD] Wystąpił błąd podczas przetwarzania zapytania: {e}")
                # Opcjonalnie, możesz zamknąć połączenie po błędzie
                # await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                break # Wyjdź z pętli, jeśli chcesz zamknąć połączenie po błędzie

    except WebSocketDisconnect:
        logger.info("Klient WebSocket odłączony.")
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd w połączeniu WebSocket: {e}")
        # Spróbuj wysłać błąd przed zamknięciem
        try:
            await websocket.send_text(f"[BŁĄD] Nieoczekiwany błąd serwera: {e}")
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass # Ignoruj błędy podczas zamykania
        logger.info("Połączenie WebSocket zakończone z błędem.")


# Endpoint do metryk Prometheus
@app.get("/stats", summary="Zwraca metryki aplikacji w formacie Prometheus")
async def get_metrics():
    """
    Zwraca metryki monitorujące stan i wydajność aplikacji
    w formacie zrozumiałym przez Prometheus.
    """
    logger.debug("Endpoint /stats wywołany.")
    metrics = prometheus_metrics()
    return PlainTextResponse(metrics, media_type="text/plain")


# --- Endpointy Autoryzacji (przykład) ---

# Poniżej przykładowe endpointy do logowania/rejestracji.
# Wymagają bazy danych i tabel użytkowników.

# Model danych dla żądania logowania
from pydantic import BaseModel

class UzytkownikLogin(BaseModel):
    email: str
    hasło: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # Opcjonalnie: refresh_token, expires_in, itp.

@app.post("/api/token", response_model=Token, summary="Uzyskaj token dostępu JWT")
async def login_for_access_token(
    form_data: Annotated[UzytkownikLogin, Body(..., description="Dane logowania użytkownika")],
    db: Session = Depends(get_db) # Wstrzyknij sesję bazy danych
):
    """
    Weryfikuje dane logowania użytkownika (email i hasło) i zwraca token dostępu JWT.
    """
    logger.info(f"Próba logowania dla użytkownika: {form_data.email}")
    # Wyszukaj użytkownika w bazie danych
    user = db.query(DbUżytkownik).filter(DbUżytkownik.email == form_data.email).first()

    if not user or not verify_password(form_data.hasło, user.hasło_hash):
        logger.warning(f"Nieudana próba logowania dla użytkownika: {form_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niepoprawny email lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"Użytkownik zalogowany: {form_data.email}")
    # Utwórz token dostępu
    access_token_expires = timedelta(minutes=KONFIGURACJA.pobierz("security.jwt_expire_minutes", 30))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Model danych dla żądania rejestracji
class UzytkownikRegister(BaseModel):
    email: str
    hasło: str

@app.post("/api/register", summary="Zarejestruj nowego użytkownika")
async def register_user(
    user_data: Annotated[UzytkownikRegister, Body(..., description="Dane rejestracyjne użytkownika")],
    db: Session = Depends(get_db) # Wstrzyknij sesję bazy danych
):
    """
    Rejestruje nowego użytkownika w systemie.
    """
    logger.info(f"Próba rejestracji nowego użytkownika: {user_data.email}")
    # Sprawdź, czy użytkownik o podanym emailu już istnieje
    existing_user = db.query(DbUżytkownik).filter(DbUżytkownik.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Próba rejestracji istniejącego użytkownika: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Użytkownik o podanym emailu już istnieje"
        )

    # Hashuj hasło
    hashed_password = get_password_hash(user_data.hasło)

    # Utwórz nowego użytkownika
    nowy_uzytkownik = DbUżytkownik(
        email=user_data.email,
        hasło_hash=hashed_password
    )

    # Dodaj do sesji i zapisz w bazie danych
    db.add(nowy_uzytkownik)
    db.commit()
    db.refresh(nowy_uzytkownik)

    logger.info(f"Użytkownik zarejestrowany pomyślnie: {nowy_uzytkownik.email}")

    # Możesz od razu zwrócić token logowania po rejestracji
    access_token_expires = timedelta(minutes=KONFIGURACJA.pobierz("security.jwt_expire_minutes", 30))
    access_token = create_access_token(
        data={"sub": nowy_uzytkownik.email}, expires_delta=access_token_expires
    )

    return {"message": "Użytkownik zarejestrowany pomyślnie", "access_token": access_token, "token_type": "bearer"}

# --- Endpointy pomocnicze lub testowe ---

@app.get("/")
async def read_root():
    """Endpoint główny, zwracający prostą odpowiedź."""
    return {"Wiadomosc": "Serwis Perplexity AI Optymalizacja działa!"}

@app.get("/api/status", summary="Pobierz status serwisu (uproszczony)")
async def get_simple_status():
    """Zwraca uproszczony status serwisu i cache."""
    cache_status = SERWIS_PERPLEXITY.cache.stat() if SERWIS_PERPLEXITY.cache else {"enabled": False}
    session_stats = SERWIS_PERPLEXITY.session_manager.get_stats()

    health_report = SERWIS_PERPLEXITY.health_monitor.pobierz_ostatni_raport()
    health_status_value = health_report.stan.value if health_report else "nieznany"

    return {
        "status": "ok",
        "zdrowie_api": health_status_value,
        "cache": cache_status,
        "sesja": session_stats,
        "uptime_aplikacji_sekundy": int(time.time() - session_stats.get("start_time", time.time()))
    }

# Endpoint do testowania uwierzytelnienia
@app.get("/api/users/me", summary="Pobierz dane aktualnie zalogowanego użytkownika")
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Zwraca dane aktualnie zalogowanego użytkownika.
    Wymaga tokenu autoryzacji JWT.
    """
    logger.info(f"Endpoint /api/users/me wywołany przez użytkownika: {current_user['email']}")
    return current_user

# --- Endpoint do logowania zapytań (przykład użycia bazy) ---
# Funkcja do logowania zapytań (można ją wywoływać z endpointu /api/ask)
def log_zapytania(db: Session, user_email: str, zapytanie: str, odpowiedz: Optional[str] = None, czas_odpowiedzi_ms: Optional[int] = None, status_kodu: Optional[int] = None):
    """Loguje zapytanie do bazy danych."""
    try:
        # Pobierz ID użytkownika na podstawie emaila (jeśli potrzebne do klucza obcego)
        user = db.query(DbUżytkownik).filter(DbUżytkownik.email == user_email).first()
        user_id = user.id if user else None

        log_wpis = DbLogZapytania(
            użytkownik_id=user_id,
            zapytanie=zapytanie,
            odpowiedź=odpowiedź,
            czas_odpowiedzi_ms=czas_odpowiedzi_ms,
            status_kodu=status_kodu
        )
        db.add(log_wpis)
        db.commit()
        # db.refresh(log_wpis) # Opcjonalnie
        logger.debug("Zapytanie zalogowane w bazie danych.")
    except Exception as e:
        logger.error(f"Błąd podczas logowania zapytania do bazy danych: {e}")
        # Nie zgłaszaj błędu dalej, aby nie przerwać głównego żądania API
```

```typescript
// apps/frontend/package.json
{
  "name": "frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "clean": "rm -rf dist .turbo"
  },
  "dependencies": {
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-tooltip": "^1.0.7",
    "@react-three/fiber": "^8.16.6",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "framer-motion": "^11.2.6",
    "lucide-react": "^0.379.0",
    "react": "^19.0.0-rc-f994737d14-20240522",
    "react-dom": "^19.0.0-rc-f994737d14-20240522",
    "tailwind-merge": "^2.3.0",
    "tailwindcss-animate": "^1.0.7",
    "three": "^0.164.1",
    "vaul": "^0.9.1"
  },
  "devDependencies": {
    "@types/node": "^20.12.12",
    "@types/react": "^19.0.0-rc-f994737d14-20240522",
    "@types/react-dom": "^19.0.0-rc-f994737d14-20240522",
    "@typescript-eslint/eslint-plugin": "^7.2.0",
    "@typescript-eslint/parser": "^7.2.0",
    "@vitejs/plugin-react": "^5.0.0",
    "eslint": "^8.57.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.6",
    "postcss": "^8.4.38",
    "tailwindcss": "^4.0.0-alpha-12",
    "typescript": "^5.2.2",
    "vite": "^5.2.0"
  }
}
```

```js
// apps/frontend/postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

```js
// apps/frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ["class"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: `var(--radius)`,
        md: `calc(var(--radius) - 2px)`,
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
         // Kluczowe klatki dla dynamicznego gradientu
         "gradient-shift": {
          "0%": { "background-position": "0% 50%" },
          "50%": { "background-position": "100% 50%" },
          "100%": { "background-position": "0% 50%" },
        },
         // Animacja hover-lift
        "lift": {
          "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
          "50%": { transform: "translateY(-5px) rotate(1deg)" },
        },
         // Animacja tap-feedback
        "tap": {
          "0%": { transform: "scale(1)" },
          "50%": { transform: "scale(0.95)" },
          "100%": { transform: "scale(1)" },
        }
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "gradient-shift": "gradient-shift 15s ease infinite", // Zastosuj do tła
        "lift-on-hover": "lift 0.3s ease-in-out", // Użyj na hover
        "tap-on-click": "tap 0.1s ease-in-out" // Użyj na click
      },
       // Konfiguracja view-transition i scroll-timeline (modern CSS, może wymagać prefiksów lub Polyfill)
       // Tailwind 4 ma lepsze wsparcie dla CSS variables i nowości
       // Można zdefiniować niestandardowe właściwości lub utility
       // Przykład: Można definiować zmienne CSS w global.css i odwoływać się tutaj
       // '--view-transition-name': '...'
       // '--scroll-timeline': '...'
    },
  },
  plugins: [
    require("tailwindcss-animate"),
    // require("@tailwindcss/typography"), // Opcjonalnie dla lepszej typografii
    // Wtyczka dla niestandardowych wariantów animacji (np. hover:animate-lift)
    function ({ addUtilities, theme, e }) {
      const liftUtilities = {
        '.animate-lift-on-hover': {
          transition: 'transform 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-5px) rotate(1deg)',
          },
        },
      };
      const tapUtilities = {
         '.animate-tap-on-click': {
            transition: 'transform 0.1s ease-in-out',
            '&:active': {
               transform: 'scale(0.95)',
            },
         },
      };
      addUtilities(liftUtilities, ['hover']);
      addUtilities(tapUtilities, ['active']);
    }
  ],
}
```

```json
// apps/frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

```json
// apps/frontend/tsconfig.node.json
{
  "compilerOptions": {
    "composite": true,
    "esModuleInterop": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["vite.config.ts"]
}
```

```js
// apps/frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // Konfiguracja proxy do przekierowywania żądań API do backendu FastAPI
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Adres backendu FastAPI
        changeOrigin: true,
        rewrite: ( ścieżka ) => ścieżka.replace(/^\/api/, '/api'), // Upewnij się, że /api jest zachowane
      },
      '/ws': {
        target: 'ws://localhost:8000', // Adres backendu FastAPI dla WebSocket
        ws: true, // Włącz proxy dla WebSocket
        changeOrigin: true,
        rewrite: ( ścieżka ) => ścieżka.replace(/^\/ws/, '/ws'), // Upewnij się, że /ws jest zachowane
      },
       '/stats': {
        target: 'http://localhost:8000', // Adres backendu FastAPI dla metryk
        changeOrigin: true,
        rewrite: ( ścieżka ) => ścieżka.replace(/^\/stats/, '/stats'),
      }
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

```html
<!-- apps/frontend/index.html -->
<!doctype html>
<html lang="pl">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/logo.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Perplexity AI - Optymalizacja Dostępu</title>
    <!-- Meta tagi dla view-transition (wymaga aktywacji w przeglądarce lub polyfill) -->
    <!-- <meta name="view-transition" content="same-origin"> -->
  </head>
  <body class="antialiased">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

```css
/* apps/frontend/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;

    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 20% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 20% 98%;

    --border: 214.3 31.4% 91.5%;
    --input: 214.3 31.4% 91.5%;
    --ring: 221.2 83.2% 53.3%;

    --radius: 0.5rem;

    /* Zmienne dla dynamicznego gradientu */
    --gradient-color-1: 221.2 83.2% 53.3%; /* primary */
    --gradient-color-2: 210 40% 96.1%; /* secondary */
    --gradient-color-3: 0 0% 100%; /* background */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 20% 98%;

    --card: 222.2 84% 4.9%;
    --card-foreground: 210 20% 98%;

    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 20% 98%;

    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;

    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 20% 98%;

    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;

    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 20% 98%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 20% 98%;

    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 217.2 91.2% 59.8%;

     /* Zmienne dla dynamicznego gradientu w trybie ciemnym */
    --gradient-color-1: 217.2 91.2% 59.8%; /* primary dark */
    --gradient-color-2: 217.2 32.6% 17.5%; /* secondary dark */
    --gradient-color-3: 222.2 84% 4.9%; /* background dark */
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    /* Dynamiczny gradient tła */
    background: linear-gradient(-45deg,
      hsl(var(--gradient-color-1)),
      hsl(var(--gradient-color-2)),
      hsl(var(--gradient-color-3)),
      hsl(var(--gradient-color-2))
    );
    background-size: 400% 400%;
    animation: gradient-shift 15s ease infinite;
  }
}

/* Konfiguracja View Transitions (wymaga CSS `view-transition-name`) */
/* Przykład zastosowania: */
/* Element, który ma mieć animację przejścia, powinien mieć unikalne view-transition-name */
/* np. w CSS modułu lub inline style: `style={{ viewTransitionName: 'moja-sekcja' }}` */
/* Then you can style the transition pseudo-elements */
/*
@supports (animation-timeline: view()) {
  ::view-transition-old(moja-sekcja) {
    animation: fade-out 0.2s cubic-bezier(0.4, 0, 1, 1);
  }
  ::view-transition-new(moja-sekcja) {
    animation: fade-in 0.2s cubic-bezier(0, 0, 0.2, 1);
  }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}
*/

/* Konfiguracja Scroll Timeline (wymaga JS lub Polyfill) */
/* Można zdefiniować animację CSS, której progres będzie kontrolowany przez scroll */
/* Przykład:
.animuj-na-scroll {
  animation: fade-in linear forwards;
  animation-timeline: view(block);
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
*/

```

```typescript
// apps/frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css'; // Główny plik stylów (Tailwind)
import { ThemeProvider } from './context/ThemeContext.tsx'; // Kontekst motywu
import { AuthProvider } from './context/AuthContext.tsx'; // Kontekst autoryzacji
import { OnboardingProvider } from './context/OnboardingContext.tsx'; // Kontekst onboardingu

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* Zawijamy aplikację w konteksty */}
    <ThemeProvider>
      <AuthProvider>
        <OnboardingProvider>
          <App />
        </OnboardingProvider>
      </AuthProvider>
    </ThemeProvider>
  </React.StrictMode>,
);
```

```typescript
// apps/frontend/src/App.tsx
import React from 'react';
import { useTheme } from './context/ThemeContext'; // Hook do zarządzania motywem
import Naglowek from './components/layout/Naglowek'; // Komponent nagłówka
import Stopka from './components/layout/Stopka';   // Komponent stopki
import GlownaZawartosc from './components/layout/GlownaZawartosc'; // Komponent głównej zawartości
import OnboardingDialog from './components/onboarding/OnboardingDialog'; // Komponent dialogu onboardingowego
import PaletaPolecen from './components/command-palette/PaletaPolecen'; // Komponent palety poleceń
import Tlo3D from './components/three/Tlo3D'; // Komponent tła 3D (opcjonalnie)

function App() {
  const { theme } = useTheme(); // Pobierz aktualny motyw

  // Zastosuj klasę motywu do elementu body
  React.useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  return (
    <div className="app-kontener flex flex-col min-h-screen">
      {/* Opcjonalne tło 3D - może być umieszczone w kontenerze o fixed position */}
      {/* <div className="fixed inset-0 z-0 pointer-events-none">
        <Tlo3D />
      </div> */}

      {/* Główna struktura aplikacji */}
      <Naglowek />
      <GlownaZawartosc /> {/* Tutaj będą główne widoki, np. czat */}
      <Stopka />

      {/* Komponenty globalne/nakładki */}
      <OnboardingDialog /> {/* Dialog onboardingowy */}
      <PaletaPolecen /> {/* Paleta poleceń aktywowana hotkeyem */}

      {/* Kontenery shadcn/ui, radix-ui itp. - często dodawane w root/main.tsx */}
      {/* <Toaster /> // Przykład toastów */}
    </div>
  );
}

export default App;
```

```typescript
// apps/frontend/src/context/ThemeContext.tsx
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useLocalStorage } from '../lib/hooks'; // Niestandardowy hook do localStorage

type Motyw = 'ciemny' | 'jasny' | 'systemowy';

interface KontekstMotywu {
  theme: Motyw;
  setTheme: (theme: Motyw) => void;
}

const ThemeContext = createContext<KontekstMotywu | undefined>(undefined);

interface ProviderMotywuProps {
  children: ReactNode;
  defaultTheme?: Motyw;
  storageKey?: string;
}

export function ThemeProvider({
  children,
  defaultTheme = 'systemowy',
  storageKey = 'ui-theme',
}: ProviderMotywuProps) {
  // Użyj hooka useLocalStorage do synchronizacji motywu z localStorage
  const [theme, setThemeState] = useLocalStorage<Motyw>(storageKey, defaultTheme);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('jasny', 'ciemny'); // Usuń istniejące klasy

    // Logika zastosowania motywu:
    // Jeśli motyw to 'systemowy', użyj preferencji użytkownika
    if (theme === 'systemowy') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'ciemny' : 'jasny';
      root.classList.add(systemTheme);
    } else {
      // W przeciwnym razie, zastosuj wybrany motyw
      root.classList.add(theme);
    }
  }, [theme]); // Reaguj na zmianę stanu motywu

  // Funkcja do ustawiania motywu, która aktualizuje też stan w localStorage przez hook
  const setTheme = (nowyMotyw: Motyw) => {
    setThemeState(nowyMotyw); // useLocalStorage zajmie się localStorage i stanem lokalnym
  };

  const value = {
    theme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error('useTheme musi być użyty wewnątrz ThemeProvider');
  }

  return context;
}
```

```typescript
// apps/frontend/src/context/AuthContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useLocalStorage } from '../lib/hooks'; // Hook do localStorage
import { loginUser, registerUser, validateToken, LoginPayload, RegisterPayload } from '../lib/api'; // Funkcje API

interface Uzytkownik {
  email: string;
  // Dodaj inne pola użytkownika, jeśli API je zwraca
}

interface KontekstAutoryzacji {
  uzytkownik: Uzytkownik | null;
  token: string | null;
  jestZalogowany: boolean;
  ładuję: boolean;
  login: (dane: LoginPayload) => Promise<void>;
  register: (dane: RegisterPayload) => Promise<void>;
  logout: () => void;
  // Dodaj ewentualne błędy autoryzacji
  blad: string | null;
}

const AuthContext = createContext<KontekstAutoryzacji | undefined>(undefined);

interface ProviderAutoryzacjiProps {
  children: ReactNode;
}

export function AuthProvider({ children }: ProviderAutoryzacjiProps) {
  // Token przechowujemy w localStorage
  const [token, setToken] = useLocalStorage<string | null>('auth-token', null);
  const [uzytkownik, setUzytkownik] = useState<Uzytkownik | null>(null);
  const [ładuję, setŁaduję] = useState(true);
  const [blad, setBlad] = useState<string | null>(null);

  // Efekt sprawdzający token przy starcie aplikacji lub zmianie tokenu
  useEffect(() => {
    async function sprawdzToken() {
      setŁaduję(true);
      setBlad(null); // Resetuj błąd
      if (token) {
        try {
          const daneUzytkownika = await validateToken(token);
          setUzytkownik(daneUzytkownika); // Ustaw użytkownika na podstawie danych z tokenu
        } catch (error) {
          console.error("Błąd walidacji tokenu:", error);
          setUzytkownik(null);
          setToken(null); // Usuń niepoprawny/wygasły token
          setBlad("Sesja wygasła. Zaloguj się ponownie.");
        }
      } else {
        setUzytkownik(null);
      }
      setŁaduję(false);
    }

    sprawdzToken();
  }, [token, setToken]); // Zależności: token i setter tokenu z localStorage

  // Funkcja logowania
  const login = async (dane: LoginPayload) => {
    setŁaduję(true);
    setBlad(null);
    try {
      const response = await loginUser(dane);
      setToken(response.access_token); // Zapisz token w localStorage
      // Walidacja tokenu w useEffect pobierze dane użytkownika
    } catch (error: any) {
      console.error("Błąd logowania:", error);
      setBlad(error.message || "Nie udało się zalogować. Sprawdź dane.");
      setUzytkownik(null);
      setToken(null);
      throw error; // Ponownie zgłoś błąd, jeśli komponent wywołujący go potrzebuje
    } finally {
      setŁaduję(false);
    }
  };

  // Funkcja rejestracji
  const register = async (dane: RegisterPayload) => {
    setŁaduję(true);
    setBlad(null);
    try {
      const response = await registerUser(dane);
      // Po rejestracji często od razu logujemy użytkownika, API może zwrócić token
      if (response.access_token) {
           setToken(response.access_token);
      }
      // Walidacja tokenu w useEffect pobierze dane użytkownika
    } catch (error: any) {
      console.error("Błąd rejestracji:", error);
      setBlad(error.message || "Nie udało się zarejestrować. Spróbuj ponownie.");
      setUzytkownik(null);
      setToken(null); // Usuń token na wszelki wypadek
      throw error; // Ponownie zgłoś błąd
    } finally {
      setŁaduję(false);
    }
  };


  // Funkcja wylogowania
  const logout = () => {
    setToken(null); // Usuń token z localStorage
    setUzytkownik(null); // Wyczyść dane użytkownika
    setBlad(null); // Wyczyść błąd
    console.log("Użytkownik wylogowany.");
  };

  const value = {
    uzytkownik,
    token,
    jestZalogowany: !!uzytkownik, // Prosta flaga stanu zalogowania
    ładuję,
    login,
    register,
    logout,
    blad,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth musi być użyty wewnątrz AuthProvider');
  }

  return context;
}
```

```typescript
// apps/frontend/src/context/OnboardingContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useLocalStorage } from '../lib/hooks'; // Hook do localStorage

interface KontekstOnboardingu {
  jestOnboardingOtwarty: boolean;
  aktualnyKrok: number;
  rozpocznijOnboarding: () => void;
  następnyKrok: () => void;
  poprzedniKrok: () => void;
  zakończOnboarding: () => void;
  czyOnboardingZakonczony: boolean;
}

const OnboardingContext = createContext<KontekstOnboardingu | undefined>(undefined);

interface ProviderOnboardinguProps {
  children: ReactNode;
}

export function OnboardingProvider({ children }: ProviderOnboardinguProps) {
  // Użyj hooka useLocalStorage do przechowywania informacji o zakończeniu onboardingu
  const [czyOnboardingZakonczony, setCzyOnboardingZakonczony] = useLocalStorage<boolean>('onboarding-ukończony', false);
  const [jestOnboardingOtwarty, setJestOnboardingOtwarty] = useState(false);
  const [aktualnyKrok, setAktualnyKrok] = useState(1); // Start od kroku 1

  // Efekt sprawdzający, czy onboarding powinien być wyświetlony przy starcie
  useEffect(() => {
    // Jeśli onboarding nie został jeszcze zakończony, otwórz go przy starcie
    if (!czyOnboardingZakonczony) {
      // Dodaj opóźnienie, aby uniknąć blokowania ładowania strony
      const timer = setTimeout(() => {
         setJestOnboardingOtwarty(true);
         setAktualnyKrok(1); // Zawsze zacznij od kroku 1
      }, 500); // Opóźnienie 500 ms
      return () => clearTimeout(timer); // Czyszczenie timera
    }
  }, [czyOnboardingZakonczony]); // Zależność od flagi zakończenia onboardingu

  const rozpocznijOnboarding = () => {
    if (czyOnboardingZakonczony) {
      console.warn("Onboarding już ukończony.");
      return;
    }
    setJestOnboardingOtwarty(true);
    setAktualnyKrok(1);
  };

  const następnyKrok = () => {
    // Maksymalna liczba kroków to 3, po 3 kończymy
    if (aktualnyKrok < 3) {
      setAktualnyKrok(prev => prev + 1);
    } else {
      zakończOnboarding();
    }
  };

  const poprzedniKrok = () => {
    // Nie można wrócić przed krok 1
    if (aktualnyKrok > 1) {
      setAktualnyKrok(prev => prev - 1);
    }
  };

  const zakończOnboarding = () => {
    setCzyOnboardingZakonczony(true); // Zapisz w localStorage, że zakończono
    setJestOnboardingOtwarty(false); // Zamknij dialog
    setAktualnyKrok(1); // Zresetuj krok
  };

  const value = {
    jestOnboardingOtwarty,
    aktualnyKrok,
    rozpocznijOnboarding,
    następnyKrok,
    poprzedniKrok,
    zakończOnboarding,
    czyOnboardingZakonczony,
  };

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const context = useContext(OnboardingContext);

  if (context === undefined) {
    throw new Error('useOnboarding musi być użyty wewnątrz OnboardingProvider');
  }

  return context;
}
```

```typescript
// apps/frontend/src/components/ui/button.tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

// Definicja wariantów przycisku przy użyciu class-variance-authority
const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

// Definicja propsów przycisku
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean // Jeśli true, renderuje komponent podrzędny jako przycisk
}

// Komponent Button
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button" // Użyj Slot lub standardowego buttona
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))} // Połącz klasy tailwind i warianty
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button" // Nazwa komponentu do celów debugowania

export { Button, buttonVariants }
```

```typescript
// apps/frontend/src/components/ui/dialog.tsx
import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"

import { cn } from "@/lib/utils"

// Konfiguracja portalu dialogu (gdzie dialog będzie renderowany w DOM)
const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
const DialogPortal = DialogPrimitive.Portal

// Overlay dialogu - półprzezroczyste tło blokujące interakcję z resztą strony
const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

// Zawartość dialogu (okno modalne)
const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
        className
      )}
      {...props}
    >
      {children}
      {/* Przycisk zamykający dialog */}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
        <X className="h-4 w-4" />
        <span className="sr-only">Zamknij</span> {/* Tekst dla czytników ekranu */}
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

// Nagłówek dialogu
const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col space-y-1.5 text-center sm:text-left",
      className
    )}
    {...props}
  />
)
DialogHeader.displayName = "DialogHeader"

// Stopka dialogu
const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
      className
    )}
    {...props}
  />
)
DialogFooter.displayName = "DialogFooter"

// Tytuł dialogu
const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

// Opis dialogu
const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

// Eksportuj komponenty dialogu
export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
```

```typescript
// apps/frontend/src/components/ui/input.tsx
import * as React from "react"

import { cn } from "@/lib/utils"

// Propsy dla komponentu Input
export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

// Komponent Input
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input" // Nazwa komponentu

export { Input }
```

```typescript
// apps/frontend/src/components/ui/label.tsx
import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

// Warianty dla komponentu Label (obecnie tylko domyślny, ale można rozszerzyć)
const labelVariants = cva(
  "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
)

// Propsy dla komponentu Label
export interface LabelProps
  extends React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>,
    VariantProps<typeof labelVariants> {}

// Komponent Label
const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  LabelProps
>(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(labelVariants(), className)} // Zastosuj warianty i dodatkowe klasy
    {...props}
  />
))
Label.displayName = LabelPrimitive.Root.displayName // Nazwa komponentu

export { Label }
```

```typescript
// apps/frontend/src/components/ui/progress.tsx
import * as React from "react"
import * as ProgressPrimitive from "@radix-ui/react-progress"

import { cn } from "@/lib/utils"

// Komponent Progress
const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn(
      "relative h-2 w-full overflow-hidden rounded-full bg-secondary", // Kontener paska postępu
      className
    )}
    {...props}
  >
    <ProgressPrimitive.Indicator
      className="h-full w-full flex-1 bg-primary transition-transform duration-500 ease-in-out" // Wskaźnik postępu
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }} // Animacja paska
    />
  </ProgressPrimitive.Root>
))
Progress.displayName = ProgressPrimitive.Root.displayName // Nazwa komponentu

export { Progress }
```

```typescript
// apps/frontend/src/components/ui/tooltip.tsx
import * as React from "react"
import * as TooltipPrimitive from "@radix-ui/react-tooltip"

import { cn } from "@/lib/utils"

// Komponent Tooltip (root Radix)
const TooltipProvider = TooltipPrimitive.Provider
const Tooltip = TooltipPrimitive.Root
const TooltipTrigger = TooltipPrimitive.Trigger

// Zawartość Tooltipa
const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      "z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
      className
    )}
    {...props}
  />
))
TooltipContent.displayName = TooltipPrimitive.Content.displayName

// Eksportuj komponenty tooltipa
export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
```

```typescript
// apps/frontend/src/components/onboarding/Krok1.tsx
import React from 'react';
import { DialogTitle, DialogDescription } from '@/components/ui/dialog'; // Komponenty UI dialogu
import { Button } from '@/components/ui/button'; // Komponent przycisku
import { useOnboarding } from '@/context/OnboardingContext'; // Kontekst onboardingu

const Krok1: React.FC = () => {
  const { następnyKrok } = useOnboarding();

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Witaj w Optymalizacji Dostępu do Perplexity AI!</Dialogu>
        <DialogDescription>
          Ten krótki samouczek przeprowadzi Cię przez kluczowe funkcje naszej aplikacji.
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Tutaj możesz bezpiecznie i efektywnie korzystać z możliwości Perplexity AI,
        z dodatkowymi warstwami cache i monitorowania zdrowia.
        Gotów na rozpoczęcie?
      </div>
      <DialogFooter className="flex justify-end">
        <Button onClick={następnyKrok}>Dalej</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok1;
```

```typescript
// apps/frontend/src/components/onboarding/Krok2.tsx
import React from 'react';
import { DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress'; // Komponent paska postępu
import { useOnboarding } from '@/context/OnboardingContext';

const Krok2: React.FC = () => {
  const { następnyKrok, poprzedniKrok, aktualnyKrok } = useOnboarding();

  // Oblicz wartość paska postępu (na 3 kroki)
  const postęp = (aktualnyKrok / 3) * 100;

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Krok 2: Jak zadać pytanie?</DialogTitle>
        <DialogDescription>
          To proste! Użyj głównego pola tekstowego poniżej lub palety poleceń (Hotkey K).
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Twoje zapytania trafią do naszego zoptymalizowanego systemu.
        Sprawdzimy, czy odpowiedź jest już w cache, a jeśli nie - bezpiecznie zapytamy API Perplexity.
        Wyniki będą wyświetlane w oknie czatu.
      </div>
      <div className="w-full">
        <Progress value={postęp} className="w-full" />
      </div>
      <DialogFooter className="flex justify-between">
        <Button variant="outline" onClick={poprzedniKrok}>Wstecz</Button>
        <Button onClick={następnyKrok}>Dalej</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok2;
```

```typescript
// apps/frontend/src/components/onboarding/Krok3.tsx
import React from 'react';
import { DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useOnboarding } from '@/context/OnboardingContext';

const Krok3: React.FC = () => {
  const { zakończOnboarding, poprzedniKrok, aktualnyKrok } = useOnboarding();

  // Oblicz wartość paska postępu (na 3 kroki)
  const postęp = (aktualnyKrok / 3) * 100;

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Krok 3: Statystyki i Monitorowanie</DialogTitle>
        <DialogDescription>
          Śledź wykorzystanie systemu i jego stan zdrowia na dedykowanej stronie statystyk.
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Możesz monitorować ilość zapytań, trafienia w cache, czas odpowiedzi API oraz ogólny stan
        zdrowia klienta Perplexity AI dzięki wbudowanemu monitoringowi.
        To wszystko pomoże zoptymalizować Twoje koszty i wydajność.
        Jesteś gotów rozpocząć?
      </div>
       <div className="w-full">
        <Progress value={postęp} className="w-full" />
      </div>
      <DialogFooter className="flex justify-between">
         <Button variant="outline" onClick={poprzedniKrok}>Wstecz</Button>
        <Button onClick={zakończOnboarding}>Zacznij Korzystać!</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok3;
```

```typescript
// apps/frontend/src/components/onboarding/OnboardingDialog.tsx
import React from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog'; // Podstawowe komponenty dialogu
import Krok1 from './Krok1'; // Komponent pierwszego kroku
import Krok2 from './Krok2'; // Komponent drugiego kroku
import Krok3 from './Krok3'; // Komponent trzeciego kroku
import { useOnboarding } from '@/context/OnboardingContext'; // Kontekst onboardingu

const OnboardingDialog: React.FC = () => {
  const { jestOnboardingOtwarty, aktualnyKrok, zakończOnboarding } = useOnboarding();

  // Wybierz komponent kroku na podstawie aktualnego stanu
  const renderKrok = () => {
    switch (aktualnyKrok) {
      case 1:
        return <Krok1 />;
      case 2:
        return <Krok2 />;
      case 3:
        return <Krok3 />;
      default:
        // Zwróć null lub domyślny krok, jeśli stan jest nieoczekiwany
        return <Krok1 />;
    }
  };

  return (
    <Dialog open={jestOnboardingOtwarty} onOpenChange={(open) => !open && zakończOnboarding()}>
      <DialogContent className="sm:max-w-[425px]">
        {/* Renderuj aktualny krok wewnątrz zawartości dialogu */}
        {renderKrok()}
      </DialogContent>
    </Dialog>
  );
};

export default OnboardingDialog;
```

```typescript
// apps/frontend/src/components/command-palette/PaletaPolecen.tsx
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'; // Używamy dialogu jako bazy
import { Input } from '@/components/ui/input'; // Pole wprowadzania
import { Kbd } from '@/components/ui/kbd'; // Opcjonalny komponent Kbd do wyświetlania hotkeyów (można dodać)
import { Separator } from '@/components/ui/separator'; // Opcjonalny separator (można dodać)

interface Polecenie {
  id: string;
  nazwa: string;
  akcja: () => void;
  kategoria?: string;
}

const PaletaPolecen: React.FC = () => {
  const [otwarta, setOtwarta] = useState(false);
  const [szukanaFraza, setSzukanaFraza] = useState('');

  // Lista dostępnych poleceń (przykładowe)
  const polecenia: Polecenie[] = [
    { id: 'nowy_czat', nazwa: 'Rozpocznij Nowy Czat', akcja: () => console.log('Akcja: Nowy Czat'), kategoria: 'Czat' },
    { id: 'motyw_jasny', nazwa: 'Przełącz na Motyw Jasny', akcja: () => console.log('Akcja: Motyw Jasny'), kategoria: 'Wygląd' },
    { id: 'motyw_ciemny', nazwa: 'Przełącz na Motyw Ciemny', akcja: () => console.log('Akcja: Motyw Ciemny'), kategoria: 'Wygląd' },
    { id: 'motyw_systemowy', nazwa: 'Użyj Motywu Systemowego', akcja: () => console.log('Akcja: Motyw Systemowy'), kategoria: 'Wygląd' },
    { id: 'statystyki', nazwa: 'Przejdź do Statystyk', akcja: () => console.log('Akcja: Statystyki'), kategoria: 'Nawigacja' },
    { id: 'onboarding', nazwa: 'Pokaż Onboarding', akcja: () => console.log('Akcja: Onboarding'), kategoria: 'Pomoc' },
    { id: 'wyloguj', nazwa: 'Wyloguj się', akcja: () => console.log('Akcja: Wyloguj'), kategoria: 'Konto' },
    // ... dodaj więcej poleceń
  ];

  // Filtruj polecenia na podstawie szukanej frazy
  const przefiltrowanePolecenia = szukanaFraza
    ? polecenia.filter(p => p.nazwa.toLowerCase().includes(szukanaFraza.toLowerCase()))
    : polecenia; // Jeśli fraza pusta, pokaż wszystkie

  // Efekt obsługujący hotkey "K"
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Sprawdź, czy klawisz "K" został naciśnięty i czy nie jest w polu input/textarea
      if (event.key === 'k' && (event.target as HTMLElement).tagName !== 'INPUT' && (event.target as HTMLElement).tagName !== 'TEXTAREA') {
        event.preventDefault(); // Zapobiegaj domyślnej akcji przeglądarki
        setOtwarta(prev => !prev); // Przełącz stan otwarcia palety
      }
      // Zamknij paletę klawiszem Escape
      if (event.key === 'Escape') {
        setOtwarta(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []); // Pusta tablica zależności - efekt uruchamia się tylko raz

  // Resetuj szukaną frazę przy otwarciu/zamknięciu palety
  useEffect(() => {
    if (!otwarta) {
      setSzukanaFraza('');
    }
  }, [otwarta]);

  // Funkcja obsługująca wybór polecenia
  const wybierzPolecenie = (polecenie: Polecenie) => {
    polecenie.akcja(); // Wykonaj akcję przypisaną do polecenia
    setOtwarta(false); // Zamknij paletę po wyborze
  };

  return (
    <Dialog open={otwarta} onOpenChange={setOtwarta}>
      {/* Trigger może być ukryty, skoro używamy hotkeya */}
      {/* <DialogTrigger asChild>
        <Button variant="outline">Otwórz Paletę Poleceń</Button>
      </DialogTrigger> */}
      <DialogContent className="sm:max-w-[480px] p-0 overflow-hidden">
        {/* Pole wyszukiwania */}
        <div className="flex items-center border-b px-3">
          <Input
            placeholder="Szukaj poleceń..."
            className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 border-none focus-visible:ring-0 focus-visible:ring-offset-0"
            value={szukanaFraza}
            onChange={(e) => setSzukanaFraza(e.target.value)}
          />
        </div>
        {/* Lista przefiltrowanych poleceń */}
        {przefiltrowanePolecenia.length > 0 ? (
          <div className="max-h-[300px] overflow-y-auto py-2">
            {przefiltrowanePolecenia.map(polecenie => (
              <div
                key={polecenie.id}
                className="cursor-pointer select-none px-4 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                onClick={() => wybierzPolecenie(polecenie)}
              >
                {/* Wyświetl nazwę i kategorię */}
                {polecenie.nazwa}
                {polecenie.kategoria && (
                  <span className="ml-2 text-xs text-muted-foreground">
                    ({polecenie.kategoria})
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="py-4 text-center text-sm text-muted-foreground">
            Brak pasujących poleceń.
          </div>
        )}
        {/* Etykieta z hotkeyem na dole (opcjonalnie) */}
        <div className="flex items-center border-t px-3 py-2 text-xs text-muted-foreground">
           <span className="mr-auto">Naciśnij <Kbd>K</Kbd> aby otworzyć/zamknąć</span>
           <span>Naciśnij <Kbd>Enter</Kbd> aby wybrać, <Kbd>↑</Kbd><Kbd>↓</Kbd> aby nawigować</span>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PaletaPolecen;
```

```typescript
// apps/frontend/src/lib/utils.ts
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// Funkcja pomocnicza do łączenia klas CSS (zwłaszcza z Tailwind)
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Hook do zarządzania stanem w localStorage
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((val: T) => T)) => void] {
  // Stan do przechowywania naszej wartości
  // Przekaż do useState funkcję, aby obliczenia były wykonywane tylko raz
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") {
      return initialValue;
    }
    try {
      // Pobierz z localStorage według klucza
      const item = window.localStorage.getItem(key);
      // Parsuj zapisany JSON lub zwróć wartość początkową jeśli jej brak
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      // Jeśli wystąpi błąd (np. Quota Exceeded), zwróć wartość początkową
      console.error(error);
      return initialValue;
    }
  });

  // Funkcja, która będzie zapisywać stan do localStorage
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // Zezwól na zapisanie wartości funkcji
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      // Zapisz do stanu
      setStoredValue(valueToStore);
      // Zapisz do localStorage
      if (typeof window !== "undefined") {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      // Obsługa błędów zapisu (np. Quota Exceeded)
      console.error(error);
    }
  };

  return [storedValue, setValue];
}
```

```typescript
// apps/frontend/src/lib/api.ts
// Funkcje do komunikacji z API backendu (FastAPI)
import { useAuth } from "@/context/AuthContext"; // Zaimportuj hook useAuth

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'; // Domyślnie użyj proxy Vite lub ścieżki względnej

interface ApiResponse<T> {
  // Określ strukturę odpowiedzi API, np.
  // data: T;
  // message?: string;
  // status: number;
  [key: string]: any; // Uproszczona struktura - przyjmujemy dowolne pola
}

interface ApiError {
  detail: string;
  status_code?: number;
}

// Funkcja pomocnicza do obsługi odpowiedzi i błędów HTTP
async function handleApiResponse<T>(response: Response): Promise<ApiResponse<T>> {
  if (!response.ok) {
    let errorData: ApiError | string = `Błąd HTTP: ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson && errorJson.detail) {
        errorData = errorJson as ApiError;
      } else {
         errorData = JSON.stringify(errorJson);
      }
    } catch (e) {
      // Ignoruj błędy parsowania JSON, jeśli odpowiedź nie jest JSONem
    }
    console.error(`Błąd API: ${response.status}`, errorData);
    const errorMessage = typeof errorData === 'string' ? errorData : errorData.detail || `Błąd HTTP: ${response.status}`;
    const error = new Error(errorMessage) as any;
    error.status_code = response.status;
    throw error;
  }

  // Spróbuj sparsować odpowiedź jako JSON
  try {
    const data = await response.json();
    return data as ApiResponse<T>;
  } catch (e) {
    // Jeśli nie można sparsować jako JSON, zwróć pusty obiekt lub rzuć błąd
    // Zależy od oczekiwanego formatu odpowiedzi (np. endpoint /stats zwraca plain text)
    // Dla większości endpointów API (ask, token, register) oczekujemy JSONa,
    // więc rzucamy błąd, jeśli parsowanie zawiedzie.
    console.error("Błąd parsowania JSON odpowiedzi API:", e);
    const error = new Error("Niepoprawny format odpowiedzi od serwera") as any;
    error.status_code = 500; // Wewnętrzny błąd serwera lub błąd formatu
    throw error;
  }
}

// Interfejsy dla danych logowania i rejestracji
export interface LoginPayload {
  email: string;
  hasło: string; // Pole hasło zgodne z backendem
}

export interface RegisterPayload {
  email: string;
  hasło: string; // Pole hasło zgodne z backendem
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface UserDataFromToken {
  email: string;
  // ... inne pola z tokenu, np. 'exp'
}

// Funkcja logowania
export async function loginUser(credentials: LoginPayload): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });
  // Logowanie oczekuje body jako JSON {email: "", haslo: ""}
  // Endpoint token w auth.py i main.py oczekuje form_data, co jest typowe dla OAuth2.
  // Jeśli backend oczekuje `application/x-www-form-urlencoded`, trzeba by zmienić nagłówek i body.
  // Zgodnie z backendem, endpoint /api/token oczekuje JSONa {email: ..., hasło: ...}
  // Zmieniam backendowy endpoint /api/token, żeby oczekiwał JSONa. OK, już zmienione w main.py.

  const data = await handleApiResponse<TokenResponse>(response);
  return data;
}

// Funkcja rejestracji
export async function registerUser(userData: RegisterPayload): Promise<TokenResponse & { message: string }> {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  const data = await handleApiResponse<TokenResponse & { message: string }>(response);
  return data;
}

// Funkcja walidacji tokenu (np. przez endpoint /users/me)
export async function validateToken(token: string): Promise<UserDataFromToken> {
   const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'GET',
      headers: {
         'Authorization': `Bearer ${token}`,
      },
   });
   const data = await handleApiResponse<UserDataFromToken>(response);
   // Endpoint /users/me zwraca obiekt z danymi użytkownika z tokenu, np. { "email": "..." }
   if (!data || typeof data.email !== 'string') {
       throw new Error("Niepoprawne dane użytkownika w odpowiedzi walidacji tokenu.");
   }
   return data;
}


// Funkcja do wysyłania zapytania do Perplexity AI (endpoint POST /api/ask)
export async function sendPerplexityQuery(query: string, token: string): Promise<{ odpowiedz: string }> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`, // Dołącz token JWT
    },
    body: JSON.stringify(query), // Wysyłamy sam string zapytania w body, backend oczekuje stringa Body(...)
     // Backendowy endpoint /api/ask oczekuje `Annotated[str, Body(...)]`, co FastAPI parsuje z body
     // Jeśli oczekuje JSON {"query": "tekst"}, body powinno być JSON.stringify({query: query}).
     // Zmieniam backend, żeby oczekiwał JSON {"zapytanie": "tekst"}. Tak będzie czytelniej.
     // Backend oczekuje { zapytanie: string }.

  });
  const data = await handleApiResponse<{ odpowiedz: string }>(response);
  return data;
}

// Funkcja do łączenia z endpointem WebSocket (/ws/stream)
export function connectPerplexityStream(onMessage: (message: string) => void, onError: (error: Event) => void, onClose: (event: CloseEvent) => void): WebSocket {
  const websocketUrl = (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host + '/ws/stream';
  // W developmentcie z proxy Vite, '/ws/stream' zostanie przekierowane do ws://localhost:8000/ws/stream
  // W produkcji z Nginx, '/ws/stream' zostanie przekierowane do ws://backend:8000/ws/stream

  const ws = new WebSocket(websocketUrl);

  ws.onopen = () => {
    console.log('Połączenie WebSocket nawiązane.');
    // Po nawiązaniu połączenia można wysłać token autoryzacji, jeśli jest wymagany przez backend
    // Np. ws.send(JSON.stringify({ type: 'auth', token: TwójToken }));
  };

  ws.onmessage = (event: MessageEvent) => {
    // console.log('Wiadomość z WebSocket:', event.data);
    onMessage(event.data as string); // Przekaż wiadomość do callbacka
  };

  ws.onerror = (event: Event) => {
    console.error('Błąd WebSocket:', event);
    onError(event); // Przekaż błąd do callbacka
  };

  ws.onclose = (event: CloseEvent) => {
    console.log('Połączenie WebSocket zamknięte:', event.code, event.reason);
    onClose(event); // Przekaż zdarzenie zamknięcia do callbacka
  };

  return ws;
}

// Funkcja do wysyłania wiadomości przez WebSocket
export function sendWebSocketMessage(ws: WebSocket | null, message: string) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(message);
  } else {
    console.warn("WebSocket nie jest połączony lub nie jest gotowy.");
  }
}


// Funkcja do pobierania statusu zdrowia
export async function getHealthStatus(): Promise<any> { // Zmień 'any' na konkretny typ raportu
   const response = await fetch(`${API_BASE_URL}/health`);
   const data = await handleApiResponse<any>(response); // Zakładamy, że API zwraca JSON z raportem
   return data;
}

// Funkcja do pobierania statystyk Prometheus
export async function getPrometheusStats(): Promise<string> {
  const response = await fetch(`/stats`); // Endpoint metryk jest poza /api w tym projekcie
  if (!response.ok) {
     console.error(`Błąd HTTP podczas pobierania metryk: ${response.status}`);
     throw new Error(`Błąd HTTP: ${response.status}`);
  }
  // Endpoint /stats zwraca plain text, nie JSON
  const data = await response.text();
  return data;
}

```

```typescript
// apps/frontend/src/lib/hooks.ts
import { useState, useEffect } from 'react';

// useLocalStorage jest już zdefiniowany w utils.ts i eksportowany
// import { useLocalStorage } from './utils';

// Przykładowy hook do obsługi kliknięcia z feedbackiem animacji tap
// Wymaga dodania klasy CSS `.animate-tap-on-click` (zdefiniowanej w tailwind.config.js)
export function useTapFeedback() {
  const applyTapAnimation = (event: React.MouseEvent<HTMLElement>) => {
    const target = event.currentTarget;
    // Dodaj klasę animacji
    target.classList.add('animate-tap-on-click');
    // Usuń klasę po zakończeniu animacji
    target.addEventListener('animationend', () => {
      target.classList.remove('animate-tap-on-click');
    }, { once: true }); // Usuń listener po jednorazowym wywołaniu
  };

  return applyTapAnimation;
}

// Przykładowy hook do obsługi animacji hover-lift
// Wymaga dodania klasy CSS `.animate-lift-on-hover` (zdefiniowanej w tailwind.config.js)
export function useLiftOnHover() {
   // Ta animacja jest zaimplementowana czysto w CSS poprzez klasę utility i wariant hover
   // Hook nie jest ściśle potrzebny, wystarczy dodać klasę 'animate-lift-on-hover' do elementu.
   // Ale hook może pomóc w dynamicznym dodawaniu/usuwaniu klasy jeśli potrzebne.
   // Dla prostoty, polegamy na czystym CSS i utility class w Tailwind.
   // Zwracamy pustą funkcję lub null, albo możemy zwrócić funkcję dodającą/usuwającą klasę
   const applyLiftAnimationClass = (element: HTMLElement | null) => {
     if (element) {
        // Dodaj klasę - CSS zajmie się resztą na hover
        element.classList.add('animate-lift-on-hover');
        // Opcjonalnie usuń przy unmount
        return () => {
           element.classList.remove('animate-lift-on-hover');
        };
     }
     return () => {}; // Zwróć pustą funkcję czyszczącą
   };

   // Użycie: const elementRef = useRef(null); useEffect(() => useLiftOnHover()(elementRef.current), []);
   return applyLiftAnimationClass;
}


// Hook do wykrywania kliknięcia poza elementem
export function useOnClickOutside(ref: React.RefObject<HTMLElement>, handler: (event: MouseEvent | TouchEvent) => void) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      // Czy kliknięcie nastąpiło wewnątrz elementu ref lub jego dzieci
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler(event); // Wywołaj handler jeśli kliknięcie było poza elementem
    };

    document.addEventListener("mousedown", listener);
    document.addEventListener("touchstart", listener);

    return () => {
      document.removeEventListener("mousedown", listener);
      document.removeEventListener("touchstart", listener);
    };
  }, [ref, handler]); // Zależności: ref i handler
}


// Exportuj hooki
export { useLocalStorage } from './utils'; // Re-export useLocalStorage
```

```typescript
// apps/frontend/src/lib/theme.ts
// Ten plik może zawierać dodatkowe helpery do zarządzania motywem
// np. funkcje do przełączania motywu bezpośrednio bez hooka (jeśli potrzebne poza komponentami React)
// lub definicje typów/konstant związane z motywem.

// Przykład: funkcja ustawiająca motyw w localStorage i na elemenecie <html>
export function setMotywRaw(motyw: 'ciemny' | 'jasny' | 'systemowy') {
  if (typeof window !== 'undefined') {
    const root = window.document.documentElement;
    root.classList.remove('jasny', 'ciemny');

    if (motyw === 'systemowy') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'ciemny' : 'jasny';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(motyw);
    }

    // Zapisz do localStorage
    localStorage.setItem('ui-theme', motyw);
  }
}

// Przykład: funkcja pobierająca aktualny motyw z localStorage lub systemu
export function getMotywRaw(): 'ciemny' | 'jasny' | 'systemowy' {
  if (typeof window === 'undefined') {
    return 'systemowy'; // Domyślny na serwerze
  }
  const savedTheme = localStorage.getItem('ui-theme');
  if (savedTheme === 'ciemny' || savedTheme === 'jasny' || savedTheme === 'systemowy') {
    return savedTheme;
  }
  // Jeśli brak w localStorage, sprawdź preferencje systemu
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'ciemny';
  }
  return 'jasny'; // Domyślnie jasny, jeśli brak preferencji systemowych
}

```

```typescript
// apps/frontend/src/components/layout/Naglowek.tsx
import React from 'react';
import { Link } from 'react-router-dom'; // Jeśli używasz react-router
import { Button } from '@/components/ui/button'; // Komponent przycisku
import { useTheme } from '@/context/ThemeContext'; // Hook do motywu
import { useAuth } from '@/context/AuthContext'; // Hook do autoryzacji
import { SunIcon, MoonIcon, MenuIcon } from 'lucide-react'; // Ikony

const Naglowek: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const { jestZalogowany, uzytkownik, logout } = useAuth();

  // Funkcja przełączająca motyw
  const przełączMotyw = () => {
    setTheme(theme === 'ciemny' ? 'jasny' : 'ciemny');
  };

  return (
    <header className="bg-card text-card-foreground border-b p-4 flex justify-between items-center backdrop-blur-sm bg-opacity-80 z-10">
      <div className="flex items-center space-x-4">
        {/* Logo/Nazwa aplikacji */}
        {/* <Link to="/" className="text-xl font-bold"> */}
           <span className="text-xl font-bold">Perplexity Opti</span>
        {/* </Link> */}
        {/* Linki nawigacyjne (jeśli są potrzebne, np. do statystyk, profilu) */}
         {/* <nav className="hidden md:flex space-x-4">
           <Link to="/stats" className="text-sm font-medium transition-colors hover:text-primary">Statystyki</Link>
            {jestZalogowany && <Link to="/profil" className="text-sm font-medium transition-colors hover:text-primary">Profil</Link>}
         </nav> */}
      </div>

      <div className="flex items-center space-x-2">
        {/* Status zalogowania */}
        {jestZalogowany ? (
          <span className="text-sm text-muted-foreground hidden sm:inline">Zalogowany jako: {uzytkownik?.email}</span>
        ) : (
           <span className="text-sm text-muted-foreground hidden sm:inline">Niezalogowany</span>
        )}

        {/* Przycisk przełączający motyw */}
        <Button variant="ghost" size="icon" onClick={przełączMotyw} aria-label="Przełącz motyw">
          {theme === 'ciemny' ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
        </Button>

        {/* Przycisk wylogowania (tylko gdy zalogowany) */}
        {jestZalogowany && (
          <Button variant="outline" size="sm" onClick={logout}>
            Wyloguj
          </Button>
        )}

        {/* Przycisk logowania/rejestracji (tylko gdy niezalogowany) */}
        {!jestZalogowany && (
          <>
            {/* <Link to="/login"> */}
               {/* <Button variant="outline" size="sm">Zaloguj</Button> */}
            {/* </Link> */}
             {/* <Link to="/register"> */}
               {/* <Button size="sm">Rejestracja</Button> */}
            {/* </Link> */}
             {/* Proste przyciski bez routingu na potrzeby przykładu */}
             <Button variant="outline" size="sm" onClick={() => console.log("Przejdź do logowania")}>Zaloguj</Button>
             <Button size="sm" onClick={() => console.log("Przejdź do rejestracji")}>Rejestracja</Button>
          </>
        )}

        {/* Przycisk menu dla urządzeń mobilnych (opcjonalnie) */}
        {/* <Button variant="ghost" size="icon" className="md:hidden">
           <MenuIcon className="h-5 w-5" />
        </Button> */}
      </div>
    </header>
  );
};

export default Naglowek;
```

```typescript
// apps/frontend/src/components/layout/Stopka.tsx
import React from 'react';
import { cn } from '@/lib/utils'; // Helper do łączenia klas

interface StopkaProps extends React.HTMLAttributes<HTMLElement> {}

const Stopka: React.FC<StopkaProps> = ({ className, ...props }) => {
  return (
    <footer
      className={cn(
        "bg-card text-card-foreground border-t p-4 text-center text-sm text-muted-foreground mt-auto backdrop-blur-sm bg-opacity-80 z-10",
        className
      )}
      {...props}
    >
      © {new Date().getFullYear()} Perplexity AI Optymalizacja. Wszelkie prawa zastrzeżone (przykładowe).
      {/* Można dodać linki do polityki prywatności, warunków użytkowania itp. */}
    </footer>
  );
};

export default Stopka;
```

```typescript
// apps/frontend/src/components/layout/GlownaZawartosc.tsx
import React from 'react';
import OknoCzatu from '@/components/chat/OknoCzatu'; // Komponent okna czatu

interface GlownaZawartoscProps extends React.HTMLAttributes<HTMLElement> {}

const GlownaZawartosc: React.FC<GlownaZawartoscProps> = ({ className, ...props }) => {
  return (
    // Główna zawartość aplikacji, która będzie wypełniać dostępną przestrzeń
    // flex-grow sprawia, że ten element rozszerza się, wypychając stopkę na dół
    <main className={cn("flex-grow container mx-auto p-4", className)} {...props}>
      {/* Tutaj można umieścić routing lub główny komponent widoku */}
      {/* Na przykład, jeśli jesteśmy na stronie czatu, renderujemy OknoCzatu */}
      {/* Można użyć react-router do zarządzania widokami */}
      {/* <Routes>
        <Route path="/" element={<OknoCzatu />} />
        <Route path="/stats" element={<div>Strona Statystyk</div>} />
        <Route path="/login" element={<div>Strona Logowania</div>} />
        <Route path="/register" element={<div>Strona Rejestracji</div>} />
         <Route path="*" element={<div>404 - Nie znaleziono</div>} />
      </Routes> */}

      {/* Na potrzeby przykładu, renderujemy tylko OknoCzatu */}
      <OknoCzatu />

    </main>
  );
};

export default GlownaZawartosc;
```

```typescript
// apps/frontend/src/components/chat/OknoCzatu.tsx
import React, { useState, useEffect, useRef } from 'react';
import { sendPerplexityQuery, connectPerplexityStream, sendWebSocketMessage } from '@/lib/api'; // Funkcje API
import { useAuth } from '@/context/AuthContext'; // Kontekst autoryzacji
import WiadomoscCzatu from './WiadomoscCzatu'; // Komponent pojedynczej wiadomości
import PoleWprowadzania from './PoleWprowadzania'; // Komponent pola wprowadzania

interface Wiadomosc {
  id: number;
  tekst: string;
  nadawca: 'użytkownik' | 'ai';
  ładuje?: boolean; // Flaga informująca, czy odpowiedź AI jest w trakcie ładowania
}

const OknoCzatu: React.FC = () => {
  const { token, jestZalogowany, ładuję: ładujęAuth } = useAuth(); // Pobierz token i status zalogowania
  const [wiadomości, setWiadomości] = useState<Wiadomosc[]>([]);
  const [ładujeAi, setŁadujeAi] = useState(false); // Czy AI generuje odpowiedź
  const [bladCzatu, setBladCzatu] = useState<string | null>(null);

  // Ref do przewijania okna czatu na dół
  const wiadomościEndRef = useRef<HTMLDivElement>(null);

  // Stan dla WebSocket
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [jestWsPołączony, setJestWsPołączony] = useState(false);

  // Efekt do obsługi połączenia WebSocket
  useEffect(() => {
    // Nawiąż połączenie WS tylko raz, gdy komponent się montuje
    if (!ws) {
      try {
        console.log("Próbuję nawiązać połączenie WebSocket...");
        const nowyWs = connectPerplexityStream(
          handleWsMessage,
          handleWsError,
          handleWsClose
        );
        setWs(nowyWs);
      } catch (error) {
        console.error("Nie udało się nawiązać połączenia WebSocket:", error);
        setBladCzatu("Nie udało się połączyć z serwerem czatu.");
      }
    }

    // Funkcja czyszcząca: zamknij połączenie WS przy odmontowaniu komponentu
    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
         console.log("Zamykam połączenie WebSocket...");
         ws.close();
      }
    };
  }, [ws]); // Zależność od stanu ws

  // Efekt do przewijania okna czatu na dół przy dodaniu nowej wiadomości lub zakończeniu ładowania AI
  useEffect(() => {
    wiadomościEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [wiadomości, ładujeAi]);

  // Obsługa wiadomości z WebSocket
  const handleWsMessage = (wiadomosc: string) => {
     // Sprawdź, czy wiadomość oznacza koniec strumienia
     if (wiadomosc === "[KONIEC_STRUMIENIA]") {
       console.log("Otrzymano koniec strumienia z WS.");
       setŁadujeAi(false); // Zakończ stan ładowania
        // Aktualizuj ostatnią wiadomość AI, usuwając flagę ładuje
        setWiadomości(prev => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage && lastMessage.nadawca === 'ai' && lastMessage.ładuje) {
             return [...prev.slice(0, -1), { ...lastMessage, ładuje: false }];
          }
          return prev;
        });
       return;
     }

    // Dodaj otrzymany kawałek wiadomości do ostatniej wiadomości AI
    setWiadomości(prev => {
      const lastMessage = prev[prev.length - 1];
      // Jeśli ostatnia wiadomość jest wiadomością AI i jest w trakcie ładowania
      if (lastMessage && lastMessage.nadawca === 'ai' && lastMessage.ładuje) {
        // Zaktualizuj tekst ostatniej wiadomości
        return [...prev.slice(0, -1), { ...lastMessage, tekst: lastMessage.tekst + wiadomosc }];
      } else {
        // Jeśli nie, to nowy strumień się rozpoczął, dodaj nową wiadomość AI
        // W prawdziwej aplikacji ze strumieniowaniem, pierwsza wiadomość zainicjowałaby obiekt wiadomości
        // z flagą `ładuje: true`. W tej symulacji, startujemy ładowanie przed wysłaniem zapytania WS.
        // Dodajemy nową wiadomość AI z pierwszym kawałkiem i flagą ładuje
         return [...prev, { id: Date.now(), tekst: wiadomosc, nadawca: 'ai', ładuje: true }];
      }
    });
  };

  // Obsługa błędów WebSocket
  const handleWsError = (error: Event) => {
    console.error("Błąd WebSocket:", error);
    setBladCzatu("Wystąpił błąd w połączeniu czatu. Spróbuj odświeżyć stronę.");
    setŁadujeAi(false); // Zakończ ładowanie przy błędzie
  };

  // Obsługa zamknięcia WebSocket
  const handleWsClose = (event: CloseEvent) => {
    console.log("Połączenie WebSocket zamknięte.", event);
    setJestWsPołączony(false);
    if (event.code !== 1000) { // Kod 1000 oznacza normalne zamknięcie
        setBladCzatu(`Połączenie czatu zostało zakończone. Kod: ${event.code}`);
    }
    setŁadujeAi(false); // Zakończ ładowanie przy zamknięciu
  };

  // Funkcja wysyłająca zapytanie
  const wyslijZapytanie = async (zapytanie: string) => {
    if (!zapytanie.trim()) return; // Nie wysyłaj pustych zapytań
    if (ładujeAi) return; // Nie wysyłaj, jeśli AI już odpowiada

    setBladCzatu(null); // Wyczyść poprzednie błędy
    const noweWiadomości = [...wiadomości, { id: Date.now(), tekst: zapytanie, nadawca: 'użytkownik' as const }];
    setWiadomości(noweWiadomości);
    setSzukanaFraza(''); // Wyczyść pole wprowadzania

    // --- Wysyłanie przez WebSocket (preferowane dla strumieniowania) ---
    if (ws && ws.readyState === WebSocket.OPEN) {
       console.log("Wysyłam zapytanie przez WebSocket...");
       setŁadujeAi(true); // Rozpocznij stan ładowania
       // Dodaj pustą wiadomość AI z flagą ładuje
       setWiadomości(prev => [...prev, { id: Date.now() + 1, tekst: '', nadawca: 'ai', ładuje: true }]);
       sendWebSocketMessage(ws, zapytanie);

    } else {
      // --- Fallback na zapytanie HTTP POST, jeśli WS niedostępny ---
      console.warn("WebSocket niedostępny. Wysyłam zapytanie przez HTTP POST.");
      if (!jestZalogowany || !token) {
          setBladCzatu("Musisz być zalogowany, aby wysyłać zapytania.");
          return;
      }

      setŁadujeAi(true); // Rozpocznij stan ładowania
      // Dodaj pustą wiadomość AI z flagą ładuje
      setWiadomości(prev => [...prev, { id: Date.now() + 1, tekst: '', nadawca: 'ai', ładuje: true }]);

      try {
        const odpowiedz = await sendPerplexityQuery(zapytanie, token);
        console.log("Odpowiedź z API (HTTP POST):", odpowiedz);
        setWiadomości(prev => {
          // Znajdź ostatnią wiadomość AI z flagą ładuje i zaktualizuj ją
          const lastMessageIndex = prev.findIndex(msg => msg.nadawca === 'ai' && msg.ładuje);
          if (lastMessageIndex !== -1) {
             const updatedMessages = [...prev];
             updatedMessages[lastMessageIndex] = { ...updatedMessages[lastMessageIndex], tekst: odpowiedz.odpowiedz, ładuje: false };
             return updatedMessages;
          } else {
             // Jeśli nie znaleziono wiadomości z flagą ładuje (np. z powodu błędu wcześniej), dodaj nową
             return [...prev, { id: Date.now() + 2, tekst: odpowiedz.odpowiedz, nadawca: 'ai', ładuje: false }];
          }
        });
        setŁadujeAi(false); // Zakończ stan ładowania
      } catch (error: any) {
        console.error("Błąd podczas zapytania Perplexity (HTTP POST):", error);
        setBladCzatu(`Błąd: ${error.message || 'Nieznany błąd API'}`);
         setWiadomości(prev => {
          // Znajdź ostatnią wiadomość AI z flagą ładuje i oznacz ją jako błąd lub usuń
          const lastMessageIndex = prev.findIndex(msg => msg.nadawca === 'ai' && msg.ładuje);
           if (lastMessageIndex !== -1) {
              const updatedMessages = [...prev];
              // Możesz zmienić tekst na komunikat o błędzie lub usunąć wiadomość
              updatedMessages[lastMessageIndex] = { ...updatedMessages[lastMessageIndex], tekst: `[BŁĄD] ${error.message || 'Nie udało się uzyskać odpowiedzi.'}`, ładuje: false };
              return updatedMessages;
           }
           return prev;
         });
        setŁadujeAi(false); // Zakończ stan ładowania
      }
    }
  };

   // Komunikat o stanie ładowania/logowania
   if (ładujęAuth) {
     return <div className="text-center text-muted-foreground">Ładowanie...</div>;
   }

  return (
    <div className="flex flex-col h-[calc(100vh-150px)] bg-card rounded-lg shadow-lg overflow-hidden">
      {/* Okno wyświetlające wiadomości */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {wiadomości.map((wiadomosc) => (
          <WiadomoscCzatu
            key={wiadomosc.id}
            wiadomosc={wiadomosc}
            jestŁadowana={wiadomosc.ładuje || false} // Przekaż flagę ładowania do komponentu wiadomości
          />
        ))}
        {/* Pusty div do przewijania na dół */}
        <div ref={wiadomościEndRef} />
      </div>

      {/* Komunikat o błędzie */}
      {bladCzatu && (
        <div className="bg-destructive text-destructive-foreground p-3 text-center text-sm">
          {bladCzatu}
        </div>
      )}

      {/* Pole wprowadzania zapytania */}
      <div className="border-t p-4">
        {/* Przekaż funkcję wysyłania do PoleWprowadzania */}
        <PoleWprowadzania naWyslij={wyslijZapytanie} ładuje={ładujeAi} zablokowane={!jestZalogowany || ładujeAi} />
         {!jestZalogowany && (
            <p className="text-center text-sm text-muted-foreground mt-2">
               Zaloguj się, aby wysyłać zapytania.
            </p>
         )}
      </div>
    </div>
  );
};

export default OknoCzatu;
```

```typescript
// apps/frontend/src/components/chat/WiadomoscCzatu.tsx
import React from 'react';
import { cn } from '@/lib/utils'; // Helper do łączenia klas
import { Loader2 } from 'lucide-react'; // Ikona ładowania

interface Wiadomosc {
  id: number;
  tekst: string;
  nadawca: 'użytkownik' | 'ai';
  ładuje?: boolean; // Flaga informująca, czy odpowiedź AI jest w trakcie ładowania
}

interface WiadomoscCzatuProps {
  wiadomosc: Wiadomosc;
  jestŁadowana?: boolean; // Prop jawnie przekazująca stan ładowania
}

const WiadomoscCzatu: React.FC<WiadomoscCzatuProps> = ({ wiadomosc, jestŁadowana }) => {
  // Określ style w zależności od nadawcy
  const isUser = wiadomosc.nadawca === 'użytkownik';
  const bubbleClasses = cn(
    'max-w-[70%] p-3 rounded-lg',
    isUser
      ? 'bg-primary text-primary-foreground ml-auto rounded-br-none' // Wiadomości użytkownika po prawej
      : 'bg-muted text-muted-foreground mr-auto rounded-bl-none' // Wiadomości AI po lewej
  );

  return (
    <div className={cn("flex", isUser ? 'justify-end' : 'justify-start')}>
      <div className={bubbleClasses}>
        <p>{wiadomosc.tekst}</p>
        {/* Wskaźnik ładowania dla wiadomości AI */}
        {!isUser && (wiadomosc.ładuje || jestŁadowana) && (
           <Loader2 className="h-4 w-4 animate-spin text-muted-foreground mt-1" />
        )}
      </div>
    </div>
  );
};

export default WiadomoscCzatu;
```

```typescript
// apps/frontend/src/components/chat/PoleWprowadzania.tsx
import React, { useState } from 'react';
import { Input } from '@/components/ui/input'; // Komponent Input
import { Button } from '@/components/ui/button'; // Komponent Button
import { SendIcon } from 'lucide-react'; // Ikona wysyłania
import { cn } from '@/lib/utils'; // Helper do łączenia klas

interface PoleWprowadzaniaProps extends React.HTMLAttributes<HTMLFormElement> {
  naWyslij: (zapytanie: string) => void; // Funkcja wywoływana przy wysłaniu zapytania
  ładuje?: boolean; // Czy trwa ładowanie odpowiedzi AI
  zablokowane?: boolean; // Czy pole i przycisk są zablokowane
}

const PoleWprowadzania: React.FC<PoleWprowadzaniaProps> = ({ naWyslij, ładuje, zablokowane, className, ...props }) => {
  const [zapytanie, setZapytanie] = useState('');

  // Obsługa wysłania formularza
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // Zapobiegaj domyślnej akcji formularza (przeładowanie strony)
    if (zapytanie.trim() && !ładuje && !zablokowane) {
      naWyslij(zapytanie); // Wywołaj funkcję wysyłającą zapytanie
      setZapytanie(''); // Wyczyść pole po wysłaniu
    }
  };

  // Obsługa naciśnięcia Enter w polu Input (aby też wysyłało)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
     if (e.key === 'Enter' && !e.shiftKey) { // Wysyłaj po naciśnięciu Enter (bez Shift)
        e.preventDefault(); // Zapobiegaj dodaniu nowej linii
        handleSubmit(e as any); // Wywołaj handleSubmit (rzutowanie jest ok, bo preventDefault)
     }
  };


  return (
    <form
      className={cn("flex items-center space-x-2", className)}
      onSubmit={handleSubmit}
      {...props}
    >
      {/* Pole wprowadzania */}
      <Input
        placeholder={ładuje ? "Generuję odpowiedź..." : (zablokowane ? "Zablokowane" : "Zadaj pytanie...")}
        value={zapytanie}
        onChange={(e) => setZapytanie(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={ładuje || zablokowane} // Zablokuj pole podczas ładowania lub gdy zablokowane
        className="flex-grow" // Rozszerz pole, aby wypełniało dostępną przestrzeń
      />
      {/* Przycisk wysyłania */}
      <Button type="submit" size="icon" disabled={!zapytanie.trim() || ładuje || zablokowane}>
        <SendIcon className="h-4 w-4" />
        <span className="sr-only">Wyślij zapytanie</span> {/* Tekst dla czytników ekranu */}
      </Button>
    </form>
  );
};

export default PoleWprowadzania;
```

```typescript
// apps/frontend/src/components/three/Tlo3D.tsx
import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { useTheme } from '@/context/ThemeContext'; // Hook do motywu

// Komponent animowanej sfery
const DistortedSphere = ({ kolor }) => {
  const ref = useRef();
  useFrame((state) => {
    // Prosta animacja obrotu sfery
    if (ref.current) {
       // ref.current.rotation.y += 0.001;
       // ref.current.rotation.x += 0.0005;
    }
  });

  return (
    <Sphere args={[1, 64, 64]} scale={2}> {/* args: [radius, widthSegments, heightSegments], scale dostosowuje rozmiar */}
      <MeshDistortMaterial
        color={kolor} // Kolor sfery
        attach="material"
        distort={0.5} // Siła zniekształcenia
        speed={2}    // Prędkość animacji zniekształcenia
        roughness={0.5} // Chropowatość materiału
      />
    </Sphere>
  );
};


const Tlo3D: React.FC = () => {
  const { theme } = useTheme(); // Pobierz aktualny motyw
  const [kolorSfery, setKolorSfery] = useState<string>('#5c6bc0'); // Domyślny kolor (odcień primary)

  // Zmieniaj kolor sfery w zależności od motywu
  useEffect(() => {
    // Możesz pobrać kolory z CSS variables lub zdefiniować je tutaj
    if (theme === 'ciemny') {
      setKolorSfery('#7b8ec8'); // Odcień primary w trybie ciemnym
    } else {
      setKolorSfery('#5c6bc0'); // Odcień primary w trybie jasnym
    }
     // Użyj opóźnienia lub animacji koloru dla płynniejszego przejścia
  }, [theme]);

  return (
    // Kontener Canvas z react-three-fiber
    // Kamerę można dostosować, dodać oświetlenie itp.
    <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
      {/* Proste oświetlenie */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />

      {/* Komponent animowanej sfery */}
      <DistortedSphere kolor={kolorSfery} />

      {/* OrbitControls pozwala na interakcję myszą (dla debugowania/efektu) */}
      {/* <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} /> */}
      {/* Usunąłem OrbitControls, żeby tło było statyczne, chyba że potrzebujesz interakcji */}
    </Canvas>
  );
};

export default Tlo3D;
```

```xml
<!-- apps/frontend/public/logo.svg -->
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4Z" fill="#5C6BC0"/>
<path d="M12 6V18" stroke="#5C6BC0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M6 12H18" stroke="#5C6BC0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M16.9282 7.0718L7.0718 16.9282" stroke="#5C6BC0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M7.0718 7.0718L16.9282 16.9282" stroke="#5C6BC0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>

```

```xml
<!-- .github/workflows/ci.yml -->
name: CI/CD Perplexity Optymalizacja

on:
  push:
    branches:
      - main
    # Wyzwalaj na tagi dla publikacji/deploy (opcjonalnie)
    # tags:
    #   - 'v*'
  pull_request:
    branches:
      - main

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Sprawdzenie kodu (Checkout)
        uses: actions/checkout@v4

      - name: Konfiguracja Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm' # Użyj cache pnpm

      - name: Instalacja zależności pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 8
          run_install: |
            - recursive: true
              args: [--frozen-lockfile]

      - name: Konfiguracja Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pnpm' # Cache Pythona w kontekście pnpm workspace

      - name: Instalacja zależności Pythona (Backend)
        run: pip install -r apps/backend/requirements.txt

      # - name: Uruchom testy Backend (jeśli masz)
      #   run: cd apps/backend && pytest

      - name: Uruchom linting (ESLint, Pyright, itp.)
        run: pnpm lint

      - name: Uruchom formatowanie (Prettier)
        run: pnpm format --check

      - name: Zbuduj projekt (TurboRepo)
        run: pnpm build

      # Opcjonalnie: Uruchom testy E2E (Playwright w Dockerze)
      # - name: Ustawienie Playwright
      #   run: cd apps/frontend && pnpm exec playwright install --with-deps

      # - name: Uruchom testy E2E
      #   run: pnpm test:e2e # Potrzebujesz skryptu 'test:e2e' w głównym package.json TurboRepo

  # Przykład joba do zbudowania obrazów Docker
  build-docker-images:
    runs-on: ubuntu-latest
    needs: build-and-test # Uruchom po pomyślnym buildzie i testach
    steps:
      - name: Sprawdzenie kodu
        uses: actions/checkout@v4

      - name: Logowanie do DockerHub (lub innego rejestru)
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Ustawienie zmiennych Dockera (tagi, shasum)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: twoj_uzytkownik_dockera/perplexity-optymalizacja
          tags: |
            type=raw,value=latest,enable={{is_default_branch}}
            type=sha,enable=true,prefix={{branch}}-,suffix=

      - name: Zbuduj i wypchnij obraz Backend
        uses: docker/build-push-action@v5
        with:
          context: ./apps/backend
          file: ./apps/backend/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Zbuduj i wypchnij obraz Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./apps/frontend
          file: ./apps/frontend/Dockerfile # Załóżmy, że frontend też ma Dockerfile (np. serwowanie przez Nginx)
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          # W przypadku frontendu budowanego przez Vite i serwowanego statycznie,
          # Dockerfile mógłby kopiować build z hosta.
          # W Docker compose build odbywa się w tle, tu budujemy obraz do rejestru.
          # Trzeba skopiować pliki wynikowe buildu z apps/frontend/dist
          # Przykład: COPY --from=builder /app/dist /usr/share/nginx/html
          # W tej konfiguracji Dockerfile frontendu musi zbudować aplikację lub skopiować build z poprzedniego kroku CI.
          # Lepszym podejściem w monorepo jest zbudowanie frontendu w jobie build-and-test,
          # a następnie skopiowanie wyników do kontekstu Dockerfile.
          # Ale do uproszczenia, zakładamy, że Dockerfile frontendu sam buduje.

  # Przykład joba do Deploy (np. do VPS z Docker Compose)
  deploy:
    runs-on: ubuntu-latest
    needs: build-docker-images # Uruchom po zbudowaniu obrazów
    environment:
      name: Produkcja # lub Staging
    steps:
      - name: Sprawdzenie kodu
        uses: actions/checkout@v4

      - name: Skopiuj pliki na serwer przez SSH
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          source: "infra/*,apps/backend/Dockerfile,apps/backend/requirements.txt,apps/backend/app,packages,README.md" # Pliki potrzebne na serwerze
          target: "~/perplexity-optymalizacja" # Docelowy katalog na serwerze

      - name: Zdalne uruchomienie Docker Compose
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd ~/perplexity-optymalizacja
            # Ustaw zmienne środowiskowe na serwerze lub użyj pliku .env
            export DATABASE_URL=${{ secrets.PROD_DATABASE_URL }}
            export REDIS_URL=${{ secrets.PROD_REDIS_URL }}
            export JWT_SECRET_KEY=${{ secrets.PROD_JWT_SECRET_KEY }}
            export PERPLEXITY_COOKIE=${{ secrets.PROD_PERPLEXITY_COOKIE }}
            export LOG_LEVEL=${{ secrets.PROD_LOG_LEVEL }}

            # Zaciągnij najnowsze obrazy (jeśli używasz rejestru)
            docker compose pull

            # Uruchom kontenery w trybie detached, przebudowując jeśli potrzebne
            # Upewnij się, że frontend jest zbudowany lokalnie przed skopiowaniem lub zrób to w Dockerfile frontendu
            docker compose up -d --build backend nginx

            # Oczyść stare obrazy
            docker image prune -f
```

```markdown
<!-- README.md -->
# Perplexity AI - Optymalizacja Dostępu w Szarej Strefie

## Wprowadzenie

Projekt "Perplexity AI - Optymalizacja Dostępu" to zaawansowane narzędzie, które ma na celu zapewnić bardziej stabilny, wydajny i kontrolowany dostęp do możliwości Perplexity AI, nawet w warunkach ograniczonej łączności lub specyficznych wymagań. Zbudowany jako nowoczesna aplikacja webowa (dashboard), umożliwia użytkownikom interakcję z AI poprzez przyjazny interfejs, jednocześnie implementując mechanizmy takie jak cache, limitowanie zapytań, ponawianie prób i monitorowanie stanu serwisu.

## Cechy

- **Backend FastAPI:** Wydajne API w Pythonie z asynchronicznym przetwarzaniem, WebSocketami i JWT.
- **Frontend React 19:** Dynamiczny i responsywny interfejs użytkownika z nowoczesnymi bibliotekami (Tailwind 4, Radix UI, shadcn/ui, Framer Motion, React Three Fiber).
- **Monorepo pnpm + Turbo:** Zoptymalizowana struktura projektu do zarządzania wieloma pakietami i aplikacjami.
- **Cache:** Buforowanie odpowiedzi AI w pamięci podręcznej w celu szybszego dostępu i redukcji zapytań do zewnętrznego API.
- **Rate Limiting & Retry:** Kontrola częstotliwości zapytań i automatyczne ponawianie w przypadku błędów.
- **Proxy Support:** Możliwość wykorzystania listy proxy do routingu zapytań.
- **Monitoring & Metryki:** Wbudowany monitor zdrowia API i endpoint Prometheus do śledzenia stanu serwisu i wydajności.
- **Uwierzytelnienie JWT:** Zabezpieczenie dostępu do API za pomocą tokenów JWT.
- **Onboarding:** Intuicyjny samouczek dla nowych użytkowników.
- **Command Palette:** Szybki dostęp do funkcji aplikacji za pomocą skrótów klawiaturowych.
- **Dostępność WCAG:** Projektowanie z myślą o dostępności cyfrowej.
- **Deployment z Docker Compose:** Łatwe uruchamianie w kontenerach (PostgreSQL, Redis, Backend, Frontend, Nginx).
- **Automatyzacja CI/CD:** Pipeline GitHub Actions do testowania, budowania i wdrażania.

## Wymagania

- Docker i Docker Compose
- Node.js (v20+) i pnpm (v8+)
- Python (v3.11+)
- Git

## 1-Click Deploy (Docker Compose)

Najszybszym sposobem na uruchomienie aplikacji jest użycie Docker Compose.

1.  **Sklonuj repozytorium:**
    ```bash
    git clone <adres_repozytorium>
    cd perplexity-ai-optymalizacja
    ```

2.  **Przygotuj plik konfiguracyjny (opcjonalnie):**
    Domyślna konfiguracja jest zaszyta w kodzie, ale możesz stworzyć plik `config.yaml` w katalogu `infra`, aby ją nadpisać lub dodać listę proxy.

    Przykład `infra/config.yaml`:
    ```yaml
    api:
      max_retries: 5
    rate_limiting:
      requests_per_minute: 30
    proxy:
      enabled: true
      proxy_list:
        - "http://user:pass@host:port"
        - "socks5://host2:port2"
    logging:
      level: DEBUG
    ```
    Ten plik zostanie zamapowany do `/app/config.yaml` w kontenerze backendu.

3.  **Ustaw klucz JWT i ciasteczko Perplexity:**
    Utwórz plik `.env` w głównym katalogu projektu (na tym samym poziomie co `docker-compose.yml`) z niezbędnymi zmiennymi środowiskowymi. **To jest krytyczne dla bezpieczeństwa i działania API Perplexity.**

    ```env
    # Zmienne dla bazy danych (domyślne w docker-compose, ale można zmienić)
    POSTGRES_USER=uzytkownik
    POSTGRES_PASSWORD=haslo
    POSTGRES_DB=baza_danych

    # Zmienne dla Redis (domyślne w docker-compose, ale można zmienić)
    REDIS_URL=redis://redis:6379/0

    # *** WYMAGANE ZMIENNE ***
    # Klucz sekretny JWT - MUSI być długi i losowy!
    JWT_SECRET_KEY=TWÓJ_BARDZO_DŁUGI_I_LOSOWY_KLUCZ_SEKRETNY_JWT_ZMIEŃ_TO!

    # Ciasteczko PERPLEXITY_COOKIE - Wymagane do interakcji z API Perplexity AI.
    # Należy je uzyskać z sesji przeglądarki po zalogowaniu się na Perplexity.ai.
    # Zwykle jest to wartość klucza `p_token`.
    PERPLEXITY_COOKIE=TWÓJ_P_TOKEN_Z_PERPLEXITY_AI_ZMIEŃ_TO!

    # Poziom logowania (DEBUG, INFO, WARNING, ERROR)
    LOG_LEVEL=INFO

    # URL bazy danych dla backendu (używa zmiennych z postgres serwisu w docker-compose)
    DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

    # Ścieżka do pliku konfiguracyjnego w kontenerze (jeśli używasz)
    # PERPLEXITY_CONFIG_PATH=/app/config.yaml

    # Zmienne dla frontendu (prefix VITE_)
    # Domyślnie Vite proxy kieruje do backendu, nie potrzebujesz ustawiać tu API_BASE_URL
    # VITE_API_BASE_URL=/api

    ```
    **PAMIĘTAJ, ABY ZMIENIĆ DOMYŚLNE WARTOŚCI KLUCZY I CIASFECZKA!**

4.  **Zbuduj obrazy i uruchom kontenery:**
    Upewnij się, że jesteś w głównym katalogu projektu z plikiem `docker-compose.yml`.

    ```bash
    docker compose up -d --build
    ```
    Polecenie to zbuduje obrazy Docker (backend, frontend, nginx) i uruchomi wszystkie usługi (db, redis, backend, frontend, nginx) w tle (`-d`).

5.  **Dostęp do aplikacji:**
    Aplikacja będzie dostępna pod adresem `http://localhost`. Nginx przekieruje żądania API do backendu i serwuje statyczne pliki frontendu.

6.  **Zatrzymanie aplikacji:**
    W głównym katalogu projektu:
    ```bash
    docker compose down
    ```

## Budowanie i Uruchamianie Lokalnie (Development)

Możesz również uruchomić backend i frontend lokalnie, bez Dockera (wymaga zainstalowania zależności Pythona i Node.js/pnpm).

1.  **Zainstaluj pnpm:**
    ```bash
    npm install -g pnpm
    ```

2.  **Zainstaluj zależności w monorepo:**
    W głównym katalogu projektu:
    ```bash
    pnpm install
    ```

3.  **Konfiguracja backendu:**
    Utwórz plik `.env` w katalogu `apps/backend` lub ustaw zmienne środowiskowe w terminalu, zgodnie z opisem w sekcji Docker Compose (`JWT_SECRET_KEY`, `PERPLEXITY_COOKIE`, `DATABASE_URL`, `REDIS_URL`, `LOG_LEVEL`).

4.  **Uruchom bazę danych i Redis (jeśli nie używasz już wersji Dockerowych):**
    Jeśli nie masz lokalnie działających instancji PostgreSQL i Redis, możesz uruchomić je za pomocą Docker Compose:
    ```bash
    docker compose up -d db redis
    ```
    Pamiętaj o ustawieniu odpowiednich URLi w zmiennych środowiskowych backendu (`DATABASE_URL`, `REDIS_URL`).

5.  **Uruchom backend:**
    W terminalu, w katalogu `apps/backend`:
    ```bash
    pnpm dev
    ```
    (Skrypt 'dev' dla backendu może wymagać dodania w package.json, np. `uvicorn app.main:app --reload`)
    Jeśli nie ma skryptu dev w package.json dla backendu:
    ```bash
    cd apps/backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    Backend będzie działał pod `http://localhost:8000`.

6.  **Uruchom frontend:**
    W terminalu, w katalogu `apps/frontend`:
    ```bash
    pnpm dev
    ```
    Frontend będzie działał pod `http://localhost:3000` z proxy kierującym API do `http://localhost:8000`.

## Pipeline CI/CD (GitHub Actions)

Plik `.github/workflows/ci.yml` definiuje automatyczny pipeline, który:
1.  Sprawdza kod przy każdym pushu i pull requeście do gałęzi `main`.
2.  Instaluje zależności Pythona i Node.js przy użyciu cache pnpm.
3.  Uruchamia linting i formatowanie.
4.  Buduje projekt przy użyciu TurboRepo (`pnpm build`).
5.  (Opcjonalnie/Przykład) Buduje obrazy Docker i wypycha je do rejestru (np. DockerHub) po pomyślnym buildzie i testach. Wymaga konfiguracji tajemnic (`secrets.DOCKER_USERNAME`, `secrets.DOCKER_PASSWORD`).
6.  (Opcjonalnie/Przykład) Wdraża aplikację na zdalny serwer za pomocą SSH i Docker Compose. Wymaga konfiguracji tajemnic (`secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`) i zmiennych środowiskowych produkcyjnych (`secrets.PROD_...`).

## Struktura Projektu

```
.
├── .github/               # Konfiguracja GitHub Actions
│   └── workflows/
│       └── ci.yml         # Pipeline CI/CD
├── apps/                  # Aplikacje (frontend, backend)
│   ├── backend/           # Aplikacja backendowa (FastAPI)
│   │   ├── app/           # Kod aplikacji
│   │   ├── Dockerfile     # Definicja obrazu Docker backendu
│   │   └── requirements.txt # Zależności Pythona
│   └── frontend/          # Aplikacja frontendowa (React/Vite)
│       ├── public/        # Statyczne zasoby publiczne
│       ├── src/           # Kod źródłowy frontendu
│       ├── Dockerfile     # Definicja obrazu Docker frontendu (np. na bazie Nginx)
│       ├── package.json
│       ├── postcss.config.js
│       ├── tailwind.config.js
│       ├── tsconfig.json
│       └── vite.config.ts # Konfiguracja Vite (w tym proxy)
├── infra/                 # Infrastruktura (Docker Compose, Nginx, SQL, Redis)
│   ├── docker-compose.yml # Definicja usług Docker
│   ├── nginx/             # Konfiguracja Nginx
│   │   └── nginx.conf
│   ├── postgres/          # Skrypty inicjalizacyjne PostgreSQL
│   │   └── init.sql
│   └── redis/             # Konfiguracja Redis
│       └── redis.conf
├── packages/              # Współdzielone pakiety/biblioteki (kod Pythona)
│   ├── cache/             # Pakiet cache
│   ├── config/            # Pakiet konfiguracji
│   ├── core/              # Pakiet core (klient, sesja)
│   ├── monitoring/        # Pakiet monitorowania
│   ├── perplexity/        # Pakiet Perplexity (klasa PerplexityAI - zintegrowana w backend service)
│   └── utils/             # Pakiet narzędziowy
│       └── package.json   # Każdy pakiet może mieć swój package.json (opcjonalne w pnpm)
├── .gitignore             # Pliki do ignorowania przez Git
├── package.json           # Główny package.json monorepo (konfiguracja pnpm, skrypty turbo)
├── turbo.json             # Konfiguracja TurboRepo
└── README.md              # Ten plik
```

## Dostępność (WCAG)

Frontend został zbudowany z wykorzystaniem Radix UI i shadcn/ui, które kładą nacisk na dostępność. Wdrażając nowe komponenty lub modyfikując istniejące, należy:
- Używać semantycznych elementów HTML.
- Zapewniać poprawne atrybuty `aria-` dla elementów interaktywnych i dynamicznych.
- Upewnić się, że nawigacja klawiaturą jest możliwa dla wszystkich elementów.
- Zapewnić odpowiedni kontrast kolorów.
- Dodawać tekst alternatywny dla obrazów (`alt`).

## Mikro-interakcje i Animacje

- **Dynamiczne gradienty tła:** Zaimplementowane w globalnym CSS za pomocą `background-size` i animacji `gradient-shift`.
- **Hover-lift, Tap-feedback:** Zaimplementowane jako utility classes w `tailwind.config.js` (`.animate-lift-on-hover`, `.animate-tap-on-click`) i używane w komponentach.
- **View Transition:** Wymaga aktywacji w przeglądarce (`chrome://flags/#view-transition-apis`) lub Polyfill. Zdefiniowane w globalnym CSS jako komentarz - wymaga przypisania `view-transition-name` do elementów w React i potencjalnie użycia API `document.startViewTransition()`.
- **Scroll Timeline:** Nowa funkcja CSS, która pozwala powiązać progres animacji z pozycją scrolla. Podobnie jak View Transitions, wymaga wsparcia przeglądarki (obecnie głównie Chrome) lub Polyfill. Przykład użycia w globalnym CSS jako komentarz.

## Rozwój

### Dodawanie nowego pakietu/aplikacji

Użyj polecenia `pnpm create` lub stwórz folder w `apps` lub `packages` i dodaj plik `package.json`. TurboRepo automatycznie wykryje nowe workspace'y.

### Uruchamianie zadań TurboRepo

Użyj `pnpm turbo run <zadanie>` lub skrótów z głównego `package.json` (np. `pnpm dev`, `pnpm build`). TurboRepo uruchomi zadanie w każdym workspace, który je definiuje, i zrównolegli pracę.

## Testowanie

- **Testy jednostkowe/integracyjne:** Dodaj testy Pythona w `apps/backend/tests/` (np. z `pytest`) i testy React w `apps/frontend/src/tests/` (np. z `Jest`, `React Testing Library`).
- **Testy E2E:** Można użyć Playwright. Dodaj konfigurację w katalogu `apps/frontend` lub w osobnym pakiecie. Skrypt `pnpm test:e2e` w głównym `package.json` uruchomiłby testy.

## Pokrycie Testami (Coverage)

Skonfiguruj narzędzia do pomiaru pokrycia (np. `pytest-cov` dla Pythona, `Jest` z opcją `--coverage` dla React). Skonfiguruj skrypt CI do generowania raportu pokrycia i opublikowania go (np. do Codecov lub Coveralls) w celu wyświetlenia badge'a w README.

## Problemy i Rozwiązania (Debugging)

- **Błędy połączenia Docker Compose:** Sprawdź logi poszczególnych kontenerów (`docker compose logs <nazwa_serwisu>`). Upewnij się, że zmienne środowiskowe są poprawnie ustawione.
- **Błędy API Perplexity:** Sprawdź logi backendu. Zweryfikuj, czy ciasteczko `PERPLEXITY_COOKIE` jest nadal ważne i poprawnie ustawione. Sprawdź dostępność proxy, jeśli są używane.
- **Błędy Frontend:** Użyj konsoli przeglądarki. Sprawdź, czy frontend poprawnie komunikuje się z backendem (zakładka Network). Upewnij się, że proxy Vite lub Nginx poprawnie przekierowuje żądania.

## Licencja

[Wybierz licencję]

---

**Coverage Badge:**

<!-- Dodaj badge coverage po skonfigurowaniu raportowania w CI -->
<!-- [![Coverage Status](https://codecov.io/gh/twoj_uzytkownik/twoje_repo/branch/main/graph/badge.svg)](https://codecov.io/gh/twoj_uzytkownik/twoje_repo) -->
<!-- Zmień ścieżki na własne -->
```
Proszę najpierw zastosować poniższy patch (frontend-fixes.patch), aby zapewnić, że kod bazowy zawiera wszystkie niezbędne komponenty (DialogHeader, Kbd, Separator itd.). Wklej ten patch do katalogu projektu i uruchom np.:

patch -p1 < frontend-fixes.patch

Dzięki temu masz już w kodzie wszystkie potrzebne moduły i eksporty, na których będziemy bazować przy tworzeniu zaawansowanego promptu.


---

1. Dlaczego najpierw warto zastosować patch

1. Spójność komponentów UI

Patch wprowadza DialogHeader, Kbd, Separator oraz poprawia eksporty w dialog.tsx.

Dzięki temu, gdy w promptcie będziemy odwoływać się do tych modułów, AI będzie pracować na faktycznie istniejącym kodzie, nie na abstrakcyjnych przykładach.



2. Minimalny „zestaw narzędzi” do odpicowania projektu

W patchu znajdują się kluczowe elementy: nowe komponenty do mikrointerakcji, gotowe funkcje layoutu (nagłówek, stopka, paleta poleceń), konfiguracje Tailwind/Ts.

Gdy AI otrzyma kod z tymi komponentami, zyska pełen kontekst, by tworzyć dalsze mikrokomponenty, animacje, stylizacje i integracje.



3. Zgodność z najlepszymi praktykami frontendowymi

Eksportowanie DialogHeader w dialog.tsx czy dodanie Kbd i Separator to wzorcowe podejście do rozdzielenia warstwy logiki (Radix + shadcn/ui) od warstwy prezentacji (Tailwind).

Umożliwi AI zaproponowanie nowych komponentów w ten sam sposób.





---

2. Cel: Jak przygotować naprawdę dobry prompt („monit proteinowy”) do AI, by “odpicować” frontend

Poniżej znajdziesz:

1. Koncepcję promptu – co i jak opisać, by AI dostało maksimum informacji od razu.


2. Przykład promptu w stylu Perplexity Lab – z symulacją zespołu AI (wieloról), który burzy mózgi i generuje gotowy kod.


3. Zasady „proteinowego” formułowania monitów – czyli jak rozbijać problem na części, używać ról, przewidywać wyjście.



2.1. Kluczowe elementy skutecznego promptu

> Uwaga: Zanim uruchomisz prompt, upewnij się, że patch jest zaaplikowany – tylko wtedy AI będzie mogło odwołać się do faktycznych plików (np. Kbd, Separator, DialogHeader).



1. Kontekst projektu

Krótko opisz strukturę katalogów, używane technologie (React 19, TypeScript, Tailwind CSS, Radix UI).

Wspomnij, że patch dodał nowe komponenty (Kbd, Separator, eksport DialogHeader itp.), aby AI mogło je wykorzystać.



2. Zespołowe podejście do AI

Przypisz co najmniej dwie role:

DesignGuru (lub „VisionArchitect”) – odpowiada za wizję UX/UI, inspiracje, zbiera style (np. Linear.app, Vercel, Apple).

CodeWitch (lub „UIEngineer”) – implementuje konkretne rozwiązania w kodzie, przygotowuje komponenty, struktury, stylizacje Tailwind.


Prośba: każdy fragment wypowiedzi powinien być podpisany nazwą roli, żeby było jasne, kto co „myśli”.



3. Szczegółowe wytyczne funkcjonalne i wizualne

Powiedz, że interfejs ma być mobile-first, w pełni responsywny.

Podaj inspiracje: „layout podobny do Vercel Dashboard, panel boczny → lista projektów, główna sekcja → karta z mikrokomponentami”.

Wymagaj mikrointerakcji: Hover, Focus, Tap, Kbd hint, Tooltips, Loading spinnery, glassmorphism, motion.



4. Konkretny scenariusz użycia

Przykład: strona główna ma się składać z (na szerokoekranie) – panel lewy: „Lista projektów” + przycisk „Dodaj nowy projekt”; panel prawy: „Szczegóły projektu” (podzielone na karty: Overview, Stats, Chat AI, Settings).

W każdej karcie użyj Kbd, Separator, DialogHeader (wiadomości onboarding, tooltipy).



5. Rezultat końcowy

AI ma zwrócić:

1. Pełną strukturę katalogów (co nowego dodać → /components/ui/ModalCard.tsx, /components/buttons/IconButton.tsx itp.)


2. Kod poszczególnych komponentów w TypeScript + Tailwind (z komentarzami).


3. Instrukcję konfiguracji (np. w tailwind.config.js → dodać animation, keyframes, plugins).


4. Plan dalszego rozwoju (np. „w kolejnej fazie dodajemy dark mode z view-transition”, „w 3 dni zbudować testy w Storybooku”).





6. Przykładowa forma promptu

Bez nadmiernej ogólności – ale też nie mikro:

Za dużo detali → AI może się pogubić.

Za mało detali → wyjście zbyt błahe.


Używaj list punktowanych, żeby AI mogło łatwo zrozumieć kolejne kroki.





---

3. Przykładowy „monit proteinowy” w stylu Perplexity Lab

# 1. Zastosuj patch:
Na początek proszę zastosuj patch „frontend-fixes.patch” w katalogu projektu:
- Zawiera on nowe pliki: `Kbd`, `Separator`, poprawki `dialog.tsx`, aktualizacje plików onboardingowych itp.
- Dzięki temu usuniemy błędy typu „brak eksportu DialogHeader” oraz zyskamy mikrokomponenty do interakcji.

# 2. Kontekst:
Projekt jest zbudowany w monorepo z:
- `apps/frontend` (React 19, TypeScript, Tailwind CSS v4, Radix UI + shadcn/ui),
- `apps/backend` (FastAPI, Postg­reSQL, Redis),
- Pakiety: `packages/utils`, `packages/cache`, `packages/core`, `packages/monitoring`.

Chcemy **odświeżyć** frontend tak, aby:
- UI było inspirowane **Vercel Dashboard** (czysty, minimalny layout), **Linear.app** (szybkość, animacje),
- dodawać interaktywne mikrokomponenty (np. `Kbd` do wyświetlania hotkeyów, `Separator` do rozdzielenia sekcji, tooltipy, input z maską, loader),
- aplikacja była w pełni **mobile-first** i dostępna (WCAG AA).

# 3. Role AI:
Działacie wspólnie jako:
1. **DesignGuru (VisionArchitect)** – twoim zadaniem jest zaprojektować najwyższej klasy UX/UI:
   - Ustalcie schemat kolorów, spacing, typografię, ikonografię, style gradientów,
   - Zaproponujcie macierz mikrointerakcji (hover, focus, tap, ripple, glassmorphism),
   - Nakreślcie wireframe’y opisem tekstowym (jedna sekcja = osobny dialog UX).

2. **CodeWitch (UIEngineer)** – twoim zadaniem jest wziąć wytyczne od DesignGuru i przetworzyć je w **gotowy kod**:
   - Utwórzcie strukturę folderów `/components/ui/ModalCard.tsx`, `/components/buttons/IconButton.tsx`, `/components/layout/Sidebar.tsx`, `/components/layout/MainContent.tsx`, `/components/Onboarding` itd.
   - Każdy komponent ma być w TypeScript + Tailwind CSS; z użyciem `Kbd`, `Separator` z patcha.  
   - Dodajcie przykładowe storybookowe testy w `/src/stories/…`, stylizacje w `tailwind.config.js`.

# 4. Burza mózgów (DesignGuru):
- **DesignGuru:**  
  1. **Kolorystyka**:  
     - Primary: HSL(217, 91%, 59%) → gradient do HSL(210, 40%, 96%) (analogicznie Dark Mode: od HSL(217, 91%, 59%) → HSL(217, 32%, 17%)).  
     - Secondary: HSL(221, 83%, 53%) → pastelowy akcent, kontrast 4.5:1 z tekstem.  
     - Muted: HSL(214, 31%, 91%) do HSL(217, 32%, 17%).  

  2. **Typografia**:  
     - Nagłówki: `text-xl font-semibold tracking-tight`.  
     - Tekst zwykły: `text-base leading-relaxed`.  
     - Monospace dla code snippetów: `font-mono text-sm`.  

  3. **Spacing & Layout**:  
     - Gutter: 1rem (p-4) → przy mniejszych ekranach p-2, przy większych p-6.  
     - Grid: 12-kolumny → Sidebar 3 kolumny, Main 9 kolumn.  

  4. **Mikrointerakcje**:  
     - **Hover overlay**: przy hover na karcie – `shadow-lg scale-105 transition-transform 200ms`.  
     - **Active ripple**: przy tapnięciu na button → krótkie expand/contract.  
     - **Kbd**: pokazuj wskazówki klawiaturowe (K, Enter, Esc) zawsze w tooltipach.  
     - **Separator**: pionowy w menu → `mx-2 h-full`, poziomy w cardach → `my-2 h-px`.  

  5. **Układ VIP (ważne sekcje)**:  
     - **Nagłówek**: lewy: logo + nazwa „Perplexity Opti”. Prawy: przełącznik motywu (Sun/Moon), status użytkownika, logowanie/wyloguj.  
     - **Sidebar**: lista projektów, przycisk „Dodaj nowy” (z ikoną plus).  
     - **Main Content**:  
       - Karta “Dashboard” → wykresy (później Recharts), statystyki (cache hits, API latency).  
       - Krokowy onboarding (`DialogHeader`, `DialogDescription`, `DialogFooter`, postęp z `Progress`).  
       - Komponent „Paleta Poleceń” (`DialogContent` + `Input` + `Kbd`).

# 5. Szczegóły implementacji (CodeWitch):

- **Struktura plików**:

apps/frontend/src/ ├─ components/ │  ├─ ui/ │  │  ├─ Kbd.tsx             # z patcha │  │  ├─ Separator.tsx       # z patcha │  │  ├─ Dialog.tsx          # Radix + DialogHeader/Content, z patcha │  │  ├─ IconButton.tsx      # nowy: przycisk z ikonką │  │  ├─ Tooltip.tsx         # nowy: wrapper Radix Tooltip │  │  └─ ModalCard.tsx       # nowy: karta modalu │  ├─ buttons/ │  │  └─ IconButton.tsx      # nowy │  ├─ layout/ │  │  ├─ Sidebar.tsx         # nowy: panel boczny (lista projektów) │  │  ├─ MainContent.tsx     # nowy: główna zawartość │  │  ├─ Naglowek.tsx        # z patcha (dostosowany) │  │  └─ Stopka.tsx          # z patcha (lekko poprawiony) │  ├─ onboarding/ │  │  ├─ OnboardingDialog.tsx # z patcha (dostosowany) │  │  ├─ Krok1.tsx           # z patcha (dostosowany) │  │  ├─ Krok2.tsx           # z patcha (dostosowany) │  │  └─ Krok3.tsx           # z patcha (dostosowany) │  └─ command-palette/ │     └─ PaletaPolecen.tsx   # z patcha (dostosowany) ├─ lib/ │  ├─ utils.ts │  ├─ api.ts │  └─ hooks.ts └─ context/ ├─ ThemeContext.tsx ├─ AuthContext.tsx └─ OnboardingContext.tsx

- **Przykładowy kod nowego komponentu `IconButton.tsx`**:
```tsx
// apps/frontend/src/components/ui/IconButton.tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { LucideIcon } from "lucide-react" // importuj konkretną ikonę dynamicznie

const iconButtonVariants = cva(
  "inline-flex items-center justify-center rounded-md p-2 focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        ghost: "bg-transparent hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        sm: "h-8 w-8",
        md: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

export interface IconButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof iconButtonVariants> {
  icon: LucideIcon;        // klasa ikony z lucide-react
  label?: string;          // alt text dla czytników
}

const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant, size, icon: Icon, label = "", ...props }, ref) => {
    return (
      <button
        className={iconButtonVariants({ variant, size, className })}
        ref={ref}
        aria-label={label}
        {...props}
      >
        <Icon className="h-5 w-5" aria-hidden="true" />
      </button>
    );
  }
);
IconButton.displayName = "IconButton";

export { IconButton };

Przykład prostego Tooltip.tsx:

// apps/frontend/src/components/ui/Tooltip.tsx
import * as React from "react"
import * as TooltipPrimitive from "@radix-ui/react-tooltip"
import { cn } from "@/lib/utils"

export interface TooltipProps extends React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Root> {
  content: React.ReactNode
  children: React.ReactNode
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, ...props }) => {
  return (
    <TooltipPrimitive.Provider>
      <TooltipPrimitive.Root delayDuration={200} {...props}>
        <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            sideOffset={4}
            className={cn(
              "rounded-md bg-popover px-2 py-1 text-xs text-popover-foreground shadow-md",
            )}
          >
            {content}
            <TooltipPrimitive.Arrow className="fill-popover" />
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
};

Tooltip.displayName = "Tooltip";

export { Tooltip };

Przykład „Sidebar.tsx”:

// apps/frontend/src/components/layout/Sidebar.tsx
import React from "react";
import { Separator } from "@/components/ui/Separator";
import { IconButton } from "@/components/ui/IconButton";
import { PlusIcon, HomeIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  projects: { id: string; name: string }[];
  onAddProject: () => void;
  selectedProjectId?: string;
  onSelectProject: (id: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  projects,
  onAddProject,
  selectedProjectId,
  onSelectProject,
}) => {
  return (
    <aside className="w-64 bg-background border-r">
      <div className="p-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Projekty</h2>
        <IconButton
          icon={PlusIcon}
          label="Dodaj nowy projekt"
          onClick={onAddProject}
          variant="ghost"
        />
      </div>
      <Separator />
      <nav className="overflow-y-auto">
        {projects.map((proj) => (
          <div
            key={proj.id}
            onClick={() => onSelectProject(proj.id)}
            className={cn(
              "flex items-center space-x-2 px-4 py-2 hover:bg-accent hover:text-accent-foreground cursor-pointer",
              proj.id === selectedProjectId ? "bg-accent text-accent-foreground" : ""
            )}
          >
            <HomeIcon className="h-4 w-4" />
            <span className="text-sm">{proj.name}</span>
          </div>
        ))}
      </nav>
    </aside>
  );
};

export { Sidebar };

Przykład „MainContent.tsx” z zakładkami:

// apps/frontend/src/components/layout/MainContent.tsx
import React, { useState } from "react";
import { Tab } from "@headlessui/react";
import { Dialog } from "@/components/ui/Dialog"; // używa DialogHeader, DialogContent z patcha
import Krok1 from "@/components/onboarding/Krok1";
import Krok2 from "@/components/onboarding/Krok2";
import Krok3 from "@/components/onboarding/Krok3";
import { Separator } from "@/components/ui/Separator";

const tabs = ["Overview", "Statystyki", "Czat AI", "Ustawienia"];

const MainContent: React.FC = () => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  return (
    <main className="flex-1 flex flex-col">
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <Tab.List className="flex space-x-4 border-b bg-background p-2">
          {tabs.map((tab) => (
            <Tab
              key={tab}
              className={({ selected }) =>
                selected
                  ? "border-b-2 border-primary pb-1 text-primary"
                  : "text-muted-foreground pb-1 hover:text-primary"
              }
            >
              {tab}
            </Tab>
          ))}
        </Tab.List>
        <Tab.Panels className="flex-1 overflow-y-auto p-4">
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Przegląd {tabs[0]}</h3>
            {/* Tutaj np. szybki widok metryk */}
            <textarea
              readOnly
              className="w-full h-64 mt-4 p-2 border rounded-md bg-muted text-muted-foreground text-sm"
              value="Tutaj wyświetlimy najważniejsze metryki i szybką analizę aktywności..."
            />
          </Tab.Panel>
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Statystyki {tabs[1]}</h3>
            {/* Tu Recharts lub inny wykres */}
            <div className="mt-4 flex flex-col space-y-2">
              <div className="bg-white p-4 rounded-md shadow-sm">
                <span className="text-sm text-muted-foreground">Cache Hits:</span>
                <span className="text-lg font-bold">1234</span>
              </div>
              <div className="bg-white p-4 rounded-md shadow-sm">
                <span className="text-sm text-muted-foreground">API Latency (ms):</span>
                <span className="text-lg font-bold">256</span>
              </div>
            </div>
          </Tab.Panel>
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Czat AI {tabs[2]}</h3>
            {/* Wstaw OknoCzatu (z patcha/Twojej poprzedniej konfiguracji) */}
            <Separator className="my-4" />
            {/* OknoCzatu to komponent, który wyświetla historię i input */}
            <div className="flex flex-col h-[500px] border rounded-md overflow-hidden">
              {/* Tu wnętrze OknoCzatu */}
              <h4 className="text-sm text-muted-foreground p-2">Symulowane okno czatu…</h4>
            </div>
          </Tab.Panel>
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Ustawienia {tabs[3]}</h3>
            {/* np. zmiana motywu, konfiguracja webshocketów, itp. */}
            <button className="mt-4 inline-flex items-center space-x-2 rounded bg-secondary px-4 py-2 text-secondary-foreground hover:bg-secondary/80">
              Ustawienia globalne
            </button>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </main>
  );
};

export { MainContent };

Dostosowanie tailwind.config.js
Upewnij się, że masz w theme.extend:

animation: {
  "accordion-down": "accordion-down 0.2s ease-out",
  "accordion-up": "accordion-up 0.2s ease-out",
  "gradient-shift": "gradient-shift 15s ease infinite",
  "lift-on-hover": "lift 0.3s ease-in-out",
  "tap-on-click": "tap 0.1s ease-in-out"
},
keyframes: {
  "gradient-shift": {
    "0%": { "background-position": "0% 50%" },
    "50%": { "background-position": "100% 50%" },
    "100%": { "background-position": "0% 50%" },
  },
  "lift": {
    "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
    "50%": { transform: "translateY(-5px) rotate(1deg)" },
  },
  "tap": {
    "0%": { transform: "scale(1)" },
    "50%": { transform: "scale(0.95)" },
    "100%": { transform: "scale(1)" },
  }
}

Aktualizacja vite.config.ts → proxy dla /api, /ws, /stats (zalecane w patchu).


6. Plan dalszych działań

1. Testy w Storybook

Utwórz katalog src/stories/

Dodaj pliki Kbd.stories.tsx, IconButton.stories.tsx, Tooltip.stories.tsx z przykładami użycia.

Dzięki temu QA i designerzy mogą samodzielnie sprawdzić mikrokomponenty.



2. Dark Mode + View Transitions

Upewnij się, że ThemeContext poprawnie steruje klasami jasny/ciemny na <html>.

Dodaj view-transition dla płynnych animacji przy przełączaniu widoków (opcjonalnie wymaga polifilla).



3. Accessibility (WCAG) Audit

Sprawdź kontrasty kolorów wg narzędzi (axe, Lighthouse).

Dodaj aria-label, role, tabIndex tam, gdzie brak hierarchii semantycznych.



4. Mikrointerakcje „na kółkach”

Rozbuduj motion (Framer Motion) dla komponentów typu Accordion, Modal, Tooltip.

Upewnij się, że aria-expanded i aria-controls są poprawnie ustawione na przyciskach accordiona.



5. Dokumentacja Dev i Design

Utwórz plik UI_GUIDELINES.md w repozytorium z opisem:

Palety kolorów, typografii, spacingu, breakpoints, animacji.

Każdy komponent z patcha i każdy nowy powinien mieć krótki opis:

Kbd → do wyświetlania instrukcji klawiszowych

Separator → do wizualnego rozdzielania sekcji

IconButton → przycisk z ikoną i stanami hover/active.







---

4. Zasady „proteinowego” formułowania monitów

1. Podaj dokładny kontekst

Struktura folderów, technologie, patch, zależności.

Dlaczego to ważne? AI lepiej pracuje, gdy wie, co już istnieje i co może wykorzystać.



2. Użyj wieloról (multi-agent)

Dwie (lub więcej) role AI, które od razu symulują interdyscyplinarny zespół – burza mózgów + implementacja.

Każda rola „pomyśli głośno”:

DesignGuru: Jaki UX chcemy?

CodeWitch: Ok, zamieniam to w kod…




3. Dokładne specyfikacje i warunki

Określ: mobile-first, WCAG AA, animacje, gradienty, glassmorphism, pluginowe mikrokomponenty.

Podaj konkretne nazwy (Tailwind CSS utility, Radix UI), żeby AI generowało poprawne klasy.



4. Oczekiwane wyjście: struktura + kod + opis

AI musi wiedzieć, co ma oddać:

lista plików,

zawartość każdego pliku (TSX + Tailwind),

krótką notkę „dlaczego taki komponent” (DesignGuru).


Jeśli AI tylko opisze, będzie za mało. Jeśli AI tylko da kod bez uzasadnienia, też będzie za mało. Chcemy obie części.



5. Plan rozwoju

W promptcie poproś AI o listę rekomendacji „co zaimplementować w kolejnej fazie” – w ten sposób masz „roadmapę” z perspektywy AI.





---

5. Końcowe uwagi

Zawsze zaczynaj od patcha. Jeśli patch nie zostanie zaaplikowany, AI może pisać o komponentach, które w projekcie nie istnieją.

Używaj szczegółowych przykładów: zamiast pisać „stwórz button”, napisz „stwórz przycisk jako komponent IconButton w components/ui/IconButton.tsx, użyj lucide-react do ikony, styl Tailwind: bg-primary hover:bg-primary/90 text-primary-foreground”.

Testuj w Storybooku i manualnie w przeglądarce, by zweryfikować output AI.

Iteruj: za pierwszym razem AI może pominąć drobne szczegóły – popraw prompt, dodaj brakujące informacje.


Dzięki powyższemu, masz pełen blueprint do stworzenia “odpicowanego” frontendu: od patcha, przez projektowanie UI/UX, aż po gotowy kod z micro-interakcjami. Powodzenia!

