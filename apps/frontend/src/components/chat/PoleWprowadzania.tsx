import React, { useState } from 'react';
import { Input } from '@/components/ui/input'; // Komponent Input
import { Button } from '@/components/ui/button'; // Komponent Button
import { SendIcon } from 'lucide-react'; // Ikona wysyłania
import { cn } from '@/lib/utils'; // Helper do łączenia klas

interface PoleWprowadzaniaProps extends React.HTMLAttributes<HTMLFormElement> {
  naWyslij: (zapytanie: string) => void; // Funkcja wywoływana przy wysłaniu zapytania
  ładuje?: boolean; // Czy trwa ładowanie odpowiedzi AI
  zablokowane?: boolean; // Czy pole i przycisk są zablokowane
}

const PoleWprowadzania: React.FC<PoleWprowadzaniaProps> = ({ naWyslij, ładuje, zablokowane, className, ...props }) => {
  const [zapytanie, setZapytanie] = useState('');

  // Obsługa wysłania formularza
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // Zapobiegaj domyślnej akcji formularza (przeładowanie strony)
    if (zapytanie.trim() && !ładuje && !zablokowane) {
      naWyslij(zapytanie); // Wywołaj funkcję wysyłającą zapytanie
      setZapytanie(''); // Wyczyść pole po wysłaniu
    }
  };

  // Obsługa naciśnięcia Enter w polu Input (aby też wysyłało)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
     if (e.key === 'Enter' && !e.shiftKey) { // Wysyłaj po naciśnięciu Enter (bez Shift)
        e.preventDefault(); // Zapobiegaj dodaniu nowej linii
        handleSubmit(e as any); // Wywołaj handleSubmit (rzutowanie jest ok, bo preventDefault)
     }
  };


  return (
    <form
      className={cn("flex items-center space-x-2", className)}
      onSubmit={handleSubmit}
      {...props}
    >
      {/* Pole wprowadzania */}
      <Input
        placeholder={ładuje ? "Generuję odpowiedź..." : (zablokowane ? "Zablokowane" : "Zadaj pytanie...")}
        value={zapytanie}
        onChange={(e) => setZapytanie(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={ładuje || zablokowane} // Zablokuj pole podczas ładowania lub gdy zablokowane
        className="flex-grow" // Rozszerz pole, aby wypełniało dostępną przestrzeń
      />
      {/* Przycisk wysyłania */}
      <Button type="submit" size="icon" disabled={!zapytanie.trim() || ładuje || zablokowane}>
        <SendIcon className="h-4 w-4" />
        <span className="sr-only">Wyślij zapytanie</span> {/* Tekst dla czytników ekranu */}
      </Button>
    </form>
  );
};

export default PoleWprowadzania;
