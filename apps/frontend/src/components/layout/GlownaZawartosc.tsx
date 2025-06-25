import React from 'react';
import OknoCzatu from '@/components/chat/OknoCzatu'; // Komponent okna czatu

interface GlownaZawartoscProps extends React.HTMLAttributes<HTMLElement> {}

const GlownaZawartosc: React.FC<GlownaZawartoscProps> = ({ className, ...props }) => {
  return (
    // Główna zawartość aplikacji, która będzie wypełniać dostępną przestrzeń
    // flex-grow sprawia, że ten element rozszerza się, wypychając stopkę na dół
    <main className={cn("flex-grow container mx-auto p-4", className)} {...props}>
      {/* Tutaj można umieścić routing lub główny komponent widoku */}
      {/* Na przykład, jeśli jesteśmy na stronie czatu, renderujemy OknoCzatu */}
      {/* Można użyć react-router do zarządzania widokami */}
      {/* <Routes>
        <Route path="/" element={<OknoCzatu />} />
        <Route path="/stats" element={<div>Strona Statystyk</div>} />
        <Route path="/login" element={<div>Strona Logowania</div>} />
        <Route path="/register" element={<div>Strona Rejestracji</div>} />
         <Route path="*" element={<div>404 - Nie znaleziono</div>} />
      </Routes> */}

      {/* Na potrzeby przykładu, renderujemy tylko OknoCzatu */}
      <OknoCzatu />

    </main>
  );
};

export default GlownaZawartosc;
