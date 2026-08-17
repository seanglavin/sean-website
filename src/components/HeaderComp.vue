<template>
  <header class="top-bar">
    <nav class="top-bar-nav" aria-label="Main navigation">
      <!-- Add nav icons later! -->
      <router-link class="nav-bar-link"
        v-for="(link, index) in headerLinks" :key="index" :to="link.to">
        <span>{{ link.text }}</span>
        <!-- adds a | between each link -->
        <span v-if="index < headerLinks.length - 1" class="text-textColor"> | </span>
      </router-link>
      <span class="text-textColor"> | </span>
      <button
        type="button"
        class="theme-toggle"
        :aria-pressed="theme === 'dark'"
        :aria-label="theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'"
        @click="toggleTheme"
      >{{ theme === 'light' ? 'Dark' : 'Light' }}</button>
    </nav>
  </header>
</template>

<script setup>
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme } = useTheme()

const headerLinks = [
  { text: 'Home', to: '/' },
  { text: 'About', to: '/about' },
  { text: 'My Cat', to: '/mycat' },
  { text: 'Projects', to: '/projects' },
  // { text: 'Resume', to: '/resume' },
]
</script>

<style scoped>
.top-bar {
  @apply bg-surfaceColor p-5 w-full
}
.top-bar-nav {
  @apply flex items-center justify-center flex-wrap gap-2
}
.nav-bar-link {
  @apply font-bold text-textColor hover:text-accentColor
}
.nav-bar-link.router-link-active {
  @apply text-accentColor
}
.theme-toggle {
  @apply font-bold text-textColor hover:text-accentColor cursor-pointer
}
</style>
