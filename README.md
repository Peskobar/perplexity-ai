# Perplexity AI — Optymalizacja Dostępu

Projekt rozwija nieoficjalnego klienta Perplexity AI w kierunku kontrolowanej, lokalnej warstwy dostępu: biblioteki Python, zarządzania sesjami i kontami, API aplikacyjnego, dashboardu oraz integracji MCP.

> Projekt korzysta z nieoficjalnych interfejsów webowych. Zmiany po stronie Perplexity mogą czasowo przerwać działanie. Używaj wyłącznie własnych kont i własnych sesji; pliki cookies traktuj jak hasło.

## Co znajduje się w repozytorium

### Rdzeń Python

- klient synchroniczny `perplexity.Client`;
- klient asynchroniczny `perplexity_async`;
- obsługa wyszukiwania, trybów Pro/reasoning/deep research i przesyłania plików;
- istniejące moduły zarządzania kontami i Emailnator pozostają zachowane;
- obsługa Perplexity Labs.

### Platforma Peskobar

- backend FastAPI;
- frontend React 19, Tailwind, Radix UI i shadcn/ui;
- cache, retry i kontrola częstotliwości zapytań;
- monitoring i metryki Prometheus;
- JWT, onboarding i panel operatora;
- Docker Compose z PostgreSQL, Redis i Nginx;
- pakiety `core`, `config`, `cache`, `monitoring` i `utils`.

### MCP — aktualizacja 2026

Gałąź aktualizacyjna dodaje lokalny serwer MCP bez usuwania istniejących modułów:

- `perplexity_ask` — tryb automatyczny;
- `perplexity_search` — wyszukiwanie Pro;
- `perplexity_reason` — tryb rozumowania;
- `perplexity_research` — deep research;
- `perplexity_account_status` — stan sesji bez ujawniania cookies.

Parser obsługuje zarówno starszy format odpowiedzi oparty na zagnieżdżonym polu `text`, jak i nowszy format `blocks[].markdown_block`.

## Instalacja rdzenia i MCP

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[mcp]"
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
pip install -e ".[mcp]"
```

Termux — tryb eksperymentalny:

```bash
pkg install python git
python -m pip install --upgrade pip
pip install -e ".[mcp]"
```

## Podłączenie własnej sesji

Najbezpieczniej przechowywać eksport cookies poza katalogiem repozytorium:

```bash
export PERPLEXITY_COOKIES_FILE="$HOME/.config/perplexity/cookies.json"
perplexity-mcp
```

Alternatywnie można przekazać obiekt JSON bezpośrednio przez zmienną środowiskową:

```bash
export PERPLEXITY_COOKIES='{"next-auth.session-token":"..."}'
perplexity-mcp
```

Obsługiwany jest również eksport przeglądarkowy w formie listy obiektów zawierających pola `name` i `value`.

Bez cookies serwer działa anonimowo i udostępnia wyłącznie `perplexity_ask` oraz `perplexity_account_status`.

## Transport MCP

Domyślnie używany jest transport `stdio`:

```bash
perplexity-mcp
```

Lokalny transport HTTP:

```bash
export MCP_TRANSPORT=http
export MCP_HOST=127.0.0.1
export MCP_PORT=8000
perplexity-mcp
```

Logi nie trafiają na `stdout`, ponieważ ten kanał jest zarezerwowany dla JSON-RPC MCP. Są zapisywane domyślnie w:

```text
~/.local/state/perplexity-ai/perplexity.log
```

Ścieżkę można zmienić przez `PERPLEXITY_LOG_FILE`.

## Docker Compose — platforma

```bash
cd infra
docker compose up -d --build
```

Główne komponenty:

- backend: `apps/backend`;
- frontend: `apps/frontend`;
- infrastruktura: `infra`;
- wspólne pakiety: `packages`.

## Zasady bezpieczeństwa repozytorium

- nie commituj cookies, tokenów ani plików `.env`;
- MCP nigdy nie zwraca surowych cookies jako wyniku narzędzia;
- uruchamiaj endpoint HTTP wyłącznie na `127.0.0.1`, dopóki nie dodasz własnego uwierzytelniania;
- przed aktualizacją upstreamu używaj osobnej gałęzi i PR;
- sprawdzaj zmiany protokołu Perplexity przed wdrożeniem produkcyjnym.

## Status aktualizacji upstream

Aktualizacja jest wykonywana selektywnie. Zachowujemy własny dashboard, backend, moduły kont i wcześniejsze poprawki, a z upstreamu przenosimy elementy potrzebne do aktualnego MCP, pakowania i stabilnego logowania. Szczegóły znajdują się w `docs/UPSTREAM_SYNC_2026.md`.

## Licencja

MIT. Projekt nie jest powiązany ani oficjalnie wspierany przez Perplexity AI.
