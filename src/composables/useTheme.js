import { ref } from 'vue'

const STORAGE_KEY = 'theme'
const mediaQuery = window.matchMedia('(prefers-color-scheme: light)')

function storedPreference() {
  return localStorage.getItem(STORAGE_KEY)
}

function effectiveTheme() {
  return storedPreference() ?? (mediaQuery.matches ? 'light' : 'dark')
}

const theme = ref(effectiveTheme())

function syncDocument() {
  const stored = storedPreference()
  if (stored) {
    document.documentElement.setAttribute('data-theme', stored)
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
  theme.value = effectiveTheme()
}

mediaQuery.addEventListener('change', syncDocument)

export function useTheme() {
  function toggleTheme() {
    localStorage.setItem(STORAGE_KEY, theme.value === 'light' ? 'dark' : 'light')
    syncDocument()
  }

  return { theme, toggleTheme }
}
