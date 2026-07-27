const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

interface ApiErrorPayload {
  detail?: string;
}

export interface LoginPayload {
  email: string;
  hasło: string;
}

export interface RegisterPayload {
  email: string;
  hasło: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface UserDataFromToken {
  email: string;
}

async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `Błąd HTTP: ${response.status}`;
    try {
      const payload = (await response.json()) as ApiErrorPayload;
      if (payload.detail) message = payload.detail;
    } catch {
      // Odpowiedź błędu nie musi być JSON-em.
    }

    const error = new Error(message) as Error & { status_code?: number };
    error.status_code = response.status;
    throw error;
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new Error('Niepoprawny format odpowiedzi od serwera');
  }
}

export async function loginUser(credentials: LoginPayload): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
  return handleApiResponse<TokenResponse>(response);
}

export async function registerUser(
  userData: RegisterPayload,
): Promise<TokenResponse & { message: string }> {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
  return handleApiResponse<TokenResponse & { message: string }>(response);
}

export async function validateToken(token: string): Promise<UserDataFromToken> {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await handleApiResponse<UserDataFromToken>(response);
  if (typeof data.email !== 'string') {
    throw new Error('Niepoprawne dane użytkownika w odpowiedzi walidacji tokenu.');
  }
  return data;
}

export async function sendPerplexityQuery(
  query: string,
  token: string,
): Promise<{ odpowiedz: string }> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(query),
  });
  return handleApiResponse<{ odpowiedz: string }>(response);
}

export function connectPerplexityStream(
  onMessage: (message: string) => void,
  onError: (error: Event) => void,
  onClose: (event: CloseEvent) => void,
): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const websocketUrl = `${protocol}//${window.location.host}/ws/stream`;
  const ws = new WebSocket(websocketUrl);

  ws.onmessage = (event: MessageEvent) => onMessage(String(event.data));
  ws.onerror = onError;
  ws.onclose = onClose;

  return ws;
}

export function sendWebSocketMessage(ws: WebSocket | null, message: string) {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(message);
  }
}

export async function getHealthStatus(): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleApiResponse<Record<string, unknown>>(response);
}

export async function getPrometheusStats(): Promise<string> {
  const response = await fetch('/stats');
  if (!response.ok) {
    throw new Error(`Błąd HTTP: ${response.status}`);
  }
  return response.text();
}
