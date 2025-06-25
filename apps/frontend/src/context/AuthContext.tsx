import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useLocalStorage } from '../lib/hooks'; // Hook do localStorage
import { loginUser, registerUser, validateToken, LoginPayload, RegisterPayload } from '../lib/api'; // Funkcje API

interface Uzytkownik {
  email: string;
  // Dodaj inne pola użytkownika, jeśli API je zwraca
}

interface KontekstAutoryzacji {
  uzytkownik: Uzytkownik | null;
  token: string | null;
  jestZalogowany: boolean;
  ładuję: boolean;
  login: (dane: LoginPayload) => Promise<void>;
  register: (dane: RegisterPayload) => Promise<void>;
  logout: () => void;
  // Dodaj ewentualne błędy autoryzacji
  blad: string | null;
}

const AuthContext = createContext<KontekstAutoryzacji | undefined>(undefined);

interface ProviderAutoryzacjiProps {
  children: ReactNode;
}

export function AuthProvider({ children }: ProviderAutoryzacjiProps) {
  // Token przechowujemy w localStorage
  const [token, setToken] = useLocalStorage<string | null>('auth-token', null);
  const [uzytkownik, setUzytkownik] = useState<Uzytkownik | null>(null);
  const [ładuję, setŁaduję] = useState(true);
  const [blad, setBlad] = useState<string | null>(null);

  // Efekt sprawdzający token przy starcie aplikacji lub zmianie tokenu
  useEffect(() => {
    async function sprawdzToken() {
      setŁaduję(true);
      setBlad(null); // Resetuj błąd
      if (token) {
        try {
          const daneUzytkownika = await validateToken(token);
          setUzytkownik(daneUzytkownika); // Ustaw użytkownika na podstawie danych z tokenu
        } catch (error) {
          console.error("Błąd walidacji tokenu:", error);
          setUzytkownik(null);
          setToken(null); // Usuń niepoprawny/wygasły token
          setBlad("Sesja wygasła. Zaloguj się ponownie.");
        }
      } else {
        setUzytkownik(null);
      }
      setŁaduję(false);
    }

    sprawdzToken();
  }, [token, setToken]); // Zależności: token i setter tokenu z localStorage

  // Funkcja logowania
  const login = async (dane: LoginPayload) => {
    setŁaduję(true);
    setBlad(null);
    try {
      const response = await loginUser(dane);
      setToken(response.access_token); // Zapisz token w localStorage
      // Walidacja tokenu w useEffect pobierze dane użytkownika
    } catch (error: any) {
      console.error("Błąd logowania:", error);
      setBlad(error.message || "Nie udało się zalogować. Sprawdź dane.");
      setUzytkownik(null);
      setToken(null);
      throw error; // Ponownie zgłoś błąd, jeśli komponent wywołujący go potrzebuje
    } finally {
      setŁaduję(false);
    }
  };

  // Funkcja rejestracji
  const register = async (dane: RegisterPayload) => {
    setŁaduję(true);
    setBlad(null);
    try {
      const response = await registerUser(dane);
      // Po rejestracji często od razu logujemy użytkownika, API może zwrócić token
      if (response.access_token) {
           setToken(response.access_token);
      }
      // Walidacja tokenu w useEffect pobierze dane użytkownika
    } catch (error: any) {
      console.error("Błąd rejestracji:", error);
      setBlad(error.message || "Nie udało się zarejestrować. Spróbuj ponownie.");
      setUzytkownik(null);
      setToken(null); // Usuń token na wszelki wypadek
      throw error; // Ponownie zgłoś błąd
    } finally {
      setŁaduję(false);
    }
  };


  // Funkcja wylogowania
  const logout = () => {
    setToken(null); // Usuń token z localStorage
    setUzytkownik(null); // Wyczyść dane użytkownika
    setBlad(null); // Wyczyść błąd
    console.log("Użytkownik wylogowany.");
  };

  const value = {
    uzytkownik,
    token,
    jestZalogowany: !!uzytkownik, // Prosta flaga stanu zalogowania
    ładuję,
    login,
    register,
    logout,
    blad,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth musi być użyty wewnątrz AuthProvider');
  }

  return context;
}
