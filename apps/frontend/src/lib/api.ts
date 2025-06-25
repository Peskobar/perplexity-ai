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
