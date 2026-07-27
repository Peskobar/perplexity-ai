import React from 'react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import { MoonIcon, SunIcon } from 'lucide-react';

const Naglowek: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const { jestZalogowany, uzytkownik, logout } = useAuth();

  const przelaczMotyw = () => {
    setTheme(theme === 'ciemny' ? 'jasny' : 'ciemny');
  };

  return (
    <header className="z-10 flex items-center justify-between border-b bg-card/80 p-4 text-card-foreground backdrop-blur-sm">
      <span className="text-xl font-bold">Perplexity Opti</span>

      <div className="flex items-center space-x-2">
        <span className="hidden text-sm text-muted-foreground sm:inline">
          {jestZalogowany ? `Zalogowany jako: ${uzytkownik?.email ?? ''}` : 'Niezalogowany'}
        </span>

        <Button variant="ghost" size="icon" onClick={przelaczMotyw} aria-label="Przełącz motyw">
          {theme === 'ciemny' ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
        </Button>

        {jestZalogowany ? (
          <Button variant="outline" size="sm" onClick={logout}>
            Wyloguj
          </Button>
        ) : (
          <>
            <Button variant="outline" size="sm" onClick={() => console.log('Przejdź do logowania')}>
              Zaloguj
            </Button>
            <Button size="sm" onClick={() => console.log('Przejdź do rejestracji')}>
              Rejestracja
            </Button>
          </>
        )}
      </div>
    </header>
  );
};

export default Naglowek;
