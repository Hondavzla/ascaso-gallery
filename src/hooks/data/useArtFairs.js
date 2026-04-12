import fairs from '../../data/artFairs/index.json'

const sorted = [...fairs].sort((a, b) => b.endDate.localeCompare(a.endDate))

export function useArtFairs() {
  return { data: sorted, isLoading: false, error: null }
}

export function useLatestArtFair() {
  const data = sorted[0] ?? null
  return { data, isLoading: false, error: null }
}

export function useArtFair(slug) {
  const data = sorted.find((f) => f.slug === slug) ?? null
  return { data, isLoading: false, error: null }
}
