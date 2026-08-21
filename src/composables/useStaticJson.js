import { ref, shallowRef } from 'vue'

const cache = new Map()

function fetchJson(url) {
  if (!cache.has(url)) {
    cache.set(
      url,
      fetch(url).then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      }),
    )
  }
  return cache.get(url)
}

export function useStaticJson(url) {
  const data = shallowRef(null)
  const error = ref(null)
  const loading = ref(true)

  async function load() {
    loading.value = true
    error.value = null
    try {
      data.value = await fetchJson(url)
    } catch (e) {
      // A rejected promise must not poison the cache for later retries.
      cache.delete(url)
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  load()

  return { data, error, loading, reload: load }
}

export function loadStaticJson(url) {
  return fetchJson(url).catch((e) => {
    cache.delete(url)
    throw e
  })
}
