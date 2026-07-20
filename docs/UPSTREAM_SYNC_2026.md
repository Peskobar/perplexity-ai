# Upstream Sync 2026

## Cel

Zaktualizować `Peskobar/perplexity-ai` bez utraty własnych elementów projektu: dashboardu, backendu FastAPI, pakietów platformy, modułów zarządzania kontami oraz wcześniejszych poprawek.

## Stan porównania

Punktem wspólnym forka i upstreamu jest commit `d7306ff`. W chwili rozpoczęcia synchronizacji:

- upstream `helallao/perplexity-ai` miał 46 commitów ponad wspólną bazę;
- `Peskobar/perplexity-ai` miał 11 własnych commitów ponad wspólną bazę;
- gałęzie były rozbieżne, dlatego automatyczne nadpisanie `main` zostało odrzucone.

## Przeniesione w etapie 1

- serwer MCP działający przez `stdio` i lokalny HTTP;
- pięć narzędzi MCP, w tym bezpieczny podgląd stanu konta;
- parser zgodny ze starszym i nowszym formatem odpowiedzi Perplexity;
- odczyt cookies z JSON w zmiennej środowiskowej lub z pliku poza repozytorium;
- logowanie MCP do `stderr` oraz katalogu stanu użytkownika;
- `pyproject.toml` z opcjonalną zależnością MCP i komendą `perplexity-mcp`;
- `.gitignore` chroniący cookies, sesje, tokeny i pliki środowiskowe;
- test dymny wykonywany przez GitHub Actions;
- uzupełniona dokumentacja instalacji i uruchamiania.

## Celowo zachowane

- `perplexity.Client.create_account`;
- moduły `Emailnator` w wersji synchronicznej i asynchronicznej;
- `perplexity_async`;
- aplikacje w `apps/backend` i `apps/frontend`;
- pakiety w `packages/`;
- infrastruktura Docker, Redis, PostgreSQL i Nginx;
- wcześniejsza poprawka opcjonalnego `wait_for` w asynchronicznym Emailnatorze.

## Celowo nieprzeniesione w etapie 1

- wygenerowane katalogi `__pycache__` i `*.egg-info`;
- plik `perplexity.log` z upstreamu;
- automatyczne publikowanie paczki;
- pełne nadpisanie klienta synchronicznego i asynchronicznego;
- dokumenty upstreamu niezwiązane bezpośrednio z działaniem kodu;
- zmiany, które mogłyby usunąć lub zmienić własne funkcje forka.

## Następny etap

Po przejściu testów należy osobno ocenić aktualizacje:

1. endpointów i mapowania modeli;
2. obsługi uploadu plików;
3. parsera SSE w klientach sync/async;
4. testów kontraktowych na zanonimizowanych próbkach odpowiedzi;
5. integracji MCP z backendem FastAPI i panelem operatora.

Każdy etap powinien trafiać do osobnego PR, aby błędna zmiana protokołu nie uszkodziła całej platformy.
