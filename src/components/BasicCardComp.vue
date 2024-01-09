<template>
  <div class="card">
    <h2 class="card-title">{{ title }}</h2>
    <h3 class="card-subtitle">{{ subtitle }}</h3>
    <p class="card-body">{{ body }}</p>
  </div>
</template>

<script>
export default {
  props: {
    title: String,
    subtitle: String,
    body: String
  }
}
</script>
s
<style scoped>
.card {
  @apply mt-4 pt-4 px-2 pb-2 text-left sm:max-w-lg mx-auto;
  @apply bg-black rounded-xl bg-opacity-20;
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