<template>
  <ul class="card-grid">
    <li v-for="card in cards" :key="card.code">
      <CardTile :card="card" @select="$emit('select', $event)" />
    </li>
  </ul>
</template>

<script setup>
import CardTile from './CardTile.vue'

defineProps({ cards: { type: Array, required: true } })
defineEmits(['select'])
</script>

<style scoped>
.card-grid {
  @apply grid gap-3 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6
}
</style>
