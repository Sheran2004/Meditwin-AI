import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MediTwin AI — Predict. Prevent. Protect.",
  description: "AI-powered digital twin healthcare platform",
};

// Runs before React hydrates so the correct theme applies on first paint —
// no "flash of wrong theme" when a returning user has dark mode saved.
const THEME_INIT_SCRIPT = `
(function () {
  try {
    var stored = localStorage.getItem('meditwin_theme');
    var theme = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    if (theme === 'dark') document.documentElement.classList.add('dark');
  } catch (e) {}
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
