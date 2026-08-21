import { computed, ref, watch } from 'vue'
import { exportPayload, isAvailable, parseImport, read, write } from '../lib/storage'

const KEY = 'collection'

// Module-level so every panel shares one collection without a store library.
const items = ref(read(KEY, {}))
const persisted = ref(isAvailable())

watch(items, (value) => {
  persisted.value = write(KEY, value)
}, { deep: true })

export function useCollection() {
  const entries = computed(() =>
    Object.entries(items.value)
      .map(([code, entry]) => ({ code, owned: entry.owned ?? 0, wanted: entry.wanted ?? 0 }))
      .filter((entry) => entry.owned > 0 || entry.wanted > 0),
  )

  const ownedCount = computed(() => entries.value.reduce((sum, entry) => sum + entry.owned, 0))
  const wantedCount = computed(() => entries.value.reduce((sum, entry) => sum + entry.wanted, 0))

  function entryFor(code) {
    return items.value[code] ?? { owned: 0, wanted: 0 }
  }

  function set(code, field, value) {
    const next = { ...entryFor(code), [field]: Math.max(0, value) }
    if (next.owned === 0 && next.wanted === 0) {
      const { [code]: _removed, ...rest } = items.value
      items.value = rest
      return
    }
    items.value = { ...items.value, [code]: next }
  }

  function adjust(code, field, delta) {
    set(code, field, entryFor(code)[field] + delta)
  }

  function clear() {
    items.value = {}
  }

  function toExport() {
    return exportPayload(KEY, items.value)
  }

  function fromImport(text, { merge = false } = {}) {
    const value = parseImport(text, KEY)
    items.value = merge ? { ...items.value, ...value } : value
  }

  return {
    items,
    entries,
    ownedCount,
    wantedCount,
    persisted,
    entryFor,
    set,
    adjust,
    clear,
    toExport,
    fromImport,
  }
}
