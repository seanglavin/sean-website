<template>
  <span class="badge" :class="statusClass">
    {{ retailer.name }}
    <span class="badge-detail">{{ detail }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { relativeDays } from '../lib/money'

const props = defineProps({ retailer: { type: Object, required: true } })

const statusClass = computed(() => `badge-${props.retailer.status ?? 'ok'}`)

const detail = computed(() => {
  if (props.retailer.status === 'error') return 'refresh failed'
  return `updated ${relativeDays(props.retailer.generated_at)}`
})
</script>

<style scoped>
.badge {
  @apply inline-flex items-center gap-2 px-3 py-1 rounded-lg text-sm bg-black bg-opacity-20
}
.badge-detail {
  @apply text-xs opacity-70
}
.badge-error {
  @apply text-accentColor
}
</style>
