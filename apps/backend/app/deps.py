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
