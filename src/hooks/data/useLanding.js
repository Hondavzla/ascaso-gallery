import landing from '../../data/landing.json'

export function useLanding() {
  return { data: landing, isLoading: false, error: null }
}
