import exhibitions from '../../data/exhibitions/index.json'

export function useExhibitions() {
  return { data: exhibitions, isLoading: false, error: null }
}

export function useCurrentExhibition() {
  const data = exhibitions.find((e) => e.status === 'current') ?? null
  return { data, isLoading: false, error: null }
}

export function useExhibition(slug) {
  const data = exhibitions.find((e) => e.slug === slug) ?? null
  return { data, isLoading: false, error: null }
}
