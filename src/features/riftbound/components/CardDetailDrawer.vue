<template>
  <aside v-if="card" class="drawer" aria-labelledby="drawer-title">
    <div class="drawer-head">
      <h2 id="drawer-title" class="drawer-title">{{ card.name }}</h2>
      <button class="close-button" type="button" @click="$emit('close')">Close</button>
    </div>
    <div class="drawer-body">
      <img
        class="drawer-art"
        :src="card.image.large"
        :alt="`${card.name} (${card.code})`"
        loading="lazy"
      />
      <dl class="drawer-stats">
        <div v-for="stat in stats" :key="stat.label" class="stat">
          <dt>{{ stat.label }}</dt>
          <dd>{{ stat.value }}</dd>
        </div>
      </dl>
    </div>
    <slot name="collection" :card="card" />
    <slot name="prices" :card="card" />
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ card: { type: Object, default: null } })
defineEmits(['close'])

const stats = computed(() => {
  const card = props.card
  if (!card) return []
  return [
    { label: 'Code', value: card.code },
    { label: 'Set', value: card.set_name },
    { label: 'Type', value: card.type ?? '—' },
    { label: 'Rarity', value: card.rarity ?? '—' },
    { label: 'Domains', value: card.domains.length ? card.domains.join(', ') : '—' },
    { label: 'Energy', value: card.energy ?? '—' },
    { label: 'Might', value: card.might ?? '—' },
    { label: 'Power', value: card.power ?? '—' },
  ]
})
</script>

<style scoped>
.drawer {
  @apply mb-6 p-4 rounded-xl bg-black bg-opacity-30
}
.drawer-head {
  @apply flex items-center justify-between gap-3 mb-3
}
.drawer-title {
  @apply text-xl font-extrabold text-accentColor sm:text-2xl
}
.close-button {
  @apply px-3 py-1 rounded-lg font-bold bg-black bg-opacity-20 hover:text-accentColor
}
.drawer-body {
  @apply flex flex-col gap-4 sm:flex-row
}
.drawer-art {
  @apply w-48 h-auto rounded-lg mx-auto sm:mx-0
}
.drawer-stats {
  @apply grid grid-cols-2 gap-x-6 gap-y-1 content-start flex-1
}
.stat {
  @apply flex justify-between gap-3 border-b border-white border-opacity-10 py-1
}
.stat dt {
  @apply font-bold opacity-80
}
</style>
