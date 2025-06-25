import { useState, useEffect } from 'react';

// useLocalStorage jest już zdefiniowany w utils.ts i eksportowany
// import { useLocalStorage } from './utils';

// Przykładowy hook do obsługi kliknięcia z feedbackiem animacji tap
// Wymaga dodania klasy CSS `.animate-tap-on-click` (zdefiniowanej w tailwind.config.js)
export function useTapFeedback() {
  const applyTapAnimation = (event: React.MouseEvent<HTMLElement>) => {
    const target = event.currentTarget;
    // Dodaj klasę animacji
    target.classList.add('animate-tap-on-click');
    // Usuń klasę po zakończeniu animacji
    target.addEventListener('animationend', () => {
      target.classList.remove('animate-tap-on-click');
    }, { once: true }); // Usuń listener po jednorazowym wywołaniu
  };

  return applyTapAnimation;
}

// Przykładowy hook do obsługi animacji hover-lift
// Wymaga dodania klasy CSS `.animate-lift-on-hover` (zdefiniowanej w tailwind.config.js)
export function useLiftOnHover() {
   // Ta animacja jest zaimplementowana czysto w CSS poprzez klasę utility i wariant hover
   // Hook nie jest ściśle potrzebny, wystarczy dodać klasę 'animate-lift-on-hover' do elementu.
   // Ale hook może pomóc w dynamicznym dodawaniu/usuwaniu klasy jeśli potrzebne.
   // Dla prostoty, polegamy na czystym CSS i utility class w Tailwind.
   // Zwracamy pustą funkcję lub null, albo możemy zwrócić funkcję dodającą/usuwającą klasę
   const applyLiftAnimationClass = (element: HTMLElement | null) => {
     if (element) {
        // Dodaj klasę - CSS zajmie się resztą na hover
        element.classList.add('animate-lift-on-hover');
        // Opcjonalnie usuń przy unmount
        return () => {
           element.classList.remove('animate-lift-on-hover');
        };
     }
     return () => {}; // Zwróć pustą funkcję czyszczącą
   };

   // Użycie: const elementRef = useRef(null); useEffect(() => useLiftOnHover()(elementRef.current), []);
   return applyLiftAnimationClass;
}


// Hook do wykrywania kliknięcia poza elementem
export function useOnClickOutside(ref: React.RefObject<HTMLElement>, handler: (event: MouseEvent | TouchEvent) => void) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      // Czy kliknięcie nastąpiło wewnątrz elementu ref lub jego dzieci
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler(event); // Wywołaj handler jeśli kliknięcie było poza elementem
    };

    document.addEventListener("mousedown", listener);
    document.addEventListener("touchstart", listener);

    return () => {
      document.removeEventListener("mousedown", listener);
      document.removeEventListener("touchstart", listener);
    };
  }, [ref, handler]); // Zależności: ref i handler
}


// Exportuj hooki
export { useLocalStorage } from './utils'; // Re-export useLocalStorage
