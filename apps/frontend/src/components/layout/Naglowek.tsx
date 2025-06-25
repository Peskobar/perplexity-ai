import React from 'react';
import { Link } from 'react-router-dom'; // Jeśli używasz react-router
import { Button } from '@/components/ui/button'; // Komponent przycisku
import { useTheme } from '@/context/ThemeContext'; // Hook do motywu
import { useAuth } from '@/context/AuthContext'; // Hook do autoryzacji
import { SunIcon, MoonIcon, MenuIcon } from 'lucide-react'; // Ikony

const Naglowek: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const { jestZalogowany, uzytkownik, logout } = useAuth();

  // Funkcja przełączająca motyw
  const przełączMotyw = () => {
    setTheme(theme === 'ciemny' ? 'jasny' : 'ciemny');
  };

  return (
    <header className="bg-card text-card-foreground border-b p-4 flex justify-between items-center backdrop-blur-sm bg-opacity-80 z-10">
      <div className="flex items-center space-x-4">
        {/* Logo/Nazwa aplikacji */}
        {/* <Link to="/" className="text-xl font-bold"> */}
           <span className="text-xl font-bold">Perplexity Opti</span>
        {/* </Link> */}
        {/* Linki nawigacyjne (jeśli są potrzebne, np. do statystyk, profilu) */}
         {/* <nav className="hidden md:flex space-x-4">
           <Link to="/stats" className="text-sm font-medium transition-colors hover:text-primary">Statystyki</Link>
            {jestZalogowany && <Link to="/profil" className="text-sm font-medium transition-colors hover:text-primary">Profil</Link>}
         </nav> */}
      </div>

      <div className="flex items-center space-x-2">
        {/* Status zalogowania */}
        {jestZalogowany ? (
          <span className="text-sm text-muted-foreground hidden sm:inline">Zalogowany jako: {uzytkownik?.email}</span>
        ) : (
           <span className="text-sm text-muted-foreground hidden sm:inline">Niezalogowany</span>
        )}

        {/* Przycisk przełączający motyw */}
        <Button variant="ghost" size="icon" onClick={przełączMotyw} aria-label="Przełącz motyw">
          {theme === 'ciemny' ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
        </Button>

        {/* Przycisk wylogowania (tylko gdy zalogowany) */}
        {jestZalogowany && (
          <Button variant="outline" size="sm" onClick={logout}>
            Wyloguj
          </Button>
        )}

        {/* Przycisk logowania/rejestracji (tylko gdy niezalogowany) */}
        {!jestZalogowany && (
          <>
            {/* <Link to="/login"> */}
               {/* <Button variant="outline" size="sm">Zaloguj</Button> */}
            {/* </Link> */}
             {/* <Link to="/register"> */}
               {/* <Button size="sm">Rejestracja</Button> */}
            {/* </Link> */}
             {/* Proste przyciski bez routingu na potrzeby przykładu */}
             <Button variant="outline" size="sm" onClick={() => console.log("Przejdź do logowania")}>Zaloguj</Button>
             <Button size="sm" onClick={() => console.log("Przejdź do rejestracji")}>Rejestracja</Button>
          </>
        )}

        {/* Przycisk menu dla urządzeń mobilnych (opcjonalnie) */}
        {/* <Button variant="ghost" size="icon" className="md:hidden">
           <MenuIcon className="h-5 w-5" />
        </Button> */}
      </div>
    </header>
  );
};

export default Naglowek;
