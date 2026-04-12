# Data-Driven Frontend Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move all hardcoded content (exhibitions, artists, news, art fairs, Carlos Medina detail) out of JSX into `src/data/*.json` files read through custom hooks in `src/hooks/data/`, so phase 2 can swap the hooks to a Flask API with zero component changes.

**Architecture:** Each content resource lives in `src/data/<resource>/` as JSON that matches the eventual REST payload shape. Components import `{useExhibitions, useFeaturedArtists, useLatestNews, useLatestArtFair, useArtist, useRelatedArtists}` from a barrel `src/hooks/data/index.js`. Every hook returns `{ data, isLoading, error }`. Homepage curation is hybrid: exhibitions use a `status` field, featured artists use a `landing.json` manifest, news sorts by date.

**Tech Stack:** React 19 + Vite + React Router 7. Vitest + @testing-library/react added for hook unit tests only (components remain untested — animation-heavy, low value).

**Spec:** `docs/superpowers/specs/2026-04-12-data-driven-refactor-design.md`

---

## File Structure

**Created files:**

```
src/
├── data/
│   ├── landing.json
│   ├── exhibitions/
│   │   └── index.json
│   ├── artists/
│   │   ├── index.json
│   │   └── carlos-medina.json
│   ├── news/
│   │   └── index.json
│   └── artFairs/
│       └── index.json
├── hooks/
│   └── data/
│       ├── index.js
│       ├── useExhibitions.js
│       ├── useArtists.js
│       ├── useNews.js
│       ├── useArtFairs.js
│       ├── useLanding.js
│       └── __tests__/
│           ├── useExhibitions.test.js
│           ├── useArtists.test.js
│           ├── useNews.test.js
│           └── useArtFairs.test.js
├── utils/
│   └── formatDate.js
├── components/
│   └── ArtistDetailSkeleton.jsx
└── pages/
    └── ArtistDetail.jsx   (replaces CarlosMedina.jsx)
```

**Modified files:**

- `src/App.jsx` — route `/artists/carlos-medina` → `/artists/:slug`
- `src/sections/Exhibition.jsx` — bindings
- `src/sections/Artists.jsx` — bindings + empty-array guard
- `src/sections/News.jsx` — bindings + formatter + empty-array guard
- `src/sections/ArtFair.jsx` — bindings
- `package.json` — add vitest + testing libs, add `test` script
- `vite.config.js` — add vitest config

**Deleted files:**

- `src/pages/CarlosMedina.jsx` — replaced by `src/pages/ArtistDetail.jsx`

---

## Task 1: Install testing infrastructure

**Files:**
- Modify: `package.json`
- Modify: `vite.config.js`
- Create: `src/test/setup.js`

- [ ] **Step 1: Install vitest + testing libraries**

Run:
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom jsdom
```

Expected: packages added to `devDependencies`; no errors.

- [ ] **Step 2: Add `test` script to package.json**

Edit `package.json` scripts block to add a `test` entry:
```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "lint": "eslint .",
  "preview": "vite preview",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- [ ] **Step 3: Read current vite.config.js to see its shape**

Run: `cat vite.config.js` (use Read tool, not cat).

Note: most Vite projects have a minimal config; we need to add a `test` block and change the default export to include it. If the file uses `defineConfig`, add the test block inside.

- [ ] **Step 4: Add vitest config to vite.config.js**

Inside the `defineConfig({...})` call, add:
```js
test: {
  environment: 'jsdom',
  globals: true,
  setupFiles: ['./src/test/setup.js'],
},
```

If the existing config does not use `defineConfig`, wrap it:
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
  },
})
```

- [ ] **Step 5: Create test setup file**

Create `src/test/setup.js`:
```js
import '@testing-library/jest-dom/vitest'
```

- [ ] **Step 6: Write a smoke test to prove the harness works**

Create `src/test/smoke.test.js`:
```js
import { describe, it, expect } from 'vitest'

describe('test harness', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2)
  })
})
```

- [ ] **Step 7: Run the smoke test**

Run: `npm test`
Expected: 1 test passes. If jsdom or vitest errors appear, resolve before moving on.

- [ ] **Step 8: Delete the smoke test**

Run: `rm src/test/smoke.test.js`

- [ ] **Step 9: Commit**

```bash
git add package.json package-lock.json vite.config.js src/test/setup.js
git commit -m "chore: add vitest + testing-library harness for hook tests"
```

---

## Task 2: Create exhibitions data and hook (TDD)

**Files:**
- Create: `src/data/exhibitions/index.json`
- Create: `src/hooks/data/useExhibitions.js`
- Create: `src/hooks/data/__tests__/useExhibitions.test.js`

- [ ] **Step 1: Create exhibitions data file**

Create `src/data/exhibitions/index.json`:
```json
[
  {
    "slug": "forms-in-space",
    "title": "Forms in Space",
    "subtitle": "Contemporary Sculpture & Painting",
    "status": "current",
    "startDate": "2025-12-04",
    "endDate": "2026-02-09",
    "dateLabel": "December 4 – February 9",
    "image": "/images/exhibition-forms-in-space.jpeg",
    "eyebrow": "On View"
  }
]
```

- [ ] **Step 2: Write the failing tests**

Create `src/hooks/data/__tests__/useExhibitions.test.js`:
```js
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
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `npm test -- useExhibitions`
Expected: FAIL — `Failed to resolve import '../useExhibitions'` (the hook file does not exist yet).

- [ ] **Step 4: Implement useExhibitions**

Create `src/hooks/data/useExhibitions.js`:
```js
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
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `npm test -- useExhibitions`
Expected: all 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/data/exhibitions/ src/hooks/data/useExhibitions.js src/hooks/data/__tests__/useExhibitions.test.js
git commit -m "feat(data): useExhibitions hook + JSON data file"
```

---

## Task 3: Create artists summary data and landing manifest

**Files:**
- Create: `src/data/artists/index.json`
- Create: `src/data/landing.json`

No tests in this task — data files only. The hook tests in Task 4 will exercise this data.

- [ ] **Step 1: Create artists summary data**

Create `src/data/artists/index.json`:
```json
[
  {
    "slug": "javier-martin",
    "name": "Javier Martin",
    "medium": "Painting",
    "image": "/images/artist-javier-martin.jpg",
    "hasDetailPage": false
  },
  {
    "slug": "julio-larraz",
    "name": "Julio Larraz",
    "medium": "Painting",
    "image": "/images/artist-julio-larraz.png",
    "hasDetailPage": false
  },
  {
    "slug": "carlos-cruz-diez",
    "name": "Carlos Cruz-Diez",
    "medium": "Kinetic Art",
    "image": "/images/artist-carlos-cruz-diez.jpg",
    "hasDetailPage": false
  },
  {
    "slug": "carlos-medina",
    "name": "Carlos Medina",
    "medium": "Sculpture",
    "image": "/images/artist-carlos-medina.jpg",
    "hasDetailPage": true
  },
  {
    "slug": "alirio-palacios",
    "name": "Alirio Palacios",
    "medium": "Painting",
    "image": "/images/artist-alirio-palacios.jpg",
    "hasDetailPage": false
  }
]
```

- [ ] **Step 2: Create landing manifest**

Create `src/data/landing.json`:
```json
{
  "featuredArtistSlugs": [
    "javier-martin",
    "julio-larraz",
    "carlos-cruz-diez",
    "carlos-medina",
    "alirio-palacios"
  ],
  "relatedArtistsFallbackSlugs": [
    "javier-martin",
    "julio-larraz",
    "carlos-cruz-diez",
    "alirio-palacios"
  ]
}
```

- [ ] **Step 3: Commit**

```bash
git add src/data/artists/index.json src/data/landing.json
git commit -m "feat(data): artist summary list + landing manifest"
```

---

## Task 4: Create Carlos Medina detail data

**Files:**
- Create: `src/data/artists/carlos-medina.json`

- [ ] **Step 1: Create detail record**

Create `src/data/artists/carlos-medina.json`. Copy content **verbatim** from `src/pages/CarlosMedina.jsx` to guarantee the refactor is pixel-identical:

```json
{
  "slug": "carlos-medina",
  "name": "Carlos Medina",
  "medium": "Sculpture",
  "heroImage": "/images/artist-carlos-medina.jpg",
  "eyebrow": "Sculpture",
  "bio": {
    "short": "Venezuelan artist (1953). Currently lives and works in Paris. Always focused on geometric abstraction, going from volumetric to spatial concerns, in the last two decades he has focused his interest in exploring spatial proposals that abandon the support as an element of the work. His work is consolidated in the essential and imperceptible interpretation of universe and nature, a leading concept in his work.",
    "full": [
      "Venezuelan artist (1953). Currently lives and works in Paris. Always focused on geometric abstraction, going from volumetric to spatial concerns, in the last two decades he has focused his interest in exploring spatial proposals that abandon the support as an element of the work. His work is consolidated in the essential and imperceptible interpretation of universe and nature, a leading concept in his work.",
      "Studied at the Escuela de Artes Plásticas Cristóbal Rojas, Caracas. Continued studies at the Centro de Enseñanza Gráfica (CEGRA), Caracas. Attended workshops in sculpture and spatial arts in Paris."
    ]
  },
  "quote": {
    "text": "El espacio es el material con el que trabajo, la escultura es solo su consecuencia.",
    "attribution": "Carlos Medina",
    "eyebrow": "El Artista"
  },
  "works": [
    {
      "slug": "circulo-total",
      "title": "Círculo Total",
      "image": "/images/carlos-medina-work-1.jpg"
    },
    {
      "slug": "hoja-cuenca",
      "title": "Hoja Cuenca",
      "image": "/images/carlos-medina-work-2.jpg"
    },
    {
      "slug": "fragmentos-de-neutrinos-2016",
      "title": "Fragmentos de Neutrinos 2016",
      "image": "/images/carlos-medina-work-3.jpg"
    }
  ],
  "exhibitions": [
    {
      "year": 2024,
      "items": [
        "Ascaso Gallery, Miami — Solo Exhibition",
        "Art Miami — Booth AM125"
      ]
    },
    {
      "year": 2023,
      "items": [
        "Galerie Mitterrand, Paris — Group Exhibition",
        "ARCO Madrid — Ascaso Gallery Booth"
      ]
    },
    {
      "year": 2022,
      "items": [
        "Museo de Arte Contemporáneo de Caracas — Retrospective",
        "Art Basel Miami Beach — Ascaso Gallery"
      ]
    },
    {
      "year": 2021,
      "items": [
        "Ascaso Gallery, Caracas — \"Spatial Proposals\""
      ]
    },
    {
      "year": 2019,
      "items": [
        "Biennale de Lyon — Selected Artist",
        "Museo Nacional de Bellas Artes, Caracas"
      ]
    },
    {
      "year": 2017,
      "items": [
        "Galería de Arte Nacional, Caracas — Solo Exhibition",
        "Pinta Miami — Ascaso Gallery"
      ]
    }
  ],
  "monumentalWorks": [
    {
      "year": 2023,
      "items": ["Escultura Monumental, Brickell City Centre, Miami"]
    },
    {
      "year": 2020,
      "items": ["Intervención Espacial, Parque del Este, Caracas"]
    },
    {
      "year": 2016,
      "items": ["Fragmentos de Neutrinos, Parc de la Villette, Paris"]
    },
    {
      "year": 2012,
      "items": ["Escultura Pública, Universidad Central de Venezuela, Caracas"]
    }
  ],
  "awards": [
    "Premio Nacional de Artes Plásticas, Venezuela",
    "Premio Salón Michelena, Valencia, Venezuela",
    "Mención Honorífica, Salón Arturo Michelena",
    "Beca Fundación Gran Mariscal de Ayacucho, Paris"
  ],
  "collections": [
    "Museo de Arte Contemporáneo de Caracas",
    "Galería de Arte Nacional, Caracas",
    "Museo de Bellas Artes, Caracas",
    "Fundación Cisneros, Caracas",
    "Colección Patricia Phelps de Cisneros, New York",
    "Museo de Arte Moderno Jesús Soto, Ciudad Bolívar",
    "Private collections in USA, Europe, and Latin America"
  ]
}
```

- [ ] **Step 2: Sanity-check the JSON parses**

Run: `node -e "console.log(Object.keys(require('./src/data/artists/carlos-medina.json')))"`
Expected: prints an array of top-level keys (`slug, name, medium, heroImage, eyebrow, bio, quote, works, exhibitions, monumentalWorks, awards, collections`). If it errors, fix the JSON.

- [ ] **Step 3: Commit**

```bash
git add src/data/artists/carlos-medina.json
git commit -m "feat(data): Carlos Medina detail record"
```

---

## Task 5: Create useLanding internal helper hook

**Files:**
- Create: `src/hooks/data/useLanding.js`

No tests for this file — it is tested transitively by `useArtists.test.js` in Task 6 through `useFeaturedArtists`.

- [ ] **Step 1: Create useLanding**

Create `src/hooks/data/useLanding.js`:
```js
import landing from '../../data/landing.json'

export function useLanding() {
  return { data: landing, isLoading: false, error: null }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/hooks/data/useLanding.js
git commit -m "feat(data): useLanding internal manifest helper"
```

---

## Task 6: Create useArtists hook (TDD)

**Files:**
- Create: `src/hooks/data/useArtists.js`
- Create: `src/hooks/data/__tests__/useArtists.test.js`

- [ ] **Step 1: Write failing tests for synchronous hooks**

Create `src/hooks/data/__tests__/useArtists.test.js`:
```js
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
```

- [ ] **Step 2: Run tests to verify failure**

Run: `npm test -- useArtists`
Expected: FAIL — `Failed to resolve import '../useArtists'`.

- [ ] **Step 3: Implement useArtists**

Create `src/hooks/data/useArtists.js`:
```js
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm test -- useArtists`
Expected: all tests pass. The `useArtist` loading-state test must see `isLoading: true` on initial render (before the dynamic import resolves), then flip to `false` after `waitFor`.

- [ ] **Step 5: Commit**

```bash
git add src/hooks/data/useArtists.js src/hooks/data/__tests__/useArtists.test.js
git commit -m "feat(data): useArtists family of hooks (summary, featured, detail, related)"
```

---

## Task 7: Create news data and hook (TDD)

**Files:**
- Create: `src/data/news/index.json`
- Create: `src/hooks/data/useNews.js`
- Create: `src/hooks/data/__tests__/useNews.test.js`

- [ ] **Step 1: Create news data**

Create `src/data/news/index.json`:
```json
[
  {
    "slug": "muestra-colectiva-legado-julio-larraz",
    "date": "2025-10-15",
    "title": "Muestra colectiva en Miami honra el legado de Julio Larraz",
    "excerpt": "Collective Exhibition in Miami Honors the Legacy of Julio Larraz. Ascaso Gallery presents Reciprocity, a living tribute.",
    "image": "/images/news-1.jpg",
    "url": "#",
    "source": null
  },
  {
    "slug": "reciprocity-bridges-generation-gap",
    "date": "2025-10-01",
    "title": "Reciprocity at Ascaso Gallery Bridges Generation Gap",
    "excerpt": "Artist Julio Larraz Exhibits Alongside Emerging Artists in Miami.",
    "image": "/images/news-2.jpg",
    "url": "#",
    "source": null
  },
  {
    "slug": "reciprocity-next-generation-artistic-freedom",
    "date": "2025-10-01",
    "title": "Reciprocity: Julio Larraz and the Next Generation of Artistic Freedom",
    "excerpt": "Julio Larraz and the Next Generation of Artistic Freedom. Source: ArtDaily.",
    "image": "/images/news-3.jpg",
    "url": "#",
    "source": "ArtDaily"
  }
]
```

- [ ] **Step 2: Write failing tests**

Create `src/hooks/data/__tests__/useNews.test.js`:
```js
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
```

- [ ] **Step 3: Run tests to verify failure**

Run: `npm test -- useNews`
Expected: FAIL — `Failed to resolve import '../useNews'`.

- [ ] **Step 4: Implement useNews**

Create `src/hooks/data/useNews.js`:
```js
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `npm test -- useNews`
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/data/news/ src/hooks/data/useNews.js src/hooks/data/__tests__/useNews.test.js
git commit -m "feat(data): useNews hooks + news JSON data file"
```

---

## Task 8: Create art fairs data and hook (TDD)

**Files:**
- Create: `src/data/artFairs/index.json`
- Create: `src/hooks/data/useArtFairs.js`
- Create: `src/hooks/data/__tests__/useArtFairs.test.js`

- [ ] **Step 1: Create art fairs data**

Create `src/data/artFairs/index.json`:
```json
[
  {
    "slug": "art-miami-2025",
    "name": "Art Miami 2025",
    "startDate": "2025-12-02",
    "endDate": "2025-12-07",
    "dateLabel": "December 2 – December 7, 2025",
    "booth": "AM125",
    "description": "Ascaso Gallery at Art Miami 2025 – Booth AM125, with works by Pablo Atchugarry, Fernando Botero, Carlos Cruz-Diez, Olga de Amaral, Jiménez Deredia, Julio Larraz.",
    "image": "/images/art-fair-miami.jpg",
    "eyebrow": "Last Art Fair"
  }
]
```

- [ ] **Step 2: Write failing tests**

Create `src/hooks/data/__tests__/useArtFairs.test.js`:
```js
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
```

- [ ] **Step 3: Run tests to verify failure**

Run: `npm test -- useArtFairs`
Expected: FAIL — `Failed to resolve import '../useArtFairs'`.

- [ ] **Step 4: Implement useArtFairs**

Create `src/hooks/data/useArtFairs.js`:
```js
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `npm test -- useArtFairs`
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/data/artFairs/ src/hooks/data/useArtFairs.js src/hooks/data/__tests__/useArtFairs.test.js
git commit -m "feat(data): useArtFairs hooks + art fairs JSON data file"
```

---

## Task 9: Create barrel export and run full test suite

**Files:**
- Create: `src/hooks/data/index.js`

- [ ] **Step 1: Create the barrel**

Create `src/hooks/data/index.js`:
```js
export { useExhibitions, useCurrentExhibition, useExhibition } from './useExhibitions'
export { useArtists, useFeaturedArtists, useArtist, useRelatedArtists } from './useArtists'
export { useNews, useLatestNews, useNewsItem } from './useNews'
export { useArtFairs, useLatestArtFair, useArtFair } from './useArtFairs'
```

Note: `useLanding` is intentionally NOT exported — it is an internal helper.

- [ ] **Step 2: Run the full test suite**

Run: `npm test`
Expected: all tests from Tasks 2, 6, 7, 8 pass. No test file failures.

- [ ] **Step 3: Run the build to verify imports resolve**

Run: `npm run build`
Expected: successful build with no errors. (The hooks are unused by components at this point, but they must still type-check and bundle.)

- [ ] **Step 4: Commit**

```bash
git add src/hooks/data/index.js
git commit -m "feat(data): barrel export for data hooks"
```

---

## Task 10: Create date formatter utility

**Files:**
- Create: `src/utils/formatDate.js`

- [ ] **Step 1: Create formatter**

Create `src/utils/formatDate.js`:
```js
export function formatNewsDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
```

- [ ] **Step 2: Commit**

```bash
git add src/utils/formatDate.js
git commit -m "feat(utils): formatNewsDate helper"
```

---

## Task 11: Refactor Exhibition.jsx

**Files:**
- Modify: `src/sections/Exhibition.jsx`

- [ ] **Step 1: Read the current file**

Run: (use Read tool on `src/sections/Exhibition.jsx`)

- [ ] **Step 2: Add the hook import and binding**

At the top of the file, add:
```js
import { useCurrentExhibition } from '../hooks/data'
```

Inside `export default function Exhibition()`, before the `useEffect`, add:
```js
const { data: exhibition, isLoading } = useCurrentExhibition()
```

- [ ] **Step 3: Add the empty-state guard**

After the `useEffect` hook (or before, doesn't matter — React rules: after all hook calls), add:
```js
if (isLoading || !exhibition) return null
```

Important: this return MUST come after all `useEffect`/`useRef` calls to respect React's rules of hooks. Place it immediately before the `return (` JSX line.

- [ ] **Step 4: Replace hardcoded strings with bindings**

In the JSX, replace:

| Current text | Replacement |
|---|---|
| `On View` (inside the eyebrow `<p>`) | `{exhibition.eyebrow}` |
| `Forms in Space` (inside the `<h2>`) | `{exhibition.title}` |
| `Contemporary Sculpture &amp; Painting` | `{exhibition.subtitle}` |
| `December 4 – February 9` | `{exhibition.dateLabel}` |
| `src="/images/exhibition-forms-in-space.jpeg"` | `src={exhibition.image}` |
| `alt="Forms in Space — Contemporary Sculpture & Painting"` | `alt={`${exhibition.title} — ${exhibition.subtitle}`}` |

Leave everything else (button text "See Exhibition", styles, GSAP, layout) untouched.

- [ ] **Step 5: Run the dev server and verify the exhibition section renders identically**

Run: `npm run dev`
Open: `http://localhost:5173`
Expected: the Exhibition section renders visually identical to before (title "Forms in Space", subtitle, dates, image). Stop the dev server when done.

- [ ] **Step 6: Run build to verify no errors**

Run: `npm run build`
Expected: successful.

- [ ] **Step 7: Commit**

```bash
git add src/sections/Exhibition.jsx
git commit -m "refactor(exhibition): bind to useCurrentExhibition hook"
```

---

## Task 12: Refactor Artists.jsx

**Files:**
- Modify: `src/sections/Artists.jsx`

- [ ] **Step 1: Read the current file**

- [ ] **Step 2: Add hook import**

Add at the top:
```js
import { useFeaturedArtists } from '../hooks/data'
```

- [ ] **Step 3: Delete the hardcoded `artists` array**

Delete these lines near the top of the file:
```js
const artists = [
  { name: 'Javier Martin', medium: 'Painting', image: '/images/artist-javier-martin.jpg' },
  { name: 'Julio Larraz', medium: 'Painting', image: '/images/artist-julio-larraz.png' },
  { name: 'Carlos Cruz-Diez', medium: 'Kinetic Art', image: '/images/artist-carlos-cruz-diez.jpg' },
  { name: 'Carlos Medina', medium: 'Sculpture', image: '/images/artist-carlos-medina.jpg', slug: 'carlos-medina' },
  { name: 'Alirio Palacios', medium: 'Painting', image: '/images/artist-alirio-palacios.jpg' },
]
```

- [ ] **Step 4: Fetch from hook inside the component**

Inside `export default function Artists()`, as the first line:
```js
const { data: artists } = useFeaturedArtists()
```

- [ ] **Step 5: Update ArtistCard clickability check**

In `ArtistCard`, change:
```js
if (!artist.slug) return
```
to:
```js
if (!artist.hasDetailPage) return
```

And change:
```js
cursor: artist.slug ? 'pointer' : 'default',
border: artist.slug
  ? `1px solid ${hovered ? '#C9A84C' : 'transparent'}`
  : '1px solid transparent',
```
to:
```js
cursor: artist.hasDetailPage ? 'pointer' : 'default',
border: artist.hasDetailPage
  ? `1px solid ${hovered ? '#C9A84C' : 'transparent'}`
  : '1px solid transparent',
```

- [ ] **Step 6: Guard the GSAP effect against empty array**

In the `useEffect` that sets up ScrollTrigger, add an early return and a dependency:

```js
useEffect(() => {
  if (!artists.length) return
  const track = trackRef.current
  const totalWidth = artists.length * CARD_WIDTH + (artists.length - 1) * CARD_GAP
  // ... rest of the effect unchanged
}, [artists.length])
```

The dependency on `artists.length` ensures the effect re-runs once data arrives (matters for phase 2; harmless in phase 1 since data is synchronous).

- [ ] **Step 7: Dev server smoke test**

Run: `npm run dev`
Open: `http://localhost:5173`
Expected: Artists section renders all 5 cards in order: Javier Martin, Julio Larraz, Carlos Cruz-Diez, Carlos Medina, Alirio Palacios. Horizontal scroll animation works. Clicking Carlos Medina's card navigates to `/artists/carlos-medina`. Other cards are not clickable.

- [ ] **Step 8: Run build**

Run: `npm run build`
Expected: successful.

- [ ] **Step 9: Commit**

```bash
git add src/sections/Artists.jsx
git commit -m "refactor(artists): bind to useFeaturedArtists hook"
```

---

## Task 13: Refactor News.jsx

**Files:**
- Modify: `src/sections/News.jsx`

- [ ] **Step 1: Read the current file**

- [ ] **Step 2: Add imports**

At the top:
```js
import { useLatestNews } from '../hooks/data'
import { formatNewsDate } from '../utils/formatDate'
```

- [ ] **Step 3: Delete the hardcoded `news` array**

Delete the `const news = [ ... ]` block at the top of the file.

- [ ] **Step 4: Fetch from hook inside the component**

Inside `export default function News()`, as the first line:
```js
const { data: news } = useLatestNews(3)
```

- [ ] **Step 5: Replace the date binding with the formatter**

Change:
```jsx
{item.date}
```
to:
```jsx
{formatNewsDate(item.date)}
```

- [ ] **Step 6: Use slug as key instead of title**

Change:
```jsx
<article
  key={item.title}
  data-animate="news-card"
```
to:
```jsx
<article
  key={item.slug}
  data-animate="news-card"
```

- [ ] **Step 7: Guard the GSAP effect**

In the `useEffect`, add:
```js
useEffect(() => {
  if (!news.length) return
  // ... rest of the effect unchanged
}, [news.length])
```

- [ ] **Step 8: Dev server smoke test**

Run: `npm run dev`
Open: `http://localhost:5173`
Expected: News section renders 3 cards with dates displayed as "October 15, 2025", "October 1, 2025", "October 1, 2025" (the format from the current design is preserved because `formatNewsDate` produces the same output). Titles and excerpts match the originals.

- [ ] **Step 9: Build**

Run: `npm run build`
Expected: successful.

- [ ] **Step 10: Commit**

```bash
git add src/sections/News.jsx
git commit -m "refactor(news): bind to useLatestNews hook + date formatter"
```

---

## Task 14: Refactor ArtFair.jsx

**Files:**
- Modify: `src/sections/ArtFair.jsx`

- [ ] **Step 1: Read the current file**

- [ ] **Step 2: Add hook import**

At the top:
```js
import { useLatestArtFair } from '../hooks/data'
```

- [ ] **Step 3: Fetch from hook and guard**

Inside `export default function ArtFair()`, as the first lines:
```js
const { data: fair, isLoading } = useLatestArtFair()
```

After all `useEffect`/`useRef` calls and before the `return (` JSX line, add:
```js
if (isLoading || !fair) return null
```

- [ ] **Step 4: Replace hardcoded strings**

| Current text | Replacement |
|---|---|
| `src="/images/art-fair-miami.jpg"` | `src={fair.image}` |
| `alt="Art Miami 2025"` | `alt={fair.name}` |
| `Booth AM125` (hover overlay eyebrow) | `{`Booth ${fair.booth}`}` |
| `Art Miami 2025` (hover overlay heading) | `{fair.name}` |
| `December 2 – 7, 2025` (hover overlay subtext) | `{fair.dateLabel}` |
| `Last Art Fair` (right-column eyebrow) | `{fair.eyebrow}` |
| `Art Miami 2025` (right-column `<h2>`) | `{fair.name}` |
| `December 2 – December 7, 2025` (right-column date) | `{fair.dateLabel}` |
| The long description paragraph starting `"Ascaso Gallery at Art Miami 2025..."` | `{fair.description}` |

Leave the button text "See Details" and all styles/animations untouched.

- [ ] **Step 5: Dev server smoke test**

Run: `npm run dev`
Open: `http://localhost:5173`
Expected: Art Fair section renders with "Art Miami 2025" title, dates, description, booth info on hover. Tilt and overlay animations work identically.

- [ ] **Step 6: Build**

Run: `npm run build`
Expected: successful.

- [ ] **Step 7: Commit**

```bash
git add src/sections/ArtFair.jsx
git commit -m "refactor(art-fair): bind to useLatestArtFair hook"
```

---

## Task 15: Create ArtistDetailSkeleton component

**Files:**
- Create: `src/components/ArtistDetailSkeleton.jsx`

- [ ] **Step 1: Create the skeleton**

Create `src/components/ArtistDetailSkeleton.jsx`:
```jsx
export default function ArtistDetailSkeleton() {
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0D0D0D',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        width: '240px',
        height: '12px',
        background: 'rgba(201,168,76,0.2)',
        marginBottom: '24px',
      }} />
      <div style={{
        width: '480px',
        maxWidth: '80vw',
        height: '56px',
        background: 'rgba(250,249,246,0.08)',
      }} />
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ArtistDetailSkeleton.jsx
git commit -m "feat(components): ArtistDetailSkeleton placeholder"
```

---

## Task 16: Create ArtistDetail.jsx (generalized from CarlosMedina.jsx)

**Files:**
- Create: `src/pages/ArtistDetail.jsx`
- (later in Task 17) Delete: `src/pages/CarlosMedina.jsx`

- [ ] **Step 1: Read `src/pages/CarlosMedina.jsx` to understand the current structure**

- [ ] **Step 2: Create ArtistDetail.jsx**

Create `src/pages/ArtistDetail.jsx`. This is a near-verbatim copy of CarlosMedina.jsx with the following changes:
- New imports: `useParams`, `Navigate` from `react-router-dom`; `useArtist`, `useRelatedArtists` from `'../hooks/data'`; `ArtistDetailSkeleton` from `'../components/ArtistDetailSkeleton'`.
- Remove the hardcoded `relatedArtists` array and the hardcoded `works` array at the top.
- Inside the component, add `const { slug } = useParams()`, then fetch artist + related.
- Add `isLoading` and `error/!artist` guards that return skeleton or redirect.
- Replace all hardcoded strings with bindings.
- Update the "Related Artists" grid to check `artist.hasDetailPage` for clickability (but the current CarlosMedina page doesn't make those cards clickable, so this is purely a future-friendliness note — leave as non-clickable for now to preserve behavior).

Full file content:

```jsx
import { useEffect, useRef, useState } from 'react'
import { Link, useParams, Navigate } from 'react-router-dom'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Footer from '../sections/Footer'
import ArtistDetailSkeleton from '../components/ArtistDetailSkeleton'
import { useArtist, useRelatedArtists } from '../hooks/data'

gsap.registerPlugin(ScrollTrigger)

const modalLabelStyle = {
  fontFamily: 'DM Sans, sans-serif',
  fontSize: '13px',
  letterSpacing: '0.2em',
  textTransform: 'uppercase',
  color: '#C9A84C',
  margin: '48px 0 20px 0',
}

const modalYearStyle = {
  fontFamily: 'Cormorant Garamond, serif',
  fontSize: '20px',
  fontWeight: 400,
  color: '#FAF9F6',
  margin: '24px 0 8px 0',
}

const modalItemStyle = {
  fontFamily: 'DM Sans, sans-serif',
  fontSize: '14px',
  lineHeight: 1.7,
  color: '#FAF9F6',
  opacity: 0.75,
  margin: '0 0 4px 0',
  paddingLeft: '16px',
}

function WorkCard({ work }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      data-animate="work-card"
      style={{
        aspectRatio: '4/3',
        borderRadius: '2px',
        overflow: 'hidden',
        cursor: 'pointer',
        transition: 'transform 400ms ease',
        position: 'relative',
        transform: hovered ? 'scale(1.02)' : 'scale(1)',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <img
        src={work.image}
        alt={work.title}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          display: 'block',
        }}
      />
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '20px 24px',
        background: 'linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%)',
        opacity: hovered ? 1 : 0,
        transition: 'opacity 400ms ease',
      }}>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
          color: '#FAF9F6',
          margin: 0,
          letterSpacing: '0.05em',
        }}>
          {work.title}
        </p>
      </div>
    </div>
  )
}

export default function ArtistDetail() {
  const { slug } = useParams()
  const { data: artist, isLoading, error } = useArtist(slug)
  const { data: related } = useRelatedArtists(slug)

  const [scrolled, setScrolled] = useState(false)
  const [navLight, setNavLight] = useState(true)
  const [bioModalOpen, setBioModalOpen] = useState(false)
  const heroRef = useRef(null)
  const relatedRef = useRef(null)
  const bioRef = useRef(null)
  const worksRef = useRef(null)
  const quoteRef = useRef(null)
  const modalRef = useRef(null)

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (!artist) return
    const triggers = []

    if (heroRef.current) {
      triggers.push(ScrollTrigger.create({
        trigger: heroRef.current,
        start: 'top top',
        end: 'bottom top',
        onEnter: () => setNavLight(true),
        onLeave: () => setNavLight(false),
        onLeaveBack: () => setNavLight(true),
      }))
    }

    if (relatedRef.current) {
      triggers.push(ScrollTrigger.create({
        trigger: relatedRef.current,
        start: 'top top',
        end: 'bottom top',
        onEnter: () => setNavLight(true),
        onLeave: () => setNavLight(true),
        onEnterBack: () => setNavLight(true),
        onLeaveBack: () => setNavLight(false),
      }))
    }

    return () => triggers.forEach((t) => t.kill())
  }, [artist])

  useEffect(() => {
    if (!artist) return
    const ctx = gsap.context(() => {
      gsap.from('[data-animate="page-nav"]', {
        y: -60,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
      })

      gsap.from('[data-animate="back-link"]', {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        delay: 0.2,
      })

      gsap.from('[data-animate="artist-label"]', {
        y: 20,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
        delay: 0.3,
      })

      gsap.from('[data-animate="artist-name"]', {
        y: 40,
        opacity: 0,
        duration: 1.4,
        ease: 'power3.out',
        delay: 0.6,
      })
    })

    return () => ctx.revert()
  }, [artist])

  useEffect(() => {
    if (!artist) return
    const ctx = gsap.context(() => {
      if (bioRef.current) {
        gsap.from(bioRef.current, {
          y: 40,
          opacity: 0,
          scrollTrigger: {
            trigger: bioRef.current,
            start: 'top 75%',
            end: 'top 25%',
            scrub: 0.5,
          },
        })
      }

      if (quoteRef.current) {
        gsap.from(quoteRef.current, {
          y: 30,
          opacity: 0,
          scrollTrigger: {
            trigger: quoteRef.current,
            start: 'top 75%',
            end: 'top 25%',
            scrub: 0.5,
          },
        })
      }

      const cards = document.querySelectorAll('[data-animate="work-card"]')
      if (cards.length) {
        gsap.from(cards, {
          y: 30,
          opacity: 0,
          stagger: 0.1,
          scrollTrigger: {
            trigger: worksRef.current,
            start: 'top 75%',
            end: 'top 25%',
            scrub: 0.5,
          },
        })
      }
    })

    return () => ctx.revert()
  }, [artist])

  const openModal = () => {
    setBioModalOpen(true)
    document.body.style.overflow = 'hidden'
    requestAnimationFrame(() => {
      if (modalRef.current) {
        gsap.fromTo(modalRef.current,
          { y: '100%' },
          { y: '0%', duration: 0.6, ease: 'power3.out' }
        )
      }
    })
  }

  const closeModal = () => {
    if (modalRef.current) {
      gsap.to(modalRef.current, {
        y: '100%',
        duration: 0.5,
        ease: 'power3.in',
        onComplete: () => {
          setBioModalOpen(false)
          document.body.style.overflow = ''
        },
      })
    }
  }

  if (isLoading) return <ArtistDetailSkeleton />
  if (error || !artist) return <Navigate to="/" replace />

  return (
    <>
      {/* Navigation */}
      <nav data-animate="page-nav" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '24px 48px',
        background: scrolled
          ? navLight ? 'rgba(13,13,13,0.95)' : 'rgba(250,249,246,0.95)'
          : 'transparent',
        backdropFilter: scrolled ? 'blur(8px)' : 'none',
        WebkitBackdropFilter: scrolled ? 'blur(8px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(13,13,13,0.08)' : '1px solid transparent',
        transition: 'background 0.3s ease, border-bottom 0.3s ease',
      }}>
        <Link to="/" style={{ display: 'block' }}>
          <img
            src="/logo.svg"
            alt="Ascaso Gallery"
            style={{
              height: '44px',
              filter: navLight ? 'brightness(0) invert(1)' : 'none',
              transition: 'filter 0.3s ease',
            }}
          />
        </Link>
        <ul style={{
          display: 'flex',
          alignItems: 'center',
          gap: '40px',
          listStyle: 'none',
          margin: 0,
          padding: 0,
        }}>
          {['Artists', 'Exhibitions', 'Contact'].map((link) => (
            <li key={link}>
              <a
                href={`/#${link.toLowerCase()}`}
                style={{
                  fontFamily: 'DM Sans, sans-serif',
                  fontSize: '14px',
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  textDecoration: 'none',
                  color: navLight ? '#FAF9F6' : 'rgba(13,13,13,0.7)',
                  transition: 'color 0.3s ease',
                }}
              >
                {link}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Back link */}
      <Link data-animate="back-link" to="/" style={{
        position: 'fixed',
        top: '90px',
        left: '48px',
        zIndex: 49,
        fontFamily: 'DM Sans, sans-serif',
        fontSize: '12px',
        color: '#C9A84C',
        textDecoration: 'none',
        transition: 'opacity 0.3s ease',
      }}>
        &larr; Back
      </Link>

      {/* Section 1 — Hero banner */}
      <section ref={heroRef} style={{
        height: '60vh',
        background: '#0D0D0D',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <p data-animate="artist-label" style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: '#C9A84C',
          marginBottom: '24px',
        }}>
          {artist.eyebrow}
        </p>
        <h1 data-animate="artist-name" style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontSize: '80px',
          fontWeight: 300,
          color: '#FAF9F6',
          margin: 0,
          textAlign: 'center',
        }}>
          {artist.name}
        </h1>
      </section>

      {/* Section 2 — Bio */}
      <section ref={bioRef} style={{
        background: '#FAF9F6',
        padding: '100px 0',
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 64px',
          display: 'flex',
          gap: '80px',
          alignItems: 'flex-start',
        }}>
          <div style={{
            flex: '0 0 45%',
            maxWidth: '45%',
            height: '600px',
            overflow: 'hidden',
          }}>
            <img
              src={artist.heroImage}
              alt={artist.name}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                objectPosition: 'top center',
                display: 'block',
              }}
            />
          </div>

          <div style={{
            flex: '0 0 55%',
            maxWidth: '55%',
            paddingLeft: '40px',
          }}>
            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '13px',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: '#C9A84C',
              marginBottom: '24px',
            }}>
              About the Artist
            </p>

            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '16px',
              lineHeight: 1.9,
              color: '#0D0D0D',
              opacity: 0.75,
              marginBottom: '24px',
            }}>
              {artist.bio.short}
            </p>

            <button
              onClick={openModal}
              style={{
                background: 'none',
                border: 'none',
                padding: 0,
                fontFamily: 'DM Sans, sans-serif',
                fontSize: '13px',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: '#C9A84C',
                cursor: 'pointer',
                marginBottom: '40px',
              }}
            >
              Read More +
            </button>

            <br />

            <button style={{
              border: '1px solid #0D0D0D',
              background: 'transparent',
              padding: '14px 32px',
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '11px',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              cursor: 'pointer',
              color: '#0D0D0D',
              transition: 'all 0.5s ease',
            }}>
              Download Catalog
            </button>
          </div>
        </div>
      </section>

      {/* Quote strip */}
      <section ref={quoteRef} style={{
        background: '#0D0D0D',
        padding: '80px 0',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}>
        <div style={{
          maxWidth: '800px',
          padding: '0 48px',
          textAlign: 'center',
        }}>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: '#C9A84C',
            marginBottom: '32px',
          }}>
            {artist.quote.eyebrow}
          </p>
          <p style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '48px',
            fontWeight: 300,
            fontStyle: 'italic',
            lineHeight: 1.4,
            color: '#FAF9F6',
            margin: 0,
          }}>
            {artist.quote.text}
          </p>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            color: '#C9A84C',
            marginTop: '24px',
          }}>
            — {artist.quote.attribution}
          </p>
        </div>
      </section>

      {/* Section 3 — Works grid */}
      <section ref={worksRef} style={{
        background: '#FAF9F6',
        padding: '80px 0',
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 64px',
        }}>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: '#C9A84C',
            marginBottom: '16px',
          }}>
            Obra
          </p>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '56px',
            fontWeight: 300,
            lineHeight: 1.1,
            color: '#0D0D0D',
            margin: '0 0 48px 0',
          }}>
            Selected Works
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '24px',
          }}>
            {artist.works.map((work) => (
              <WorkCard key={work.slug} work={work} />
            ))}
          </div>
        </div>
      </section>

      {/* Section 4 — Related Artists */}
      <section ref={relatedRef} style={{
        background: '#0D0D0D',
        padding: '100px 0',
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 64px',
        }}>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: '#C9A84C',
            marginBottom: '16px',
          }}>
            También te puede interesar
          </p>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '48px',
            fontWeight: 300,
            lineHeight: 1.1,
            color: '#FAF9F6',
            margin: '0 0 48px 0',
          }}>
            Related Artists
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '24px',
          }}>
            {related.map((r) => (
              <div
                key={r.slug}
                style={{
                  height: '320px',
                  borderRadius: '2px',
                  overflow: 'hidden',
                  position: 'relative',
                }}
              >
                <img
                  src={r.image}
                  alt={r.name}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    objectPosition: 'top center',
                    display: 'block',
                  }}
                />
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)',
                  pointerEvents: 'none',
                }} />
                <div style={{
                  position: 'absolute',
                  bottom: '24px',
                  left: '24px',
                  right: '24px',
                }}>
                  <p style={{
                    fontFamily: 'DM Sans, sans-serif',
                    fontSize: '11px',
                    letterSpacing: '0.15em',
                    textTransform: 'uppercase',
                    color: '#C9A84C',
                    marginBottom: '8px',
                  }}>
                    {r.medium}
                  </p>
                  <h3 style={{
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: '28px',
                    fontWeight: 300,
                    fontStyle: 'italic',
                    lineHeight: 1.15,
                    color: '#FFFFFF',
                    margin: 0,
                  }}>
                    {r.name}
                  </h3>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />

      {/* Bio Modal Overlay */}
      {bioModalOpen && (
        <div
          ref={modalRef}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            background: 'rgba(13,13,13,0.97)',
            overflowY: 'auto',
            transform: 'translateY(100%)',
          }}
        >
          <button
            onClick={closeModal}
            style={{
              position: 'fixed',
              top: '32px',
              right: '48px',
              zIndex: 10000,
              background: 'none',
              border: 'none',
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '32px',
              color: '#C9A84C',
              cursor: 'pointer',
              lineHeight: 1,
            }}
          >
            &times;
          </button>

          <div style={{
            maxWidth: '800px',
            margin: '0 auto',
            padding: '80px 48px 120px',
          }}>
            <h2 style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: '48px',
              fontWeight: 300,
              color: '#FAF9F6',
              margin: '0 0 16px 0',
            }}>
              {artist.name}
            </h2>
            {artist.bio.full.map((paragraph, i) => (
              <p key={i} style={{
                fontFamily: 'DM Sans, sans-serif',
                fontSize: '14px',
                lineHeight: 1.8,
                color: '#FAF9F6',
                opacity: 0.75,
                marginBottom: '8px',
              }}>
                {paragraph}
              </p>
            ))}

            <h3 style={modalLabelStyle}>Exhibitions &amp; Events</h3>
            {artist.exhibitions.map((group) => (
              <div key={group.year}>
                <p style={modalYearStyle}>{group.year}</p>
                {group.items.map((item, i) => (
                  <p key={i} style={modalItemStyle}>{item}</p>
                ))}
              </div>
            ))}

            <h3 style={modalLabelStyle}>Public Monumental Works</h3>
            {artist.monumentalWorks.map((group) => (
              <div key={group.year}>
                <p style={modalYearStyle}>{group.year}</p>
                {group.items.map((item, i) => (
                  <p key={i} style={modalItemStyle}>{item}</p>
                ))}
              </div>
            ))}

            <h3 style={modalLabelStyle}>Awards Selection</h3>
            {artist.awards.map((item) => (
              <p key={item} style={modalItemStyle}>{item}</p>
            ))}

            <h3 style={modalLabelStyle}>Collection</h3>
            {artist.collections.map((item) => (
              <p key={item} style={modalItemStyle}>{item}</p>
            ))}
          </div>
        </div>
      )}
    </>
  )
}
```

Note: the GSAP effects are gated on `if (!artist) return` at the top of each effect, because they must be declared before the early-return for `isLoading` (rules of hooks). The effects then run once `artist` arrives, with `artist` in their dependency arrays.

- [ ] **Step 3: Build to verify it compiles**

Run: `npm run build`
Expected: successful build.

- [ ] **Step 4: Commit**

```bash
git add src/pages/ArtistDetail.jsx
git commit -m "feat(pages): generalized ArtistDetail page driven by useArtist(slug)"
```

---

## Task 17: Wire ArtistDetail into App.jsx and remove CarlosMedina.jsx

**Files:**
- Modify: `src/App.jsx`
- Delete: `src/pages/CarlosMedina.jsx`

- [ ] **Step 1: Read `src/App.jsx` to confirm current routes**

- [ ] **Step 2: Update imports and route**

Change:
```js
import CarlosMedina from './pages/CarlosMedina'
```
to:
```js
import ArtistDetail from './pages/ArtistDetail'
```

Change:
```jsx
<Route path="/artists/carlos-medina" element={<CarlosMedina />} />
```
to:
```jsx
<Route path="/artists/:slug" element={<ArtistDetail />} />
```

- [ ] **Step 3: Delete CarlosMedina.jsx**

Run: `rm src/pages/CarlosMedina.jsx`

- [ ] **Step 4: Dev server smoke test — full page tour**

Run: `npm run dev`
Open: `http://localhost:5173`

Checks:
1. Homepage renders all sections: Intro, Hero, Quote, Exhibition, Artists, News, ArtFair, Footer.
2. Exhibition section shows "Forms in Space" with correct dates and image.
3. Artists carousel shows 5 cards in order. Only Carlos Medina's card has a gold border on hover and is clickable.
4. News section shows 3 cards with correctly formatted dates.
5. ArtFair section shows Art Miami 2025 with tilt + hover overlay working.
6. Click Carlos Medina's card → navigates to `/artists/carlos-medina`.
7. ArtistDetail page renders: hero, bio, quote strip, works grid (3 works), related artists (4 cards: Javier Martin, Julio Larraz, Carlos Cruz-Diez, Alirio Palacios — NOT Carlos Medina himself).
8. Click "Read More +" → modal opens with bio paragraphs, exhibitions by year, monumental works by year, awards, collections.
9. Close modal → returns to detail page.
10. Click "← Back" → returns to homepage.
11. Visit `/artists/does-not-exist` directly → redirects to `/`.
12. Browser console: no errors, no React warnings. (Dev-mode `[useFeaturedArtists]` or `[useArtist]` warnings should NOT appear with the current data.)

Stop dev server when done.

- [ ] **Step 5: Run full test suite**

Run: `npm test`
Expected: all hook tests still pass.

- [ ] **Step 6: Run build**

Run: `npm run build`
Expected: successful.

- [ ] **Step 7: Commit**

```bash
git add src/App.jsx src/pages/CarlosMedina.jsx
git commit -m "refactor(routing): generalize artist detail route + remove hardcoded CarlosMedina page"
```

Note: `git add` on a deleted file records the deletion.

---

## Task 18: Final verification pass

**Files:** none created or modified.

- [ ] **Step 1: Run the full test suite**

Run: `npm test`
Expected: all tests pass.

- [ ] **Step 2: Run lint**

Run: `npm run lint`
Expected: no errors. If warnings exist in files we didn't touch, leave them alone.

- [ ] **Step 3: Run production build**

Run: `npm run build`
Expected: successful, no errors, no warnings beyond what existed before this refactor.

- [ ] **Step 4: Visual diff against the original**

Run: `npm run preview`
Open the preview URL.

Walk through every section comparing against the screenshots/behavior from before the refactor (or against `git stash`ed memory):
- Hero: unchanged
- Quote: unchanged
- Exhibition: title, subtitle, dates, image, button — pixel-identical
- Artists: 5 cards, same order, same images, same horizontal scroll, same gold-border-on-hover for Carlos Medina
- News: 3 cards, same titles, same excerpts, same dates in "October 15, 2025" format, same images
- ArtFair: same image, same tilt-on-hover, same overlay, same description
- Footer: unchanged
- CarlosMedina detail: same hero, bio, quote, works, modal content — everything pixel-identical

- [ ] **Step 5: Verify no stray files**

Run:
```bash
git status
git log --oneline -20
```
Expected: working tree clean. Commit history shows the refactor as a coherent sequence.

- [ ] **Step 6: Final commit if anything changed during verification**

If steps 1–5 surfaced any issue that needed a tweak, commit with a clear fix message. Otherwise this task produces no commit.

---

## Post-implementation notes

When phase 2 (Flask API) arrives, the swap plan from the spec applies:

1. Add `src/config/api.js` with `VITE_API_BASE_URL`
2. Rewrite each `src/hooks/data/*.js` body to use `fetch()`
3. Delete `src/data/` (or keep as test fixtures)
4. Fill out `ArtistDetailSkeleton` and add skeletons to sections that currently `return null`
5. Consider React Query inside the hook bodies if caching/mutation needs arise

The hook signatures, component code, and JSON shape do not change.
