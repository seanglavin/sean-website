<template>
  <div class="card text-left p-3">
    <h2 class="card-title text-xl font-extrabold sm:text-4xl">{{ title }}</h2>
    <h3 class="card-subtitle block font-extrabold text-accentColor">{{ subtitle }}</h3>
    <p class="card-body mt-2 max-w-lg sm:text-xl/relaxed">{{ body }}</p>
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
