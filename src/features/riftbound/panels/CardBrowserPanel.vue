<template>
  <section class="panel">
    <AsyncState :loading="loading" :error="error" :empty="!cards.length">
      <CardDetailDrawer :card="selected" @close="selected = null" />
      <CardFilters
        v-model:query="query"
        :filters="filters"
        :sets="sets"
        :rarities="rarities"
        :types="types"
        :domains="domains"
        :energies="energies"
        :active="active"
        @reset="reset"
      />
      <p class="result-count">
        {{ matches.length }} of {{ cards.length }} cards
        <span v-if="truncated">(showing the first {{ MAX_RESULTS }})</span>
      </p>
      <p v-if="!matches.length" class="no-results">No cards match those filters.</p>
      <CardGrid v-else :cards="visible" @select="selected = $event" />
    </AsyncState>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import AsyncState from '@/components/ui/AsyncState.vue'
import CardDetailDrawer from '../components/CardDetailDrawer.vue'
import CardFilters from '../components/CardFilters.vue'
import CardGrid from '../components/CardGrid.vue'
import { useCardCatalog } from '../composables/useCardCatalog'
import { useCardFilters } from '../composables/useCardFilters'

const { cards, sets, rarities, types, domains, error, loading } = useCardCatalog()
const { query, filters, matches, visible, truncated, active, reset, MAX_RESULTS } =
  useCardFilters(cards)

const selected = ref(null)

const energies = computed(() =>
  [...new Set(cards.value.map((card) => card.energy).filter((value) => value != null))].sort(
    (a, b) => a - b,
  ),
)
</script>

<style scoped>
.panel {
  @apply max-w-6xl mx-auto text-left
}
.result-count {
  @apply text-sm opacity-70 mb-2
}
.no-results {
  @apply p-6 text-center bg-black rounded-xl bg-opacity-20
}
</style>
