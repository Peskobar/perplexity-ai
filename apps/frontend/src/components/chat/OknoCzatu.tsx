import React, { useState, useEffect, useRef } from 'react';
import { sendPerplexityQuery, connectPerplexityStream, sendWebSocketMessage } from '@/lib/api'; // Funkcje API
import { useAuth } from '@/context/AuthContext'; // Kontekst autoryzacji
import WiadomoscCzatu from './WiadomoscCzatu'; // Komponent pojedynczej wiadomości
import PoleWprowadzania from './PoleWprowadzania'; // Komponent pola wprowadzania

interface Wiadomosc {
  id: number;
  tekst: string;
  nadawca: 'użytkownik' | 'ai';
  ładuje?: boolean; // Flaga informująca, czy odpowiedź AI jest w trakcie ładowania
}

const OknoCzatu: React.FC = () => {
  const { token, jestZalogowany, ładuję: ładujęAuth } = useAuth(); // Pobierz token i status zalogowania
  const [wiadomości, setWiadomości] = useState<Wiadomosc[]>([]);
  const [ładujeAi, setŁadujeAi] = useState(false); // Czy AI generuje odpowiedź
  const [bladCzatu, setBladCzatu] = useState<string | null>(null);

  // Ref do przewijania okna czatu na dół
  const wiadomościEndRef = useRef<HTMLDivElement>(null);

  // Stan dla WebSocket
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [jestWsPołączony, setJestWsPołączony] = useState(false);

  // Efekt do obsługi połączenia WebSocket
  useEffect(() => {
    // Nawiąż połączenie WS tylko raz, gdy komponent się montuje
    if (!ws) {
      try {
        console.log("Próbuję nawiązać połączenie WebSocket...");
        const nowyWs = connectPerplexityStream(
          handleWsMessage,
          handleWsError,
          handleWsClose
        );
        setWs(nowyWs);
      } catch (error) {
        console.error("Nie udało się nawiązać połączenia WebSocket:", error);
        setBladCzatu("Nie udało się połączyć z serwerem czatu.");
      }
    }

    // Funkcja czyszcząca: zamknij połączenie WS przy odmontowaniu komponentu
    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
         console.log("Zamykam połączenie WebSocket...");
         ws.close();
      }
    };
  }, [ws]); // Zależność od stanu ws

  // Efekt do przewijania okna czatu na dół przy dodaniu nowej wiadomości lub zakończeniu ładowania AI
  useEffect(() => {
    wiadomościEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [wiadomości, ładujeAi]);

  // Obsługa wiadomości z WebSocket
  const handleWsMessage = (wiadomosc: string) => {
     // Sprawdź, czy wiadomość oznacza koniec strumienia
     if (wiadomosc === "[KONIEC_STRUMIENIA]") {
       console.log("Otrzymano koniec strumienia z WS.");
       setŁadujeAi(false); // Zakończ stan ładowania
        // Aktualizuj ostatnią wiadomość AI, usuwając flagę ładuje
        setWiadomości(prev => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage && lastMessage.nadawca === 'ai' && lastMessage.ładuje) {
             return [...prev.slice(0, -1), { ...lastMessage, ładuje: false }];
          }
          return prev;
        });
       return;
     }

    // Dodaj otrzymany kawałek wiadomości do ostatniej wiadomości AI
    setWiadomości(prev => {
      const lastMessage = prev[prev.length - 1];
      // Jeśli ostatnia wiadomość jest wiadomością AI i jest w trakcie ładowania
      if (lastMessage && lastMessage.nadawca === 'ai' && lastMessage.ładuje) {
        // Zaktualizuj tekst ostatniej wiadomości
        return [...prev.slice(0, -1), { ...lastMessage, tekst: lastMessage.tekst + wiadomosc }];
      } else {
        // Jeśli nie, to nowy strumień się rozpoczął, dodaj nową wiadomość AI
        // W prawdziwej aplikacji ze strumieniowaniem, pierwsza wiadomość zainicjowałaby obiekt wiadomości
        // z flagą `ładuje: true`. W tej symulacji, startujemy ładowanie przed wysłaniem zapytania WS.
        // Dodajemy nową wiadomość AI z pierwszym kawałkiem i flagą ładuje
         return [...prev, { id: Date.now(), tekst: wiadomosc, nadawca: 'ai', ładuje: true }];
      }
    });
  };

  // Obsługa błędów WebSocket
  const handleWsError = (error: Event) => {
    console.error("Błąd WebSocket:", error);
    setBladCzatu("Wystąpił błąd w połączeniu czatu. Spróbuj odświeżyć stronę.");
    setŁadujeAi(false); // Zakończ ładowanie przy błędzie
  };

  // Obsługa zamknięcia WebSocket
  const handleWsClose = (event: CloseEvent) => {
    console.log("Połączenie WebSocket zamknięte.", event);
    setJestWsPołączony(false);
    if (event.code !== 1000) { // Kod 1000 oznacza normalne zamknięcie
        setBladCzatu(`Połączenie czatu zostało zakończone. Kod: ${event.code}`);
    }
    setŁadujeAi(false); // Zakończ ładowanie przy zamknięciu
  };

  // Funkcja wysyłająca zapytanie
  const wyslijZapytanie = async (zapytanie: string) => {
    if (!zapytanie.trim()) return; // Nie wysyłaj pustych zapytań
    if (ładujeAi) return; // Nie wysyłaj, jeśli AI już odpowiada

    setBladCzatu(null); // Wyczyść poprzednie błędy
    const noweWiadomości = [...wiadomości, { id: Date.now(), tekst: zapytanie, nadawca: 'użytkownik' as const }];
    setWiadomości(noweWiadomości);
    setSzukanaFraza(''); // Wyczyść pole wprowadzania

    // --- Wysyłanie przez WebSocket (preferowane dla strumieniowania) ---
    if (ws && ws.readyState === WebSocket.OPEN) {
       console.log("Wysyłam zapytanie przez WebSocket...");
       setŁadujeAi(true); // Rozpocznij stan ładowania
       // Dodaj pustą wiadomość AI z flagą ładuje
       setWiadomości(prev => [...prev, { id: Date.now() + 1, tekst: '', nadawca: 'ai', ładuje: true }]);
       sendWebSocketMessage(ws, zapytanie);

    } else {
      // --- Fallback na zapytanie HTTP POST, jeśli WS niedostępny ---
      console.warn("WebSocket niedostępny. Wysyłam zapytanie przez HTTP POST.");
      if (!jestZalogowany || !token) {
          setBladCzatu("Musisz być zalogowany, aby wysyłać zapytania.");
          return;
      }

      setŁadujeAi(true); // Rozpocznij stan ładowania
      // Dodaj pustą wiadomość AI z flagą ładuje
      setWiadomości(prev => [...prev, { id: Date.now() + 1, tekst: '', nadawca: 'ai', ładuje: true }]);

      try {
        const odpowiedz = await sendPerplexityQuery(zapytanie, token);
        console.log("Odpowiedź z API (HTTP POST):", odpowiedz);
        setWiadomości(prev => {
          // Znajdź ostatnią wiadomość AI z flagą ładuje i zaktualizuj ją
          const lastMessageIndex = prev.findIndex(msg => msg.nadawca === 'ai' && msg.ładuje);
          if (lastMessageIndex !== -1) {
             const updatedMessages = [...prev];
             updatedMessages[lastMessageIndex] = { ...updatedMessages[lastMessageIndex], tekst: odpowiedz.odpowiedz, ładuje: false };
             return updatedMessages;
          } else {
             // Jeśli nie znaleziono wiadomości z flagą ładuje (np. z powodu błędu wcześniej), dodaj nową
             return [...prev, { id: Date.now() + 2, tekst: odpowiedz.odpowiedz, nadawca: 'ai', ładuje: false }];
          }
        });
        setŁadujeAi(false); // Zakończ stan ładowania
      } catch (error: any) {
        console.error("Błąd podczas zapytania Perplexity (HTTP POST):", error);
        setBladCzatu(`Błąd: ${error.message || 'Nieznany błąd API'}`);
         setWiadomości(prev => {
          // Znajdź ostatnią wiadomość AI z flagą ładuje i oznacz ją jako błąd lub usuń
          const lastMessageIndex = prev.findIndex(msg => msg.nadawca === 'ai' && msg.ładuje);
           if (lastMessageIndex !== -1) {
              const updatedMessages = [...prev];
              // Możesz zmienić tekst na komunikat o błędzie lub usunąć wiadomość
              updatedMessages[lastMessageIndex] = { ...updatedMessages[lastMessageIndex], tekst: `[BŁĄD] ${error.message || 'Nie udało się uzyskać odpowiedzi.'}`, ładuje: false };
              return updatedMessages;
           }
           return prev;
         });
        setŁadujeAi(false); // Zakończ stan ładowania
      }
    }
  };

   // Komunikat o stanie ładowania/logowania
   if (ładujęAuth) {
     return <div className="text-center text-muted-foreground">Ładowanie...</div>;
   }

  return (
    <div className="flex flex-col h-[calc(100vh-150px)] bg-card rounded-lg shadow-lg overflow-hidden">
      {/* Okno wyświetlające wiadomości */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {wiadomości.map((wiadomosc) => (
          <WiadomoscCzatu
            key={wiadomosc.id}
            wiadomosc={wiadomosc}
            jestŁadowana={wiadomosc.ładuje || false} // Przekaż flagę ładowania do komponentu wiadomości
          />
        ))}
        {/* Pusty div do przewijania na dół */}
        <div ref={wiadomościEndRef} />
      </div>

      {/* Komunikat o błędzie */}
      {bladCzatu && (
        <div className="bg-destructive text-destructive-foreground p-3 text-center text-sm">
          {bladCzatu}
        </div>
      )}

      {/* Pole wprowadzania zapytania */}
      <div className="border-t p-4">
        {/* Przekaż funkcję wysyłania do PoleWprowadzania */}
        <PoleWprowadzania naWyslij={wyslijZapytanie} ładuje={ładujeAi} zablokowane={!jestZalogowany || ładujeAi} />
         {!jestZalogowany && (
            <p className="text-center text-sm text-muted-foreground mt-2">
               Zaloguj się, aby wysyłać zapytania.
            </p>
         )}
      </div>
    </div>
  );
};

export default OknoCzatu;
