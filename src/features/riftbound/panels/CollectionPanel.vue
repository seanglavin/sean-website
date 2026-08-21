<template>
  <section class="panel">
    <AsyncState :loading="loading" :error="error">
      <p v-if="!persisted" class="warning" role="alert">
        This browser is blocking local storage, so changes will not survive a reload.
        Export the collection to keep it.
      </p>

      <div class="summary">
        <span class="stat"><strong>{{ ownedCount }}</strong> owned</span>
        <span class="stat"><strong>{{ wantedCount }}</strong> wanted</span>
        <span class="stat"><strong>{{ formatCents(ownedValueCents) }}</strong> owned value</span>
        <span class="stat"><strong>{{ formatCents(wantedCostCents) }}</strong> to buy the want list</span>
      </div>

      <div class="actions">
        <button class="action" type="button" @click="exportCollection">Export JSON</button>
        <button class="action" type="button" @click="fileInput.click()">Import JSON</button>
        <button v-if="rows.length" class="action" type="button" @click="confirmClear">Clear</button>
        <input ref="fileInput" class="sr-only" type="file" accept="application/json" @change="importCollection" />
      </div>
      <p v-if="message" class="message" role="status">{{ message }}</p>

      <CardDetailDrawer :card="selected" @close="selected = null">
        <template #collection="{ card }">
          <CollectionControls :code="card.code" />
        </template>
        <template #prices="{ card }">
          <PriceTable :code="card.code" :offers="priceIndex.offersFor(card.code)" />
        </template>
      </CardDetailDrawer>

      <p v-if="!rows.length" class="hint">
        Nothing tracked yet. Open a card from the Cards or Prices tab and use its Owned and
        Wanted steppers, or import a previously exported file.
      </p>
      <DataTable
        v-else
        :columns="columns"
        :rows="rows"
        row-key-field="code"
        caption="Tracked collection"
        default-sort="name"
      >
        <template #cell-name="{ row }">
          <button class="name-button" type="button" @click="selected = row.card">
            {{ row.name }}
          </button>
        </template>
        <template #cell-unitCents="{ value }">{{ formatCents(value) }}</template>
        <template #cell-ownedValueCents="{ value }">{{ formatCents(value) }}</template>
      </DataTable>
    </AsyncState>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import AsyncState from '@/components/ui/AsyncState.vue'
import DataTable from '@/components/ui/DataTable.vue'
import CardDetailDrawer from '../components/CardDetailDrawer.vue'
import CollectionControls from '../components/CollectionControls.vue'
import PriceTable from '../components/PriceTable.vue'
import { useCardCatalog } from '../composables/useCardCatalog'
import { useCollection } from '../composables/useCollection'
import { usePriceIndex } from '../composables/usePriceIndex'
import { downloadJson } from '../lib/storage'
import { formatCents } from '../lib/money'

const catalog = useCardCatalog()
const priceIndex = usePriceIndex()
const collection = useCollection()

const { ownedCount, wantedCount, persisted } = collection
const selected = ref(null)
const fileInput = ref(null)
const message = ref('')

const loading = computed(() => catalog.loading.value || priceIndex.loading.value)
const error = computed(() => catalog.error.value || priceIndex.error.value)

const rows = computed(() =>
  collection.entries.value.map((entry) => {
    const card = catalog.byCode.value.get(entry.code)
    const cheapest = priceIndex.cheapestFor(entry.code)
    const unitCents = cheapest?.priceCents ?? null
    return {
      card: card ?? null,
      code: entry.code,
      name: card?.name ?? entry.code,
      set: card?.set_name ?? '—',
      owned: entry.owned,
      wanted: entry.wanted,
      unitCents,
      ownedValueCents: unitCents == null ? null : unitCents * entry.owned,
    }
  }),
)

const ownedValueCents = computed(() =>
  rows.value.reduce((sum, row) => sum + (row.ownedValueCents ?? 0), 0),
)
const wantedCostCents = computed(() =>
  rows.value.reduce((sum, row) => sum + (row.unitCents ?? 0) * row.wanted, 0),
)

const columns = [
  { key: 'name', label: 'Card', sortable: true },
  { key: 'code', label: 'Code', sortable: true },
  { key: 'set', label: 'Set', sortable: true },
  { key: 'owned', label: 'Owned', sortable: true },
  { key: 'wanted', label: 'Wanted', sortable: true },
  { key: 'unitCents', label: 'Cheapest', sortable: true },
  { key: 'ownedValueCents', label: 'Owned value', sortable: true },
]

function exportCollection() {
  downloadJson('riftbound-collection.json', collection.toExport())
  message.value = 'Exported riftbound-collection.json.'
}

async function importCollection(event) {
  const file = event.target.files?.[0]
  if (!file) return
  try {
    collection.fromImport(await file.text())
    message.value = `Imported ${collection.entries.value.length} cards.`
  } catch (e) {
    message.value = `Import failed: ${e.message}`
  } finally {
    event.target.value = ''
  }
}

function confirmClear() {
  if (window.confirm('Remove every tracked card? Export first if you want a copy.')) {
    collection.clear()
    message.value = 'Collection cleared.'
  }
}
</script>

<style scoped>
.panel {
  @apply max-w-5xl mx-auto text-left
}
.warning {
  @apply p-3 mb-3 rounded-xl bg-black bg-opacity-30 text-accentColor font-bold
}
.summary {
  @apply flex flex-wrap gap-4 mb-3
}
.stat {
  @apply px-3 py-1 rounded-lg bg-black bg-opacity-20
}
.actions {
  @apply flex flex-wrap gap-2 mb-3
}
.action {
  @apply px-3 py-1 rounded-lg font-bold bg-black bg-opacity-20 hover:text-accentColor
}
.message {
  @apply text-sm opacity-80 mb-3
}
.hint {
  @apply p-6 text-center bg-black rounded-xl bg-opacity-20
}
.name-button {
  @apply font-bold text-accentColor underline text-left
}
</style>
