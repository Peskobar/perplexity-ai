import React from 'react';
import { useTheme } from './context/ThemeContext';
import Naglowek from './components/layout/Naglowek';
import Stopka from './components/layout/Stopka';
import GlownaZawartosc from './components/layout/GlownaZawartosc';
import OnboardingDialog from './components/onboarding/OnboardingDialog';
import PaletaPolecen from './components/command-palette/PaletaPolecen';

function App() {
  const { theme } = useTheme();

  React.useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  return (
    <div className="app-kontener flex min-h-screen flex-col">
      <Naglowek />
      <GlownaZawartosc />
      <Stopka />
      <OnboardingDialog />
      <PaletaPolecen />
    </div>
  );
}

export default App;
