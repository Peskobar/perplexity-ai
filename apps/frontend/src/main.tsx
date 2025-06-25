import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css'; // Główny plik stylów (Tailwind)
import { ThemeProvider } from './context/ThemeContext.tsx'; // Kontekst motywu
import { AuthProvider } from './context/AuthContext.tsx'; // Kontekst autoryzacji
import { OnboardingProvider } from './context/OnboardingContext.tsx'; // Kontekst onboardingu

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* Zawijamy aplikację w konteksty */}
    <ThemeProvider>
      <AuthProvider>
        <OnboardingProvider>
          <App />
        </OnboardingProvider>
      </AuthProvider>
    </ThemeProvider>
  </React.StrictMode>,
);
