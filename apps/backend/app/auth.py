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
