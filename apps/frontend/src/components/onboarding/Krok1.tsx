import React from 'react';
import { DialogTitle, DialogDescription } from '@/components/ui/dialog'; // Komponenty UI dialogu
import { Button } from '@/components/ui/button'; // Komponent przycisku
import { useOnboarding } from '@/context/OnboardingContext'; // Kontekst onboardingu

const Krok1: React.FC = () => {
  const { następnyKrok } = useOnboarding();

  return (
    <div className="flex flex-col space-y-4">
      <DialogHeader>
        <DialogTitle>Witaj w Optymalizacji Dostępu do Perplexity AI!</Dialogu>
        <DialogDescription>
          Ten krótki samouczek przeprowadzi Cię przez kluczowe funkcje naszej aplikacji.
        </DialogDescription>
      </DialogHeader>
      <div className="text-sm text-muted-foreground">
        Tutaj możesz bezpiecznie i efektywnie korzystać z możliwości Perplexity AI,
        z dodatkowymi warstwami cache i monitorowania zdrowia.
        Gotów na rozpoczęcie?
      </div>
      <DialogFooter className="flex justify-end">
        <Button onClick={następnyKrok}>Dalej</Button>
      </DialogFooter>
    </div>
  );
};

export default Krok1;
