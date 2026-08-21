const formatter = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' })

export function formatCents(cents) {
  if (cents == null) return '—'
  return formatter.format(cents / 100)
}

export function relativeDays(isoDate) {
  if (!isoDate) return 'unknown'
  const days = Math.floor((Date.now() - new Date(isoDate).getTime()) / 86_400_000)
  if (Number.isNaN(days)) return 'unknown'
  if (days <= 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days} days ago`
}
