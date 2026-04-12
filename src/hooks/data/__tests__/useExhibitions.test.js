import { describe, it, expect } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useExhibitions,
  useCurrentExhibition,
  useExhibition,
} from '../useExhibitions'

describe('useExhibitions', () => {
  it('returns the full exhibitions array', () => {
    const { result } = renderHook(() => useExhibitions())
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(Array.isArray(result.current.data)).toBe(true)
    expect(result.current.data.length).toBeGreaterThan(0)
  })
})

describe('useCurrentExhibition', () => {
  it('returns the first exhibition with status "current"', () => {
    const { result } = renderHook(() => useCurrentExhibition())
    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).not.toBeNull()
    expect(result.current.data.status).toBe('current')
  })
})

describe('useExhibition(slug)', () => {
  it('returns the exhibition matching the slug', () => {
    const { result } = renderHook(() => useExhibition('forms-in-space'))
    expect(result.current.data).not.toBeNull()
    expect(result.current.data.slug).toBe('forms-in-space')
    expect(result.current.data.title).toBe('Forms in Space')
  })

  it('returns null for an unknown slug', () => {
    const { result } = renderHook(() => useExhibition('does-not-exist'))
    expect(result.current.data).toBeNull()
  })
})
