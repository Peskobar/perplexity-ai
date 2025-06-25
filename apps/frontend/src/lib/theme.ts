// Ten plik może zawierać dodatkowe helpery do zarządzania motywem
// np. funkcje do przełączania motywu bezpośrednio bez hooka (jeśli potrzebne poza komponentami React)
// lub definicje typów/konstant związane z motywem.

// Przykład: funkcja ustawiająca motyw w localStorage i na elemenecie <html>
export function setMotywRaw(motyw: 'ciemny' | 'jasny' | 'systemowy') {
  if (typeof window !== 'undefined') {
    const root = window.document.documentElement;
    root.classList.remove('jasny', 'ciemny');

    if (motyw === 'systemowy') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'ciemny' : 'jasny';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(motyw);
    }

    // Zapisz do localStorage
    localStorage.setItem('ui-theme', motyw);
  }
}

// Przykład: funkcja pobierająca aktualny motyw z localStorage lub systemu
export function getMotywRaw(): 'ciemny' | 'jasny' | 'systemowy' {
  if (typeof window === 'undefined') {
    return 'systemowy'; // Domyślny na serwerze
  }
  const savedTheme = localStorage.getItem('ui-theme');
  if (savedTheme === 'ciemny' || savedTheme === 'jasny' || savedTheme === 'systemowy') {
    return savedTheme;
  }
  // Jeśli brak w localStorage, sprawdź preferencje systemu
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'ciemny';
  }
  return 'jasny'; // Domyślnie jasny, jeśli brak preferencji systemowych
}
