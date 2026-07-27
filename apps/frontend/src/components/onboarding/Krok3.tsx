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

const Krok3: React.FC = () => {
  const { zakończOnboarding, poprzedniKrok, aktualnyKrok } = useOnboarding();
  const postęp = (aktualnyKrok / 3) * 100;

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Krok 3: Statystyki i monitorowanie</DialogTitle>
        <DialogDescription>
          Kontroluj wykorzystanie systemu, cache i stan połączenia z usługą.
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Panel metryk pokazuje liczbę zapytań, trafienia w cache i czas odpowiedzi,
        dzięki czemu łatwiej ocenić stabilność oraz koszty działania.
      </div>
      <Progress value={postęp} className="w-full" />
      <DialogFooter className="flex justify-between">
        <Button variant="outline" onClick={poprzedniKrok}>Wstecz</Button>
        <Button onClick={zakończOnboarding}>Zacznij korzystać</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok3;
