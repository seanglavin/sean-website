const BASE = `${import.meta.env.BASE_URL}riftbound-data/`

export const MANIFEST_URL = `${BASE}manifest.json`

export function dataUrl(file) {
  return BASE + file
}
