import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useLocalStorage } from '../lib/hooks'; // Niestandardowy hook do localStorage

type Motyw = 'ciemny' | 'jasny' | 'systemowy';

interface KontekstMotywu {
  theme: Motyw;
  setTheme: (theme: Motyw) => void;
}

const ThemeContext = createContext<KontekstMotywu | undefined>(undefined);

interface ProviderMotywuProps {
  children: ReactNode;
  defaultTheme?: Motyw;
  storageKey?: string;
}

export function ThemeProvider({
  children,
  defaultTheme = 'systemowy',
  storageKey = 'ui-theme',
}: ProviderMotywuProps) {
  // Użyj hooka useLocalStorage do synchronizacji motywu z localStorage
  const [theme, setThemeState] = useLocalStorage<Motyw>(storageKey, defaultTheme);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('jasny', 'ciemny'); // Usuń istniejące klasy

    // Logika zastosowania motywu:
    // Jeśli motyw to 'systemowy', użyj preferencji użytkownika
    if (theme === 'systemowy') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'ciemny' : 'jasny';
      root.classList.add(systemTheme);
    } else {
      // W przeciwnym razie, zastosuj wybrany motyw
      root.classList.add(theme);
    }
  }, [theme]); // Reaguj na zmianę stanu motywu

  // Funkcja do ustawiania motywu, która aktualizuje też stan w localStorage przez hook
  const setTheme = (nowyMotyw: Motyw) => {
    setThemeState(nowyMotyw); // useLocalStorage zajmie się localStorage i stanem lokalnym
  };

  const value = {
    theme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error('useTheme musi być użyty wewnątrz ThemeProvider');
  }

  return context;
}
