/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        textColor: 'var(--color-text)',
        surfaceColor: 'var(--color-surface)',
        accentColor: 'var(--color-accent)',
        accentColor2: 'var(--color-accent-2)',
        onAccent: 'var(--color-on-accent)',
      },
      fontFamily: {
        mono: ['IBMPlexMono', 'monospace'],
        sans: ['Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
