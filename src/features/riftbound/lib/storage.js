const NAMESPACE = 'riftbound:v1:'
const SCHEMA_VERSION = 1

// Storage access itself throws in private-browsing and thumbnail contexts, so
// every read and write degrades to an in-memory value rather than propagating.
function backend() {
  try {
    return window.localStorage
  } catch {
    return null
  }
}

export function isAvailable() {
  const store = backend()
  if (!store) return false
  try {
    const canary = `${NAMESPACE}__probe`
    store.setItem(canary, '1')
    store.removeItem(canary)
    return true
  } catch {
    return false
  }
}

export function read(key, fallback) {
  const store = backend()
  if (!store) return fallback
  try {
    const raw = store.getItem(NAMESPACE + key)
    if (!raw) return fallback
    const parsed = JSON.parse(raw)
    if (parsed?.schema_version !== SCHEMA_VERSION) return fallback
    return parsed.value ?? fallback
  } catch {
    return fallback
  }
}

export function write(key, value) {
  const store = backend()
  if (!store) return false
  try {
    store.setItem(NAMESPACE + key, JSON.stringify({ schema_version: SCHEMA_VERSION, value }))
    return true
  } catch {
    return false
  }
}

export function exportPayload(key, value) {
  return {
    schema_version: SCHEMA_VERSION,
    exported_at: new Date().toISOString(),
    key,
    value,
  }
}

export function parseImport(text, key) {
  const parsed = JSON.parse(text)
  if (parsed?.schema_version !== SCHEMA_VERSION) {
    throw new Error(`Unsupported file version ${parsed?.schema_version ?? 'unknown'}`)
  }
  if (parsed.key !== key) {
    throw new Error(`This file holds "${parsed.key}", not "${key}"`)
  }
  return parsed.value
}

export function downloadJson(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}
