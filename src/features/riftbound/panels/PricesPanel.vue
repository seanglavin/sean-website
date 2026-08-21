<template>
  <section class="panel">
    <AsyncState :loading="loading" :error="error">
      <div class="retailers">
        <RetailerBadge v-for="entry in retailers" :key="entry.id" :retailer="entry" />
      </div>

      <CardDetailDrawer :card="selected" @close="selected = null">
        <template #prices="{ card }">
          <PriceTable :code="card.code" :offers="priceIndex.offersFor(card.code)" />
        </template>
      </CardDetailDrawer>

      <SearchBox
        :model-value="query"
        label="Search cards by name or code"
        placeholder="Search a card to compare prices (e.g. Defy, OGN-045)…"
        @update:model-value="query = $event"
      />

      <p v-if="!query.trim()" class="hint">
        Search for a card to compare prices across {{ retailers.length }} Canadian stores.
      </p>
      <p v-else-if="!rows.length" class="hint">No cards match “{{ query }}”.</p>
      <DataTable
        v-else
        class="results"
        :columns="columns"
        :rows="rows"
        row-key-field="code"
        caption="Card search results with cheapest in-stock price"
        default-sort="name"
      >
        <template #cell-name="{ row }">
          <button class="name-button" type="button" @click="selected = row.card">
            {{ row.name }}
          </button>
        </template>
        <template #cell-cheapestCents="{ value }">{{ formatCents(value) }}</template>
      </DataTable>
    </AsyncState>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import AsyncState from '@/components/ui/AsyncState.vue'
import DataTable from '@/components/ui/DataTable.vue'
import SearchBox from '@/components/ui/SearchBox.vue'
import CardDetailDrawer from '../components/CardDetailDrawer.vue'
import PriceTable from '../components/PriceTable.vue'
import RetailerBadge from '../components/RetailerBadge.vue'
import { useCardCatalog } from '../composables/useCardCatalog'
import { usePriceIndex } from '../composables/usePriceIndex'
import { formatCents } from '../lib/money'

const MAX_RESULTS = 50

const catalog = useCardCatalog()
const priceIndex = usePriceIndex()

const query = ref('')
const selected = ref(null)

const loading = computed(() => catalog.loading.value || priceIndex.loading.value)
const error = computed(() => catalog.error.value || priceIndex.error.value)
const retailers = computed(() => priceIndex.retailers.value)

const rows = computed(() => {
  const needle = query.value.trim().toLowerCase()
  if (!needle) return []
  return catalog.cards.value
    .filter(
      (card) =>
        card.name.toLowerCase().includes(needle) || card.code.toLowerCase().includes(needle),
    )
    .slice(0, MAX_RESULTS)
    .map((card) => {
      const cheapest = priceIndex.cheapestFor(card.code)
      return {
        card,
        code: card.code,
        name: card.name,
        set: card.set_name,
        cheapestCents: cheapest?.priceCents ?? null,
        cheapestStore: cheapest?.retailerName ?? 'No stock',
      }
    })
})

const columns = [
  { key: 'name', label: 'Card', sortable: true },
  { key: 'code', label: 'Code', sortable: true },
  { key: 'set', label: 'Set', sortable: true },
  { key: 'cheapestCents', label: 'Cheapest in stock', sortable: true },
  { key: 'cheapestStore', label: 'Store', sortable: true },
]
</script>

<style scoped>
.panel {
  @apply max-w-5xl mx-auto text-left
}
.retailers {
  @apply flex flex-wrap gap-2 mb-4
}
.hint {
  @apply p-6 mt-3 text-center bg-black rounded-xl bg-opacity-20
}
.results {
  @apply mt-3
}
.name-button {
  @apply font-bold text-accentColor underline text-left
}
</style>
