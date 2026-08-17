<template>
  <router-link :to="linkTo" class="card">
    <h2 class="card-title">{{ title }}</h2>
    <h3 class="card-subtitle">{{ category }}</h3>
    <p class="card-body">{{ summary }}</p>
  </router-link>
</template>

<script setup>
defineProps({
  title: String,
  category: String,
  summary: String,
  linkTo: String,
})
</script>

<style scoped>
.card {
  @apply block mt-4 p-4 text-left sm:max-w-lg mx-auto;
  @apply bg-black rounded-xl bg-opacity-20 hover:bg-opacity-30;
}
.card-title {
  @apply block text-xl font-extrabold sm:text-3xl
}
.card-subtitle {
  @apply block font-extrabold text-accentColor sm:text-xl
}
.card-body {
  @apply mt-2 max-w-lg sm:text-xl/relaxed
}
</style>
