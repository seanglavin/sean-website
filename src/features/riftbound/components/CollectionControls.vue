<template>
  <div class="controls">
    <div v-for="field in fields" :key="field.key" class="stepper">
      <span class="stepper-label">{{ field.label }}</span>
      <button class="step" type="button" :aria-label="`Decrease ${field.label}`" @click="adjust(code, field.key, -1)">−</button>
      <span class="count">{{ entry[field.key] }}</span>
      <button class="step" type="button" :aria-label="`Increase ${field.label}`" @click="adjust(code, field.key, 1)">+</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCollection } from '../composables/useCollection'

const props = defineProps({ code: { type: String, required: true } })

const { entryFor, adjust } = useCollection()
const entry = computed(() => entryFor(props.code))

const fields = [
  { key: 'owned', label: 'Owned' },
  { key: 'wanted', label: 'Wanted' },
]
</script>

<style scoped>
.controls {
  @apply flex flex-wrap gap-4 mt-4
}
.stepper {
  @apply flex items-center gap-2
}
.stepper-label {
  @apply font-bold opacity-80
}
.step {
  @apply w-8 h-8 rounded-lg font-extrabold bg-black bg-opacity-30 hover:text-accentColor
}
.count {
  @apply min-w-8 text-center font-extrabold
}
</style>
