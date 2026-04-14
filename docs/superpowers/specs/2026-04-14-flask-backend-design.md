# Flask Backend — Ascaso Gallery

**Date:** 2026-04-14
**Status:** Design approved, ready for implementation planning
**Author:** Brainstormed with Claude (Opus 4.6)

## Context

The Ascaso Gallery landing page is a React + Vite SPA. Content (artists, exhibitions, news, art fairs) currently lives in committed JSON files under `src/data/` and is consumed via hooks in `src/hooks/data/`. There is no backend today.

This spec defines a Flask JSON API that becomes the source of truth for gallery content and enables a React-based admin panel (tracked as a separate, future effort) to manage it.

## Goals

- Replace static JSON content with a database-backed JSON API.
- Ship JWT-authenticated CRUD endpoints for all editable resources.
- Support Cloudinary image uploads for portraits, hero images, and artwork photos.
- Deploy to Render alongside the existing frontend.
- Preserve the current frontend shape so the migration is isolated to the 5 data hook files.

## Non-goals (v1)

- React admin UI (separate brainstorm + spec).
- Refresh tokens or server-side token revocation.
- Direct-to-Cloudinary signed uploads (upgrade path documented).
- Cloudinary asset deletion / orphan cleanup.
- Rate limiting (except the one login guard noted in §4).
- End-to-end browser tests.
- Performance / load testing.
- GitHub Actions CI (easy to add later).
- Many-to-many linking (e.g. artists ↔ exhibitions).

## Decisions locked during brainstorming

| Decision | Choice | Rationale |
|---|---|---|
| Data model fidelity | Relational Artist + ArtWork; JSONB for editorial prose blocks | Relational where queries happen, JSONB where the admin edits as blocks |
| Admin UI | Headless — React `/admin` route tree (future) | Keeps the editorial design system |
| Seeding | `flask seed` CLI reads committed JSON fixtures | Decouples content from schema migrations |
| Serialization | Marshmallow + marshmallow-sqlalchemy | Idiomatic Flask, handles JSONB as `fields.Dict` |
| Image upload | Proxy through Flask (v1), signed direct upload (v2) | Simpler; small files; upgrade path clear |
| Folder layout | Blueprints by resource, models/schemas split by file | Idiomatic Flask, room to grow |
| Deployment | Render with `render.yaml` | Same platform as frontend |
| First admin | `flask create-admin` CLI command | Scriptable, no committed secrets |
| Dev DB | SQLite default, Postgres via env var | Fast local loop |
| Test DB | In-memory SQLite via `conftest.py` | Fast, isolated |
| Packaging | `requirements.txt` + pip | Simpler, standard for Render |
| Dates on exhibitions / art fairs | Free-text `dates String(200)` | Editorial flexibility matters more than sortability |
| Frontend data layer | Plain `fetch` in v1 | Defer TanStack Query to v2 if caching matters |

---

## Section 1 — Folder layout

```
backend/
├── app/
│   ├── __init__.py              # create_app(config_name) factory
│   ├── config.py                # DevConfig, TestConfig, ProdConfig
│   ├── extensions.py            # db, ma, jwt, cors, limiter singletons
│   ├── errors.py                # centralized JSON error handlers
│   │
│   ├── models/
│   │   ├── __init__.py          # re-exports all models
│   │   ├── artist.py            # Artist + ArtWork
│   │   ├── exhibition.py
│   │   ├── news.py              # NewsArticle
│   │   ├── artfair.py           # ArtFair
│   │   └── admin_user.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── artist.py            # ArtistSchema, ArtistSummarySchema, ArtWorkSchema
│   │   ├── exhibition.py
│   │   ├── news.py
│   │   ├── artfair.py
│   │   └── auth.py              # LoginSchema, TokenSchema
│   │
│   ├── blueprints/
│   │   ├── __init__.py          # register_blueprints(app)
│   │   ├── artists.py           # /api/artists
│   │   ├── exhibitions.py       # /api/exhibitions
│   │   ├── news.py              # /api/news
│   │   ├── artfairs.py          # /api/artfairs
│   │   ├── auth.py              # /api/auth/login, /api/auth/me
│   │   └── upload.py            # /api/upload
│   │
│   └── services/
│       ├── __init__.py
│       ├── cloudinary.py        # upload_image(file) -> dict
│       ├── auth.py              # hash_password, verify_password, admin_required
│       └── slugify.py           # slug generation + uniqueness helper
│
├── migrations/                  # Alembic (generated via `flask db init`)
│   └── versions/
├── fixtures/                    # JSON seeds — 1:1 with src/data/
│   ├── artists/
│   │   ├── index.json           # present but ignored at seed time
│   │   └── carlos-medina.json
│   ├── exhibitions.json
│   ├── news.json
│   ├── artfairs.json
│   └── landing.json             # featured slugs reference (not seeded)
├── scripts/
│   ├── __init__.py
│   └── cli.py                   # flask create-admin, flask seed, flask reset-db
├── tests/
│   ├── conftest.py              # app fixture, db fixture, auth helpers
│   ├── test_artists.py
│   ├── test_exhibitions.py
│   ├── test_news.py
│   ├── test_artfairs.py
│   ├── test_auth.py
│   └── test_upload.py
├── wsgi.py                      # gunicorn entrypoint
├── .env.example
├── .gitignore
├── requirements.txt             # pinned runtime deps
├── requirements-dev.txt         # pytest + lint tools
├── render.yaml                  # web service + managed postgres
└── README.md                    # setup, migrations, seed, test commands
```

**Key conventions:**
- `create_app(config_name)` is the only way to build a Flask app. No module-level `app = Flask(...)`. This lets tests spin up isolated app instances with the in-memory test config.
- `wsgi.py` is 3 lines: `from app import create_app; app = create_app(os.getenv('FLASK_ENV', 'prod'))`. Render start command: `gunicorn wsgi:app`.
- Blueprints are thin. Route → schema validate → service call → schema dump. Business logic lives in `services/`.
- `scripts/cli.py` registers Click commands via Flask's `@app.cli.command` so they're invoked as `flask create-admin`, `flask seed`, `flask reset-db`.

---

## Section 2 — Data model

All tables use bigserial-equivalent integer primary keys. `slug` is the public identifier; numeric ids never appear in API responses.

### `artists`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `slug` | String(120) unique not null | URL key |
| `name` | String(200) not null | |
| `medium` | String(100) | e.g. "Sculpture", "Painting" |
| `nationality` | String(100) | |
| `eyebrow` | String(100) | editorial label |
| `hero_image_url` | String(500) | |
| `featured` | Boolean default false | drives `GET /api/artists?featured=true` |
| `display_order` | Integer default 0 | `order` is a reserved word |
| `bio` | JSONB | `{ short: str, full: [str, str, ...] }` |
| `quote` | JSONB | `{ text, attribution, eyebrow }` |
| `awards` | JSONB | `[str, ...]` |
| `collections` | JSONB | `[str, ...]` |
| `exhibitions_history` | JSONB | `[{ year: int, items: [str, ...] }]` |
| `monumental_works` | JSONB | `[{ year: int, items: [str, ...] }]` |
| `created_at` | DateTime default now() | |
| `updated_at` | DateTime onupdate now() | |

### `artworks`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `artist_id` | FK → artists.id on delete cascade | |
| `slug` | String(120) not null | unique per artist |
| `title` | String(200) not null | |
| `year` | Integer nullable | |
| `medium` | String(100) nullable | |
| `image_url` | String(500) not null | |
| `display_order` | Integer default 0 | |
| `created_at` | DateTime | |

Unique constraint: `(artist_id, slug)`.

### `exhibitions`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `slug` | String(120) unique not null | |
| `title` | String(200) not null | |
| `subtitle` | String(300) | |
| `status` | Enum('current','upcoming','past') | indexed |
| `dates` | String(200) | free-text display, e.g. "April 10 – June 15, 2026" |
| `hero_image_url` | String(500) | |
| `description` | Text | markdown or plain |
| `display_order` | Integer default 0 | |
| `created_at` / `updated_at` | | |

Current / upcoming / past filtering is driven by the `status` column, which the admin sets manually — there is no date-parsing logic.

### `news_articles`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `slug` | String(200) unique not null | |
| `title` | String(300) not null | |
| `excerpt` | String(500) | |
| `content` | Text | markdown |
| `hero_image_url` | String(500) | |
| `published_at` | DateTime nullable | `NULL` means draft |
| `created_at` / `updated_at` | | |

Public list filters `WHERE published_at IS NOT NULL AND published_at <= now()`. Admin list (`?drafts=true`, JWT required) shows everything.

### `art_fairs`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `slug` | String(120) unique not null | |
| `name` | String(200) not null | |
| `dates` | String(200) | free-text display |
| `location` | String(200) | |
| `booth` | String(50) | |
| `description` | Text | |
| `hero_image_url` | String(500) | |
| `year` | Integer indexed | sort key for "latest fair" |
| `created_at` / `updated_at` | | |

### `admin_users`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `email` | String(200) unique not null | |
| `password_hash` | String(255) not null | bcrypt via `passlib` |
| `created_at` | DateTime | |
| `last_login_at` | DateTime nullable | |

### Relationships

- `Artist` 1─∞ `ArtWork` — cascade delete.
- No other relations in v1.

### JSONB on SQLite

Postgres uses `JSONB`. SQLite falls back to the `JSON` type (stored as text). Marshmallow sees both as `dict` / `list`, so application code is identical. JSONB indexing is unavailable in dev but we never query inside these blocks.

---

## Section 3 — API routes

All routes under `/api`. JSON in, JSON out.

### Conventions

- **List responses** are enveloped: `{ "data": [...], "count": N }`. Lets us add pagination later non-breakingly.
- **Detail / single-record responses** are unenveloped: the record object itself.
- **Error responses** are always `{ "error": { "code", "message", "details"?, "request_id" } }`.
- **Lookups are always by slug.** Numeric ids never appear in responses.
- **Timestamps** are ISO 8601 UTC strings.
- **Field naming**: the API returns **snake_case** (matches Python / DB columns). The React API client (`src/lib/api.js`, §10) applies a one-time snake → camel transform on every response so the existing frontend hooks and components continue to see `heroImage`, `monumentalWorks`, `exhibitionsHistory`, etc. Backend code stays Pythonic; frontend code is unchanged outside the hook layer.
- **Public routes** are read-only. Mutation routes require a valid JWT.

### Artists — `app/blueprints/artists.py`

| Method | Path | Auth | Schema in | Schema out | Notes |
|---|---|---|---|---|---|
| GET | `/api/artists` | public | — | `ArtistSummarySchema(many=True)` | `?featured=true` optional |
| GET | `/api/artists/<slug>` | public | — | `ArtistSchema` | full detail |
| POST | `/api/artists` | JWT | `ArtistSchema` | `ArtistSchema` | slug auto-generated if omitted |
| PUT | `/api/artists/<slug>` | JWT | `ArtistSchema(partial=True)` | `ArtistSchema` | partial updates |
| DELETE | `/api/artists/<slug>` | JWT | — | 204 | cascades to artworks |
| POST | `/api/artists/<slug>/artworks` | JWT | `ArtWorkSchema` | `ArtWorkSchema` | |
| PUT | `/api/artists/<slug>/artworks/<work_slug>` | JWT | `ArtWorkSchema(partial=True)` | `ArtWorkSchema` | |
| DELETE | `/api/artists/<slug>/artworks/<work_slug>` | JWT | — | 204 | |

`ArtistSummarySchema` fields: `slug`, `name`, `medium`, `eyebrow`, `hero_image_url`, `featured`, `display_order`.

`ArtistSchema` fields: all Artist columns + nested `works: [ArtWorkSchema]`.

### Exhibitions — `app/blueprints/exhibitions.py`

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/api/exhibitions` | public | `?status=current\|upcoming\|past` optional |
| GET | `/api/exhibitions/<slug>` | public | |
| POST | `/api/exhibitions` | JWT | |
| PUT | `/api/exhibitions/<slug>` | JWT | |
| DELETE | `/api/exhibitions/<slug>` | JWT | |

### News — `app/blueprints/news.py`

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/api/news` | public | only published, newest first |
| GET | `/api/news?drafts=true` | JWT | admin list; includes drafts |
| GET | `/api/news/<slug>` | public | 404 if draft |
| POST | `/api/news` | JWT | `published_at` null = draft |
| PUT | `/api/news/<slug>` | JWT | |
| DELETE | `/api/news/<slug>` | JWT | |

### Art Fairs — `app/blueprints/artfairs.py`

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/api/artfairs` | public | `?year=2026` optional; default `ORDER BY year DESC` |
| GET | `/api/artfairs/latest` | public | convenience — matches `useLatestArtFair` hook |
| GET | `/api/artfairs/<slug>` | public | |
| POST | `/api/artfairs` | JWT | |
| PUT | `/api/artfairs/<slug>` | JWT | |
| DELETE | `/api/artfairs/<slug>` | JWT | |

### Health

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/api/health` | public | `{"status":"ok"}` — Render probe target |

---

## Section 4 — Authentication

### Hashing and tokens

- **Hashing**: `passlib[bcrypt]`, 12 rounds.
- **Tokens**: `Flask-JWT-Extended` access tokens, HS256, signed with `JWT_SECRET_KEY`.
- **Expiry**: 12 hours. Admin re-logs in once a day.
- **Refresh tokens**: not in v1.
- **Storage**: frontend stores the token in `localStorage`. Acceptable for a small-admin internal CMS; revisit if the admin count grows or third-party scripts are ever embedded.

### Routes — `app/blueprints/auth.py`

| Method | Path | Auth | Schema in | Schema out |
|---|---|---|---|---|
| POST | `/api/auth/login` | public | `LoginSchema {email, password}` | `TokenSchema {access_token, user: {id, email}}` |
| GET | `/api/auth/me` | JWT | — | `{id, email, created_at, last_login_at}` |

**Login behavior:**
- Validate schema → look up admin by email → verify bcrypt → update `last_login_at` → issue JWT.
- On any failure (unknown email OR wrong password) return **byte-identical** 401 response. Tests assert this to guard against user enumeration.

**`/auth/me` behavior:**
- Returns the current admin from `get_jwt_identity()`.
- Used by the frontend on page load to restore session when a token is present in `localStorage`.

**No `/logout` endpoint.** JWT logout is client-side — drop the token. Server-side revocation is a v2 concern.

### `admin_required` decorator — `app/services/auth.py`

```python
def admin_required(fn):
    @jwt_required()
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = AdminUser.query.get(user_id)
        if not user:
            abort(401)
        g.current_admin = user
        return fn(*args, **kwargs)
    return wrapper
```

Applied to every mutation route and to the admin-only news list path.

### Login rate limit

Flask-Limiter with a single rule: **5 login attempts per minute per IP**. Two lines in `extensions.py`, one decorator on `/api/auth/login`. No other routes are rate-limited in v1.

### CORS

Flask-CORS with explicit origin allowlist, **not wildcard**:
- Dev: `http://localhost:5173`
- Prod: Render frontend URL + any bound custom domain
- Origins come from the `CORS_ORIGINS` env var (comma-separated) so redeploy is not required to add a domain.
- `supports_credentials=True` enabled so a cookie-based auth upgrade later is non-breaking.

---

## Section 5 — Upload flow

### Route — `app/blueprints/upload.py`

| Method | Path | Auth | Accepts | Returns |
|---|---|---|---|---|
| POST | `/api/upload` | JWT | `multipart/form-data` with `file` field | `{ url, public_id, width, height, format, bytes }` |

### Guardrails (fail fast, in order)

1. **`MAX_CONTENT_LENGTH = 15 * 1024 * 1024`** in `BaseConfig`. Flask rejects oversize requests with 413 before the route runs.
2. **MIME allowlist**: `{'image/jpeg', 'image/png', 'image/webp'}` checked against `request.files['file'].mimetype`. Reject with 415.
3. **Magic-byte sniff**: first 12 bytes verified against JPEG / PNG / WebP signatures. Rejects `malicious.exe` renamed to `.jpg`. ~8 lines, no dependency.
4. **Cloudinary upload** via `cloudinary.uploader.upload(file, folder='ascaso-gallery', resource_type='image')`.
5. **Return a normalized subset** of Cloudinary's response — not the raw object. Keeps the API contract small.

### Service — `app/services/cloudinary.py`

```python
def upload_image(file_storage) -> dict:
    # 1. validate mime + magic bytes
    # 2. call cloudinary.uploader.upload()
    # 3. return { url, public_id, width, height, format, bytes }
```

Cloudinary is configured once in `create_app()`:

```python
cloudinary.config(cloudinary_url=app.config['CLOUDINARY_URL'])
```

`CLOUDINARY_URL` format (native SDK env var): `cloudinary://<api-key>:<api-secret>@<cloud-name>`.

### Explicitly out of scope (v1)

- No server-side transformation pipeline. Cloudinary handles resize/format via URL params on read (`w_800,q_auto,f_auto`).
- No deletion endpoint. Orphaned Cloudinary assets accrue; cleanup is a v2 concern.
- No direct-to-Cloudinary signed uploads. Upgrade path: replace `/api/upload` with `/api/upload/sign` + `/api/upload/confirm` when bandwidth or worker time becomes a problem.

---

## Section 6 — Config, environment, and Render deployment

### `app/config.py`

```python
class BaseConfig:
    SECRET_KEY = os.environ['SECRET_KEY']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')

class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret'
    JWT_SECRET_KEY = 'test-jwt-secret'
    CLOUDINARY_URL = 'cloudinary://test:test@test'

class ProdConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
```

`create_app(config_name)` selects a class by name: `{'dev': DevConfig, 'test': TestConfig, 'prod': ProdConfig}[config_name]`. `wsgi.py` reads `FLASK_ENV` (default `prod`).

### `.env.example` (committed)

```
FLASK_ENV=dev
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me
DATABASE_URL=sqlite:///dev.db
CLOUDINARY_URL=cloudinary://<api-key>:<api-secret>@<cloud-name>
CORS_ORIGINS=http://localhost:5173
```

`.env` is gitignored. `python-dotenv` loads it in dev only (`load_dotenv()` in `wsgi.py`, guarded by `FLASK_ENV != 'prod'`).

### `render.yaml` (`backend/render.yaml`)

```yaml
services:
  - type: web
    name: ascaso-gallery-api
    runtime: python
    rootDir: backend
    buildCommand: "pip install -r requirements.txt && flask db upgrade"
    startCommand: "gunicorn wsgi:app --workers 2 --timeout 60"
    healthCheckPath: /api/health
    envVars:
      - key: FLASK_ENV
        value: prod
      - key: FLASK_APP
        value: wsgi.py
      - key: PYTHON_VERSION
        value: 3.12.3
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: ascaso-gallery-db
          property: connectionString
      - key: CORS_ORIGINS
        sync: false
      - key: CLOUDINARY_URL
        sync: false

databases:
  - name: ascaso-gallery-db
    plan: free
    postgresMajorVersion: "16"
```

**Notes:**
- `flask db upgrade` runs on every deploy — idempotent, no-op if schema is already at head.
- **Seeding never runs on deploy.** Seeding is a manual one-time `flask seed` from Render Shell after the first successful deploy. Automating it would risk re-inserting content on every push.
- `sync: false` means Render won't overwrite dashboard values from the file. Paste `CORS_ORIGINS` and `CLOUDINARY_URL` in the dashboard once.
- `--workers 2 --timeout 60` targets the Render free tier (512MB RAM). 60s timeout accommodates Cloudinary uploads.

### Health check

```python
@app.get('/api/health')
def health():
    return {'status': 'ok'}
```

Render probes this path. A 5xx or timeout restarts the service.

---

## Section 7 — Seeding strategy

### Fixtures — `backend/fixtures/`, structured 1:1 with `src/data/`

```
backend/fixtures/
├── artists/
│   ├── index.json              # present but ignored at seed time (derived from details)
│   └── carlos-medina.json      # full artist detail → one Artist + N ArtWork rows
├── exhibitions.json            # array of exhibition records
├── news.json                   # array of news articles
├── artfairs.json               # array of art fairs
└── landing.json                # featured slugs — referenced by seeder to set artist.featured
```

### `flask seed` command — `backend/scripts/cli.py`

```python
@app.cli.command('seed')
@click.option('--wipe', is_flag=True, help='Delete existing content rows before seeding')
def seed(wipe):
    # 1. if --wipe: truncate content tables (never touches admin_users)
    # 2. load fixtures/artists/*.json (except index.json):
    #    - upsert Artist by slug
    #    - upsert child ArtWork rows by (artist_id, slug) — matches the
    #      unique constraint defined in §2
    # 3. load fixtures/exhibitions.json -> upsert by slug
    # 4. load fixtures/news.json -> upsert by slug
    # 5. load fixtures/artfairs.json -> upsert by slug
    # 6. read fixtures/landing.json featuredArtistSlugs, set artist.featured=True
    # 7. print summary: "Seeded N artists (M artworks), X exhibitions, Y news, Z art fairs"
```

- **Upsert logic**: `SELECT ... WHERE slug = ?` → `UPDATE` if found, `INSERT` otherwise. Idempotent.
- `--wipe` is a dev-only convenience; not used in prod.
- Admin users are never touched by seed. Always bootstrap via `flask create-admin`.
- After seeding, `artist.featured` is the source of truth — `landing.json` is no longer consulted at runtime.

### First-run order, dev

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env            # fill in real values
flask db upgrade                 # create schema
flask seed                       # load fixtures
flask create-admin               # interactive: email + password
flask run                        # localhost:5000
```

### First-run order, Render prod (one-time, from Render Shell)

```bash
flask seed                       # schema already applied by buildCommand
flask create-admin               # interactive: email + password
```

---

## Section 8 — Testing strategy

### `backend/tests/conftest.py`

```python
@pytest.fixture
def app():
    app = create_app('test')                 # TestConfig → sqlite:///:memory:
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token(app):
    user = AdminUser(email='test@test.com', password_hash=hash_password('test'))
    db.session.add(user); db.session.commit()
    return create_access_token(identity=user.id)
```

**Why `db.create_all()` instead of alembic**: tests verify behavior, not migration history. Using SQLAlchemy metadata directly is faster, has no migration-ordering gotchas, and catches model/schema mismatches instantly. Migrations themselves are exercised by the dev loop (`flask db upgrade` against a fresh local DB).

### Per-resource coverage (`test_artists.py`, `test_exhibitions.py`, `test_news.py`, `test_artfairs.py`)

Each file covers:

1. **GET list** — empty DB → `{data: [], count: 0}`; seeded DB → correct shape.
2. **GET detail** — by slug; 404 for unknown slug.
3. **POST** — happy path; `ValidationError` → 422; missing auth → 401.
4. **PUT** — partial update; 404 for unknown slug; missing auth → 401.
5. **DELETE** — removes record; 404 for unknown slug; missing auth → 401.
6. **One resource-specific test**:
   - artists: `?featured=true` filter; cascade-delete `ArtWork` when parent `Artist` is deleted
   - exhibitions: `?status=current` filter
   - news: draft visibility (public 404, admin sees it)
   - artfairs: `/api/artfairs/latest` returns highest-year record

### `test_auth.py`

- Login with valid credentials → 200 + token
- Login with wrong password → 401 (generic body)
- Login with unknown email → 401 (**byte-identical** to wrong-password response)
- `/auth/me` without token → 401
- `/auth/me` with valid token → 200 + user payload

### `test_upload.py`

- Cloudinary is mocked via `monkeypatch` on `cloudinary.uploader.upload`. Tests never hit the real Cloudinary.
- Cases: happy path; oversize → 413; wrong mime → 415; magic-byte mismatch → 415; missing auth → 401.

### Explicitly not tested in v1

- React frontend end-to-end — separate concern.
- Load / performance — out of scope.
- Alembic migrations — exercised by the dev loop.

CI is not defined in this spec. A GitHub Actions workflow running `pytest` on PRs touching `backend/` is a ~20-line add whenever you want it.

---

## Section 9 — Error handling

**Goal: every error response has the same shape. No route ever returns a bare string or a Flask default HTML error page.**

### Shape

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request body failed validation",
    "details": { "name": ["Missing data for required field."] },
    "request_id": "7c2f..."
  }
}
```

### Handlers — `app/errors.py`, registered in `create_app()`

| Exception | Status | `code` | Notes |
|---|---|---|---|
| `marshmallow.ValidationError` | 422 | `validation_error` | `details` = `err.messages` |
| `werkzeug.exceptions.NotFound` | 404 | `not_found` | generic message |
| `werkzeug.exceptions.Unauthorized` | 401 | `unauthorized` | |
| `flask_jwt_extended.exceptions.NoAuthorizationError` | 401 | `unauthorized` | |
| `flask_jwt_extended.exceptions.JWTDecodeError` | 401 | `invalid_token` | |
| `werkzeug.exceptions.Forbidden` | 403 | `forbidden` | |
| `werkzeug.exceptions.RequestEntityTooLarge` | 413 | `file_too_large` | raised by `MAX_CONTENT_LENGTH` |
| `werkzeug.exceptions.UnsupportedMediaType` | 415 | `unsupported_media_type` | |
| `sqlalchemy.exc.IntegrityError` | 409 | `conflict` | duplicate slug, etc. |
| `Exception` (catch-all) | 500 | `internal_error` | generic `"An unexpected error occurred"`; full traceback goes to `app.logger`, never to the client |

### Validation helper

```python
def load_body(schema):
    try:
        return schema.load(request.get_json() or {})
    except ValidationError as err:
        raise   # caught by the global handler
```

No per-route `try/except` noise.

### Logging

- `app.logger` configured in `create_app()`:
  - Prod: JSON lines via `python-json-logger`
  - Dev: plain text
- Request-id middleware: generate a UUID per request, attach to `g.request_id`, include in every log line and in `error.request_id` so admins can paste it into a bug report and you can grep.

---

## Section 10 — Frontend integration plan

### Current state (observed)

- `src/hooks/data/useArtists.js`, `useExhibitions.js`, `useNews.js`, `useArtFairs.js`, `useLanding.js` all import JSON synchronously at module load and return `{ data, isLoading: false, error: null }` immediately.
- `useArtist(slug)` is the only async-style hook — it dynamic-imports the detail file.
- Tests under `src/hooks/data/__tests__` assume the current JSON-import shape.

### Strategy

**Hooks keep the same public signature. Internals change. No component touches `fetch` directly.** The whole migration is isolated to ~5 hook files.

### Steps (ordered)

1. **Add `src/lib/api.js`** — a single API client. Reads `VITE_API_BASE_URL` from Vite env. Exposes `api.get(path)`, `api.post(path, body, token)`, etc. Plain `fetch`; no library. Throws on non-2xx so callers can manage the state machine normally. **Applies a snake_case → camelCase transform to every response body** so the rest of the frontend sees the same field names it sees today (`heroImage`, `monumentalWorks`, `exhibitionsHistory`, `publishedAt`, ...). The reverse transform (camel → snake) is applied to request bodies on `POST`/`PUT`.
2. **Rewrite hooks one at a time**, starting with `useArtists`:
   - Same return shape: `{ data, isLoading, error }`
   - Internals switch to `useEffect` + `api.get(...)`
   - **Fallback**: on fetch error, log and fall back to the committed JSON import. Removed once prod is stable (~2–3 months).
   - **Field-rename shim in the hook**. The generic snake → camel transform in `api.js` handles most fields correctly, but two fields have semantic renames the transform can't infer. The hook applies them so components stay unchanged:
     - `heroImageUrl` → `heroImage` (on Artist, Exhibition, NewsArticle, ArtFair)
     - `exhibitionsHistory` → `exhibitions` (on Artist detail)
   - These renames are intentionally scoped to `useArtists` / `useArtist` / `useExhibitions` / `useNews` / `useArtFairs`. Components keep reading `artist.heroImage` and `artist.exhibitions` exactly as they do today.
3. **Update `__tests__`** to mock `fetch` (MSW or vitest mock). Tests shift from "assert the imported JSON shape" to "assert the hook's state machine: loading → data / loading → error."
4. **`landing.json`** (featured artist slugs) stays a frontend-only concern. `useFeaturedArtists` continues to read it and filters against `useArtists` results. When the admin UI lands, the hook switches to `GET /api/artists?featured=true` — the DB already has the `featured` column.
5. **Admin route tree (`/admin`)** is a separate spec. This backend only shapes the API contract (JWT, CORS, mutation endpoints) it will eventually consume.
6. **Prod cutover order**:
   - Push backend → Render `buildCommand` runs `pip install` + `flask db upgrade`
   - Render Shell: `flask seed` (one-time), `flask create-admin` (one-time)
   - Smoke-test via `/api/health` and a couple of `curl` calls
   - Deploy frontend with `VITE_API_BASE_URL=https://ascaso-gallery-api.onrender.com`
   - Rollback strategy: frontend JSON fallback keeps the site readable if the API 5xx's

### What stays in the frontend repo after cutover

- `src/data/*.json` — committed fallback and initial seed source. Delete only after prolonged stable prod.
- `src/hooks/data/*.js` — same filenames, same exports, new internals.
- Tests — updated to mock fetch instead of import JSON.

### Deferred to v2

- **TanStack Query.** Plain `fetch` is sufficient for v1 because the hooks already own the loading/error state machine. Upgrade path: swap hook internals to `useQuery` when caching/revalidation becomes a real concern.

---

## Open questions deferred to implementation

None. All design questions were resolved during brainstorming.

## Out-of-scope items tracked for v2

- React `/admin` route tree (separate brainstorm + spec)
- Signed direct-to-Cloudinary uploads
- Cloudinary orphan cleanup / `DELETE /api/upload/<public_id>`
- Refresh tokens + server-side revocation
- Rate limiting beyond the login guard
- Cookie-based auth (would require CSRF tokens)
- Many-to-many relationships (exhibitions ↔ artists)
- GitHub Actions CI
- TanStack Query on the frontend
