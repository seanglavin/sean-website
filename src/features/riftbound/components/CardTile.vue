<template>
  <button class="card-tile" type="button" @click="$emit('select', card)">
    <img
      class="card-art"
      :src="card.image.small"
      :alt="`${card.name} (${card.code})`"
      loading="lazy"
      width="146"
      height="204"
    />
    <span class="card-name">{{ card.name }}</span>
    <span class="card-meta">{{ card.code }}</span>
  </button>
</template>

<script setup>
defineProps({ card: { type: Object, required: true } })
defineEmits(['select'])
</script>

<style scoped>
.card-tile {
  @apply flex flex-col items-center gap-1 p-2 rounded-xl bg-black bg-opacity-20;
  @apply hover:bg-opacity-40 focus:outline-none focus:ring-2 focus:ring-accentColor;
}
.card-art {
  @apply w-full h-auto rounded-lg
}
.card-name {
  @apply text-sm font-bold leading-tight
}
.card-meta {
  @apply text-xs opacity-70
}
</style>
