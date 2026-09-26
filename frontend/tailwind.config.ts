import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // MediTwin brand: clinical teal (trust) + deep navy (precision)
        brand: {
          50: "#e6f7f4",
          100: "#b3e6db",
          400: "#1f9d84",
          500: "#0f7d67",
          600: "#0a5f4f",
          900: "#04231d",
        },
        risk: {
          low: "#1f9d84",
          medium: "#d99a1f",
          high: "#c9432f",
        },
      },
      borderRadius: {
        xl: "1rem",
      },
    },
  },
  plugins: [],
};

export default config;
