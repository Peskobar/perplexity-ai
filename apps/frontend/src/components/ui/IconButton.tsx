import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { LucideIcon } from "lucide-react" // importuj konkretną ikonę dynamicznie

const iconButtonVariants = cva(
  "inline-flex items-center justify-center rounded-md p-2 focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        ghost: "bg-transparent hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        sm: "h-8 w-8",
        md: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

export interface IconButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof iconButtonVariants> {
  icon: LucideIcon;        // klasa ikony z lucide-react
  label?: string;          // alt text dla czytników
}

const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant, size, icon: Icon, label = "", ...props }, ref) => {
    return (
      <button
        className={iconButtonVariants({ variant, size, className })}
        ref={ref}
        aria-label={label}
        {...props}
      >
        <Icon className="h-5 w-5" aria-hidden="true" />
      </button>
    );
  }
);
IconButton.displayName = "IconButton";

export { IconButton };

Przykład prostego Tooltip.tsx:

// apps/frontend/src/components/ui/Tooltip.tsx
import * as React from "react"
import * as TooltipPrimitive from "@radix-ui/react-tooltip"
import { cn } from "@/lib/utils"

export interface TooltipProps extends React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Root> {
  content: React.ReactNode
  children: React.ReactNode
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, ...props }) => {
  return (
    <TooltipPrimitive.Provider>
      <TooltipPrimitive.Root delayDuration={200} {...props}>
        <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            sideOffset={4}
            className={cn(
              "rounded-md bg-popover px-2 py-1 text-xs text-popover-foreground shadow-md",
            )}
          >
            {content}
            <TooltipPrimitive.Arrow className="fill-popover" />
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
};

Tooltip.displayName = "Tooltip";

export { Tooltip };

Przykład „Sidebar.tsx”:

// apps/frontend/src/components/layout/Sidebar.tsx
import React from "react";
import { Separator } from "@/components/ui/Separator";
import { IconButton } from "@/components/ui/IconButton";
import { PlusIcon, HomeIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  projects: { id: string; name: string }[];
  onAddProject: () => void;
  selectedProjectId?: string;
  onSelectProject: (id: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  projects,
  onAddProject,
  selectedProjectId,
  onSelectProject,
}) => {
  return (
    <aside className="w-64 bg-background border-r">
      <div className="p-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Projekty</h2>
        <IconButton
          icon={PlusIcon}
          label="Dodaj nowy projekt"
          onClick={onAddProject}
          variant="ghost"
        />
      </div>
      <Separator />
      <nav className="overflow-y-auto">
        {projects.map((proj) => (
          <div
            key={proj.id}
            onClick={() => onSelectProject(proj.id)}
            className={cn(
              "flex items-center space-x-2 px-4 py-2 hover:bg-accent hover:text-accent-foreground cursor-pointer",
              proj.id === selectedProjectId ? "bg-accent text-accent-foreground" : ""
            )}
          >
            <HomeIcon className="h-4 w-4" />
            <span className="text-sm">{proj.name}</span>
          </div>
        ))}
      </nav>
    </aside>
  );
};

export { Sidebar };

Przykład „MainContent.tsx” z zakładkami:

// apps/frontend/src/components/layout/MainContent.tsx
import React, { useState } from "react";
import { Tab } from "@headlessui/react";
import { Dialog } from "@/components/ui/Dialog"; // używa DialogHeader, DialogContent z patcha
import Krok1 from "@/components/onboarding/Krok1";
import Krok2 from "@/components/onboarding/Krok2";
import Krok3 from "@/components/onboarding/Krok3";
import { Separator } from "@/components/ui/Separator";

const tabs = ["Overview", "Statystyki", "Czat AI", "Ustawienia"];

const MainContent: React.FC = () => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  return (
    <main className="flex-1 flex flex-col">
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <Tab.List className="flex space-x-4 border-b bg-background p-2">
          {tabs.map((tab) => (
            <Tab
              key={tab}
              className={({ selected }) =>
                selected
                  ? "border-b-2 border-primary pb-1 text-primary"
                  : "text-muted-foreground pb-1 hover:text-primary"
              }
            >
              {tab}
            </Tab>
          ))}
        </Tab.List>
        <Tab.Panels className="flex-1 overflow-y-auto p-4">
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Przegląd {tabs[0]}</h3>
            {/* Tutaj np. szybki widok metryk */}
            <textarea
              readOnly
              className="w-full h-64 mt-4 p-2 border rounded-md bg-muted text-muted-foreground text-sm"
              value="Tutaj wyświetlimy najważniejsze metryki i szybką analizę aktywności..."
            />
          </Tab.Panel>
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Statystyki {tabs[1]}</h3>
            {/* Tu Recharts lub inny wykres */}
            <div className="mt-4 flex flex-col space-y-2">
              <div className="bg-white p-4 rounded-md shadow-sm">
                <span className="text-sm text-muted-foreground">Cache Hits:</span>
                <span className="text-lg font-bold">1234</span>
              </div>
              <div className="bg-white p-4 rounded-md shadow-sm">
                <span className="text-sm text-muted-foreground">API Latency (ms):</span>
                <span className="text-lg font-bold">256</span>
              </div>
            </div>
          </Tab.Panel>
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Czat AI {tabs[2]}</h3>
            {/* Wstaw OknoCzatu (z patcha/Twojej poprzedniej konfiguracji) */}
            <Separator className="my-4" />
            {/* OknoCzatu to komponent, który wyświetla historię i input */}
            <div className="flex flex-col h-[500px] border rounded-md overflow-hidden">
              {/* Tu wnętrze OknoCzatu */}
              <h4 className="text-sm text-muted-foreground p-2">Symulowane okno czatu…</h4>
            </div>
          </Tab.Panel>
          <Tab.Panel>
            <h3 className="text-xl font-semibold">Ustawienia {tabs[3]}</h3>
            {/* np. zmiana motywu, konfiguracja webshocketów, itp. */}
            <button className="mt-4 inline-flex items-center space-x-2 rounded bg-secondary px-4 py-2 text-secondary-foreground hover:bg-secondary/80">
              Ustawienia globalne
            </button>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </main>
  );
};

export { MainContent };

Dostosowanie tailwind.config.js
Upewnij się, że masz w theme.extend:

animation: {
  "accordion-down": "accordion-down 0.2s ease-out",
  "accordion-up": "accordion-up 0.2s ease-out",
  "gradient-shift": "gradient-shift 15s ease infinite",
  "lift-on-hover": "lift 0.3s ease-in-out",
  "tap-on-click": "tap 0.1s ease-in-out"
},
keyframes: {
  "gradient-shift": {
    "0%": { "background-position": "0% 50%" },
    "50%": { "background-position": "100% 50%" },
    "100%": { "background-position": "0% 50%" },
  },
  "lift": {
    "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
    "50%": { transform: "translateY(-5px) rotate(1deg)" },
  },
  "tap": {
    "0%": { transform: "scale(1)" },
    "50%": { transform: "scale(0.95)" },
    "100%": { transform: "scale(1)" },
  }
}

Aktualizacja vite.config.ts → proxy dla /api, /ws, /stats (zalecane w patchu).


6. Plan dalszych działań

1. Testy w Storybook

Utwórz katalog src/stories/

Dodaj pliki Kbd.stories.tsx, IconButton.stories.tsx, Tooltip.stories.tsx z przykładami użycia.

Dzięki temu QA i designerzy mogą samodzielnie sprawdzić mikrokomponenty.



2. Dark Mode + View Transitions

Upewnij się, że ThemeContext poprawnie steruje klasami jasny/ciemny na <html>.

Dodaj view-transition dla płynnych animacji przy przełączaniu widoków (opcjonalnie wymaga polifilla).



3. Accessibility (WCAG) Audit

Sprawdź kontrasty kolorów wg narzędzi (axe, Lighthouse).

Dodaj aria-label, role, tabIndex tam, gdzie brak hierarchii semantycznych.



4. Mikrointerakcje „na kółkach”

Rozbuduj motion (Framer Motion) dla komponentów typu Accordion, Modal, Tooltip.

Upewnij się, że aria-expanded i aria-controls są poprawnie ustawione na przyciskach accordiona.



5. Dokumentacja Dev i Design

Utwórz plik UI_GUIDELINES.md w repozytorium z opisem:

Palety kolorów, typografii, spacingu, breakpoints, animacji.

Każdy komponent z patcha i każdy nowy powinien mieć krótki opis:

Kbd → do wyświetlania instrukcji klawiszowych

Separator → do wizualnego rozdzielania sekcji

IconButton → przycisk z ikoną i stanami hover/active.







---

4. Zasady „proteinowego” formułowania monitów

1. Podaj dokładny kontekst

Struktura folderów, technologie, patch, zależności.

Dlaczego to ważne? AI lepiej pracuje, gdy wie, co już istnieje i co może wykorzystać.



2. Użyj wieloról (multi-agent)

Dwie (lub więcej) role AI, które od razu symulują interdyscyplinarny zespół – burza mózgów + implementacja.

Każda rola „pomyśli głośno”:

DesignGuru: Jaki UX chcemy?

CodeWitch: Ok, zamieniam to w kod…




3. Dokładne specyfikacje i warunki

Określ: mobile-first, WCAG AA, animacje, gradienty, glassmorphism, pluginowe mikrokomponenty.

Podaj konkretne nazwy (Tailwind CSS utility, Radix UI), żeby AI generowało poprawne klasy.



4. Oczekiwane wyjście: struktura + kod + opis

AI musi wiedzieć, co ma oddać:

lista plików,

zawartość każdego pliku (TSX + Tailwind),

krótką notkę „dlaczego taki komponent” (DesignGuru).


Jeśli AI tylko opisze, będzie za mało. Jeśli AI tylko da kod bez uzasadnienia, też będzie za mało. Chcemy obie części.



5. Plan rozwoju

W promptcie poproś AI o listę rekomendacji „co zaimplementować w kolejnej fazie” – w ten sposób masz „roadmapę” z perspektywy AI.





---

5. Końcowe uwagi

Zawsze zaczynaj od patcha. Jeśli patch nie zostanie zaaplikowany, AI może pisać o komponentach, które w projekcie nie istnieją.

Używaj szczegółowych przykładów: zamiast pisać „stwórz button”, napisz „stwórz przycisk jako komponent IconButton w components/ui/IconButton.tsx, użyj lucide-react do ikony, styl Tailwind: bg-primary hover:bg-primary/90 text-primary-foreground”.

Testuj w Storybooku i manualnie w przeglądarce, by zweryfikować output AI.

Iteruj: za pierwszym razem AI może pominąć drobne szczegóły – popraw prompt, dodaj brakujące informacje.


Dzięki powyższemu, masz pełen blueprint do stworzenia “odpicowanego” frontendu: od patcha, przez projektowanie UI/UX, aż po gotowy kod z micro-interakcjami. Powodzenia!
