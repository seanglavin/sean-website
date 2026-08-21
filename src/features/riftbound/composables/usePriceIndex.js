import { computed, ref, shallowRef } from 'vue'
import { loadStaticJson } from '@/composables/useStaticJson'
import { MANIFEST_URL, dataUrl } from '../lib/dataPaths'

export function usePriceIndex() {
  const manifest = shallowRef(null)
  const sources = shallowRef([])
  const error = ref(null)
  const loading = ref(true)

  async function load() {
    loading.value = true
    error.value = null
    try {
      const loaded = await loadStaticJson(MANIFEST_URL)
      manifest.value = loaded
      // The manifest is the only place retailers are named; a retailer whose
      // last scrape failed has no usable file and is skipped, not fatal.
      const usable = (loaded.retailers ?? []).filter((entry) => entry.file)
      sources.value = await Promise.all(
        usable.map(async (entry) => ({
          retailer: entry,
          data: await loadStaticJson(dataUrl(entry.file)).catch(() => null),
        })),
      )
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  load()

  const retailers = computed(() => manifest.value?.retailers ?? [])
  const generatedAt = computed(() => manifest.value?.generated_at ?? null)

  function offersFor(code) {
    const rows = []
    for (const { retailer, data } of sources.value) {
      const printings = data?.cards?.[code]
      if (!printings) continue
      for (const printing of printings) {
        for (const [condition, grade, cents, available] of printing.offers) {
          rows.push({
            key: `${retailer.id}-${printing.handle}-${condition}`,
            retailerId: retailer.id,
            retailerName: retailer.name,
            finish: printing.finish,
            condition,
            grade,
            priceCents: cents,
            available,
            url: data.product_url_template.replace('{handle}', printing.handle),
          })
        }
      }
    }
    rows.sort(
      (a, b) =>
        Number(b.available) - Number(a.available) ||
        a.grade - b.grade ||
        a.priceCents - b.priceCents,
    )
    return rows
  }

  function cheapestFor(code, { availableOnly = true } = {}) {
    const rows = offersFor(code).filter((row) => (availableOnly ? row.available : true))
    return rows.length ? rows.reduce((best, row) => (row.priceCents < best.priceCents ? row : best)) : null
  }

  function coveredCodes() {
    const codes = new Set()
    for (const { data } of sources.value) {
      for (const code of Object.keys(data?.cards ?? {})) codes.add(code)
    }
    return codes
  }

  return { retailers, generatedAt, offersFor, cheapestFor, coveredCodes, error, loading, reload: load }
}
