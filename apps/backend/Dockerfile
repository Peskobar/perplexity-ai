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
