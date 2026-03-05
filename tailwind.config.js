/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'media',
  theme: {
    extend: {
      colors: {
        primaryLight: 'var(--primary-light)',
        secondaryBlueLight: 'var(--secondary-blue-light)',
        secondaryBlueDark: 'var(--secondary-blue-dark)',
        accentColor: 'var(--accent-color)',
        accentColor2: 'var(--accent-color-2)',
        primaryDark: 'var(--primary-dark)',
        secondaryDark: 'var(--secondary-dark)',
      },
      fontFamily: {
        mono: ['IBMPlexMono', 'monospace'],
        sans: ['Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
