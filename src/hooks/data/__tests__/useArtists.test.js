import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import {
  useArtists,
  useFeaturedArtists,
  useArtist,
  useRelatedArtists,
} from '../useArtists'

describe('useArtists', () => {
  it('returns the full summary list', () => {
    const { result } = renderHook(() => useArtists())
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.data.length).toBeGreaterThanOrEqual(5)
  })

  it('every record has a slug, name, medium, image, and hasDetailPage flag', () => {
    const { result } = renderHook(() => useArtists())
    for (const artist of result.current.data) {
      expect(artist.slug).toBeTypeOf('string')
      expect(artist.name).toBeTypeOf('string')
      expect(artist.medium).toBeTypeOf('string')
      expect(artist.image).toBeTypeOf('string')
      expect(typeof artist.hasDetailPage).toBe('boolean')
    }
  })
})

describe('useFeaturedArtists', () => {
  it('returns artists in manifest order', () => {
    const { result } = renderHook(() => useFeaturedArtists())
    const slugs = result.current.data.map((a) => a.slug)
    expect(slugs).toEqual([
      'javier-martin',
      'julio-larraz',
      'carlos-cruz-diez',
      'carlos-medina',
      'alirio-palacios',
    ])
  })
})

describe('useRelatedArtists', () => {
  it('returns fallback artists excluding the given slug', () => {
    const { result } = renderHook(() => useRelatedArtists('carlos-medina'))
    const slugs = result.current.data.map((a) => a.slug)
    expect(slugs).not.toContain('carlos-medina')
    expect(slugs.length).toBeGreaterThan(0)
  })
})

describe('useArtist(slug)', () => {
  it('starts in loading state', () => {
    const { result } = renderHook(() => useArtist('carlos-medina'))
    expect(result.current.isLoading).toBe(true)
    expect(result.current.data).toBeNull()
  })

  it('resolves to the detail record', async () => {
    const { result } = renderHook(() => useArtist('carlos-medina'))
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).not.toBeNull()
    expect(result.current.data.slug).toBe('carlos-medina')
    expect(result.current.data.name).toBe('Carlos Medina')
    expect(Array.isArray(result.current.data.works)).toBe(true)
  })

  it('resolves to null with error for unknown slug', async () => {
    const { result } = renderHook(() => useArtist('does-not-exist'))
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toBeNull()
    expect(result.current.error).not.toBeNull()
  })
})
