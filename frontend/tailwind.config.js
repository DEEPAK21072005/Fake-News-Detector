/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0B0F19',
          800: '#111827',
          700: '#1F2937',
          600: '#374151',
        },
        brand: {
          500: '#6366F1', // Indigo
          600: '#4F46E5',
          700: '#4338CA',
        },
        verdict: {
          real: '#10B981', // Emerald
          fake: '#EF4444', // Rose/Red
          uncertain: '#F59E0B', // Amber
          insufficient: '#6B7280', // Gray
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
