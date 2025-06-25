import React from 'react';
import { DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useOnboarding } from '@/context/OnboardingContext';

const Krok3: React.FC = () => {
  const { zakończOnboarding, poprzedniKrok, aktualnyKrok } = useOnboarding();

  // Oblicz wartość paska postępu (na 3 kroki)
  const postęp = (aktualnyKrok / 3) * 100;

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Krok 3: Statystyki i Monitorowanie</DialogTitle>
        <DialogDescription>
          Śledź wykorzystanie systemu i jego stan zdrowia na dedykowanej stronie statystyk.
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Możesz monitorować ilość zapytań, trafienia w cache, czas odpowiedzi API oraz ogólny stan
        zdrowia klienta Perplexity AI dzięki wbudowanemu monitoringowi.
        To wszystko pomoże zoptymalizować Twoje koszty i wydajność.
        Jesteś gotów rozpocząć?
      </div>
       <div className="w-full">
        <Progress value={postęp} className="w-full" />
      </div>
      <DialogFooter className="flex justify-between">
         <Button variant="outline" onClick={poprzedniKrok}>Wstecz</Button>
        <Button onClick={zakończOnboarding}>Zacznij Korzystać!</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok3;
