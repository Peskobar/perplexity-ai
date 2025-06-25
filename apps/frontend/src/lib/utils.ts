import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// Funkcja pomocnicza do łączenia klas CSS (zwłaszcza z Tailwind)
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Hook do zarządzania stanem w localStorage
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((val: T) => T)) => void] {
  // Stan do przechowywania naszej wartości
  // Przekaż do useState funkcję, aby obliczenia były wykonywane tylko raz
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") {
      return initialValue;
    }
    try {
      // Pobierz z localStorage według klucza
      const item = window.localStorage.getItem(key);
      // Parsuj zapisany JSON lub zwróć wartość początkową jeśli jej brak
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      // Jeśli wystąpi błąd (np. Quota Exceeded), zwróć wartość początkową
      console.error(error);
      return initialValue;
    }
  });

  // Funkcja, która będzie zapisywać stan do localStorage
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // Zezwól na zapisanie wartości funkcji
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      // Zapisz do stanu
      setStoredValue(valueToStore);
      // Zapisz do localStorage
      if (typeof window !== "undefined") {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      // Obsługa błędów zapisu (np. Quota Exceeded)
      console.error(error);
    }
  };

  return [storedValue, setValue];
}
