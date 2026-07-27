import React, { useEffect, useRef, useState } from 'react';
import {
  connectPerplexityStream,
  sendPerplexityQuery,
  sendWebSocketMessage,
} from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import WiadomoscCzatu from './WiadomoscCzatu';
import PoleWprowadzania from './PoleWprowadzania';

interface Wiadomosc {
  id: number;
  tekst: string;
  nadawca: 'użytkownik' | 'ai';
  ładuje?: boolean;
}

const OknoCzatu: React.FC = () => {
  const { token, jestZalogowany, ładuję: ładujęAuth } = useAuth();
  const [wiadomości, setWiadomości] = useState<Wiadomosc[]>([]);
  const [ładujeAi, setŁadujeAi] = useState(false);
  const [bladCzatu, setBladCzatu] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const wiadomościEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMessage = (fragment: string) => {
      if (fragment === '[KONIEC_STRUMIENIA]') {
        setŁadujeAi(false);
        setWiadomości((poprzednie) => {
          const ostatnia = poprzednie.at(-1);
          if (!ostatnia || ostatnia.nadawca !== 'ai') return poprzednie;
          return [...poprzednie.slice(0, -1), { ...ostatnia, ładuje: false }];
        });
        return;
      }

      setWiadomości((poprzednie) => {
        const ostatnia = poprzednie.at(-1);
        if (ostatnia?.nadawca === 'ai' && ostatnia.ładuje) {
          return [
            ...poprzednie.slice(0, -1),
            { ...ostatnia, tekst: ostatnia.tekst + fragment },
          ];
        }
        return [
          ...poprzednie,
          { id: Date.now(), tekst: fragment, nadawca: 'ai', ładuje: true },
        ];
      });
    };

    const socket = connectPerplexityStream(
      handleMessage,
      () => {
        setBladCzatu('Wystąpił błąd połączenia WebSocket.');
        setŁadujeAi(false);
      },
      (event) => {
        if (event.code !== 1000) {
          setBladCzatu(`Połączenie czatu zostało zakończone. Kod: ${event.code}`);
        }
        setŁadujeAi(false);
      },
    );

    setWs(socket);
    return () => socket.close();
  }, []);

  useEffect(() => {
    wiadomościEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [wiadomości, ładujeAi]);

  const dodajOczekującąOdpowiedź = () => {
    setWiadomości((poprzednie) => [
      ...poprzednie,
      { id: Date.now() + 1, tekst: '', nadawca: 'ai', ładuje: true },
    ]);
  };

  const wyslijZapytanie = async (zapytanie: string) => {
    const tekst = zapytanie.trim();
    if (!tekst || ładujeAi) return;

    setBladCzatu(null);
    setWiadomości((poprzednie) => [
      ...poprzednie,
      { id: Date.now(), tekst, nadawca: 'użytkownik' },
    ]);
    setŁadujeAi(true);
    dodajOczekującąOdpowiedź();

    if (ws?.readyState === WebSocket.OPEN) {
      sendWebSocketMessage(ws, tekst);
      return;
    }

    if (!jestZalogowany || !token) {
      setBladCzatu('Musisz być zalogowany, aby wysyłać zapytania.');
      setŁadujeAi(false);
      return;
    }

    try {
      const odpowiedz = await sendPerplexityQuery(tekst, token);
      setWiadomości((poprzednie) => {
        const indeks = poprzednie.findLastIndex(
          (wiadomosc) => wiadomosc.nadawca === 'ai' && wiadomosc.ładuje,
        );
        if (indeks < 0) return poprzednie;
        const wynik = [...poprzednie];
        wynik[indeks] = {
          ...wynik[indeks],
          tekst: odpowiedz.odpowiedz,
          ładuje: false,
        };
        return wynik;
      });
    } catch (error) {
      const komunikat = error instanceof Error ? error.message : 'Nieznany błąd API';
      setBladCzatu(`Błąd: ${komunikat}`);
    } finally {
      setŁadujeAi(false);
    }
  };

  if (ładujęAuth) {
    return <div className="text-center text-muted-foreground">Ładowanie...</div>;
  }

  return (
    <div className="flex h-[calc(100vh-150px)] flex-col overflow-hidden rounded-lg bg-card shadow-lg">
      <div className="flex-grow space-y-4 overflow-y-auto p-4">
        {wiadomości.map((wiadomosc) => (
          <WiadomoscCzatu
            key={wiadomosc.id}
            wiadomosc={wiadomosc}
            jestŁadowana={Boolean(wiadomosc.ładuje)}
          />
        ))}
        <div ref={wiadomościEndRef} />
      </div>

      {bladCzatu && (
        <div className="bg-destructive p-3 text-center text-sm text-destructive-foreground">
          {bladCzatu}
        </div>
      )}

      <div className="border-t p-4">
        <PoleWprowadzania
          naWyslij={wyslijZapytanie}
          ładuje={ładujeAi}
          zablokowane={!jestZalogowany || ładujeAi}
        />
        {!jestZalogowany && (
          <p className="mt-2 text-center text-sm text-muted-foreground">
            Zaloguj się, aby wysyłać zapytania.
          </p>
        )}
      </div>
    </div>
  );
};

export default OknoCzatu;
