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
