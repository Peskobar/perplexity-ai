import React from 'react';
import {
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useOnboarding } from '@/context/OnboardingContext';

const Krok2: React.FC = () => {
  const { następnyKrok, poprzedniKrok, aktualnyKrok } = useOnboarding();
  const postęp = (aktualnyKrok / 3) * 100;

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Krok 2: Jak zadać pytanie?</DialogTitle>
        <DialogDescription>
          Użyj głównego pola tekstowego albo palety poleceń otwieranej klawiszem K.
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Zapytanie najpierw trafia do warstwy cache, a następnie — gdy jest to potrzebne —
        do klienta Perplexity. Wynik pojawi się w oknie czatu.
      </div>
      <Progress value={postęp} className="w-full" />
      <DialogFooter className="flex justify-between">
        <Button variant="outline" onClick={poprzedniKrok}>Wstecz</Button>
        <Button onClick={następnyKrok}>Dalej</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok2;
