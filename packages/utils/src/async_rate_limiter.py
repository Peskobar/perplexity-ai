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
