import React from 'react';
import { useTheme } from './context/ThemeContext'; // Hook do zarządzania motywem
import Naglowek from './components/layout/Naglowek'; // Komponent nagłówka
import Stopka from './components/layout/Stopka';   // Komponent stopki
import GlownaZawartosc from './components/layout/GlownaZawartosc'; // Komponent głównej zawartości
import OnboardingDialog from './components/onboarding/OnboardingDialog'; // Komponent dialogu onboardingowego
import PaletaPolecen from './components/command-palette/PaletaPolecen'; // Komponent palety poleceń
import Tlo3D from './components/three/Tlo3D'; // Komponent tła 3D (opcjonalnie)

function App() {
  const { theme } = useTheme(); // Pobierz aktualny motyw

  // Zastosuj klasę motywu do elementu body
  React.useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  return (
    <div className="app-kontener flex flex-col min-h-screen">
      {/* Opcjonalne tło 3D - może być umieszczone w kontenerze o fixed position */}
      {/* <div className="fixed inset-0 z-0 pointer-events-none">
        <Tlo3D />
      </div> */}

      {/* Główna struktura aplikacji */}
      <Naglowek />
      <GlownaZawartosc /> {/* Tutaj będą główne widoki, np. czat */}
      <Stopka />

      {/* Komponenty globalne/nakładki */}
      <OnboardingDialog /> {/* Dialog onboardingowy */}
      <PaletaPolecen /> {/* Paleta poleceń aktywowana hotkeyem */}

      {/* Kontenery shadcn/ui, radix-ui itp. - często dodawane w root/main.tsx */}
      {/* <Toaster /> // Przykład toastów */}
    </div>
  );
}

export default App;
