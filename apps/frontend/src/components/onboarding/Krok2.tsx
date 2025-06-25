import React from 'react';
import { DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress'; // Komponent paska postępu
import { useOnboarding } from '@/context/OnboardingContext';

const Krok2: React.FC = () => {
  const { następnyKrok, poprzedniKrok, aktualnyKrok } = useOnboarding();

  // Oblicz wartość paska postępu (na 3 kroki)
  const postęp = (aktualnyKrok / 3) * 100;

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Krok 2: Jak zadać pytanie?</DialogTitle>
        <DialogDescription>
          To proste! Użyj głównego pola tekstowego poniżej lub palety poleceń (Hotkey K).
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Twoje zapytania trafią do naszego zoptymalizowanego systemu.
        Sprawdzimy, czy odpowiedź jest już w cache, a jeśli nie - bezpiecznie zapytamy API Perplexity.
        Wyniki będą wyświetlane w oknie czatu.
      </div>
      <div className="w-full">
        <Progress value={postęp} className="w-full" />
      </div>
      <DialogFooter className="flex justify-between">
        <Button variant="outline" onClick={poprzedniKrok}>Wstecz</Button>
        <Button onClick={następnyKrok}>Dalej</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok2;
