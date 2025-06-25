import React from 'react';
import { cn } from '@/lib/utils'; // Helper do łączenia klas
import { Loader2 } from 'lucide-react'; // Ikona ładowania

interface Wiadomosc {
  id: number;
  tekst: string;
  nadawca: 'użytkownik' | 'ai';
  ładuje?: boolean; // Flaga informująca, czy odpowiedź AI jest w trakcie ładowania
}

interface WiadomoscCzatuProps {
  wiadomosc: Wiadomosc;
  jestŁadowana?: boolean; // Prop jawnie przekazująca stan ładowania
}

const WiadomoscCzatu: React.FC<WiadomoscCzatuProps> = ({ wiadomosc, jestŁadowana }) => {
  // Określ style w zależności od nadawcy
  const isUser = wiadomosc.nadawca === 'użytkownik';
  const bubbleClasses = cn(
    'max-w-[70%] p-3 rounded-lg',
    isUser
      ? 'bg-primary text-primary-foreground ml-auto rounded-br-none' // Wiadomości użytkownika po prawej
      : 'bg-muted text-muted-foreground mr-auto rounded-bl-none' // Wiadomości AI po lewej
  );

  return (
    <div className={cn("flex", isUser ? 'justify-end' : 'justify-start')}>
      <div className={bubbleClasses}>
        <p>{wiadomosc.tekst}</p>
        {/* Wskaźnik ładowania dla wiadomości AI */}
        {!isUser && (wiadomosc.ładuje || jestŁadowana) && (
           <Loader2 className="h-4 w-4 animate-spin text-muted-foreground mt-1" />
        )}
      </div>
    </div>
  );
};

export default WiadomoscCzatu;
