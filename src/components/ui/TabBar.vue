<template>
  <nav class="tab-bar" :aria-label="ariaLabel">
    <router-link
      v-for="tab in tabs"
      :key="tab.id"
      class="tab"
      :to="tab.to"
      exact-active-class="tab-active"
    >
      {{ tab.label }}
    </router-link>
  </nav>
</template>

<script setup>
defineProps({
  tabs: { type: Array, required: true },
  ariaLabel: { type: String, default: 'Section navigation' },
})
</script>

<style scoped>
.tab-bar {
  @apply flex flex-wrap items-center justify-center gap-2 mb-4
}
.tab {
  @apply px-4 py-2 rounded-lg font-bold bg-black bg-opacity-20 text-textColor;
  @apply hover:text-accentColor;
}
.tab-active {
  @apply bg-accentColor text-onAccent hover:text-onAccent
}
</style>
