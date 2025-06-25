import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'; // Używamy dialogu jako bazy
import { Input } from '@/components/ui/input'; // Pole wprowadzania
import { Kbd } from '@/components/ui/kbd'; // Opcjonalny komponent Kbd do wyświetlania hotkeyów (można dodać)
import { Separator } from '@/components/ui/separator'; // Opcjonalny separator (można dodać)

interface Polecenie {
  id: string;
  nazwa: string;
  akcja: () => void;
  kategoria?: string;
}

const PaletaPolecen: React.FC = () => {
  const [otwarta, setOtwarta] = useState(false);
  const [szukanaFraza, setSzukanaFraza] = useState('');

  // Lista dostępnych poleceń (przykładowe)
  const polecenia: Polecenie[] = [
    { id: 'nowy_czat', nazwa: 'Rozpocznij Nowy Czat', akcja: () => console.log('Akcja: Nowy Czat'), kategoria: 'Czat' },
    { id: 'motyw_jasny', nazwa: 'Przełącz na Motyw Jasny', akcja: () => console.log('Akcja: Motyw Jasny'), kategoria: 'Wygląd' },
    { id: 'motyw_ciemny', nazwa: 'Przełącz na Motyw Ciemny', akcja: () => console.log('Akcja: Motyw Ciemny'), kategoria: 'Wygląd' },
    { id: 'motyw_systemowy', nazwa: 'Użyj Motywu Systemowego', akcja: () => console.log('Akcja: Motyw Systemowy'), kategoria: 'Wygląd' },
    { id: 'statystyki', nazwa: 'Przejdź do Statystyk', akcja: () => console.log('Akcja: Statystyki'), kategoria: 'Nawigacja' },
    { id: 'onboarding', nazwa: 'Pokaż Onboarding', akcja: () => console.log('Akcja: Onboarding'), kategoria: 'Pomoc' },
    { id: 'wyloguj', nazwa: 'Wyloguj się', akcja: () => console.log('Akcja: Wyloguj'), kategoria: 'Konto' },
    // ... dodaj więcej poleceń
  ];

  // Filtruj polecenia na podstawie szukanej frazy
  const przefiltrowanePolecenia = szukanaFraza
    ? polecenia.filter(p => p.nazwa.toLowerCase().includes(szukanaFraza.toLowerCase()))
    : polecenia; // Jeśli fraza pusta, pokaż wszystkie

  // Efekt obsługujący hotkey "K"
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Sprawdź, czy klawisz "K" został naciśnięty i czy nie jest w polu input/textarea
      if (event.key === 'k' && (event.target as HTMLElement).tagName !== 'INPUT' && (event.target as HTMLElement).tagName !== 'TEXTAREA') {
        event.preventDefault(); // Zapobiegaj domyślnej akcji przeglądarki
        setOtwarta(prev => !prev); // Przełącz stan otwarcia palety
      }
      // Zamknij paletę klawiszem Escape
      if (event.key === 'Escape') {
        setOtwarta(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []); // Pusta tablica zależności - efekt uruchamia się tylko raz

  // Resetuj szukaną frazę przy otwarciu/zamknięciu palety
  useEffect(() => {
    if (!otwarta) {
      setSzukanaFraza('');
    }
  }, [otwarta]);

  // Funkcja obsługująca wybór polecenia
  const wybierzPolecenie = (polecenie: Polecenie) => {
    polecenie.akcja(); // Wykonaj akcję przypisaną do polecenia
    setOtwarta(false); // Zamknij paletę po wyborze
  };

  return (
    <Dialog open={otwarta} onOpenChange={setOtwarta}>
      {/* Trigger może być ukryty, skoro używamy hotkeya */}
      {/* <DialogTrigger asChild>
        <Button variant="outline">Otwórz Paletę Poleceń</Button>
      </DialogTrigger> */}
      <DialogContent className="sm:max-w-[480px] p-0 overflow-hidden">
        {/* Pole wyszukiwania */}
        <div className="flex items-center border-b px-3">
          <Input
            placeholder="Szukaj poleceń..."
            className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 border-none focus-visible:ring-0 focus-visible:ring-offset-0"
            value={szukanaFraza}
            onChange={(e) => setSzukanaFraza(e.target.value)}
          />
        </div>
        {/* Lista przefiltrowanych poleceń */}
        {przefiltrowanePolecenia.length > 0 ? (
          <div className="max-h-[300px] overflow-y-auto py-2">
            {przefiltrowanePolecenia.map(polecenie => (
              <div
                key={polecenie.id}
                className="cursor-pointer select-none px-4 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                onClick={() => wybierzPolecenie(polecenie)}
              >
                {/* Wyświetl nazwę i kategorię */}
                {polecenie.nazwa}
                {polecenie.kategoria && (
                  <span className="ml-2 text-xs text-muted-foreground">
                    ({polecenie.kategoria})
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="py-4 text-center text-sm text-muted-foreground">
            Brak pasujących poleceń.
          </div>
        )}
        {/* Etykieta z hotkeyem na dole (opcjonalnie) */}
        <div className="flex items-center border-t px-3 py-2 text-xs text-muted-foreground">
           <span className="mr-auto">Naciśnij <Kbd>K</Kbd> aby otworzyć/zamknąć</span>
           <span>Naciśnij <Kbd>Enter</Kbd> aby wybrać, <Kbd>↑</Kbd><Kbd>↓</Kbd> aby nawigować</span>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PaletaPolecen;
