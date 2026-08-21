import { computed } from 'vue'
import { useStaticJson } from '@/composables/useStaticJson'
import { dataUrl } from '../lib/dataPaths'

export function useCardCatalog() {
  const { data, error, loading } = useStaticJson(dataUrl('cards.json'))

  const cards = computed(() => data.value?.cards ?? [])
  const byCode = computed(() => new Map(cards.value.map((card) => [card.code, card])))

  const sets = computed(() => uniqueBy(cards.value, (card) => [card.set, card.set_name]))
  const rarities = computed(() => uniqueValues(cards.value.map((card) => card.rarity)))
  const types = computed(() => uniqueValues(cards.value.map((card) => card.type)))
  const domains = computed(() => uniqueValues(cards.value.flatMap((card) => card.domains)))

  return { cards, byCode, sets, rarities, types, domains, error, loading }
}

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))].sort()
}

function uniqueBy(cards, pick) {
  const seen = new Map()
  for (const card of cards) {
    const [value, label] = pick(card)
    if (value && !seen.has(value)) seen.set(value, label ?? value)
  }
  return [...seen].map(([value, label]) => ({ value, label })).sort((a, b) => a.label.localeCompare(b.label))
}
