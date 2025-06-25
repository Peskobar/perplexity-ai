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
