import { useEffect, useState } from 'react'
import artistsIndex from '../../data/artists/index.json'
import landing from '../../data/landing.json'

export function useArtists() {
  return { data: artistsIndex, isLoading: false, error: null }
}

export function useFeaturedArtists() {
  const bySlug = new Map(artistsIndex.map((a) => [a.slug, a]))
  const data = landing.featuredArtistSlugs
    .map((slug) => {
      const artist = bySlug.get(slug)
      if (!artist && import.meta.env.DEV) {
        console.warn(`[useFeaturedArtists] unknown slug in landing.json: "${slug}"`)
      }
      return artist
    })
    .filter(Boolean)
  return { data, isLoading: false, error: null }
}

export function useRelatedArtists(slug) {
  const bySlug = new Map(artistsIndex.map((a) => [a.slug, a]))
  const data = landing.relatedArtistsFallbackSlugs
    .filter((s) => s !== slug)
    .map((s) => bySlug.get(s))
    .filter(Boolean)
  return { data, isLoading: false, error: null }
}

export function useArtist(slug) {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })

  useEffect(() => {
    let cancelled = false
    setState({ data: null, isLoading: true, error: null })

    import(`../../data/artists/${slug}.json`)
      .then((mod) => {
        if (cancelled) return
        const detail = mod.default
        if (import.meta.env.DEV) {
          const summary = artistsIndex.find((a) => a.slug === slug)
          if (summary) {
            if (summary.name !== detail.name || summary.medium !== detail.medium) {
              console.warn(
                `[useArtist] summary/detail mismatch for "${slug}":`,
                { summary, detail }
              )
            }
          }
        }
        setState({ data: detail, isLoading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        setState({ data: null, isLoading: false, error: err })
      })

    return () => {
      cancelled = true
    }
  }, [slug])

  return state
}
