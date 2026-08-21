<template>
  <div v-if="loading" class="async-message" role="status">
    <slot name="loading">Loading…</slot>
  </div>
  <div v-else-if="error" class="async-message async-error" role="alert">
    <slot name="error" :error="error">Could not load data: {{ error }}</slot>
  </div>
  <div v-else-if="empty" class="async-message">
    <slot name="empty">Nothing to show.</slot>
  </div>
  <slot v-else />
</template>

<script setup>
defineProps({
  loading: Boolean,
  error: String,
  empty: Boolean,
})
</script>

<style scoped>
.async-message {
  @apply p-6 text-center bg-black rounded-xl bg-opacity-20
}
.async-error {
  @apply text-accentColor font-bold
}
</style>
