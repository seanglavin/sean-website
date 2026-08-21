import { computed, reactive, ref } from 'vue'

const MAX_RESULTS = 300

export function useCardFilters(cards) {
  const query = ref('')
  const filters = reactive({ set: '', rarity: '', type: '', domain: '', energy: '' })

  const matches = computed(() => {
    const needle = query.value.trim().toLowerCase()
    return cards.value.filter((card) => {
      if (filters.set && card.set !== filters.set) return false
      if (filters.rarity && card.rarity !== filters.rarity) return false
      if (filters.type && card.type !== filters.type) return false
      if (filters.domain && !card.domains.includes(filters.domain)) return false
      if (filters.energy !== '' && String(card.energy ?? '') !== filters.energy) return false
      if (!needle) return true
      return (
        card.name.toLowerCase().includes(needle) || card.code.toLowerCase().includes(needle)
      )
    })
  })

  const visible = computed(() => matches.value.slice(0, MAX_RESULTS))
  const truncated = computed(() => matches.value.length > visible.value.length)
  const active = computed(
    () => Boolean(query.value.trim()) || Object.values(filters).some((value) => value !== ''),
  )

  function reset() {
    query.value = ''
    Object.keys(filters).forEach((key) => {
      filters[key] = ''
    })
  }

  return { query, filters, matches, visible, truncated, active, reset, MAX_RESULTS }
}
