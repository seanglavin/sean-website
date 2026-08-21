<template>
  <div class="price-table">
    <div class="price-head">
      <h3 class="price-title">Canadian prices</h3>
      <label class="stock-toggle">
        <input type="checkbox" :checked="inStockOnly" @change="inStockOnly = $event.target.checked" />
        In stock only
      </label>
    </div>
    <p v-if="!rows.length" class="price-empty">
      No {{ inStockOnly ? 'in-stock ' : '' }}listings for this card.
    </p>
    <DataTable
      v-else
      :columns="columns"
      :rows="rows"
      row-key-field="key"
      :caption="`Prices for ${code}`"
    >
      <template #cell-priceCents="{ value }">{{ formatCents(value) }}</template>
      <template #cell-finish="{ value }">{{ value === 'foil' ? 'Foil' : 'Non-foil' }}</template>
      <template #cell-available="{ value }">
        <span :class="value ? 'in-stock' : 'out-of-stock'">{{ value ? 'In stock' : 'Out' }}</span>
      </template>
      <template #cell-url="{ row }">
        <a class="buy-link" :href="row.url" target="_blank" rel="noopener noreferrer">View</a>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import { formatCents } from '../lib/money'

const props = defineProps({
  code: { type: String, required: true },
  offers: { type: Array, required: true },
})

const inStockOnly = ref(true)

const rows = computed(() =>
  props.offers.filter((offer) => (inStockOnly.value ? offer.available : true)),
)

const columns = [
  { key: 'retailerName', label: 'Store', sortable: true },
  { key: 'condition', label: 'Condition', sortable: true },
  { key: 'finish', label: 'Finish', sortable: true },
  { key: 'priceCents', label: 'Price', sortable: true },
  { key: 'available', label: 'Stock', sortable: true },
  { key: 'url', label: '' },
]
</script>

<style scoped>
.price-table {
  @apply mt-4
}
.price-head {
  @apply flex flex-wrap items-center justify-between gap-3 mb-2
}
.price-title {
  @apply text-lg font-extrabold text-accentColor
}
.stock-toggle {
  @apply flex items-center gap-2 text-sm
}
.price-empty {
  @apply p-4 text-center bg-black rounded-xl bg-opacity-20
}
.in-stock {
  @apply text-accentColor2 font-bold
}
.out-of-stock {
  @apply opacity-60
}
.buy-link {
  @apply font-bold text-accentColor underline
}
</style>
