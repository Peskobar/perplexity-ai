/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ["class"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: `var(--radius)`,
        md: `calc(var(--radius) - 2px)`,
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
         // Kluczowe klatki dla dynamicznego gradientu
         "gradient-shift": {
          "0%": { "background-position": "0% 50%" },
          "50%": { "background-position": "100% 50%" },
          "100%": { "background-position": "0% 50%" },
        },
         // Animacja hover-lift
        "lift": {
          "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
          "50%": { transform: "translateY(-5px) rotate(1deg)" },
        },
         // Animacja tap-feedback
        "tap": {
          "0%": { transform: "scale(1)" },
          "50%": { transform: "scale(0.95)" },
          "100%": { transform: "scale(1)" },
        }
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "gradient-shift": "gradient-shift 15s ease infinite", // Zastosuj do tła
        "lift-on-hover": "lift 0.3s ease-in-out", // Użyj na hover
        "tap-on-click": "tap 0.1s ease-in-out" // Użyj na click
      },
       // Konfiguracja view-transition i scroll-timeline (modern CSS, może wymagać prefiksów lub Polyfill)
       // Tailwind 4 ma lepsze wsparcie dla CSS variables i nowości
       // Można zdefiniować niestandardowe właściwości lub utility
       // Przykład: Można definiować zmienne CSS w global.css i odwoływać się tutaj
       // '--view-transition-name': '...'
       // '--scroll-timeline': '...'
    },
  },
  plugins: [
    require("tailwindcss-animate"),
    // require("@tailwindcss/typography"), // Opcjonalnie dla lepszej typografii
    // Wtyczka dla niestandardowych wariantów animacji (np. hover:animate-lift)
    function ({ addUtilities, theme, e }) {
      const liftUtilities = {
        '.animate-lift-on-hover': {
          transition: 'transform 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-5px) rotate(1deg)',
          },
        },
      };
      const tapUtilities = {
         '.animate-tap-on-click': {
            transition: 'transform 0.1s ease-in-out',
            '&:active': {
               transform: 'scale(0.95)',
            },
         },
      };
      addUtilities(liftUtilities, ['hover']);
      addUtilities(tapUtilities, ['active']);
    }
  ],
}
