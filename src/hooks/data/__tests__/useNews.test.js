import { describe, it, expect } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useNews, useLatestNews, useNewsItem } from '../useNews'

describe('useNews', () => {
  it('returns news sorted newest-first', () => {
    const { result } = renderHook(() => useNews())
    const dates = result.current.data.map((n) => n.date)
    const sorted = [...dates].sort((a, b) => b.localeCompare(a))
    expect(dates).toEqual(sorted)
  })
})

describe('useLatestNews', () => {
  it('defaults to 3 items', () => {
    const { result } = renderHook(() => useLatestNews())
    expect(result.current.data.length).toBeLessThanOrEqual(3)
  })

  it('respects the limit argument', () => {
    const { result } = renderHook(() => useLatestNews(1))
    expect(result.current.data.length).toBe(1)
  })

  it('returns newest-first', () => {
    const { result } = renderHook(() => useLatestNews(3))
    const dates = result.current.data.map((n) => n.date)
    const sorted = [...dates].sort((a, b) => b.localeCompare(a))
    expect(dates).toEqual(sorted)
  })
})

describe('useNewsItem', () => {
  it('returns the item matching the slug', () => {
    const { result } = renderHook(() =>
      useNewsItem('muestra-colectiva-legado-julio-larraz')
    )
    expect(result.current.data).not.toBeNull()
    expect(result.current.data.title).toContain('Julio Larraz')
  })

  it('returns null for unknown slug', () => {
    const { result } = renderHook(() => useNewsItem('nope'))
    expect(result.current.data).toBeNull()
  })
})
