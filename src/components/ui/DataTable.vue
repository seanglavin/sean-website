<template>
  <div class="table-scroll">
    <table class="data-table">
      <caption v-if="caption" class="sr-only">{{ caption }}</caption>
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" scope="col" :aria-sort="ariaSort(col)">
            <button v-if="col.sortable" class="sort-button" type="button" @click="toggleSort(col.key)">
              {{ col.label }}
              <span aria-hidden="true">{{ sortIndicator(col.key) }}</span>
            </button>
            <span v-else>{{ col.label }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in sortedRows" :key="rowKey(row, index)">
          <td v-for="col in columns" :key="col.key" :data-label="col.label">
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  rowKeyField: { type: String, default: null },
  caption: { type: String, default: '' },
  defaultSort: { type: String, default: null },
  defaultDirection: { type: String, default: 'asc' },
})

const sortKey = ref(props.defaultSort)
const sortDirection = ref(props.defaultDirection)

const sortedRows = computed(() => {
  if (!sortKey.value) return props.rows
  const key = sortKey.value
  const factor = sortDirection.value === 'asc' ? 1 : -1
  return [...props.rows].sort((a, b) => factor * compare(a[key], b[key]))
})

function compare(a, b) {
  if (a == null && b == null) return 0
  if (a == null) return 1
  if (b == null) return -1
  if (typeof a === 'number' && typeof b === 'number') return a - b
  return String(a).localeCompare(String(b), undefined, { numeric: true })
}

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    return
  }
  sortKey.value = key
  sortDirection.value = 'asc'
}

function sortIndicator(key) {
  if (sortKey.value !== key) return ''
  return sortDirection.value === 'asc' ? '▲' : '▼'
}

function ariaSort(col) {
  if (!col.sortable) return undefined
  if (sortKey.value !== col.key) return 'none'
  return sortDirection.value === 'asc' ? 'ascending' : 'descending'
}

function rowKey(row, index) {
  return props.rowKeyField ? row[props.rowKeyField] : index
}
</script>

<style scoped>
.table-scroll {
  @apply w-full overflow-x-auto
}
.data-table {
  @apply w-full text-left border-collapse
}
.data-table th,
.data-table td {
  @apply px-3 py-2 border-b border-white border-opacity-10 align-middle
}
.data-table th {
  @apply text-accentColor font-extrabold whitespace-nowrap
}
.sort-button {
  @apply font-extrabold hover:text-textColor
}
</style>
