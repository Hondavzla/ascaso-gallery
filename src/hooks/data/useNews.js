import newsData from '../../data/news/index.json'

// Sort once at module load — dates are ISO strings, newest first.
const sorted = [...newsData].sort((a, b) => b.date.localeCompare(a.date))

export function useNews() {
  return { data: sorted, isLoading: false, error: null }
}

export function useLatestNews(limit = 3) {
  return { data: sorted.slice(0, limit), isLoading: false, error: null }
}

export function useNewsItem(slug) {
  const data = sorted.find((n) => n.slug === slug) ?? null
  return { data, isLoading: false, error: null }
}
