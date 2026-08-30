/**
 * Tailwind-Konfiguration — **eine** Stelle statt sechs (P1.4).
 *
 * Bis zum 2026-08-30 stand dieselbe Konfiguration inline in `dashboard/web/app.py`
 * und in jeder der fuenf Landingpage-Seiten, ausgewertet von einem CDN-Skript zur
 * Laufzeit. Damit meldete **jeder Seitenaufruf** die IP des Betrachters an
 * `cdn.tailwindcss.com` — das widerspricht dem Deployment-Ziel Datenhoheit
 * direkt, und bei sechs Kopien lief die Palette frueher oder spaeter auseinander.
 *
 * **Tailwind v3, gepinnt.** Der CDN-Aufruf war v3 mit den Plugins `forms` und
 * `container-queries`; v4 bricht die Klassensyntax.
 *
 * **Was `content` erfasst, entscheidet, welche Regeln es gibt.** Tailwind
 * schreibt nur Regeln fuer Klassen, die es im Quelltext findet — eine Klasse,
 * die zur Laufzeit aus Bruchstuecken entsteht, findet der Scanner nicht, und
 * ihre Regel fehlt dann **stumm**: kein Fehler, nur ein Kasten, der anders
 * aussieht. Dagegen steht ein Waechter in `tests/test_web_overflow.py`, der
 * jede im gezeichneten DOM benutzte Klasse gegen die vorhandenen Regeln
 * haelt.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./dashboard/**/*.py",
    "./aeroforesight-ai-landing-page/*.html",
  ],
  theme: {
    extend: {
      colors: {
        // Deckungsgleich mit `theme.NAVY` und
        // `aeroforesight-ai-landing-page/design/color-tokens.json`.
        navy: {
          50: "#f0f4f9",
          100: "#e0eaf3",
          200: "#c2d5e7",
          300: "#94b8d7",
          400: "#6094c1",
          500: "#3e76a6",
          600: "#2d5e8a",
          700: "#244b70",
          800: "#1E3A5F", // Primary
          900: "#1c3453",
          950: "#122238",
        },
      },
      borderRadius: {
        DEFAULT: "0.5rem",
        lg: "0.75rem",
        xl: "1rem",
        full: "9999px",
      },
      fontFamily: {
        headline: ["Plus Jakarta Sans", "sans-serif"],
        display: ["Plus Jakarta Sans", "sans-serif"],
        body: ["Inter", "sans-serif"],
        label: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/container-queries"),
  ],
};
