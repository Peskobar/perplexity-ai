import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useLocalStorage } from '../lib/hooks'; // Hook do localStorage

interface KontekstOnboardingu {
  jestOnboardingOtwarty: boolean;
  aktualnyKrok: number;
  rozpocznijOnboarding: () => void;
  następnyKrok: () => void;
  poprzedniKrok: () => void;
  zakończOnboarding: () => void;
  czyOnboardingZakonczony: boolean;
}

const OnboardingContext = createContext<KontekstOnboardingu | undefined>(undefined);

interface ProviderOnboardinguProps {
  children: ReactNode;
}

export function OnboardingProvider({ children }: ProviderOnboardinguProps) {
  // Użyj hooka useLocalStorage do przechowywania informacji o zakończeniu onboardingu
  const [czyOnboardingZakonczony, setCzyOnboardingZakonczony] = useLocalStorage<boolean>('onboarding-ukończony', false);
  const [jestOnboardingOtwarty, setJestOnboardingOtwarty] = useState(false);
  const [aktualnyKrok, setAktualnyKrok] = useState(1); // Start od kroku 1

  // Efekt sprawdzający, czy onboarding powinien być wyświetlony przy starcie
  useEffect(() => {
    // Jeśli onboarding nie został jeszcze zakończony, otwórz go przy starcie
    if (!czyOnboardingZakonczony) {
      // Dodaj opóźnienie, aby uniknąć blokowania ładowania strony
      const timer = setTimeout(() => {
         setJestOnboardingOtwarty(true);
         setAktualnyKrok(1); // Zawsze zacznij od kroku 1
      }, 500); // Opóźnienie 500 ms
      return () => clearTimeout(timer); // Czyszczenie timera
    }
  }, [czyOnboardingZakonczony]); // Zależność od flagi zakończenia onboardingu

  const rozpocznijOnboarding = () => {
    if (czyOnboardingZakonczony) {
      console.warn("Onboarding już ukończony.");
      return;
    }
    setJestOnboardingOtwarty(true);
    setAktualnyKrok(1);
  };

  const następnyKrok = () => {
    // Maksymalna liczba kroków to 3, po 3 kończymy
    if (aktualnyKrok < 3) {
      setAktualnyKrok(prev => prev + 1);
    } else {
      zakończOnboarding();
    }
  };

  const poprzedniKrok = () => {
    // Nie można wrócić przed krok 1
    if (aktualnyKrok > 1) {
      setAktualnyKrok(prev => prev - 1);
    }
  };

  const zakończOnboarding = () => {
    setCzyOnboardingZakonczony(true); // Zapisz w localStorage, że zakończono
    setJestOnboardingOtwarty(false); // Zamknij dialog
    setAktualnyKrok(1); // Zresetuj krok
  };

  const value = {
    jestOnboardingOtwarty,
    aktualnyKrok,
    rozpocznijOnboarding,
    następnyKrok,
    poprzedniKrok,
    zakończOnboarding,
    czyOnboardingZakonczony,
  };

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const context = useContext(OnboardingContext);

  if (context === undefined) {
    throw new Error('useOnboarding musi być użyty wewnątrz OnboardingProvider');
  }

  return context;
}
