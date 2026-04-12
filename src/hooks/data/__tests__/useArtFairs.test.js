import { describe, it, expect } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useArtFairs, useLatestArtFair, useArtFair } from '../useArtFairs'

describe('useArtFairs', () => {
  it('returns the full list', () => {
    const { result } = renderHook(() => useArtFairs())
    expect(result.current.data.length).toBeGreaterThan(0)
  })
})

describe('useLatestArtFair', () => {
  it('returns the fair with the most recent endDate', () => {
    const { result } = renderHook(() => useLatestArtFair())
    expect(result.current.data).not.toBeNull()
    expect(result.current.data.slug).toBe('art-miami-2025')
  })
})

describe('useArtFair(slug)', () => {
  it('returns the fair matching the slug', () => {
    const { result } = renderHook(() => useArtFair('art-miami-2025'))
    expect(result.current.data).not.toBeNull()
    expect(result.current.data.name).toBe('Art Miami 2025')
  })

  it('returns null for unknown slug', () => {
    const { result } = renderHook(() => useArtFair('nope'))
    expect(result.current.data).toBeNull()
  })
})
