import React from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog'; // Podstawowe komponenty dialogu
import Krok1 from './Krok1'; // Komponent pierwszego kroku
import Krok2 from './Krok2'; // Komponent drugiego kroku
import Krok3 from './Krok3'; // Komponent trzeciego kroku
import { useOnboarding } from '@/context/OnboardingContext'; // Kontekst onboardingu

const OnboardingDialog: React.FC = () => {
  const { jestOnboardingOtwarty, aktualnyKrok, zakończOnboarding } = useOnboarding();

  // Wybierz komponent kroku na podstawie aktualnego stanu
  const renderKrok = () => {
    switch (aktualnyKrok) {
      case 1:
        return <Krok1 />;
      case 2:
        return <Krok2 />;
      case 3:
        return <Krok3 />;
      default:
        // Zwróć null lub domyślny krok, jeśli stan jest nieoczekiwany
        return <Krok1 />;
    }
  };

  return (
    <Dialog open={jestOnboardingOtwarty} onOpenChange={(open) => !open && zakończOnboarding()}>
      <DialogContent className="sm:max-w-[425px]">
        {/* Renderuj aktualny krok wewnątrz zawartości dialogu */}
        {renderKrok()}
      </DialogContent>
    </Dialog>
  );
};

export default OnboardingDialog;
