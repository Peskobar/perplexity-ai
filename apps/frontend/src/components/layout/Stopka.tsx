import React from 'react';
import { cn } from '@/lib/utils'; // Helper do łączenia klas

interface StopkaProps extends React.HTMLAttributes<HTMLElement> {}

const Stopka: React.FC<StopkaProps> = ({ className, ...props }) => {
  return (
    <footer
      className={cn(
        "bg-card text-card-foreground border-t p-4 text-center text-sm text-muted-foreground mt-auto backdrop-blur-sm bg-opacity-80 z-10",
        className
      )}
      {...props}
    >
      © {new Date().getFullYear()} Perplexity AI Optymalizacja. Wszelkie prawa zastrzeżone (przykładowe).
      {/* Można dodać linki do polityki prywatności, warunków użytkowania itp. */}
    </footer>
  );
};

export default Stopka;
