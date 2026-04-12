# Data-Driven Frontend Refactor — Design

**Date:** 2026-04-12
**Status:** Approved
**Scope:** Phase 1 of a two-phase project. Phase 1 moves all hardcoded content out of JSX into local JSON files accessed through custom hooks. Phase 2 (separate project) replaces the hook internals with calls to a Flask REST API.

## Goal

Every section that displays content (exhibitions, artists, news, art fairs, artist detail pages) reads from `src/data/` via custom hooks instead of hardcoding content in JSX. The hook signatures and return shapes are designed to match what a Flask REST API would return, so phase 2 is a mechanical swap of hook bodies with zero component changes.

Hero and Quote copy stay hardcoded — they are design elements, not content.

## Non-Goals

- No backend code. Flask is phase 2.
- No visual, layout, animation, or style changes. GSAP, ScrollTrigger, refs, and inline styles are untouched.
- No pagination, search, i18n, CMS integration, or React Query. Explicit YAGNI.
- No image renaming. JSON references whatever paths the current JSX uses. A per-resource image folder structure is a follow-up, not blocking.
- No TypeScript migration.

## Architecture Summary

1. **Data files** live in `src/data/<resource>/` as `.json` (not `.js`). Shape matches what a Flask serializer would return.
2. **Custom hooks** live in `src/hooks/data/`, exported via a barrel `src/hooks/data/index.js`.
3. **Every hook returns** `{ data, isLoading, error }` — components are written against this envelope from day one so phase-2 skeletons drop in without JSX surgery.
4. **Artist data is split** into summary (`artists/index.json`) and detail (`artists/<slug>.json`) resources, mirroring the eventual REST endpoints `GET /api/artists` and `GET /api/artists/:slug`.
5. **Homepage curation is hybrid:** exhibition selection uses a `status` field on the record; featured artists use an explicit manifest (`landing.json`); news uses date-sort + limit.

## File Organization

```
src/data/
├── landing.json                    # editorial manifest for homepage
├── exhibitions/
│   └── index.json                  # all exhibitions
├── artists/
│   ├── index.json                  # card-level summary array
│   ├── carlos-medina.json          # full detail record
│   └── <slug>.json                 # one file per artist with a detail page
├── news/
│   └── index.json                  # all news articles
└── artFairs/
    └── index.json                  # all art fairs

src/hooks/data/
├── index.js                        # barrel export
├── useExhibitions.js
├── useArtists.js
├── useNews.js
├── useArtFairs.js
└── useLanding.js                   # internal helper, not exported from barrel
```

**Rationale:**
- Each resource is a folder so it can scale from one file to many without moving things later. `exhibitions/` is a folder on day one even though it only holds `index.json`.
- Hooks live in `src/hooks/data/` (separate from `src/data/`) because they are React code, not data. Phase 2 rewrites the hook files; it does not touch `src/data/`.
- `.json` not `.js`: the on-disk shape **is** the API payload shape. No functions, imports, or `new Date()` leak into the data layer.

## Schemas

All schemas are defined as the **exact JSON shape on disk today and over the wire in phase 2**.

### `exhibitions/index.json`

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

- `status`: `"current" | "upcoming" | "past"`. Drives `useCurrentExhibition()`.
- `startDate`/`endDate`: ISO strings, machine-sortable.
- `dateLabel`: human-facing string, editorially controlled.
- `eyebrow`: gold-label text ("On View", "Opening Soon", etc.).

### `artists/index.json` — summary list

```json
[
  {
    "slug": "carlos-medina",
    "name": "Carlos Medina",
    "medium": "Sculpture",
    "image": "/images/artist-carlos-medina.jpg",
    "hasDetailPage": true
  }
]
```

- `slug` is always present (identity + route segment + React key).
- `hasDetailPage` replaces the current "slug exists → clickable" heuristic. Explicit.

### `artists/<slug>.json` — detail record

```json
{
  "slug": "carlos-medina",
  "name": "Carlos Medina",
  "medium": "Sculpture",
  "heroImage": "/images/artist-carlos-medina.jpg",
  "eyebrow": "Sculpture",
  "bio": {
    "short": "Venezuelan artist (1953)…",
    "full": ["Paragraph 1…", "Paragraph 2…"]
  },
  "quote": {
    "text": "El espacio es el material con el que trabajo…",
    "attribution": "Carlos Medina",
    "eyebrow": "El Artista"
  },
  "works": [
    {
      "slug": "circulo-total",
      "title": "Círculo Total",
      "image": "/images/carlos-medina-work-1.jpg"
    }
  ],
  "exhibitions": [
    {
      "year": 2024,
      "items": [
        "Ascaso Gallery, Miami — Solo Exhibition",
        "Art Miami — Booth AM125"
      ]
    }
  ],
  "monumentalWorks": [
    { "year": 2023, "items": ["Escultura Monumental, Brickell City Centre, Miami"] }
  ],
  "awards": ["Premio Nacional de Artes Plásticas, Venezuela"],
  "collections": ["Museo de Arte Contemporáneo de Caracas"]
}
```

- `bio.short` for inline section; `bio.full` is an array of paragraphs for the modal.
- `exhibitions` and `monumentalWorks` share shape `[{ year, items[] }]` so one renderer handles both.
- `works` carry their own slug to future-proof work detail pages without a schema migration.
- Summary fields (`slug`, `name`, `medium`) are intentionally duplicated from the index — this matches what `GET /api/artists/:slug` would return as a self-contained document. A dev-mode check verifies they stay in sync (see Hooks section).

### `news/index.json`

```json
[
  {
    "slug": "reciprocity-legacy-julio-larraz",
    "date": "2025-10-15",
    "title": "Muestra colectiva en Miami honra el legado de Julio Larraz",
    "excerpt": "Collective Exhibition in Miami Honors the Legacy of Julio Larraz…",
    "image": "/images/news-1.jpg",
    "url": "#",
    "source": null
  }
]
```

- `date`: ISO string. Display format is derived by a formatter utility.
- `url`: where "Continue Reading →" points.
- `source`: optional byline ("ArtDaily"). Nullable.

### `artFairs/index.json`

```json
[
  {
    "slug": "art-miami-2025",
    "name": "Art Miami 2025",
    "startDate": "2025-12-02",
    "endDate": "2025-12-07",
    "dateLabel": "December 2 – December 7, 2025",
    "booth": "AM125",
    "description": "Ascaso Gallery at Art Miami 2025 – Booth AM125, with works by…",
    "image": "/images/art-fair-miami.jpg",
    "eyebrow": "Last Art Fair"
  }
]
```

### `landing.json` — editorial manifest

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

- `featuredArtistSlugs` order is the display order in the horizontal carousel.
- `relatedArtistsFallbackSlugs` is the fallback when an artist's detail record does not yet carry its own `relatedArtistSlugs` field. Per-artist curation is a future addition to the detail schema; no hook changes needed when it arrives.

## Hooks API

### Return envelope

Every hook returns `{ data, isLoading, error }`.

- **Phase 1:** `isLoading` starts `false`, `error` is always `null`, `data` is the resolved value. The exception is `useArtist(slug)`, which uses a dynamic import and is genuinely async (resolves in the same tick but through a Promise).
- **Phase 2:** `isLoading` is `true` on first render, flips `false` when `fetch` resolves. Errors populate `error`.

Components handle all three branches from day one. In phase 1, skeleton/error branches are dead code that cost nothing.

### Signatures

```js
// useExhibitions.js
useExhibitions()              → { data: Exhibition[], isLoading, error }
useCurrentExhibition()        → { data: Exhibition | null, isLoading, error }
useExhibition(slug)           → { data: Exhibition | null, isLoading, error }

// useArtists.js
useArtists()                  → { data: ArtistSummary[], isLoading, error }
useFeaturedArtists()          → { data: ArtistSummary[], isLoading, error }
useArtist(slug)               → { data: ArtistDetail | null, isLoading, error }
useRelatedArtists(slug)       → { data: ArtistSummary[], isLoading, error }

// useNews.js
useNews()                     → { data: NewsItem[], isLoading, error }  // sorted newest-first
useLatestNews(limit = 3)      → { data: NewsItem[], isLoading, error }
useNewsItem(slug)             → { data: NewsItem | null, isLoading, error }

// useArtFairs.js
useArtFairs()                 → { data: ArtFair[], isLoading, error }
useLatestArtFair()            → { data: ArtFair | null, isLoading, error }
useArtFair(slug)              → { data: ArtFair | null, isLoading, error }

// useLanding.js — internal, not in barrel
useLanding()                  → { data: LandingManifest, isLoading, error }
```

### Behavior notes

- `useCurrentExhibition()` finds the first exhibition where `status === "current"`. Returns `null` if none — the section component renders nothing in that case.
- `useFeaturedArtists()` reads `landing.json`, resolves each slug against the summary list, returns them **in manifest order**. Silently skips slugs that don't resolve, logging a `console.warn` in dev mode only.
- `useArtist(slug)` uses a dynamic import (`import('../../data/artists/' + slug + '.json')`) so each detail file is a separate Vite code-split chunk. Returns `null` for unknown slugs.
- `useRelatedArtists(slug)` uses the artist's own `relatedArtistSlugs` field if present, otherwise falls back to `landing.json → relatedArtistsFallbackSlugs`, filtering out `slug` itself.
- `useLatestNews(3)` sorts by `date` descending inside the hook, not in the component.
- `useLatestArtFair()` sorts by `endDate` descending and returns the first.

### Dev-mode integrity check

When `useArtist(slug)` resolves, an assertion wrapped in `if (import.meta.env.DEV)` compares `detail.slug/name/medium` against the summary record for the same slug and logs a warning if they disagree. Stripped from production builds by Vite. This is the safety net for the duplicated summary fields in detail records.

### Barrel export

```js
// src/hooks/data/index.js
export { useExhibitions, useCurrentExhibition, useExhibition } from './useExhibitions'
export { useArtists, useFeaturedArtists, useArtist, useRelatedArtists } from './useArtists'
export { useNews, useLatestNews, useNewsItem } from './useNews'
export { useArtFairs, useLatestArtFair, useArtFair } from './useArtFairs'
```

Components import from `'../hooks/data'` (or the relative equivalent). They never import individual hook files and never import from `src/data/` directly. This is the seam: phase 2 rewrites the hook files; the barrel and component imports stay identical.

### Phase-1 implementation pattern (example)

```js
// src/hooks/data/useArtists.js — phase 1
import { useState, useEffect } from 'react'
import artistsIndex from '../../data/artists/index.json'
import landing from '../../data/landing.json'

export function useArtists() {
  return { data: artistsIndex, isLoading: false, error: null }
}

export function useFeaturedArtists() {
  const bySlug = new Map(artistsIndex.map((a) => [a.slug, a]))
  const data = landing.featuredArtistSlugs
    .map((slug) => bySlug.get(slug))
    .filter(Boolean)
  return { data, isLoading: false, error: null }
}

export function useArtist(slug) {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })
  useEffect(() => {
    import(`../../data/artists/${slug}.json`)
      .then((mod) => setState({ data: mod.default, isLoading: false, error: null }))
      .catch((err) => setState({ data: null, isLoading: false, error: err }))
  }, [slug])
  return state
}
```

## Component Refactor Plan

For every component below, **animation code, styles, refs, GSAP setup, and layout are untouched**. Only data-binding changes.

### `Hero.jsx` — no change
Hardcoded copy is a design element.

### `Quote.jsx` — no change
Hardcoded copy is a design element.

### `Exhibition.jsx`

- Import `useCurrentExhibition` from `'../hooks/data'`.
- `const { data: exhibition, isLoading } = useCurrentExhibition()`.
- `if (isLoading || !exhibition) return null` — section is optional.
- Bind `exhibition.eyebrow`, `exhibition.title`, `exhibition.subtitle`, `exhibition.dateLabel`, `exhibition.image` into the existing JSX in place of string literals.

### `Artists.jsx`

- Import `useFeaturedArtists`.
- `const { data: artists } = useFeaturedArtists()`.
- Delete the hardcoded `artists` array at the top of the file.
- `ArtistCard` clickability check changes from `if (artist.slug)` to `if (artist.hasDetailPage)`. The `navigate(\`/artists/${artist.slug}\`)` call stays identical.
- The GSAP `useEffect` that computes `totalWidth = artists.length * CARD_WIDTH` gets a guard: `if (!artists.length) return` at the top, and `artists.length` in the dependency array. Phase 1 fires on first render (synchronous data); phase 2 fires after fetch resolves.

### `News.jsx`

- Import `useLatestNews`.
- `const { data: news } = useLatestNews(3)`.
- Delete the hardcoded `news` array.
- Add a `formatNewsDate(iso)` utility at `src/utils/formatDate.js`:
  ```js
  export function formatNewsDate(iso) {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric'
    })
  }
  ```
- Render `{formatNewsDate(item.date)}` instead of the raw string.
- Same empty-array guard on the GSAP effect.

### `ArtFair.jsx`

- Import `useLatestArtFair`.
- `const { data: fair, isLoading } = useLatestArtFair()`.
- `if (isLoading || !fair) return null`.
- Bind `fair.name`, `fair.dateLabel`, `fair.description`, `fair.image`, `fair.booth`, `fair.eyebrow` throughout the existing JSX, including the hover-overlay strings.

### `CarlosMedina.jsx` → `ArtistDetail.jsx`

The CarlosMedina page is renamed to `ArtistDetail.jsx` and generalized. The file at `src/pages/CarlosMedina.jsx` is replaced by `src/pages/ArtistDetail.jsx`.

**Route change in `App.jsx`:**
```jsx
<Route path="/artists/:slug" element={<ArtistDetail />} />
```

`/artists/carlos-medina` continues to work — it now resolves via `useParams()` → `useArtist("carlos-medina")`.

**Inside `ArtistDetail.jsx`:**
```jsx
import { useParams, Navigate } from 'react-router-dom'
import { useArtist, useRelatedArtists } from '../hooks/data'
import ArtistDetailSkeleton from '../components/ArtistDetailSkeleton'

const { slug } = useParams()
const { data: artist, isLoading, error } = useArtist(slug)
const { data: related } = useRelatedArtists(slug)

if (isLoading) return <ArtistDetailSkeleton />
if (error || !artist) return <Navigate to="/" replace />
```

**Bindings:**
- Hero: `artist.eyebrow`, `artist.name`
- Bio (inline): `artist.bio.short`
- Bio (modal): `artist.bio.full.map(...)` → `<p>` elements
- Quote strip: `artist.quote.eyebrow`, `artist.quote.text`, `artist.quote.attribution`
- Works grid: `artist.works.map(...)`
- Modal exhibitions: loop over `artist.exhibitions[]`, each group rendering `{year}` heading and `items[]` rows. Replaces ~25 lines of hardcoded `<p>` tags.
- Modal monumental works: same loop over `artist.monumentalWorks[]`.
- Awards: `artist.awards.map(...)`
- Collections: `artist.collections.map(...)`
- Related artists grid: `related.map(...)`

**`ArtistDetailSkeleton` — new component at `src/components/ArtistDetailSkeleton.jsx`.** Minimal placeholder matching the hero band dimensions in `#FAF9F6` on `#0D0D0D`, no shimmer required. Dead code in phase 1 (dynamic import resolves same-tick), visible in phase 2.

**Unknown artist handling:** `useArtist("nonexistent")` returns `{ data: null, error }` and the page redirects to `/`. Today's behavior incorrectly renders Carlos Medina's static page for any slug; this is a behavior improvement.

### Zero-touch files

`Intro.jsx`, `Footer.jsx`, `Hero.jsx`, `Quote.jsx`, all inline styles, all GSAP/ScrollTrigger logic (except empty-array guards in Artists and News).

### Summary table

| Section | Hook | Empty-state behavior |
|---|---|---|
| Hero | none | n/a |
| Quote | none | n/a |
| Exhibition | `useCurrentExhibition()` | section hides |
| Artists | `useFeaturedArtists()` | section hides |
| News | `useLatestNews(3)` | section hides |
| ArtFair | `useLatestArtFair()` | section hides |
| ArtistDetail | `useArtist(slug)`, `useRelatedArtists(slug)` | redirect to `/` |

## Scaling

### Bundle-size

Current resource sizes are tiny (100 news entries ≈ 20 KB). Breakpoint for concern: any `index.json` crossing ~100 KB (roughly 500+ records, or fewer with large excerpts). Mitigation at that scale: split the resource into summary/detail files the same way `artists/` is split on day one. Hook layer absorbs the change; components don't notice.

Artist detail files use dynamic imports, so Vite code-splits each artist into its own chunk. Visiting `/artists/carlos-medina` downloads only `carlos-medina.json`. Already scale-correct.

### Images

Phase 1 does not rename images. JSON references whatever paths the current JSX uses. A future per-resource folder structure (`/images/artists/<slug>/portrait.jpg`, etc.) is a follow-up. The schema supports either layout.

In phase 2, paths may become absolute CDN URLs. The `image` field is still a string; components don't care.

### Data validation

- **Dev-mode console warnings:** `useFeaturedArtists()`, `useRelatedArtists()`, and `useArtist()` integrity check all log in dev. Free, ships in phase 1.
- **Vite-time validation script:** not built. Add later only if misconfigurations start biting.

## Phase-2 Transition Plan

When Flask is ready:

1. Add `src/config/api.js` with `API_BASE_URL = import.meta.env.VITE_API_BASE_URL`.
2. Rewrite each `src/hooks/data/*.js` body to use `fetch()` instead of local imports. Signatures and return shapes are unchanged.
3. Delete `src/data/` (or keep it as test fixtures).
4. Populate the skeleton components that phase 1 wired as placeholders. These are additive JSX changes inside existing section components; no hook or data changes.
5. Consider React Query or SWR as a drop-in inside hook bodies when you hit: cache invalidation, background refetching, or mutation support. Not required on day one of phase 2.

**What does not change in phase 2:**
- Any component file (skeleton fills are additive, not rewrites)
- Any JSON schema shape (Flask serializers produce these exactly)
- Any route, GSAP code, style, or ref
- The barrel export

### Schema evolution rules

- **Add a field:** free. Add to JSON, add to any component that renders it.
- **Rename a field:** touches JSON, optionally the hook (for translation), and every component that reads it.
- **Remove a field:** confirm no component reads it first (grep by name).

Translation logic, if ever needed, lives in the hook layer — e.g., if Flask returns `date_iso` but frontend wants `date`, the hook does `data.map(n => ({ ...n, date: n.date_iso }))`. Keeps components untouched and makes the translation visible in one place.

## Out of Scope (YAGNI)

- Pagination / infinite scroll for news
- Full-text search
- i18n / multi-language copy
- CMS integration (Contentful, Sanity, etc.)
- React Query / SWR in phase 1
- TypeScript migration
- Image path migration to per-resource folders
- Vite-time data validation script
- Individual work detail pages (schema supports, not built)
- Individual exhibition detail pages (schema supports, not built)
- Individual news article pages (schema supports, not built)
