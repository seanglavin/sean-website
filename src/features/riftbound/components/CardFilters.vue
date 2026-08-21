<template>
  <div class="filters">
    <SearchBox
      :model-value="query"
      label="Search cards by name or code"
      placeholder="Search by name or code (e.g. Defy, OGN-045)…"
      @update:model-value="$emit('update:query', $event)"
    />
    <div class="filter-row">
      <label v-for="field in fields" :key="field.key" class="filter">
        <span class="filter-label">{{ field.label }}</span>
        <select
          class="filter-select"
          :value="filters[field.key]"
          @change="filters[field.key] = $event.target.value"
        >
          <option value="">Any</option>
          <option v-for="option in field.options" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>
      <button v-if="active" class="reset-button" type="button" @click="$emit('reset')">
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SearchBox from '@/components/ui/SearchBox.vue'

const props = defineProps({
  query: { type: String, default: '' },
  filters: { type: Object, required: true },
  sets: { type: Array, default: () => [] },
  rarities: { type: Array, default: () => [] },
  types: { type: Array, default: () => [] },
  domains: { type: Array, default: () => [] },
  energies: { type: Array, default: () => [] },
  active: Boolean,
})
defineEmits(['update:query', 'reset'])

const toOptions = (values) => values.map((value) => ({ value: String(value), label: String(value) }))

const fields = computed(() => [
  { key: 'set', label: 'Set', options: props.sets },
  { key: 'domain', label: 'Domain', options: toOptions(props.domains) },
  { key: 'type', label: 'Type', options: toOptions(props.types) },
  { key: 'rarity', label: 'Rarity', options: toOptions(props.rarities) },
  { key: 'energy', label: 'Energy', options: toOptions(props.energies) },
])
</script>

<style scoped>
.filters {
  @apply flex flex-col gap-3 mb-4
}
.filter-row {
  @apply flex flex-wrap items-end gap-3
}
.filter {
  @apply flex flex-col gap-1 text-sm
}
.filter-label {
  @apply font-bold opacity-80
}
.filter-select {
  @apply px-2 py-1 rounded-lg bg-black bg-opacity-30 text-textColor;
  @apply border border-transparent focus:border-accentColor focus:outline-none;
}
.reset-button {
  @apply px-3 py-1 rounded-lg font-bold bg-black bg-opacity-20 hover:text-accentColor
}
</style>
