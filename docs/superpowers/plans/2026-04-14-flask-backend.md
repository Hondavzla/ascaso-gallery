# Flask Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a headless Flask + SQLAlchemy backend serving the Ascaso Gallery JSON API under `/backend`, deploy it to Render, and migrate the React frontend hooks to consume it.

**Architecture:** Flask app-factory pattern with blueprints by resource (artists, exhibitions, news, artfairs, auth, upload). SQLAlchemy ORM with JSONB columns for editorial prose blocks (bio, quote, awards, collections). Marshmallow schemas handle (de)serialization and validation. JWT auth (Flask-JWT-Extended) protects mutation routes. Cloudinary handles image uploads. Alembic (via Flask-Migrate) manages schema migrations. Pytest with in-memory SQLite for tests. Deployed to Render via `render.yaml`. Frontend React hooks keep their public signatures but switch internals from JSON imports to `fetch` calls with a snake→camel transform at the API client boundary.

**Tech Stack:** Python 3.12, Flask 3, SQLAlchemy 2, Flask-Migrate/Alembic, Marshmallow 3, marshmallow-sqlalchemy, Flask-JWT-Extended, Flask-CORS, Flask-Limiter, passlib[bcrypt], Cloudinary SDK, python-dotenv, python-json-logger, gunicorn, pytest, React + Vite (frontend).

**Spec:** `docs/superpowers/specs/2026-04-14-flask-backend-design.md`

---

## Phase 0: Conventions

- **TDD is mandatory.** Every model, schema, route, and service has a test written FIRST. No exceptions.
- **Commit after every task.** Task boundaries are commit boundaries.
- **Working directory for backend tasks:** `/Users/ricardosalcedo/projects/ascaso-gallery/backend/`. All backend commands run from there. Frontend tasks run from the repo root.
- **Test invocation:** `pytest -xvs tests/path/test_file.py::test_name` (stop on first fail, verbose, show print statements).
- **No network in tests.** Cloudinary is always mocked.

---

## Phase 1 — Scaffold the backend

### Task 1: Create backend directory structure and pin dependencies

**Files:**
- Create: `backend/.gitignore`
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/.env.example`
- Create: `backend/wsgi.py`
- Create: `backend/README.md`

- [ ] **Step 1: Create the backend directory**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery
mkdir -p backend/app/models backend/app/schemas backend/app/blueprints backend/app/services backend/fixtures/artists backend/scripts backend/tests
touch backend/app/__init__.py backend/app/models/__init__.py backend/app/schemas/__init__.py backend/app/blueprints/__init__.py backend/app/services/__init__.py backend/scripts/__init__.py backend/tests/__init__.py
```

- [ ] **Step 2: Create `backend/.gitignore`**

Content:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
.env
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# SQLite dev DB
*.db
*.db-journal

# IDE
.vscode/
.idea/
*.swp
.DS_Store
```

- [ ] **Step 3: Create `backend/requirements.txt` with pinned runtime dependencies**

Content:
```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.1
Flask-Limiter==3.8.0
marshmallow==3.22.0
marshmallow-sqlalchemy==1.1.0
SQLAlchemy==2.0.35
alembic==1.13.3
passlib[bcrypt]==1.7.4
cloudinary==1.41.0
python-dotenv==1.0.1
python-json-logger==2.0.7
gunicorn==23.0.0
psycopg2-binary==2.9.9
```

- [ ] **Step 4: Create `backend/requirements-dev.txt`**

Content:
```
-r requirements.txt
pytest==8.3.3
pytest-cov==5.0.0
```

- [ ] **Step 5: Create `backend/.env.example`**

Content:
```
FLASK_ENV=dev
FLASK_APP=wsgi.py
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me
DATABASE_URL=sqlite:///dev.db
CLOUDINARY_URL=cloudinary://<api-key>:<api-secret>@<cloud-name>
CORS_ORIGINS=http://localhost:5173
```

- [ ] **Step 6: Create `backend/wsgi.py`**

Content:
```python
import os
from dotenv import load_dotenv

if os.environ.get('FLASK_ENV', 'prod') != 'prod':
    load_dotenv()

from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'prod'))
```

- [ ] **Step 7: Create `backend/README.md`**

Content:
````markdown
# Ascaso Gallery — Backend

Flask + SQLAlchemy JSON API.

## First-run setup (dev)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env    # fill in CLOUDINARY_URL + any secrets
flask db upgrade
flask seed
flask create-admin      # interactive
flask run               # http://localhost:5000
```

## Tests

```bash
pytest
```

## Deploy

Auto-deploys to Render via `render.yaml` on push to `main`.
````

- [ ] **Step 8: Commit**

```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery
git add backend/
git commit -m "feat(backend): scaffold backend directory and pin deps"
```

---

### Task 2: Set up Python environment and verify imports

**Files:**
- No new files; this task validates the environment works before writing code.

- [ ] **Step 1: Create venv and install dev dependencies**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

Expected: all packages install successfully. If `psycopg2-binary` fails on macOS, that's fine — it's only needed in prod.

- [ ] **Step 2: Verify Flask is importable**

Run:
```bash
python -c "import flask, flask_sqlalchemy, flask_migrate, flask_jwt_extended, flask_cors, flask_limiter, marshmallow, marshmallow_sqlalchemy, cloudinary, passlib; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Verify pytest runs (no tests yet)**

Run:
```bash
pytest --co
```

Expected: `collected 0 items` — pytest finds no tests but exits 0.

- [ ] **Step 4: No commit for this task.** Environment-only.

---

### Task 3: Create `app/config.py`

**Files:**
- Create: `backend/app/config.py`
- Test: `backend/tests/test_config.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_config.py`**

Content:
```python
import os
from datetime import timedelta


def test_dev_config_defaults_to_sqlite(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'x')
    monkeypatch.setenv('JWT_SECRET_KEY', 'y')
    monkeypatch.delenv('DATABASE_URL', raising=False)
    from app.config import DevConfig
    cfg = DevConfig()
    assert cfg.SQLALCHEMY_DATABASE_URI == 'sqlite:///dev.db'
    assert cfg.DEBUG is True
    assert cfg.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert cfg.MAX_CONTENT_LENGTH == 15 * 1024 * 1024
    assert cfg.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=12)


def test_test_config_uses_memory_sqlite():
    from app.config import TestConfig
    cfg = TestConfig()
    assert cfg.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    assert cfg.TESTING is True
    assert cfg.SECRET_KEY == 'test-secret'


def test_prod_config_reads_database_url(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'x')
    monkeypatch.setenv('JWT_SECRET_KEY', 'y')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@h/db')
    from importlib import reload
    import app.config as cfg_mod
    reload(cfg_mod)
    assert cfg_mod.ProdConfig.SQLALCHEMY_DATABASE_URI == 'postgresql://u:p@h/db'
    assert cfg_mod.ProdConfig.DEBUG is False
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_config.py -xvs
```

Expected: `ModuleNotFoundError: No module named 'app.config'`

- [ ] **Step 3: Write `backend/app/config.py`**

Content:
```python
import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024
    CORS_ORIGINS = [o for o in os.environ.get('CORS_ORIGINS', '').split(',') if o]
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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')


CONFIG_MAP = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig,
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_config.py -xvs
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/config.py backend/tests/test_config.py
git commit -m "feat(backend): add config classes for dev/test/prod"
```

---

### Task 4: Create `app/extensions.py` — shared Flask extension singletons

**Files:**
- Create: `backend/app/extensions.py`

No test for this task — it's a module of singleton instances with no behavior. It's covered transitively by Task 5 (the factory uses these).

- [ ] **Step 1: Write `backend/app/extensions.py`**

Content:
```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/extensions.py
git commit -m "feat(backend): add shared extension singletons"
```

---

### Task 5: Create `app/__init__.py` — the `create_app` factory + `/api/health`

**Files:**
- Create: `backend/app/__init__.py`
- Test: `backend/tests/test_app_factory.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_app_factory.py`**

Content:
```python
def test_create_app_returns_flask_instance():
    from app import create_app
    app = create_app('test')
    assert app is not None
    assert app.config['TESTING'] is True


def test_health_route_returns_ok():
    from app import create_app
    app = create_app('test')
    with app.test_client() as client:
        resp = client.get('/api/health')
        assert resp.status_code == 200
        assert resp.get_json() == {'status': 'ok'}


def test_unknown_config_name_raises():
    from app import create_app
    import pytest
    with pytest.raises(KeyError):
        create_app('bogus')
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_app_factory.py -xvs
```

Expected: `ImportError: cannot import name 'create_app'`

- [ ] **Step 3: Write `backend/app/__init__.py`**

Content:
```python
from flask import Flask

from app.config import CONFIG_MAP
from app.extensions import db, migrate, jwt, cors, limiter


def create_app(config_name: str = 'prod') -> Flask:
    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r'/api/*': {'origins': app.config['CORS_ORIGINS'] or '*'}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_app_factory.py -xvs
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/__init__.py backend/tests/test_app_factory.py
git commit -m "feat(backend): add create_app factory and /api/health"
```

---

### Task 6: Create `app/errors.py` — centralized JSON error handlers

**Files:**
- Create: `backend/app/errors.py`
- Modify: `backend/app/__init__.py`
- Test: `backend/tests/test_errors.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_errors.py`**

Content:
```python
import pytest
from marshmallow import ValidationError


@pytest.fixture
def app():
    from app import create_app
    app = create_app('test')

    @app.get('/_boom/404')
    def boom_404():
        from flask import abort
        abort(404)

    @app.get('/_boom/500')
    def boom_500():
        raise RuntimeError('hidden detail')

    @app.get('/_boom/validation')
    def boom_validation():
        raise ValidationError({'name': ['Missing data for required field.']})

    return app


def test_404_returns_json_envelope(app):
    client = app.test_client()
    resp = client.get('/_boom/404')
    assert resp.status_code == 404
    body = resp.get_json()
    assert body['error']['code'] == 'not_found'
    assert 'request_id' in body['error']


def test_500_hides_internal_detail(app):
    client = app.test_client()
    resp = client.get('/_boom/500')
    assert resp.status_code == 500
    body = resp.get_json()
    assert body['error']['code'] == 'internal_error'
    assert body['error']['message'] == 'An unexpected error occurred'
    assert 'hidden detail' not in resp.get_data(as_text=True)


def test_validation_error_returns_422_with_details(app):
    client = app.test_client()
    resp = client.get('/_boom/validation')
    assert resp.status_code == 422
    body = resp.get_json()
    assert body['error']['code'] == 'validation_error'
    assert body['error']['details'] == {'name': ['Missing data for required field.']}
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_errors.py -xvs
```

Expected: error-handling not yet registered — 404 returns HTML, 500 returns HTML. Tests fail with JSON-parsing errors.

- [ ] **Step 3: Write `backend/app/errors.py`**

Content:
```python
import logging
import uuid

from flask import g, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import (
    NotFound,
    Unauthorized,
    Forbidden,
    RequestEntityTooLarge,
    UnsupportedMediaType,
    HTTPException,
)

logger = logging.getLogger(__name__)


def _envelope(code: str, message: str, status: int, details: dict | None = None):
    payload = {
        'error': {
            'code': code,
            'message': message,
            'request_id': getattr(g, 'request_id', None),
        }
    }
    if details is not None:
        payload['error']['details'] = details
    return jsonify(payload), status


def register_error_handlers(app):
    @app.before_request
    def _attach_request_id():
        g.request_id = uuid.uuid4().hex

    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return _envelope('validation_error', 'Request body failed validation', 422, err.messages)

    @app.errorhandler(NotFound)
    def handle_not_found(err):
        return _envelope('not_found', 'Resource not found', 404)

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(err):
        return _envelope('unauthorized', 'Authentication required', 401)

    @app.errorhandler(Forbidden)
    def handle_forbidden(err):
        return _envelope('forbidden', 'You do not have permission', 403)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_too_large(err):
        return _envelope('file_too_large', 'Uploaded file exceeds size limit', 413)

    @app.errorhandler(UnsupportedMediaType)
    def handle_bad_media(err):
        return _envelope('unsupported_media_type', 'Unsupported media type', 415)

    @app.errorhandler(IntegrityError)
    def handle_integrity(err):
        from app.extensions import db
        db.session.rollback()
        return _envelope('conflict', 'Resource already exists or violates a constraint', 409)

    @app.errorhandler(HTTPException)
    def handle_http(err):
        return _envelope(err.name.lower().replace(' ', '_'), err.description or err.name, err.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception('unhandled exception on %s %s', request.method, request.path)
        return _envelope('internal_error', 'An unexpected error occurred', 500)
```

- [ ] **Step 4: Modify `backend/app/__init__.py` to register error handlers**

Replace the `create_app` function body so it calls `register_error_handlers(app)` after extension init. The full file becomes:

```python
from flask import Flask

from app.config import CONFIG_MAP
from app.errors import register_error_handlers
from app.extensions import db, migrate, jwt, cors, limiter


def create_app(config_name: str = 'prod') -> Flask:
    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r'/api/*': {'origins': app.config['CORS_ORIGINS'] or '*'}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    register_error_handlers(app)

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    return app
```

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
pytest tests/test_errors.py tests/test_app_factory.py -xvs
```

Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/errors.py backend/app/__init__.py backend/tests/test_errors.py
git commit -m "feat(backend): centralized JSON error handlers with request-id"
```

---

## Phase 2 — Models and migrations

### Task 7: Create `app/models/admin_user.py` — `AdminUser` model

**Files:**
- Create: `backend/app/models/admin_user.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/conftest.py` (shared fixtures)
- Test: `backend/tests/test_admin_user_model.py`

- [ ] **Step 1: Write shared test fixtures — `backend/tests/conftest.py`**

Content:
```python
import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    app = create_app('test')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()
```

- [ ] **Step 2: Write the failing test — `backend/tests/test_admin_user_model.py`**

Content:
```python
def test_admin_user_can_be_created(db):
    from app.models.admin_user import AdminUser
    user = AdminUser(email='a@b.com', password_hash='hashed')
    db.session.add(user)
    db.session.commit()
    assert user.id is not None
    assert user.created_at is not None


def test_admin_user_email_is_unique(db):
    from app.models.admin_user import AdminUser
    db.session.add(AdminUser(email='dup@x.com', password_hash='h1'))
    db.session.commit()
    db.session.add(AdminUser(email='dup@x.com', password_hash='h2'))
    import pytest
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
```

- [ ] **Step 3: Run test to verify it fails**

Run:
```bash
pytest tests/test_admin_user_model.py -xvs
```

Expected: `ModuleNotFoundError: No module named 'app.models.admin_user'`

- [ ] **Step 4: Write `backend/app/models/admin_user.py`**

Content:
```python
from datetime import datetime

from app.extensions import db


class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
```

- [ ] **Step 5: Modify `backend/app/models/__init__.py`**

Content:
```python
from app.models.admin_user import AdminUser

__all__ = ['AdminUser']
```

- [ ] **Step 6: Run test to verify it passes**

Run:
```bash
pytest tests/test_admin_user_model.py -xvs
```

Expected: 2 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/admin_user.py backend/app/models/__init__.py backend/tests/conftest.py backend/tests/test_admin_user_model.py
git commit -m "feat(backend): AdminUser model + shared test fixtures"
```

---

### Task 8: Create `app/models/artist.py` — `Artist` and `ArtWork` models

**Files:**
- Create: `backend/app/models/artist.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_artist_model.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_artist_model.py`**

Content:
```python
import pytest
from sqlalchemy.exc import IntegrityError


def test_artist_can_be_created_with_jsonb_blocks(db):
    from app.models.artist import Artist
    a = Artist(
        slug='carlos-medina',
        name='Carlos Medina',
        medium='Sculpture',
        nationality='Venezuelan',
        eyebrow='Sculpture',
        hero_image_url='/x.jpg',
        featured=True,
        display_order=0,
        bio={'short': 's', 'full': ['p1', 'p2']},
        quote={'text': 't', 'attribution': 'CM', 'eyebrow': 'e'},
        awards=['A1', 'A2'],
        collections=['C1'],
        exhibitions_history=[{'year': 2024, 'items': ['x']}],
        monumental_works=[{'year': 2023, 'items': ['y']}],
    )
    db.session.add(a)
    db.session.commit()
    assert a.id is not None
    assert a.bio['short'] == 's'
    assert a.awards == ['A1', 'A2']
    assert a.created_at is not None


def test_artist_slug_unique(db):
    from app.models.artist import Artist
    db.session.add(Artist(slug='dup', name='A'))
    db.session.commit()
    db.session.add(Artist(slug='dup', name='B'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_artwork_belongs_to_artist(db):
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x', name='X')
    a.works.append(ArtWork(slug='w1', title='W1', image_url='/w1.jpg'))
    a.works.append(ArtWork(slug='w2', title='W2', image_url='/w2.jpg'))
    db.session.add(a)
    db.session.commit()
    assert len(a.works) == 2
    assert a.works[0].artist_id == a.id


def test_artwork_slug_unique_per_artist(db):
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x2', name='X')
    a.works.append(ArtWork(slug='dup', title='W', image_url='/w.jpg'))
    a.works.append(ArtWork(slug='dup', title='W2', image_url='/w2.jpg'))
    db.session.add(a)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_deleting_artist_cascades_to_artworks(db):
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x3', name='X')
    a.works.append(ArtWork(slug='w', title='W', image_url='/w.jpg'))
    db.session.add(a)
    db.session.commit()
    work_id = a.works[0].id

    db.session.delete(a)
    db.session.commit()

    assert db.session.get(ArtWork, work_id) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_artist_model.py -xvs
```

Expected: `ModuleNotFoundError: No module named 'app.models.artist'`

- [ ] **Step 3: Write `backend/app/models/artist.py`**

Content:
```python
from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from app.extensions import db


# JSONB on Postgres, JSON (text) on SQLite. Marshmallow sees both as dict/list.
JSONType = JSON().with_variant(JSONB(), 'postgresql')


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    medium = db.Column(db.String(100), nullable=True)
    nationality = db.Column(db.String(100), nullable=True)
    eyebrow = db.Column(db.String(100), nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    bio = db.Column(JSONType, nullable=True)
    quote = db.Column(JSONType, nullable=True)
    awards = db.Column(JSONType, nullable=True)
    collections = db.Column(JSONType, nullable=True)
    exhibitions_history = db.Column(JSONType, nullable=True)
    monumental_works = db.Column(JSONType, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    works = db.relationship(
        'ArtWork',
        back_populates='artist',
        cascade='all, delete-orphan',
        order_by='ArtWork.display_order',
    )


class ArtWork(db.Model):
    __tablename__ = 'artworks'
    __table_args__ = (UniqueConstraint('artist_id', 'slug', name='uq_artwork_artist_slug'),)

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False, index=True)
    slug = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    medium = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    artist = db.relationship('Artist', back_populates='works')
```

- [ ] **Step 4: Modify `backend/app/models/__init__.py`**

Content:
```python
from app.models.admin_user import AdminUser
from app.models.artist import Artist, ArtWork

__all__ = ['AdminUser', 'Artist', 'ArtWork']
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/test_artist_model.py -xvs
```

Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/artist.py backend/app/models/__init__.py backend/tests/test_artist_model.py
git commit -m "feat(backend): Artist + ArtWork models with JSONB and cascade"
```

---

### Task 9: Create `app/models/exhibition.py` — `Exhibition` model

**Files:**
- Create: `backend/app/models/exhibition.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_exhibition_model.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_exhibition_model.py`**

Content:
```python
import pytest
from sqlalchemy.exc import IntegrityError


def test_exhibition_can_be_created(db):
    from app.models.exhibition import Exhibition
    e = Exhibition(
        slug='soto-retrospective',
        title='Soto Retrospective',
        subtitle='Kinetic Origins',
        status='current',
        dates='April 10 – June 15, 2026',
        hero_image_url='/e.jpg',
        description='desc',
        display_order=0,
    )
    db.session.add(e)
    db.session.commit()
    assert e.id is not None
    assert e.status == 'current'


def test_exhibition_slug_unique(db):
    from app.models.exhibition import Exhibition
    db.session.add(Exhibition(slug='dup', title='A', status='current'))
    db.session.commit()
    db.session.add(Exhibition(slug='dup', title='B', status='current'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_exhibition_model.py -xvs
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `backend/app/models/exhibition.py`**

Content:
```python
from datetime import datetime

from app.extensions import db


class Exhibition(db.Model):
    __tablename__ = 'exhibitions'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), nullable=False, index=True)  # 'current' | 'upcoming' | 'past'
    dates = db.Column(db.String(200), nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

`status` is stored as a plain `String(20)` rather than a DB-level `ENUM` because the Marshmallow schema (Task 18) does the validation and DB enums are a headache to migrate later. Values are restricted in the schema.

- [ ] **Step 4: Modify `backend/app/models/__init__.py`**

Content:
```python
from app.models.admin_user import AdminUser
from app.models.artist import Artist, ArtWork
from app.models.exhibition import Exhibition

__all__ = ['AdminUser', 'Artist', 'ArtWork', 'Exhibition']
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/test_exhibition_model.py -xvs
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/exhibition.py backend/app/models/__init__.py backend/tests/test_exhibition_model.py
git commit -m "feat(backend): Exhibition model"
```

---

### Task 10: Create `app/models/news.py` — `NewsArticle` model

**Files:**
- Create: `backend/app/models/news.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_news_model.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_news_model.py`**

Content:
```python
from datetime import datetime


def test_news_article_published(db):
    from app.models.news import NewsArticle
    n = NewsArticle(
        slug='opening',
        title='Opening Night',
        excerpt='x',
        content='body',
        hero_image_url='/n.jpg',
        published_at=datetime(2026, 4, 1),
    )
    db.session.add(n)
    db.session.commit()
    assert n.id is not None
    assert n.published_at.year == 2026


def test_news_article_draft_has_null_published_at(db):
    from app.models.news import NewsArticle
    n = NewsArticle(slug='draft', title='Draft', published_at=None)
    db.session.add(n)
    db.session.commit()
    assert n.published_at is None
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_news_model.py -xvs
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `backend/app/models/news.py`**

Content:
```python
from datetime import datetime

from app.extensions import db


class NewsArticle(db.Model):
    __tablename__ = 'news_articles'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    excerpt = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    published_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

- [ ] **Step 4: Modify `backend/app/models/__init__.py`**

Content:
```python
from app.models.admin_user import AdminUser
from app.models.artist import Artist, ArtWork
from app.models.exhibition import Exhibition
from app.models.news import NewsArticle

__all__ = ['AdminUser', 'Artist', 'ArtWork', 'Exhibition', 'NewsArticle']
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/test_news_model.py -xvs
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/news.py backend/app/models/__init__.py backend/tests/test_news_model.py
git commit -m "feat(backend): NewsArticle model"
```

---

### Task 11: Create `app/models/artfair.py` — `ArtFair` model

**Files:**
- Create: `backend/app/models/artfair.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_artfair_model.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_artfair_model.py`**

Content:
```python
def test_artfair_can_be_created(db):
    from app.models.artfair import ArtFair
    f = ArtFair(
        slug='art-miami-2026',
        name='Art Miami 2026',
        dates='December 3–8, 2026',
        location='Miami, FL',
        booth='AM125',
        description='desc',
        hero_image_url='/f.jpg',
        year=2026,
    )
    db.session.add(f)
    db.session.commit()
    assert f.id is not None
    assert f.year == 2026
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_artfair_model.py -xvs
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `backend/app/models/artfair.py`**

Content:
```python
from datetime import datetime

from app.extensions import db


class ArtFair(db.Model):
    __tablename__ = 'art_fairs'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    dates = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    booth = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

- [ ] **Step 4: Modify `backend/app/models/__init__.py`**

Content:
```python
from app.models.admin_user import AdminUser
from app.models.artist import Artist, ArtWork
from app.models.exhibition import Exhibition
from app.models.news import NewsArticle
from app.models.artfair import ArtFair

__all__ = ['AdminUser', 'Artist', 'ArtWork', 'Exhibition', 'NewsArticle', 'ArtFair']
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/test_artfair_model.py -xvs
```

Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/artfair.py backend/app/models/__init__.py backend/tests/test_artfair_model.py
git commit -m "feat(backend): ArtFair model"
```

---

### Task 12: Initialize Flask-Migrate and generate the baseline migration

**Files:**
- Create: `backend/migrations/` (auto-generated by Flask-Migrate)
- Modify: `backend/app/__init__.py` (ensure models are imported inside `create_app` so Alembic sees them)

- [ ] **Step 1: Modify `backend/app/__init__.py` to import models during app creation**

Add `import app.models  # noqa: F401  (register models with SQLAlchemy metadata)` immediately after `db.init_app(app)`. Full file:

```python
from flask import Flask

from app.config import CONFIG_MAP
from app.errors import register_error_handlers
from app.extensions import db, migrate, jwt, cors, limiter


def create_app(config_name: str = 'prod') -> Flask:
    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)
    import app.models  # noqa: F401  -- register models with SQLAlchemy metadata
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r'/api/*': {'origins': app.config['CORS_ORIGINS'] or '*'}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    register_error_handlers(app)

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    return app
```

- [ ] **Step 2: Initialize Flask-Migrate**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery/backend
export FLASK_APP=wsgi.py FLASK_ENV=dev
flask db init
```

Expected: creates `backend/migrations/` with `alembic.ini`, `env.py`, `script.py.mako`, `versions/`.

- [ ] **Step 3: Generate the baseline migration**

Run:
```bash
flask db migrate -m "baseline: admin_users, artists, artworks, exhibitions, news_articles, art_fairs"
```

Expected: a new file at `backend/migrations/versions/<hash>_baseline.py` containing `op.create_table('admin_users', ...)`, `op.create_table('artists', ...)`, etc.

- [ ] **Step 4: Inspect the generated migration**

Read `backend/migrations/versions/<hash>_baseline.py`. Verify:
- All six tables are present.
- `artists` has JSONB-ish columns (rendered as `sa.JSON` for SQLite compatibility).
- `artworks` has the unique constraint `uq_artwork_artist_slug`.
- `news_articles.published_at` is indexed.
- `art_fairs.year` is indexed.

If anything is missing, fix the model and regenerate (`flask db downgrade base && rm backend/migrations/versions/*.py && flask db migrate -m "..."`).

- [ ] **Step 5: Apply and verify the migration works against a fresh SQLite DB**

Run:
```bash
rm -f dev.db
flask db upgrade
python -c "from app import create_app; from app.extensions import db; app = create_app('dev'); ctx = app.app_context(); ctx.push(); print(sorted(db.metadata.tables.keys()))"
```

Expected output: `['admin_users', 'art_fairs', 'artists', 'artworks', 'exhibitions', 'news_articles']`

- [ ] **Step 6: Commit**

```bash
git add backend/app/__init__.py backend/migrations/
git commit -m "feat(backend): initial alembic migration for all models"
```

---

## Phase 3 — Auth service, schemas, and routes

### Task 13: Create `app/services/auth.py` — password hashing and admin guard

**Files:**
- Create: `backend/app/services/auth.py`
- Test: `backend/tests/test_auth_service.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_auth_service.py`**

Content:
```python
def test_hash_password_returns_bcrypt():
    from app.services.auth import hash_password, verify_password
    h = hash_password('secret')
    assert h.startswith('$2')  # bcrypt prefix
    assert verify_password('secret', h) is True
    assert verify_password('wrong', h) is False


def test_hash_password_is_non_deterministic():
    from app.services.auth import hash_password
    assert hash_password('x') != hash_password('x')
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_auth_service.py -xvs
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `backend/app/services/auth.py`**

Content:
```python
import functools

from flask import abort, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from passlib.hash import bcrypt

from app.models import AdminUser


def hash_password(plain: str) -> str:
    return bcrypt.using(rounds=12).hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.verify(plain, hashed)
    except ValueError:
        return False


def admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = AdminUser.query.get(user_id)
        if not user:
            abort(401)
        g.current_admin = user
        return fn(*args, **kwargs)
    return wrapper
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_auth_service.py -xvs
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/auth.py backend/tests/test_auth_service.py
git commit -m "feat(backend): auth service with bcrypt + admin_required decorator"
```

---

### Task 14: Create `app/schemas/auth.py` and `app/blueprints/auth.py` — login and /me

**Files:**
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/blueprints/auth.py`
- Modify: `backend/app/blueprints/__init__.py`
- Modify: `backend/app/__init__.py` (register blueprint)
- Modify: `backend/app/extensions.py` (add login rate limit)
- Test: `backend/tests/test_auth_routes.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_auth_routes.py`**

Content:
```python
import pytest

from app.models import AdminUser
from app.services.auth import hash_password


@pytest.fixture
def admin(db):
    u = AdminUser(email='admin@x.com', password_hash=hash_password('pw'))
    db.session.add(u); db.session.commit()
    return u


def test_login_success(client, admin):
    resp = client.post('/api/auth/login', json={'email': 'admin@x.com', 'password': 'pw'})
    assert resp.status_code == 200
    body = resp.get_json()
    assert 'access_token' in body
    assert body['user']['email'] == 'admin@x.com'


def test_login_wrong_password_returns_generic_401(client, admin):
    resp = client.post('/api/auth/login', json={'email': 'admin@x.com', 'password': 'nope'})
    assert resp.status_code == 401
    assert resp.get_json()['error']['code'] == 'unauthorized'


def test_login_unknown_email_returns_byte_identical_401(client, admin):
    wrong_pw = client.post('/api/auth/login', json={'email': 'admin@x.com', 'password': 'nope'})
    unknown = client.post('/api/auth/login', json={'email': 'nobody@x.com', 'password': 'nope'})
    assert wrong_pw.status_code == unknown.status_code == 401
    # Bodies should be structurally identical (only request_id differs)
    a = wrong_pw.get_json()['error']
    b = unknown.get_json()['error']
    assert a['code'] == b['code']
    assert a['message'] == b['message']


def test_login_validation_error_422(client):
    resp = client.post('/api/auth/login', json={'email': 'not-an-email'})
    assert resp.status_code == 422


def test_me_requires_token(client, admin):
    resp = client.get('/api/auth/me')
    assert resp.status_code == 401


def test_me_with_valid_token(client, admin):
    login = client.post('/api/auth/login', json={'email': 'admin@x.com', 'password': 'pw'})
    token = login.get_json()['access_token']
    resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.get_json()['email'] == 'admin@x.com'
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_auth_routes.py -xvs
```

Expected: 404 or routing errors — `/api/auth/login` doesn't exist yet.

- [ ] **Step 3: Write `backend/app/schemas/auth.py`**

Content:
```python
from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class AdminUserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email()
    created_at = fields.DateTime()
    last_login_at = fields.DateTime(allow_none=True)
```

- [ ] **Step 4: Write `backend/app/blueprints/auth.py`**

Content:
```python
from datetime import datetime

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from app.extensions import db, limiter
from app.models import AdminUser
from app.schemas.auth import LoginSchema, AdminUserSchema
from app.services.auth import verify_password, admin_required

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

login_schema = LoginSchema()
user_schema = AdminUserSchema()


@bp.post('/login')
@limiter.limit('5 per minute')
def login():
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError:
        raise
    user = AdminUser.query.filter_by(email=data['email']).first()
    if not user or not verify_password(data['password'], user.password_hash):
        from flask import abort
        abort(401)
    user.last_login_at = datetime.utcnow()
    db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({'access_token': token, 'user': user_schema.dump(user)})


@bp.get('/me')
@admin_required
def me():
    return jsonify(user_schema.dump(g.current_admin))
```

- [ ] **Step 5: Write `backend/app/blueprints/__init__.py`**

Content:
```python
from app.blueprints.auth import bp as auth_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
```

- [ ] **Step 6: Modify `backend/app/__init__.py` to call `register_blueprints`**

Add the import and call. Full file:

```python
from flask import Flask

from app.blueprints import register_blueprints
from app.config import CONFIG_MAP
from app.errors import register_error_handlers
from app.extensions import db, migrate, jwt, cors, limiter


def create_app(config_name: str = 'prod') -> Flask:
    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)
    import app.models  # noqa: F401
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r'/api/*': {'origins': app.config['CORS_ORIGINS'] or '*'}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    register_error_handlers(app)
    register_blueprints(app)

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    return app
```

- [ ] **Step 7: Disable rate-limiting storage warnings in tests — modify `backend/tests/conftest.py`**

Add `app.config['RATELIMIT_ENABLED'] = False` so tests don't hit the 5/min limit when simulating many login attempts. Full `conftest.py`:

```python
import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    app = create_app('test')
    app.config['RATELIMIT_ENABLED'] = False
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()
```

- [ ] **Step 8: Run the auth tests**

Run:
```bash
pytest tests/test_auth_routes.py -xvs
```

Expected: 6 passed.

- [ ] **Step 9: Commit**

```bash
git add backend/app/schemas/auth.py backend/app/blueprints/auth.py backend/app/blueprints/__init__.py backend/app/__init__.py backend/tests/test_auth_routes.py backend/tests/conftest.py
git commit -m "feat(backend): /api/auth/login and /api/auth/me with JWT"
```

---

### Task 15: Add JWT error handlers so 401s match the global envelope

**Files:**
- Modify: `backend/app/extensions.py` (register JWT unauthorized loader)
- Test: `backend/tests/test_auth_routes.py` (add one assertion)

Flask-JWT-Extended's default unauthorized response is a plain JSON `{"msg": "..."}` — which doesn't match our `{"error": {...}}` envelope. Fix it now.

- [ ] **Step 1: Write the failing test — append to `backend/tests/test_auth_routes.py`**

Append at the end of the file:

```python
def test_me_401_uses_error_envelope(client):
    resp = client.get('/api/auth/me')
    assert resp.status_code == 401
    body = resp.get_json()
    assert 'error' in body
    assert body['error']['code'] == 'unauthorized'
```

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
pytest tests/test_auth_routes.py::test_me_401_uses_error_envelope -xvs
```

Expected: fails because Flask-JWT-Extended returns `{"msg": "Missing Authorization Header"}`.

- [ ] **Step 3: Modify `backend/app/__init__.py` to register JWT loaders after `jwt.init_app`**

Add this block after `jwt.init_app(app)`:

```python
    from flask import jsonify, g

    def _unauth(reason: str):
        return jsonify({
            'error': {
                'code': 'unauthorized',
                'message': 'Authentication required',
                'request_id': getattr(g, 'request_id', None),
            }
        }), 401

    @jwt.unauthorized_loader
    def _jwt_unauthorized(reason):
        return _unauth(reason)

    @jwt.invalid_token_loader
    def _jwt_invalid(reason):
        return _unauth(reason)

    @jwt.expired_token_loader
    def _jwt_expired(header, payload):
        return _unauth('expired')
```

- [ ] **Step 4: Run the auth tests**

Run:
```bash
pytest tests/test_auth_routes.py -xvs
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/__init__.py backend/tests/test_auth_routes.py
git commit -m "feat(backend): JWT loader errors use the shared error envelope"
```

---

### Task 16: Create `flask create-admin` CLI command

**Files:**
- Create: `backend/scripts/cli.py`
- Modify: `backend/app/__init__.py` (register CLI)
- Test: `backend/tests/test_cli_create_admin.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_cli_create_admin.py`**

Content:
```python
from app.models import AdminUser
from app.services.auth import verify_password


def test_create_admin_creates_user(app, db):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['create-admin', '--email', 'new@x.com', '--password', 'secret'])
    assert result.exit_code == 0
    assert 'created' in result.output.lower()
    u = AdminUser.query.filter_by(email='new@x.com').first()
    assert u is not None
    assert verify_password('secret', u.password_hash)


def test_create_admin_rejects_duplicate(app, db):
    runner = app.test_cli_runner()
    runner.invoke(args=['create-admin', '--email', 'dup@x.com', '--password', 'a'])
    result = runner.invoke(args=['create-admin', '--email', 'dup@x.com', '--password', 'b'])
    assert result.exit_code != 0
    assert 'already exists' in result.output.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_cli_create_admin.py -xvs
```

Expected: error — no such command `create-admin`.

- [ ] **Step 3: Write `backend/scripts/cli.py`**

Content:
```python
import click
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from app.models import AdminUser
from app.services.auth import hash_password


@click.command('create-admin')
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False)
@with_appcontext
def create_admin(email, password):
    """Create an admin user."""
    existing = AdminUser.query.filter_by(email=email).first()
    if existing:
        raise click.ClickException(f'Admin with email {email} already exists')
    user = AdminUser(email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    click.echo(f'Admin {email} created (id={user.id})')


def register_cli(app):
    app.cli.add_command(create_admin)
```

- [ ] **Step 4: Modify `backend/app/__init__.py` — register CLI inside `create_app`**

Add `from scripts.cli import register_cli` at the top and call `register_cli(app)` at the end of `create_app` (before `return app`). The top-level import won't work because `scripts` lives outside `app/` — use a local import:

```python
    from scripts.cli import register_cli
    register_cli(app)
```

Place this immediately before `return app`.

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/test_cli_create_admin.py -xvs
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/scripts/cli.py backend/app/__init__.py backend/tests/test_cli_create_admin.py
git commit -m "feat(backend): flask create-admin CLI command"
```

---

## Phase 4 — Artists blueprint (end-to-end CRUD with nested artworks)

### Task 17: Write `app/schemas/artist.py` — `ArtistSchema`, `ArtistSummarySchema`, `ArtWorkSchema`

**Files:**
- Create: `backend/app/schemas/artist.py`
- Test: `backend/tests/test_artist_schemas.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_artist_schemas.py`**

Content:
```python
import pytest
from marshmallow import ValidationError


def test_artwork_schema_roundtrip():
    from app.schemas.artist import ArtWorkSchema
    data = {'slug': 'w1', 'title': 'W1', 'image_url': '/w.jpg', 'year': 2024, 'medium': 'bronze', 'display_order': 0}
    loaded = ArtWorkSchema().load(data)
    assert loaded['slug'] == 'w1'


def test_artwork_schema_requires_title_and_image():
    from app.schemas.artist import ArtWorkSchema
    with pytest.raises(ValidationError) as err:
        ArtWorkSchema().load({'slug': 'w'})
    assert 'title' in err.value.messages
    assert 'image_url' in err.value.messages


def test_artist_schema_allows_jsonb_blocks():
    from app.schemas.artist import ArtistSchema
    data = {
        'name': 'Carlos',
        'slug': 'carlos',
        'medium': 'Sculpture',
        'bio': {'short': 's', 'full': ['a', 'b']},
        'quote': {'text': 't', 'attribution': 'c', 'eyebrow': 'e'},
        'awards': ['x'],
        'collections': ['y'],
        'exhibitions_history': [{'year': 2024, 'items': ['foo']}],
        'monumental_works': [],
    }
    loaded = ArtistSchema().load(data)
    assert loaded['bio']['short'] == 's'
    assert loaded['awards'] == ['x']


def test_artist_schema_dump_includes_works():
    from app.schemas.artist import ArtistSchema
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x', name='X')
    a.works.append(ArtWork(slug='w1', title='W1', image_url='/w.jpg'))
    dumped = ArtistSchema().dump(a)
    assert dumped['slug'] == 'x'
    assert len(dumped['works']) == 1
    assert dumped['works'][0]['slug'] == 'w1'


def test_artist_summary_schema_omits_bio():
    from app.schemas.artist import ArtistSummarySchema
    from app.models.artist import Artist
    a = Artist(slug='x', name='X', medium='Sculpture', eyebrow='S', hero_image_url='/h.jpg', featured=True, display_order=1)
    dumped = ArtistSummarySchema().dump(a)
    assert set(dumped.keys()) == {'slug', 'name', 'medium', 'eyebrow', 'hero_image_url', 'featured', 'display_order'}
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_artist_schemas.py -xvs
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `backend/app/schemas/artist.py`**

Content:
```python
from marshmallow import Schema, fields, validate


class ArtWorkSchema(Schema):
    slug = fields.String(required=True, validate=validate.Length(max=120))
    title = fields.String(required=True, validate=validate.Length(max=200))
    year = fields.Integer(allow_none=True)
    medium = fields.String(allow_none=True, validate=validate.Length(max=100))
    image_url = fields.String(required=True, validate=validate.Length(max=500))
    display_order = fields.Integer(load_default=0)
    created_at = fields.DateTime(dump_only=True)


class ArtistSummarySchema(Schema):
    slug = fields.String()
    name = fields.String()
    medium = fields.String()
    eyebrow = fields.String()
    hero_image_url = fields.String()
    featured = fields.Boolean()
    display_order = fields.Integer()


class ArtistSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=120))
    name = fields.String(required=True, validate=validate.Length(max=200))
    medium = fields.String(allow_none=True, validate=validate.Length(max=100))
    nationality = fields.String(allow_none=True, validate=validate.Length(max=100))
    eyebrow = fields.String(allow_none=True, validate=validate.Length(max=100))
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    featured = fields.Boolean(load_default=False)
    display_order = fields.Integer(load_default=0)

    bio = fields.Dict(allow_none=True)
    quote = fields.Dict(allow_none=True)
    awards = fields.List(fields.String(), allow_none=True)
    collections = fields.List(fields.String(), allow_none=True)
    exhibitions_history = fields.List(fields.Dict(), allow_none=True)
    monumental_works = fields.List(fields.Dict(), allow_none=True)

    works = fields.List(fields.Nested(ArtWorkSchema), dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_artist_schemas.py -xvs
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/artist.py backend/tests/test_artist_schemas.py
git commit -m "feat(backend): Marshmallow schemas for Artist and ArtWork"
```

---

### Task 18: Create `app/blueprints/artists.py` — public GET list and detail

**Files:**
- Create: `backend/app/blueprints/artists.py`
- Modify: `backend/app/blueprints/__init__.py`
- Test: `backend/tests/test_artists_routes.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_artists_routes.py`**

Content:
```python
import pytest

from app.models.artist import Artist, ArtWork


@pytest.fixture
def seeded(db):
    a = Artist(
        slug='carlos-medina',
        name='Carlos Medina',
        medium='Sculpture',
        eyebrow='Sculpture',
        hero_image_url='/h.jpg',
        featured=True,
        display_order=0,
        bio={'short': 's', 'full': ['p1']},
    )
    a.works.append(ArtWork(slug='w1', title='W1', image_url='/w1.jpg', display_order=0))
    b = Artist(slug='artist-two', name='Artist Two', featured=False, display_order=1)
    db.session.add_all([a, b])
    db.session.commit()
    return (a, b)


def test_list_artists_returns_envelope(client, seeded):
    resp = client.get('/api/artists')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['count'] == 2
    assert len(body['data']) == 2
    assert set(body['data'][0].keys()) == {'slug', 'name', 'medium', 'eyebrow', 'hero_image_url', 'featured', 'display_order'}


def test_list_artists_filters_featured(client, seeded):
    resp = client.get('/api/artists?featured=true')
    body = resp.get_json()
    assert body['count'] == 1
    assert body['data'][0]['slug'] == 'carlos-medina'


def test_get_artist_detail_includes_works_and_bio(client, seeded):
    resp = client.get('/api/artists/carlos-medina')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['slug'] == 'carlos-medina'
    assert body['bio']['short'] == 's'
    assert len(body['works']) == 1
    assert body['works'][0]['slug'] == 'w1'


def test_get_artist_detail_404(client):
    resp = client.get('/api/artists/nope')
    assert resp.status_code == 404
    assert resp.get_json()['error']['code'] == 'not_found'
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_artists_routes.py -xvs
```

Expected: 404 on `/api/artists`.

- [ ] **Step 3: Write `backend/app/blueprints/artists.py`**

Content:
```python
from flask import Blueprint, abort, jsonify, request

from app.models.artist import Artist
from app.schemas.artist import ArtistSchema, ArtistSummarySchema

bp = Blueprint('artists', __name__, url_prefix='/api/artists')

summary_schema = ArtistSummarySchema(many=True)
detail_schema = ArtistSchema()


@bp.get('')
def list_artists():
    query = Artist.query
    if request.args.get('featured', '').lower() == 'true':
        query = query.filter_by(featured=True)
    query = query.order_by(Artist.display_order.asc(), Artist.name.asc())
    rows = query.all()
    return jsonify({'data': summary_schema.dump(rows), 'count': len(rows)})


@bp.get('/<slug>')
def get_artist(slug):
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    return jsonify(detail_schema.dump(artist))
```

- [ ] **Step 4: Modify `backend/app/blueprints/__init__.py`**

Content:
```python
from app.blueprints.auth import bp as auth_bp
from app.blueprints.artists import bp as artists_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(artists_bp)
```

- [ ] **Step 5: Run tests**

Run:
```bash
pytest tests/test_artists_routes.py -xvs
```

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/blueprints/artists.py backend/app/blueprints/__init__.py backend/tests/test_artists_routes.py
git commit -m "feat(backend): public artists list + detail routes"
```

---

### Task 19: Add POST/PUT/DELETE routes to `app/blueprints/artists.py`

**Files:**
- Modify: `backend/app/blueprints/artists.py`
- Test: `backend/tests/test_artists_routes.py` (add tests)

- [ ] **Step 1: Append failing tests to `backend/tests/test_artists_routes.py`**

Add these fixtures and tests at the end of the file:

```python
from app.models import AdminUser
from app.services.auth import hash_password


@pytest.fixture
def admin_token(app, db):
    u = AdminUser(email='admin@x.com', password_hash=hash_password('pw'))
    db.session.add(u); db.session.commit()
    with app.test_client() as c:
        resp = c.post('/api/auth/login', json={'email': 'admin@x.com', 'password': 'pw'})
        return resp.get_json()['access_token']


@pytest.fixture
def auth_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}'}


def test_post_artist_requires_auth(client):
    resp = client.post('/api/artists', json={'slug': 'x', 'name': 'X'})
    assert resp.status_code == 401


def test_post_artist_happy_path(client, auth_headers):
    payload = {'slug': 'new-artist', 'name': 'New Artist', 'medium': 'Painting'}
    resp = client.post('/api/artists', json=payload, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body['slug'] == 'new-artist'
    assert body['id'] is not None


def test_post_artist_validation_error(client, auth_headers):
    resp = client.post('/api/artists', json={'slug': 'x'}, headers=auth_headers)
    assert resp.status_code == 422
    assert 'name' in resp.get_json()['error']['details']


def test_post_artist_duplicate_slug_409(client, auth_headers, seeded):
    resp = client.post('/api/artists', json={'slug': 'carlos-medina', 'name': 'Dupe'}, headers=auth_headers)
    assert resp.status_code == 409


def test_put_artist_partial_update(client, auth_headers, seeded):
    resp = client.put('/api/artists/carlos-medina', json={'medium': 'Painting'}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['medium'] == 'Painting'
    # other fields unchanged
    assert resp.get_json()['name'] == 'Carlos Medina'


def test_put_artist_404(client, auth_headers):
    resp = client.put('/api/artists/nope', json={'name': 'X'}, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_artist_cascades(client, auth_headers, seeded, db):
    from app.models.artist import Artist, ArtWork
    resp = client.delete('/api/artists/carlos-medina', headers=auth_headers)
    assert resp.status_code == 204
    assert Artist.query.filter_by(slug='carlos-medina').first() is None
    assert ArtWork.query.filter_by(slug='w1').first() is None


def test_delete_artist_404(client, auth_headers):
    resp = client.delete('/api/artists/nope', headers=auth_headers)
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_artists_routes.py -xvs -k "post or put or delete"
```

Expected: most fail with 405 Method Not Allowed (routes don't exist).

- [ ] **Step 3: Modify `backend/app/blueprints/artists.py` to add mutation routes**

Full file:

```python
from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.artist import Artist
from app.schemas.artist import ArtistSchema, ArtistSummarySchema
from app.services.auth import admin_required

bp = Blueprint('artists', __name__, url_prefix='/api/artists')

summary_schema = ArtistSummarySchema(many=True)
detail_schema = ArtistSchema()
load_schema = ArtistSchema()
partial_schema = ArtistSchema(partial=True)


@bp.get('')
def list_artists():
    query = Artist.query
    if request.args.get('featured', '').lower() == 'true':
        query = query.filter_by(featured=True)
    query = query.order_by(Artist.display_order.asc(), Artist.name.asc())
    rows = query.all()
    return jsonify({'data': summary_schema.dump(rows), 'count': len(rows)})


@bp.get('/<slug>')
def get_artist(slug):
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    return jsonify(detail_schema.dump(artist))


@bp.post('')
@admin_required
def create_artist():
    data = load_schema.load(request.get_json() or {})
    artist = Artist(**data)
    db.session.add(artist)
    db.session.commit()
    return jsonify(detail_schema.dump(artist)), 201


@bp.put('/<slug>')
@admin_required
def update_artist(slug):
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    data = partial_schema.load(request.get_json() or {})
    for key, value in data.items():
        setattr(artist, key, value)
    db.session.commit()
    return jsonify(detail_schema.dump(artist))


@bp.delete('/<slug>')
@admin_required
def delete_artist(slug):
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    db.session.delete(artist)
    db.session.commit()
    return '', 204
```

- [ ] **Step 4: Run all artist tests**

Run:
```bash
pytest tests/test_artists_routes.py -xvs
```

Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/blueprints/artists.py backend/tests/test_artists_routes.py
git commit -m "feat(backend): POST/PUT/DELETE routes for artists"
```

---

### Task 20: Add nested artwork CRUD under `/api/artists/<slug>/artworks`

**Files:**
- Modify: `backend/app/blueprints/artists.py`
- Test: `backend/tests/test_artworks_routes.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_artworks_routes.py`**

Content:
```python
import pytest

from app.models import AdminUser
from app.models.artist import Artist
from app.services.auth import hash_password


@pytest.fixture
def artist(db):
    a = Artist(slug='x', name='X')
    db.session.add(a); db.session.commit()
    return a


@pytest.fixture
def auth_headers(app, db):
    u = AdminUser(email='a@x.com', password_hash=hash_password('pw'))
    db.session.add(u); db.session.commit()
    resp = app.test_client().post('/api/auth/login', json={'email': 'a@x.com', 'password': 'pw'})
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_create_artwork(client, artist, auth_headers):
    resp = client.post(
        f'/api/artists/{artist.slug}/artworks',
        json={'slug': 'w1', 'title': 'W1', 'image_url': '/w.jpg'},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body['slug'] == 'w1'


def test_create_artwork_404_unknown_artist(client, auth_headers):
    resp = client.post(
        '/api/artists/nope/artworks',
        json={'slug': 'w', 'title': 'W', 'image_url': '/w.jpg'},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_create_artwork_requires_auth(client, artist):
    resp = client.post(f'/api/artists/{artist.slug}/artworks', json={'slug': 'w', 'title': 'W', 'image_url': '/w.jpg'})
    assert resp.status_code == 401


def test_update_artwork(client, artist, auth_headers, db):
    from app.models.artist import ArtWork
    w = ArtWork(artist_id=artist.id, slug='w1', title='Old', image_url='/w.jpg')
    db.session.add(w); db.session.commit()

    resp = client.put(
        f'/api/artists/{artist.slug}/artworks/w1',
        json={'title': 'New'},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()['title'] == 'New'


def test_delete_artwork(client, artist, auth_headers, db):
    from app.models.artist import ArtWork
    w = ArtWork(artist_id=artist.id, slug='w1', title='W', image_url='/w.jpg')
    db.session.add(w); db.session.commit()

    resp = client.delete(f'/api/artists/{artist.slug}/artworks/w1', headers=auth_headers)
    assert resp.status_code == 204
    assert ArtWork.query.filter_by(artist_id=artist.id, slug='w1').first() is None
```

- [ ] **Step 2: Run to verify it fails**

Run:
```bash
pytest tests/test_artworks_routes.py -xvs
```

Expected: 404s / 405s — routes don't exist.

- [ ] **Step 3: Append nested artwork routes to `backend/app/blueprints/artists.py`**

Add this at the bottom of the file:

```python
from app.models.artist import ArtWork
from app.schemas.artist import ArtWorkSchema

artwork_schema = ArtWorkSchema()
artwork_partial_schema = ArtWorkSchema(partial=True)


def _get_artist_or_404(slug: str) -> Artist:
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    return artist


@bp.post('/<slug>/artworks')
@admin_required
def create_artwork(slug):
    artist = _get_artist_or_404(slug)
    data = artwork_schema.load(request.get_json() or {})
    work = ArtWork(artist_id=artist.id, **data)
    db.session.add(work)
    db.session.commit()
    return jsonify(artwork_schema.dump(work)), 201


@bp.put('/<slug>/artworks/<work_slug>')
@admin_required
def update_artwork(slug, work_slug):
    artist = _get_artist_or_404(slug)
    work = ArtWork.query.filter_by(artist_id=artist.id, slug=work_slug).first()
    if not work:
        abort(404)
    data = artwork_partial_schema.load(request.get_json() or {})
    for key, value in data.items():
        setattr(work, key, value)
    db.session.commit()
    return jsonify(artwork_schema.dump(work))


@bp.delete('/<slug>/artworks/<work_slug>')
@admin_required
def delete_artwork(slug, work_slug):
    artist = _get_artist_or_404(slug)
    work = ArtWork.query.filter_by(artist_id=artist.id, slug=work_slug).first()
    if not work:
        abort(404)
    db.session.delete(work)
    db.session.commit()
    return '', 204
```

- [ ] **Step 4: Run tests**

Run:
```bash
pytest tests/test_artworks_routes.py tests/test_artists_routes.py -xvs
```

Expected: all passing (5 new + 12 existing = 17).

- [ ] **Step 5: Commit**

```bash
git add backend/app/blueprints/artists.py backend/tests/test_artworks_routes.py
git commit -m "feat(backend): nested artwork CRUD under /api/artists/<slug>/artworks"
```

---

## Phase 5 — Other resources (Exhibitions, News, Art Fairs)

### Task 21: Create `app/schemas/exhibition.py` and `app/blueprints/exhibitions.py`

**Files:**
- Create: `backend/app/schemas/exhibition.py`
- Create: `backend/app/blueprints/exhibitions.py`
- Modify: `backend/app/blueprints/__init__.py`
- Test: `backend/tests/test_exhibitions_routes.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_exhibitions_routes.py`**

Content:
```python
import pytest

from app.models import AdminUser
from app.models.exhibition import Exhibition
from app.services.auth import hash_password


@pytest.fixture
def auth_headers(app, db):
    u = AdminUser(email='a@x.com', password_hash=hash_password('pw'))
    db.session.add(u); db.session.commit()
    token = app.test_client().post('/api/auth/login', json={'email': 'a@x.com', 'password': 'pw'}).get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def seeded(db):
    db.session.add_all([
        Exhibition(slug='current-one', title='Current', status='current', dates='Now'),
        Exhibition(slug='past-one', title='Past', status='past', dates='Was'),
        Exhibition(slug='upcoming-one', title='Upcoming', status='upcoming', dates='Soon'),
    ])
    db.session.commit()


def test_list_exhibitions(client, seeded):
    resp = client.get('/api/exhibitions')
    assert resp.status_code == 200
    assert resp.get_json()['count'] == 3


def test_list_exhibitions_filter_status(client, seeded):
    resp = client.get('/api/exhibitions?status=current')
    body = resp.get_json()
    assert body['count'] == 1
    assert body['data'][0]['slug'] == 'current-one'


def test_get_exhibition_detail(client, seeded):
    resp = client.get('/api/exhibitions/current-one')
    assert resp.status_code == 200
    assert resp.get_json()['title'] == 'Current'


def test_get_exhibition_404(client):
    resp = client.get('/api/exhibitions/nope')
    assert resp.status_code == 404


def test_create_exhibition(client, auth_headers):
    payload = {'slug': 'new', 'title': 'New', 'status': 'upcoming', 'dates': 'Soon'}
    resp = client.post('/api/exhibitions', json=payload, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['slug'] == 'new'


def test_create_exhibition_invalid_status(client, auth_headers):
    resp = client.post('/api/exhibitions', json={'slug': 'x', 'title': 'X', 'status': 'nope'}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_exhibition_requires_auth(client):
    resp = client.post('/api/exhibitions', json={'slug': 'x', 'title': 'X', 'status': 'current'})
    assert resp.status_code == 401


def test_update_exhibition(client, auth_headers, seeded):
    resp = client.put('/api/exhibitions/current-one', json={'title': 'Updated'}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['title'] == 'Updated'


def test_delete_exhibition(client, auth_headers, seeded):
    resp = client.delete('/api/exhibitions/current-one', headers=auth_headers)
    assert resp.status_code == 204
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_exhibitions_routes.py -xvs
```

Expected: 404 — routes don't exist.

- [ ] **Step 3: Write `backend/app/schemas/exhibition.py`**

Content:
```python
from marshmallow import Schema, fields, validate


class ExhibitionSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=120))
    title = fields.String(required=True, validate=validate.Length(max=200))
    subtitle = fields.String(allow_none=True, validate=validate.Length(max=300))
    status = fields.String(required=True, validate=validate.OneOf(['current', 'upcoming', 'past']))
    dates = fields.String(allow_none=True, validate=validate.Length(max=200))
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    description = fields.String(allow_none=True)
    display_order = fields.Integer(load_default=0)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
```

- [ ] **Step 4: Write `backend/app/blueprints/exhibitions.py`**

Content:
```python
from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.exhibition import Exhibition
from app.schemas.exhibition import ExhibitionSchema
from app.services.auth import admin_required

bp = Blueprint('exhibitions', __name__, url_prefix='/api/exhibitions')

schema = ExhibitionSchema()
many_schema = ExhibitionSchema(many=True)
partial = ExhibitionSchema(partial=True)


@bp.get('')
def list_exhibitions():
    query = Exhibition.query
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Exhibition.display_order.asc(), Exhibition.id.asc())
    rows = query.all()
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@bp.get('/<slug>')
def get_exhibition(slug):
    row = Exhibition.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    return jsonify(schema.dump(row))


@bp.post('')
@admin_required
def create_exhibition():
    data = schema.load(request.get_json() or {})
    row = Exhibition(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(schema.dump(row)), 201


@bp.put('/<slug>')
@admin_required
def update_exhibition(slug):
    row = Exhibition.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    data = partial.load(request.get_json() or {})
    for key, value in data.items():
        setattr(row, key, value)
    db.session.commit()
    return jsonify(schema.dump(row))


@bp.delete('/<slug>')
@admin_required
def delete_exhibition(slug):
    row = Exhibition.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    db.session.delete(row)
    db.session.commit()
    return '', 204
```

- [ ] **Step 5: Modify `backend/app/blueprints/__init__.py`**

Content:
```python
from app.blueprints.auth import bp as auth_bp
from app.blueprints.artists import bp as artists_bp
from app.blueprints.exhibitions import bp as exhibitions_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(artists_bp)
    app.register_blueprint(exhibitions_bp)
```

- [ ] **Step 6: Run tests**

Run:
```bash
pytest tests/test_exhibitions_routes.py -xvs
```

Expected: 9 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas/exhibition.py backend/app/blueprints/exhibitions.py backend/app/blueprints/__init__.py backend/tests/test_exhibitions_routes.py
git commit -m "feat(backend): exhibitions CRUD"
```

---

### Task 22: Create `app/schemas/news.py` and `app/blueprints/news.py` (with draft visibility)

**Files:**
- Create: `backend/app/schemas/news.py`
- Create: `backend/app/blueprints/news.py`
- Modify: `backend/app/blueprints/__init__.py`
- Test: `backend/tests/test_news_routes.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_news_routes.py`**

Content:
```python
from datetime import datetime, timedelta

import pytest

from app.models import AdminUser
from app.models.news import NewsArticle
from app.services.auth import hash_password


@pytest.fixture
def auth_headers(app, db):
    u = AdminUser(email='a@x.com', password_hash=hash_password('pw'))
    db.session.add(u); db.session.commit()
    token = app.test_client().post('/api/auth/login', json={'email': 'a@x.com', 'password': 'pw'}).get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def seeded(db):
    now = datetime.utcnow()
    db.session.add_all([
        NewsArticle(slug='published-one', title='P1', published_at=now - timedelta(days=2)),
        NewsArticle(slug='published-two', title='P2', published_at=now - timedelta(days=1)),
        NewsArticle(slug='draft-one', title='D1', published_at=None),
    ])
    db.session.commit()


def test_public_list_hides_drafts(client, seeded):
    resp = client.get('/api/news')
    body = resp.get_json()
    assert body['count'] == 2
    slugs = [r['slug'] for r in body['data']]
    assert 'draft-one' not in slugs


def test_public_list_orders_newest_first(client, seeded):
    body = client.get('/api/news').get_json()
    assert body['data'][0]['slug'] == 'published-two'


def test_admin_list_includes_drafts(client, seeded, auth_headers):
    resp = client.get('/api/news?drafts=true', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['count'] == 3


def test_admin_list_drafts_requires_auth(client, seeded):
    resp = client.get('/api/news?drafts=true')
    assert resp.status_code == 401


def test_public_detail_404_on_draft(client, seeded):
    resp = client.get('/api/news/draft-one')
    assert resp.status_code == 404


def test_public_detail_published(client, seeded):
    resp = client.get('/api/news/published-one')
    assert resp.status_code == 200


def test_create_news(client, auth_headers):
    resp = client.post(
        '/api/news',
        json={'slug': 'new', 'title': 'New', 'excerpt': 'e', 'content': 'c'},
        headers=auth_headers,
    )
    assert resp.status_code == 201


def test_update_news(client, auth_headers, seeded):
    resp = client.put('/api/news/published-one', json={'title': 'Updated'}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['title'] == 'Updated'


def test_delete_news(client, auth_headers, seeded):
    resp = client.delete('/api/news/published-one', headers=auth_headers)
    assert resp.status_code == 204
```

- [ ] **Step 2: Run to verify it fails**

Run:
```bash
pytest tests/test_news_routes.py -xvs
```

Expected: 404s.

- [ ] **Step 3: Write `backend/app/schemas/news.py`**

Content:
```python
from marshmallow import Schema, fields, validate


class NewsArticleSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=200))
    title = fields.String(required=True, validate=validate.Length(max=300))
    excerpt = fields.String(allow_none=True, validate=validate.Length(max=500))
    content = fields.String(allow_none=True)
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    published_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
```

- [ ] **Step 4: Write `backend/app/blueprints/news.py`**

Content:
```python
from datetime import datetime

from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.news import NewsArticle
from app.schemas.news import NewsArticleSchema
from app.services.auth import admin_required

bp = Blueprint('news', __name__, url_prefix='/api/news')

schema = NewsArticleSchema()
many_schema = NewsArticleSchema(many=True)
partial = NewsArticleSchema(partial=True)


def _is_drafts_request() -> bool:
    return request.args.get('drafts', '').lower() == 'true'


@bp.get('')
def list_news():
    if _is_drafts_request():
        # Admin-only path: delegate to a decorated helper so the main handler stays clean.
        return _list_news_admin()
    now = datetime.utcnow()
    rows = (
        NewsArticle.query
        .filter(NewsArticle.published_at.isnot(None))
        .filter(NewsArticle.published_at <= now)
        .order_by(NewsArticle.published_at.desc())
        .all()
    )
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@admin_required
def _list_news_admin():
    rows = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@bp.get('/<slug>')
def get_news(slug):
    row = NewsArticle.query.filter_by(slug=slug).first()
    if not row or row.published_at is None or row.published_at > datetime.utcnow():
        abort(404)
    return jsonify(schema.dump(row))


@bp.post('')
@admin_required
def create_news():
    data = schema.load(request.get_json() or {})
    row = NewsArticle(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(schema.dump(row)), 201


@bp.put('/<slug>')
@admin_required
def update_news(slug):
    row = NewsArticle.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    data = partial.load(request.get_json() or {})
    for key, value in data.items():
        setattr(row, key, value)
    db.session.commit()
    return jsonify(schema.dump(row))


@bp.delete('/<slug>')
@admin_required
def delete_news(slug):
    row = NewsArticle.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    db.session.delete(row)
    db.session.commit()
    return '', 204
```

- [ ] **Step 5: Modify `backend/app/blueprints/__init__.py`**

Content:
```python
from app.blueprints.auth import bp as auth_bp
from app.blueprints.artists import bp as artists_bp
from app.blueprints.exhibitions import bp as exhibitions_bp
from app.blueprints.news import bp as news_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(artists_bp)
    app.register_blueprint(exhibitions_bp)
    app.register_blueprint(news_bp)
```

- [ ] **Step 6: Run tests**

Run:
```bash
pytest tests/test_news_routes.py -xvs
```

Expected: 9 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas/news.py backend/app/blueprints/news.py backend/app/blueprints/__init__.py backend/tests/test_news_routes.py
git commit -m "feat(backend): news CRUD with draft visibility"
```

---

### Task 23: Create `app/schemas/artfair.py` and `app/blueprints/artfairs.py`

**Files:**
- Create: `backend/app/schemas/artfair.py`
- Create: `backend/app/blueprints/artfairs.py`
- Modify: `backend/app/blueprints/__init__.py`
- Test: `backend/tests/test_artfairs_routes.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_artfairs_routes.py`**

Content:
```python
import pytest

from app.models import AdminUser
from app.models.artfair import ArtFair
from app.services.auth import hash_password


@pytest.fixture
def auth_headers(app, db):
    u = AdminUser(email='a@x.com', password_hash=hash_password('pw'))
    db.session.add(u); db.session.commit()
    token = app.test_client().post('/api/auth/login', json={'email': 'a@x.com', 'password': 'pw'}).get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def seeded(db):
    db.session.add_all([
        ArtFair(slug='am-2026', name='AM 2026', dates='Dec 2026', year=2026),
        ArtFair(slug='am-2025', name='AM 2025', dates='Dec 2025', year=2025),
        ArtFair(slug='arco-2025', name='ARCO 2025', dates='Feb 2025', year=2025),
    ])
    db.session.commit()


def test_list_orders_desc_by_year(client, seeded):
    body = client.get('/api/artfairs').get_json()
    assert body['count'] == 3
    assert body['data'][0]['slug'] == 'am-2026'


def test_list_filter_year(client, seeded):
    body = client.get('/api/artfairs?year=2025').get_json()
    assert body['count'] == 2
    assert all(f['year'] == 2025 for f in body['data'])


def test_latest_returns_highest_year(client, seeded):
    resp = client.get('/api/artfairs/latest')
    assert resp.status_code == 200
    assert resp.get_json()['slug'] == 'am-2026'


def test_latest_empty(client):
    resp = client.get('/api/artfairs/latest')
    assert resp.status_code == 404


def test_get_detail(client, seeded):
    resp = client.get('/api/artfairs/am-2026')
    assert resp.status_code == 200
    assert resp.get_json()['year'] == 2026


def test_create(client, auth_headers):
    resp = client.post(
        '/api/artfairs',
        json={'slug': 'new', 'name': 'New', 'year': 2027},
        headers=auth_headers,
    )
    assert resp.status_code == 201


def test_create_requires_auth(client):
    resp = client.post('/api/artfairs', json={'slug': 'x', 'name': 'X', 'year': 2027})
    assert resp.status_code == 401


def test_update(client, seeded, auth_headers):
    resp = client.put('/api/artfairs/am-2026', json={'name': 'Updated'}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['name'] == 'Updated'


def test_delete(client, seeded, auth_headers):
    resp = client.delete('/api/artfairs/am-2026', headers=auth_headers)
    assert resp.status_code == 204
```

- [ ] **Step 2: Run to verify it fails**

Run:
```bash
pytest tests/test_artfairs_routes.py -xvs
```

Expected: 404s.

- [ ] **Step 3: Write `backend/app/schemas/artfair.py`**

Content:
```python
from marshmallow import Schema, fields, validate


class ArtFairSchema(Schema):
    id = fields.Integer(dump_only=True)
    slug = fields.String(required=True, validate=validate.Length(max=120))
    name = fields.String(required=True, validate=validate.Length(max=200))
    dates = fields.String(allow_none=True, validate=validate.Length(max=200))
    location = fields.String(allow_none=True, validate=validate.Length(max=200))
    booth = fields.String(allow_none=True, validate=validate.Length(max=50))
    description = fields.String(allow_none=True)
    hero_image_url = fields.String(allow_none=True, validate=validate.Length(max=500))
    year = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
```

- [ ] **Step 4: Write `backend/app/blueprints/artfairs.py`**

Content:
```python
from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.artfair import ArtFair
from app.schemas.artfair import ArtFairSchema
from app.services.auth import admin_required

bp = Blueprint('artfairs', __name__, url_prefix='/api/artfairs')

schema = ArtFairSchema()
many_schema = ArtFairSchema(many=True)
partial = ArtFairSchema(partial=True)


@bp.get('')
def list_artfairs():
    query = ArtFair.query
    year = request.args.get('year')
    if year:
        query = query.filter_by(year=int(year))
    query = query.order_by(ArtFair.year.desc(), ArtFair.name.asc())
    rows = query.all()
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@bp.get('/latest')
def latest_artfair():
    row = ArtFair.query.order_by(ArtFair.year.desc(), ArtFair.id.desc()).first()
    if not row:
        abort(404)
    return jsonify(schema.dump(row))


@bp.get('/<slug>')
def get_artfair(slug):
    row = ArtFair.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    return jsonify(schema.dump(row))


@bp.post('')
@admin_required
def create_artfair():
    data = schema.load(request.get_json() or {})
    row = ArtFair(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(schema.dump(row)), 201


@bp.put('/<slug>')
@admin_required
def update_artfair(slug):
    row = ArtFair.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    data = partial.load(request.get_json() or {})
    for key, value in data.items():
        setattr(row, key, value)
    db.session.commit()
    return jsonify(schema.dump(row))


@bp.delete('/<slug>')
@admin_required
def delete_artfair(slug):
    row = ArtFair.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    db.session.delete(row)
    db.session.commit()
    return '', 204
```

Note: `/latest` must be declared **before** `/<slug>` so Flask doesn't route `latest` into `get_artfair` as a slug.

- [ ] **Step 5: Modify `backend/app/blueprints/__init__.py`**

Content:
```python
from app.blueprints.auth import bp as auth_bp
from app.blueprints.artists import bp as artists_bp
from app.blueprints.exhibitions import bp as exhibitions_bp
from app.blueprints.news import bp as news_bp
from app.blueprints.artfairs import bp as artfairs_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(artists_bp)
    app.register_blueprint(exhibitions_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(artfairs_bp)
```

- [ ] **Step 6: Run tests**

Run:
```bash
pytest tests/test_artfairs_routes.py -xvs
```

Expected: 9 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas/artfair.py backend/app/blueprints/artfairs.py backend/app/blueprints/__init__.py backend/tests/test_artfairs_routes.py
git commit -m "feat(backend): art fairs CRUD with /latest convenience"
```

---

## Phase 6 — Upload flow

### Task 24: Create `app/services/cloudinary.py` with magic-byte sniffing

**Files:**
- Create: `backend/app/services/cloudinary.py`
- Test: `backend/tests/test_cloudinary_service.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_cloudinary_service.py`**

Content:
```python
import io
import pytest

# Sample magic-byte prefixes
JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 20
PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20
WEBP_RIFF = b'RIFF\x00\x00\x00\x00WEBP' + b'\x00' * 10
GIF = b'GIF89a' + b'\x00' * 20


class FakeFile:
    def __init__(self, data: bytes, mimetype: str, filename: str = 'f.jpg'):
        self.stream = io.BytesIO(data)
        self.mimetype = mimetype
        self.filename = filename

    def read(self, n=-1):
        return self.stream.read(n)

    def seek(self, pos, whence=0):
        return self.stream.seek(pos, whence)


def test_validates_jpeg():
    from app.services.cloudinary import _validate_image_bytes
    _validate_image_bytes(FakeFile(JPEG, 'image/jpeg'))  # no raise


def test_validates_png():
    from app.services.cloudinary import _validate_image_bytes
    _validate_image_bytes(FakeFile(PNG, 'image/png'))


def test_validates_webp():
    from app.services.cloudinary import _validate_image_bytes
    _validate_image_bytes(FakeFile(WEBP_RIFF, 'image/webp'))


def test_rejects_bad_mime():
    from app.services.cloudinary import _validate_image_bytes
    from werkzeug.exceptions import UnsupportedMediaType
    with pytest.raises(UnsupportedMediaType):
        _validate_image_bytes(FakeFile(JPEG, 'image/gif'))


def test_rejects_mime_magic_mismatch():
    from app.services.cloudinary import _validate_image_bytes
    from werkzeug.exceptions import UnsupportedMediaType
    with pytest.raises(UnsupportedMediaType):
        _validate_image_bytes(FakeFile(GIF, 'image/jpeg'))


def test_upload_image_calls_cloudinary(monkeypatch):
    from app.services import cloudinary as svc
    captured = {}

    def fake_upload(file, **kwargs):
        captured['called'] = True
        captured['kwargs'] = kwargs
        return {
            'secure_url': 'https://res.cloudinary.com/x/image.jpg',
            'public_id': 'ascaso-gallery/abc',
            'width': 800,
            'height': 600,
            'format': 'jpg',
            'bytes': 12345,
        }

    monkeypatch.setattr(svc.cloudinary.uploader, 'upload', fake_upload)
    result = svc.upload_image(FakeFile(JPEG, 'image/jpeg'))
    assert captured['called']
    assert captured['kwargs']['folder'] == 'ascaso-gallery'
    assert result['url'] == 'https://res.cloudinary.com/x/image.jpg'
    assert result['public_id'] == 'ascaso-gallery/abc'
    assert result['width'] == 800
```

- [ ] **Step 2: Run to verify it fails**

Run:
```bash
pytest tests/test_cloudinary_service.py -xvs
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `backend/app/services/cloudinary.py`**

Content:
```python
import cloudinary
import cloudinary.uploader
from werkzeug.exceptions import UnsupportedMediaType

ALLOWED_MIMES = {'image/jpeg', 'image/png', 'image/webp'}

MAGIC_BYTES = {
    'image/jpeg': [b'\xff\xd8\xff'],
    'image/png': [b'\x89PNG\r\n\x1a\n'],
    'image/webp': [b'RIFF'],  # followed by 4 bytes size, then 'WEBP'
}


def _validate_image_bytes(file_storage) -> None:
    mimetype = file_storage.mimetype
    if mimetype not in ALLOWED_MIMES:
        raise UnsupportedMediaType(f'Unsupported mime type: {mimetype}')

    file_storage.seek(0)
    head = file_storage.read(12)
    file_storage.seek(0)

    if mimetype == 'image/webp':
        ok = head.startswith(b'RIFF') and head[8:12] == b'WEBP'
    else:
        ok = any(head.startswith(sig) for sig in MAGIC_BYTES[mimetype])

    if not ok:
        raise UnsupportedMediaType('File bytes do not match declared mime type')


def upload_image(file_storage) -> dict:
    _validate_image_bytes(file_storage)
    result = cloudinary.uploader.upload(
        file_storage,
        folder='ascaso-gallery',
        resource_type='image',
    )
    return {
        'url': result['secure_url'],
        'public_id': result['public_id'],
        'width': result.get('width'),
        'height': result.get('height'),
        'format': result.get('format'),
        'bytes': result.get('bytes'),
    }
```

- [ ] **Step 4: Run tests**

Run:
```bash
pytest tests/test_cloudinary_service.py -xvs
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/cloudinary.py backend/tests/test_cloudinary_service.py
git commit -m "feat(backend): cloudinary service with magic-byte validation"
```

---

### Task 25: Create `app/blueprints/upload.py` — `POST /api/upload`

**Files:**
- Create: `backend/app/blueprints/upload.py`
- Modify: `backend/app/blueprints/__init__.py`
- Modify: `backend/app/__init__.py` (configure cloudinary in factory)
- Test: `backend/tests/test_upload_routes.py`

- [ ] **Step 1: Write the failing test — `backend/tests/test_upload_routes.py`**

Content:
```python
import io

import pytest

from app.models import AdminUser
from app.services.auth import hash_password


JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 200


@pytest.fixture
def auth_headers(app, db):
    u = AdminUser(email='a@x.com', password_hash=hash_password('pw'))
    db.session.add(u); db.session.commit()
    token = app.test_client().post('/api/auth/login', json={'email': 'a@x.com', 'password': 'pw'}).get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def mock_cloudinary(monkeypatch):
    from app.services import cloudinary as svc

    def fake_upload(file, **kwargs):
        return {
            'secure_url': 'https://res.cloudinary.com/x/test.jpg',
            'public_id': 'ascaso-gallery/test',
            'width': 800,
            'height': 600,
            'format': 'jpg',
            'bytes': 4096,
        }

    monkeypatch.setattr(svc.cloudinary.uploader, 'upload', fake_upload)


def test_upload_happy_path(client, auth_headers, mock_cloudinary):
    data = {'file': (io.BytesIO(JPEG), 'portrait.jpg', 'image/jpeg')}
    resp = client.post('/api/upload', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 201
    body = resp.get_json()
    assert body['url'] == 'https://res.cloudinary.com/x/test.jpg'
    assert body['public_id'] == 'ascaso-gallery/test'


def test_upload_requires_auth(client):
    data = {'file': (io.BytesIO(JPEG), 'p.jpg', 'image/jpeg')}
    resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 401


def test_upload_rejects_wrong_mime(client, auth_headers, mock_cloudinary):
    data = {'file': (io.BytesIO(JPEG), 'p.gif', 'image/gif')}
    resp = client.post('/api/upload', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 415


def test_upload_rejects_mime_magic_mismatch(client, auth_headers, mock_cloudinary):
    gif_bytes = b'GIF89a' + b'\x00' * 100
    data = {'file': (io.BytesIO(gif_bytes), 'p.jpg', 'image/jpeg')}
    resp = client.post('/api/upload', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 415


def test_upload_rejects_oversize(client, auth_headers, mock_cloudinary):
    big = b'\xff\xd8\xff' + b'\x00' * (15 * 1024 * 1024 + 100)
    data = {'file': (io.BytesIO(big), 'big.jpg', 'image/jpeg')}
    resp = client.post('/api/upload', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 413


def test_upload_missing_file(client, auth_headers):
    resp = client.post('/api/upload', data={}, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 422
```

- [ ] **Step 2: Run to verify it fails**

Run:
```bash
pytest tests/test_upload_routes.py -xvs
```

Expected: 404.

- [ ] **Step 3: Write `backend/app/blueprints/upload.py`**

Content:
```python
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.services.auth import admin_required
from app.services.cloudinary import upload_image

bp = Blueprint('upload', __name__, url_prefix='/api/upload')


@bp.post('')
@admin_required
def upload():
    file_storage = request.files.get('file')
    if file_storage is None:
        raise ValidationError({'file': ['Missing file in multipart/form-data']})
    result = upload_image(file_storage)
    return jsonify(result), 201
```

- [ ] **Step 4: Modify `backend/app/blueprints/__init__.py`**

Content:
```python
from app.blueprints.auth import bp as auth_bp
from app.blueprints.artists import bp as artists_bp
from app.blueprints.exhibitions import bp as exhibitions_bp
from app.blueprints.news import bp as news_bp
from app.blueprints.artfairs import bp as artfairs_bp
from app.blueprints.upload import bp as upload_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(artists_bp)
    app.register_blueprint(exhibitions_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(artfairs_bp)
    app.register_blueprint(upload_bp)
```

- [ ] **Step 5: Modify `backend/app/__init__.py` — configure Cloudinary inside `create_app`**

Add this after `limiter.init_app(app)`:

```python
    import cloudinary
    if app.config.get('CLOUDINARY_URL'):
        cloudinary.config(cloudinary_url=app.config['CLOUDINARY_URL'])
```

- [ ] **Step 6: Run tests**

Run:
```bash
pytest tests/test_upload_routes.py -xvs
```

Expected: 6 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/app/blueprints/upload.py backend/app/blueprints/__init__.py backend/app/__init__.py backend/tests/test_upload_routes.py
git commit -m "feat(backend): POST /api/upload with Cloudinary proxy"
```

---

## Phase 7 — Seeding

### Task 26: Copy frontend JSON to `backend/fixtures/` and add `flask seed`

**Files:**
- Create: `backend/fixtures/artists/index.json` (copy of frontend)
- Create: `backend/fixtures/artists/carlos-medina.json` (copy)
- Create: `backend/fixtures/exhibitions.json`
- Create: `backend/fixtures/news.json`
- Create: `backend/fixtures/artfairs.json`
- Create: `backend/fixtures/landing.json` (copy of frontend)
- Modify: `backend/scripts/cli.py`
- Test: `backend/tests/test_cli_seed.py`

- [ ] **Step 1: Copy existing frontend JSON data into `backend/fixtures/`**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery
cp src/data/artists/index.json backend/fixtures/artists/index.json
cp src/data/artists/carlos-medina.json backend/fixtures/artists/carlos-medina.json
cp src/data/landing.json backend/fixtures/landing.json
```

- [ ] **Step 2: Create `backend/fixtures/exhibitions.json`**

Inspect `src/data/exhibitions/index.json` to see the existing data shape and copy it. If that file only has summary data, port what's there into an array of full records matching the `exhibitions` table shape. At minimum:

Run:
```bash
cat /Users/ricardosalcedo/projects/ascaso-gallery/src/data/exhibitions/index.json
```

Then write `backend/fixtures/exhibitions.json` as an array where each element has `slug`, `title`, `subtitle`, `status`, `dates`, `hero_image_url`, `description`, `display_order`. Example minimal fixture if the source file is sparse:

```json
[
  {
    "slug": "carlos-medina-spatial-proposals",
    "title": "Spatial Proposals",
    "subtitle": "Carlos Medina",
    "status": "current",
    "dates": "April 10 – June 15, 2026",
    "hero_image_url": "/images/artist-carlos-medina.jpg",
    "description": "A solo exhibition of Carlos Medina's recent spatial explorations.",
    "display_order": 0
  }
]
```

Adjust fields to match whatever `src/data/exhibitions/index.json` actually contains.

- [ ] **Step 3: Create `backend/fixtures/news.json`**

Run:
```bash
ls /Users/ricardosalcedo/projects/ascaso-gallery/src/data/news/
```

Port those entries into an array of news articles with `slug`, `title`, `excerpt`, `content`, `hero_image_url`, `published_at` (ISO 8601). If the source is empty, seed one placeholder matching the shape.

- [ ] **Step 4: Create `backend/fixtures/artfairs.json`**

Run:
```bash
ls /Users/ricardosalcedo/projects/ascaso-gallery/src/data/artFairs/
```

Port the entries. Required fields: `slug`, `name`, `dates`, `location`, `booth`, `description`, `hero_image_url`, `year`.

- [ ] **Step 5: Write the failing test — `backend/tests/test_cli_seed.py`**

Content:
```python
from pathlib import Path

from app.models import Artist, Exhibition, NewsArticle, ArtFair


def test_seed_loads_all_fixtures(app, db, monkeypatch, tmp_path):
    # Point the seeder at a controlled fixtures directory built from strings
    fixtures = tmp_path / 'fixtures'
    (fixtures / 'artists').mkdir(parents=True)
    (fixtures / 'artists' / 'index.json').write_text('[]')
    (fixtures / 'artists' / 'carlos-medina.json').write_text('''
    {
      "slug": "carlos-medina",
      "name": "Carlos Medina",
      "medium": "Sculpture",
      "heroImage": "/h.jpg",
      "eyebrow": "Sculpture",
      "bio": {"short": "s", "full": ["p"]},
      "quote": {"text": "t", "attribution": "c", "eyebrow": "e"},
      "works": [{"slug": "w1", "title": "W1", "image": "/w1.jpg"}],
      "exhibitions": [{"year": 2024, "items": ["x"]}],
      "monumentalWorks": [],
      "awards": ["a"],
      "collections": ["c"]
    }
    ''')
    (fixtures / 'exhibitions.json').write_text('''
    [{"slug": "e1", "title": "E1", "status": "current", "dates": "now"}]
    ''')
    (fixtures / 'news.json').write_text('''
    [{"slug": "n1", "title": "N1", "published_at": "2026-01-01T00:00:00"}]
    ''')
    (fixtures / 'artfairs.json').write_text('''
    [{"slug": "f1", "name": "F1", "year": 2026, "dates": "Dec 2026"}]
    ''')
    (fixtures / 'landing.json').write_text('{"featuredArtistSlugs": ["carlos-medina"]}')

    monkeypatch.setenv('FIXTURES_DIR', str(fixtures))

    runner = app.test_cli_runner()
    result = runner.invoke(args=['seed'])
    assert result.exit_code == 0, result.output

    assert Artist.query.count() == 1
    a = Artist.query.first()
    assert a.slug == 'carlos-medina'
    assert a.hero_image_url == '/h.jpg'
    assert a.featured is True
    assert len(a.works) == 1
    assert a.works[0].slug == 'w1'
    assert a.exhibitions_history == [{'year': 2024, 'items': ['x']}]
    assert a.awards == ['a']

    assert Exhibition.query.count() == 1
    assert NewsArticle.query.count() == 1
    assert ArtFair.query.count() == 1


def test_seed_is_idempotent(app, db, monkeypatch, tmp_path):
    fixtures = tmp_path / 'fixtures'
    (fixtures / 'artists').mkdir(parents=True)
    (fixtures / 'artists' / 'x.json').write_text('''
    {"slug": "x", "name": "X", "works": [{"slug": "w", "title": "W", "image": "/w.jpg"}]}
    ''')
    (fixtures / 'exhibitions.json').write_text('[]')
    (fixtures / 'news.json').write_text('[]')
    (fixtures / 'artfairs.json').write_text('[]')
    (fixtures / 'landing.json').write_text('{"featuredArtistSlugs": []}')

    monkeypatch.setenv('FIXTURES_DIR', str(fixtures))
    runner = app.test_cli_runner()
    runner.invoke(args=['seed'])
    runner.invoke(args=['seed'])

    assert Artist.query.count() == 1
    assert Artist.query.first().works[0].slug == 'w'  # artwork also deduped via (artist_id, slug)


def test_seed_wipe_clears_first(app, db, monkeypatch, tmp_path):
    from app.models import Artist
    db.session.add(Artist(slug='ghost', name='Ghost'))
    db.session.commit()

    fixtures = tmp_path / 'fixtures'
    (fixtures / 'artists').mkdir(parents=True)
    (fixtures / 'artists' / 'x.json').write_text('{"slug": "x", "name": "X", "works": []}')
    (fixtures / 'exhibitions.json').write_text('[]')
    (fixtures / 'news.json').write_text('[]')
    (fixtures / 'artfairs.json').write_text('[]')
    (fixtures / 'landing.json').write_text('{"featuredArtistSlugs": []}')

    monkeypatch.setenv('FIXTURES_DIR', str(fixtures))
    runner = app.test_cli_runner()
    result = runner.invoke(args=['seed', '--wipe'])
    assert result.exit_code == 0

    assert Artist.query.filter_by(slug='ghost').first() is None
    assert Artist.query.count() == 1
```

- [ ] **Step 6: Run to verify it fails**

Run:
```bash
pytest tests/test_cli_seed.py -xvs
```

Expected: command `seed` not found.

- [ ] **Step 7: Modify `backend/scripts/cli.py` — add `seed` command**

Full file:

```python
import json
import os
from pathlib import Path

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import AdminUser, Artist, ArtWork, Exhibition, NewsArticle, ArtFair
from app.services.auth import hash_password


@click.command('create-admin')
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False)
@with_appcontext
def create_admin(email, password):
    """Create an admin user."""
    existing = AdminUser.query.filter_by(email=email).first()
    if existing:
        raise click.ClickException(f'Admin with email {email} already exists')
    user = AdminUser(email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    click.echo(f'Admin {email} created (id={user.id})')


def _fixtures_dir() -> Path:
    return Path(os.environ.get('FIXTURES_DIR', Path(__file__).resolve().parent.parent / 'fixtures'))


def _upsert_artist(payload: dict) -> Artist:
    slug = payload['slug']
    artist = Artist.query.filter_by(slug=slug).first() or Artist(slug=slug)

    # Frontend JSON uses camelCase 'heroImage'; DB column is hero_image_url
    artist.name = payload.get('name')
    artist.medium = payload.get('medium')
    artist.nationality = payload.get('nationality')
    artist.eyebrow = payload.get('eyebrow')
    artist.hero_image_url = payload.get('heroImage') or payload.get('hero_image_url')
    artist.display_order = payload.get('display_order', 0)
    artist.bio = payload.get('bio')
    artist.quote = payload.get('quote')
    artist.awards = payload.get('awards')
    artist.collections = payload.get('collections')
    # Frontend JSON 'exhibitions' maps to DB 'exhibitions_history'
    artist.exhibitions_history = payload.get('exhibitions') or payload.get('exhibitions_history')
    # Frontend JSON 'monumentalWorks' maps to DB 'monumental_works'
    artist.monumental_works = payload.get('monumentalWorks') or payload.get('monumental_works')

    db.session.add(artist)
    db.session.flush()  # assign id so we can attach works

    # Upsert works by (artist_id, slug), matching the unique constraint from §2 of the spec
    existing_works = {w.slug: w for w in artist.works}
    incoming_slugs = set()
    for i, w in enumerate(payload.get('works') or []):
        w_slug = w['slug']
        incoming_slugs.add(w_slug)
        work = existing_works.get(w_slug) or ArtWork(artist_id=artist.id, slug=w_slug)
        work.title = w['title']
        work.image_url = w.get('image') or w.get('image_url')
        work.year = w.get('year')
        work.medium = w.get('medium')
        work.display_order = w.get('display_order', i)
        db.session.add(work)

    return artist


def _seed_artists(dir: Path) -> int:
    count = 0
    artists_dir = dir / 'artists'
    if not artists_dir.exists():
        return 0
    for f in sorted(artists_dir.glob('*.json')):
        if f.name == 'index.json':
            continue
        payload = json.loads(f.read_text())
        _upsert_artist(payload)
        count += 1
    return count


def _seed_simple(dir: Path, filename: str, model):
    path = dir / filename
    if not path.exists():
        return 0
    rows = json.loads(path.read_text())
    count = 0
    for payload in rows:
        slug = payload['slug']
        row = model.query.filter_by(slug=slug).first() or model(slug=slug)
        for key, value in payload.items():
            if hasattr(row, key):
                setattr(row, key, value)
        db.session.add(row)
        count += 1
    return count


def _apply_featured(dir: Path):
    landing_path = dir / 'landing.json'
    if not landing_path.exists():
        return
    landing = json.loads(landing_path.read_text())
    slugs = set(landing.get('featuredArtistSlugs', []))
    for artist in Artist.query.all():
        artist.featured = artist.slug in slugs


@click.command('seed')
@click.option('--wipe', is_flag=True, help='Delete existing content rows before seeding')
@with_appcontext
def seed(wipe):
    """Load JSON fixtures into the database."""
    if wipe:
        ArtWork.query.delete()
        Artist.query.delete()
        Exhibition.query.delete()
        NewsArticle.query.delete()
        ArtFair.query.delete()
        db.session.commit()

    dir = _fixtures_dir()
    n_artists = _seed_artists(dir)
    n_exhibitions = _seed_simple(dir, 'exhibitions.json', Exhibition)
    n_news = _seed_simple(dir, 'news.json', NewsArticle)
    n_fairs = _seed_simple(dir, 'artfairs.json', ArtFair)
    _apply_featured(dir)

    db.session.commit()
    click.echo(
        f'Seeded {n_artists} artists, {n_exhibitions} exhibitions, {n_news} news, {n_fairs} art fairs'
    )


def register_cli(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(seed)
```

- [ ] **Step 8: Run the seed tests**

Run:
```bash
pytest tests/test_cli_seed.py -xvs
```

Expected: 3 passed.

- [ ] **Step 9: Run the full backend suite**

Run:
```bash
pytest -xvs
```

Expected: everything green. Total is around 70+ tests by this point.

- [ ] **Step 10: Commit**

```bash
git add backend/fixtures/ backend/scripts/cli.py backend/tests/test_cli_seed.py
git commit -m "feat(backend): flask seed CLI + committed fixtures"
```

---

### Task 27: Run the seed against a real dev SQLite DB and smoke-test via curl

**Files:**
- None (manual verification).

- [ ] **Step 1: Reset the dev DB and apply migrations**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery/backend
source venv/bin/activate
rm -f dev.db
export FLASK_APP=wsgi.py FLASK_ENV=dev
flask db upgrade
```

Expected: `dev.db` created; Alembic reports baseline migration applied.

- [ ] **Step 2: Seed**

Run:
```bash
flask seed
```

Expected: `Seeded 1 artists, N exhibitions, N news, N art fairs` (adjust counts to whatever the fixtures contain).

- [ ] **Step 3: Create an admin**

Run:
```bash
flask create-admin --email dev@test.local --password devpass
```

Expected: `Admin dev@test.local created (id=1)`.

- [ ] **Step 4: Start the dev server in a second terminal**

Run:
```bash
flask run
```

Expected: `Running on http://127.0.0.1:5000`.

- [ ] **Step 5: Smoke-test via curl**

In the first terminal:

```bash
curl -s http://localhost:5000/api/health
curl -s http://localhost:5000/api/artists | head -c 500
curl -s http://localhost:5000/api/artists/carlos-medina | head -c 500
curl -s http://localhost:5000/api/exhibitions
curl -s http://localhost:5000/api/news
curl -s http://localhost:5000/api/artfairs

# Login and grab a token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev@test.local","password":"devpass"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token: $TOKEN"

curl -s http://localhost:5000/api/auth/me -H "Authorization: Bearer $TOKEN"
```

Expected: all endpoints return JSON responses, no 500s. Stop the dev server (Ctrl-C).

- [ ] **Step 6: No commit** (manual verification only).

---

## Phase 8 — Deployment

### Task 28: Create `backend/render.yaml`

**Files:**
- Create: `backend/render.yaml`

- [ ] **Step 1: Write `backend/render.yaml`**

Content:
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

- [ ] **Step 2: Commit**

```bash
git add backend/render.yaml
git commit -m "feat(backend): render.yaml for web service + managed postgres"
```

---

### Task 29: Push to GitHub and deploy to Render (manual ops task)

**Files:**
- None.

This task is manual-ops and requires Render dashboard access. Follow each step carefully.

- [ ] **Step 1: Push the backend branch to GitHub**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery
git push origin main
```

Expected: push succeeds.

- [ ] **Step 2: Create the Render service from the blueprint**

Open Render dashboard → "New +" → "Blueprint" → select the `ascaso-gallery` GitHub repo → Render detects `backend/render.yaml`. Click "Apply".

Expected: Render creates both the web service `ascaso-gallery-api` and the Postgres database `ascaso-gallery-db`.

- [ ] **Step 3: Set the two `sync: false` env vars in the Render dashboard**

For the `ascaso-gallery-api` service → Environment tab:
- `CORS_ORIGINS` → the production frontend URL (e.g. `https://ascaso-gallery.onrender.com`) plus any custom domain, comma-separated
- `CLOUDINARY_URL` → the real `cloudinary://<key>:<secret>@<cloud-name>` value

Save. Render restarts the service.

- [ ] **Step 4: Watch the build log**

In Render → service → Logs. The build command runs `pip install -r requirements.txt && flask db upgrade`. Expected: migrations apply cleanly on the empty managed Postgres.

- [ ] **Step 5: Verify `/api/health` from production**

Run:
```bash
curl -s https://ascaso-gallery-api.onrender.com/api/health
```

Expected: `{"status":"ok"}`. (Adjust the hostname if Render assigned a different one.)

- [ ] **Step 6: Seed production content from Render Shell**

In Render dashboard → `ascaso-gallery-api` → Shell. Run:

```bash
flask seed
flask create-admin --email founder@syn-agent.com --password <strong-password>
```

Expected: seed summary printed, admin created. **Use a strong password** — this is the prod admin.

- [ ] **Step 7: Verify a real artist fetch from prod**

Run:
```bash
curl -s https://ascaso-gallery-api.onrender.com/api/artists | head -c 500
curl -s https://ascaso-gallery-api.onrender.com/api/artists/carlos-medina | head -c 500
```

Expected: real JSON responses with the seeded content.

- [ ] **Step 8: No commit — this is an ops task.**

---

## Phase 9 — Frontend hook migration

**Precondition:** Phase 8 has completed and the backend is live at the production URL. Hooks fall back to the committed JSON if fetch fails, so any mid-cutover breakage degrades the site to static mode rather than blank screens.

### Task 30: Add `src/lib/api.js` — API client with case transforms

**Files:**
- Create: `src/lib/api.js`
- Create: `src/lib/__tests__/api.test.js`
- Modify: `.env.local` (or `.env`) — add `VITE_API_BASE_URL`

- [ ] **Step 1: Create `.env.local` in repo root (frontend-side)**

Content (adjust the URL to the deployed backend):
```
VITE_API_BASE_URL=https://ascaso-gallery-api.onrender.com/api
```

- [ ] **Step 2: Write the failing test — `src/lib/__tests__/api.test.js`**

Content:
```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { api, snakeToCamel, camelToSnake } from '../api.js'

describe('snakeToCamel', () => {
  it('transforms nested objects', () => {
    const input = { hero_image_url: '/h.jpg', bio: { short_text: 'hi' }, works: [{ display_order: 0 }] }
    expect(snakeToCamel(input)).toEqual({
      heroImageUrl: '/h.jpg',
      bio: { shortText: 'hi' },
      works: [{ displayOrder: 0 }],
    })
  })

  it('preserves arrays of primitives', () => {
    expect(snakeToCamel({ awards: ['a', 'b'] })).toEqual({ awards: ['a', 'b'] })
  })
})

describe('camelToSnake', () => {
  it('transforms request bodies', () => {
    expect(camelToSnake({ heroImageUrl: '/h.jpg', displayOrder: 1 })).toEqual({
      hero_image_url: '/h.jpg',
      display_order: 1,
    })
  })
})

describe('api.get', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  it('camelizes response bodies', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ hero_image_url: '/h.jpg', display_order: 2 }),
    })
    const result = await api.get('/artists/x')
    expect(result).toEqual({ heroImageUrl: '/h.jpg', displayOrder: 2 })
  })

  it('throws on non-2xx with parsed error envelope', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ error: { code: 'not_found', message: 'no' } }),
    })
    await expect(api.get('/artists/nope')).rejects.toMatchObject({ status: 404, code: 'not_found' })
  })
})

describe('api.post', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  it('snakes request body, camelizes response', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ display_order: 3 }),
    })
    const result = await api.post('/artists', { displayOrder: 3 }, 'tok')
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/artists'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer tok' }),
        body: JSON.stringify({ display_order: 3 }),
      }),
    )
    expect(result).toEqual({ displayOrder: 3 })
  })
})
```

- [ ] **Step 3: Run to verify it fails**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery
npx vitest run src/lib/__tests__/api.test.js
```

Expected: fails — `api.js` doesn't exist.

- [ ] **Step 4: Write `src/lib/api.js`**

Content:
```javascript
const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export function snakeToCamel(value) {
  if (Array.isArray(value)) return value.map(snakeToCamel)
  if (value !== null && typeof value === 'object') {
    const out = {}
    for (const [key, val] of Object.entries(value)) {
      const camelKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
      out[camelKey] = snakeToCamel(val)
    }
    return out
  }
  return value
}

export function camelToSnake(value) {
  if (Array.isArray(value)) return value.map(camelToSnake)
  if (value !== null && typeof value === 'object') {
    const out = {}
    for (const [key, val] of Object.entries(value)) {
      const snakeKey = key.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`)
      out[snakeKey] = camelToSnake(val)
    }
    return out
  }
  return value
}

class ApiError extends Error {
  constructor(status, code, message, details) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

async function request(method, path, body, token) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  const init = { method, headers }
  if (body !== undefined) init.body = JSON.stringify(camelToSnake(body))

  const resp = await fetch(`${BASE}${path}`, init)
  const payload = await resp.json().catch(() => ({}))

  if (!resp.ok) {
    const err = payload?.error || {}
    throw new ApiError(resp.status, err.code || 'unknown', err.message || resp.statusText, err.details)
  }
  return snakeToCamel(payload)
}

export const api = {
  get: (path, token) => request('GET', path, undefined, token),
  post: (path, body, token) => request('POST', path, body, token),
  put: (path, body, token) => request('PUT', path, body, token),
  delete: (path, token) => request('DELETE', path, undefined, token),
}
```

- [ ] **Step 5: Run the test**

Run:
```bash
npx vitest run src/lib/__tests__/api.test.js
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/lib/api.js src/lib/__tests__/api.test.js .env.local
git commit -m "feat(frontend): api client with snake<->camel transforms"
```

(Note: `.env.local` is typically gitignored. If it is, commit only `src/lib/`. Check `.gitignore` before staging.)

---

### Task 31: Rewrite `useArtists` hook to fetch with JSON fallback

**Files:**
- Modify: `src/hooks/data/useArtists.js`
- Modify: `src/hooks/data/__tests__/useArtists.test.js`

- [ ] **Step 1: Inspect the current hook and test**

Run:
```bash
cat src/hooks/data/useArtists.js
ls src/hooks/data/__tests__/
cat src/hooks/data/__tests__/useArtists.test.js
```

Note the exact exported names (`useArtists`, `useFeaturedArtists`, `useRelatedArtists`, `useArtist`) so you can keep them stable.

- [ ] **Step 2: Rewrite `src/hooks/data/useArtists.js` — use fetch with fallback**

Content:
```javascript
import { useEffect, useState } from 'react'
import { api } from '../../lib/api.js'
import artistsIndex from '../../data/artists/index.json'
import landing from '../../data/landing.json'

function applyFieldShims(detail) {
  if (!detail) return detail
  return {
    ...detail,
    heroImage: detail.heroImageUrl ?? detail.heroImage,
    exhibitions: detail.exhibitionsHistory ?? detail.exhibitions,
    works: (detail.works || []).map((w) => ({
      ...w,
      image: w.imageUrl ?? w.image,
    })),
  }
}

function applySummaryShim(row) {
  return { ...row, heroImage: row.heroImageUrl ?? row.heroImage }
}

export function useArtists() {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })

  useEffect(() => {
    let cancelled = false
    api.get('/artists')
      .then((resp) => {
        if (cancelled) return
        const list = (resp.data || []).map(applySummaryShim)
        setState({ data: list, isLoading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        console.warn('[useArtists] fetch failed, falling back to JSON', err)
        setState({ data: artistsIndex, isLoading: false, error: null })
      })
    return () => { cancelled = true }
  }, [])

  return state
}

export function useFeaturedArtists() {
  const { data, isLoading, error } = useArtists()
  if (isLoading || error || !data) return { data: null, isLoading, error }
  const bySlug = new Map(data.map((a) => [a.slug, a]))
  const featured = landing.featuredArtistSlugs
    .map((slug) => bySlug.get(slug))
    .filter(Boolean)
  return { data: featured, isLoading: false, error: null }
}

export function useRelatedArtists(slug) {
  const { data, isLoading, error } = useArtists()
  if (isLoading || error || !data) return { data: null, isLoading, error }
  const bySlug = new Map(data.map((a) => [a.slug, a]))
  const related = landing.relatedArtistsFallbackSlugs
    .filter((s) => s !== slug)
    .map((s) => bySlug.get(s))
    .filter(Boolean)
  return { data: related, isLoading: false, error: null }
}

export function useArtist(slug) {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })

  useEffect(() => {
    let cancelled = false
    setState({ data: null, isLoading: true, error: null })
    api.get(`/artists/${slug}`)
      .then((detail) => {
        if (cancelled) return
        setState({ data: applyFieldShims(detail), isLoading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        console.warn(`[useArtist] fetch failed for ${slug}, falling back to JSON`, err)
        import(`../../data/artists/${slug}.json`)
          .then((mod) => {
            if (cancelled) return
            setState({ data: mod.default, isLoading: false, error: null })
          })
          .catch((fallbackErr) => {
            if (cancelled) return
            setState({ data: null, isLoading: false, error: fallbackErr })
          })
      })
    return () => { cancelled = true }
  }, [slug])

  return state
}
```

- [ ] **Step 3: Update `src/hooks/data/__tests__/useArtists.test.js` — mock fetch via the api client**

Content:
```javascript
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useArtists, useArtist } from '../useArtists.js'
import { api } from '../../../lib/api.js'

describe('useArtists', () => {
  beforeEach(() => {
    vi.spyOn(api, 'get')
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('loads from the api and applies heroImage shim', async () => {
    api.get.mockResolvedValueOnce({
      data: [{ slug: 'x', name: 'X', heroImageUrl: '/h.jpg' }],
      count: 1,
    })
    const { result } = renderHook(() => useArtists())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toEqual([
      { slug: 'x', name: 'X', heroImageUrl: '/h.jpg', heroImage: '/h.jpg' },
    ])
  })

  it('falls back to JSON on fetch error', async () => {
    api.get.mockRejectedValueOnce(new Error('network'))
    const { result } = renderHook(() => useArtists())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toBeTruthy()
    expect(result.current.error).toBeNull()
  })
})

describe('useArtist', () => {
  beforeEach(() => {
    vi.spyOn(api, 'get')
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches detail and renames exhibitionsHistory to exhibitions', async () => {
    api.get.mockResolvedValueOnce({
      slug: 'carlos-medina',
      name: 'Carlos',
      heroImageUrl: '/h.jpg',
      exhibitionsHistory: [{ year: 2024, items: ['x'] }],
      works: [{ slug: 'w1', title: 'W1', imageUrl: '/w.jpg' }],
    })
    const { result } = renderHook(() => useArtist('carlos-medina'))
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data.heroImage).toBe('/h.jpg')
    expect(result.current.data.exhibitions).toEqual([{ year: 2024, items: ['x'] }])
    expect(result.current.data.works[0].image).toBe('/w.jpg')
  })
})
```

- [ ] **Step 4: Run the tests**

Run:
```bash
npx vitest run src/hooks/data/__tests__/useArtists.test.js
```

Expected: all passing.

- [ ] **Step 5: Browser smoke test**

Run the dev server and load the pages that use artists:

```bash
npm run dev
```

Open `http://localhost:5173/` and verify:
- Featured artists section renders (using prod API if `VITE_API_BASE_URL` is set)
- `/artists/carlos-medina` detail page renders with hero image, bio, works, exhibitions history

If the API is reachable, data comes from the backend. If not, it falls back to JSON. Both paths should render identical UIs. Stop the dev server.

- [ ] **Step 6: Commit**

```bash
git add src/hooks/data/useArtists.js src/hooks/data/__tests__/useArtists.test.js
git commit -m "feat(frontend): useArtists/useArtist fetch from API with JSON fallback"
```

---

### Task 32: Rewrite `useExhibitions` hook

**Files:**
- Modify: `src/hooks/data/useExhibitions.js`
- Modify or create: `src/hooks/data/__tests__/useExhibitions.test.js`

- [ ] **Step 1: Inspect the current file**

Run:
```bash
cat src/hooks/data/useExhibitions.js
```

Note every exported name.

- [ ] **Step 2: Rewrite `src/hooks/data/useExhibitions.js`**

Content:
```javascript
import { useEffect, useState } from 'react'
import { api } from '../../lib/api.js'
import exhibitionsFallback from '../../data/exhibitions/index.json'

function applyShim(row) {
  if (!row) return row
  return { ...row, heroImage: row.heroImageUrl ?? row.heroImage }
}

export function useExhibitions({ status } = {}) {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })

  useEffect(() => {
    let cancelled = false
    const path = status ? `/exhibitions?status=${encodeURIComponent(status)}` : '/exhibitions'
    api.get(path)
      .then((resp) => {
        if (cancelled) return
        setState({ data: (resp.data || []).map(applyShim), isLoading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        console.warn('[useExhibitions] fetch failed, falling back to JSON', err)
        const fallback = status
          ? (exhibitionsFallback.filter?.((e) => e.status === status) ?? exhibitionsFallback)
          : exhibitionsFallback
        setState({ data: fallback, isLoading: false, error: null })
      })
    return () => { cancelled = true }
  }, [status])

  return state
}
```

If the existing file exported additional names (`useCurrentExhibition`, etc.), preserve those exports by layering them on top of `useExhibitions({status: 'current'})`. Inspect the original file contents from Step 1 and port every exported name.

- [ ] **Step 3: Write the test — `src/hooks/data/__tests__/useExhibitions.test.js`**

Content:
```javascript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useExhibitions } from '../useExhibitions.js'
import { api } from '../../../lib/api.js'

describe('useExhibitions', () => {
  beforeEach(() => { vi.spyOn(api, 'get') })
  afterEach(() => { vi.restoreAllMocks() })

  it('fetches the list and shims heroImage', async () => {
    api.get.mockResolvedValueOnce({
      data: [{ slug: 'e1', title: 'E1', status: 'current', heroImageUrl: '/e.jpg' }],
      count: 1,
    })
    const { result } = renderHook(() => useExhibitions())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data[0].heroImage).toBe('/e.jpg')
  })

  it('passes status filter to the api', async () => {
    api.get.mockResolvedValueOnce({ data: [], count: 0 })
    renderHook(() => useExhibitions({ status: 'current' }))
    await waitFor(() => expect(api.get).toHaveBeenCalledWith('/exhibitions?status=current'))
  })

  it('falls back on error', async () => {
    api.get.mockRejectedValueOnce(new Error('network'))
    const { result } = renderHook(() => useExhibitions())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.error).toBeNull()
  })
})
```

- [ ] **Step 4: Run tests and browser smoke-test**

Run:
```bash
npx vitest run src/hooks/data/__tests__/useExhibitions.test.js
npm run dev
```

Open pages that show exhibitions. Verify they render. Stop the server.

- [ ] **Step 5: Commit**

```bash
git add src/hooks/data/useExhibitions.js src/hooks/data/__tests__/useExhibitions.test.js
git commit -m "feat(frontend): useExhibitions fetches from API with fallback"
```

---

### Task 33: Rewrite `useNews` hook

**Files:**
- Modify: `src/hooks/data/useNews.js`
- Create: `src/hooks/data/__tests__/useNews.test.js`

- [ ] **Step 1: Inspect the current file**

Run:
```bash
cat src/hooks/data/useNews.js
```

Note exports.

- [ ] **Step 2: Rewrite `src/hooks/data/useNews.js`**

Content:
```javascript
import { useEffect, useState } from 'react'
import { api } from '../../lib/api.js'
import newsFallback from '../../data/news/index.json'

function applyShim(row) {
  if (!row) return row
  return { ...row, heroImage: row.heroImageUrl ?? row.heroImage }
}

export function useNews() {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })

  useEffect(() => {
    let cancelled = false
    api.get('/news')
      .then((resp) => {
        if (cancelled) return
        setState({ data: (resp.data || []).map(applyShim), isLoading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        console.warn('[useNews] fetch failed, falling back to JSON', err)
        setState({ data: newsFallback, isLoading: false, error: null })
      })
    return () => { cancelled = true }
  }, [])

  return state
}
```

If the existing file's data path differs from `src/data/news/index.json`, adjust the fallback import.

- [ ] **Step 3: Write the test — `src/hooks/data/__tests__/useNews.test.js`**

Content:
```javascript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useNews } from '../useNews.js'
import { api } from '../../../lib/api.js'

describe('useNews', () => {
  beforeEach(() => { vi.spyOn(api, 'get') })
  afterEach(() => { vi.restoreAllMocks() })

  it('fetches and shims heroImage', async () => {
    api.get.mockResolvedValueOnce({
      data: [{ slug: 'n1', title: 'N1', heroImageUrl: '/n.jpg', publishedAt: '2026-01-01T00:00:00' }],
      count: 1,
    })
    const { result } = renderHook(() => useNews())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data[0].heroImage).toBe('/n.jpg')
  })

  it('falls back on error', async () => {
    api.get.mockRejectedValueOnce(new Error('network'))
    const { result } = renderHook(() => useNews())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toBeTruthy()
  })
})
```

- [ ] **Step 4: Run tests and browser smoke-test**

Run:
```bash
npx vitest run src/hooks/data/__tests__/useNews.test.js
npm run dev
```

Verify news list renders. Stop the server.

- [ ] **Step 5: Commit**

```bash
git add src/hooks/data/useNews.js src/hooks/data/__tests__/useNews.test.js
git commit -m "feat(frontend): useNews fetches from API with fallback"
```

---

### Task 34: Rewrite `useArtFairs` hook

**Files:**
- Modify: `src/hooks/data/useArtFairs.js`
- Create or modify: `src/hooks/data/__tests__/useArtFairs.test.js`

- [ ] **Step 1: Inspect the current file**

Run:
```bash
cat src/hooks/data/useArtFairs.js
```

The existing code likely exports `useArtFairs` and `useLatestArtFair`. Preserve both.

- [ ] **Step 2: Rewrite `src/hooks/data/useArtFairs.js`**

Content:
```javascript
import { useEffect, useState } from 'react'
import { api } from '../../lib/api.js'
import artFairsFallback from '../../data/artFairs/index.json'

function applyShim(row) {
  if (!row) return row
  return { ...row, heroImage: row.heroImageUrl ?? row.heroImage }
}

export function useArtFairs() {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })

  useEffect(() => {
    let cancelled = false
    api.get('/artfairs')
      .then((resp) => {
        if (cancelled) return
        setState({ data: (resp.data || []).map(applyShim), isLoading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        console.warn('[useArtFairs] fetch failed, falling back to JSON', err)
        setState({ data: artFairsFallback, isLoading: false, error: null })
      })
    return () => { cancelled = true }
  }, [])

  return state
}

export function useLatestArtFair() {
  const [state, setState] = useState({ data: null, isLoading: true, error: null })

  useEffect(() => {
    let cancelled = false
    api.get('/artfairs/latest')
      .then((row) => {
        if (cancelled) return
        setState({ data: applyShim(row), isLoading: false, error: null })
      })
      .catch((err) => {
        if (cancelled) return
        console.warn('[useLatestArtFair] fetch failed, falling back to JSON', err)
        // fallback: pick the highest-year entry from the fallback JSON
        const list = artFairsFallback || []
        const latest = [...list].sort((a, b) => (b.year ?? 0) - (a.year ?? 0))[0] ?? null
        setState({ data: latest, isLoading: false, error: null })
      })
    return () => { cancelled = true }
  }, [])

  return state
}
```

- [ ] **Step 3: Write the test — `src/hooks/data/__tests__/useArtFairs.test.js`**

Content:
```javascript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useArtFairs, useLatestArtFair } from '../useArtFairs.js'
import { api } from '../../../lib/api.js'

describe('useArtFairs', () => {
  beforeEach(() => { vi.spyOn(api, 'get') })
  afterEach(() => { vi.restoreAllMocks() })

  it('fetches the list', async () => {
    api.get.mockResolvedValueOnce({
      data: [{ slug: 'am-2026', name: 'AM 2026', year: 2026, heroImageUrl: '/f.jpg' }],
      count: 1,
    })
    const { result } = renderHook(() => useArtFairs())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data[0].heroImage).toBe('/f.jpg')
  })
})

describe('useLatestArtFair', () => {
  beforeEach(() => { vi.spyOn(api, 'get') })
  afterEach(() => { vi.restoreAllMocks() })

  it('fetches /artfairs/latest', async () => {
    api.get.mockResolvedValueOnce({ slug: 'am-2026', name: 'AM 2026', year: 2026, heroImageUrl: '/f.jpg' })
    const { result } = renderHook(() => useLatestArtFair())
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(api.get).toHaveBeenCalledWith('/artfairs/latest')
    expect(result.current.data.heroImage).toBe('/f.jpg')
  })
})
```

- [ ] **Step 4: Run tests and browser smoke-test**

Run:
```bash
npx vitest run src/hooks/data/__tests__/useArtFairs.test.js
npm run dev
```

Verify art fairs render on any page that uses them. Stop the server.

- [ ] **Step 5: Commit**

```bash
git add src/hooks/data/useArtFairs.js src/hooks/data/__tests__/useArtFairs.test.js
git commit -m "feat(frontend): useArtFairs + useLatestArtFair fetch from API"
```

---

### Task 35: Final end-to-end smoke test and deploy the frontend

**Files:**
- None (integration validation + deploy).

- [ ] **Step 1: Run the full frontend test suite**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery
npx vitest run
```

Expected: all tests pass. Investigate any red test before proceeding — don't paper over.

- [ ] **Step 2: Run the full backend test suite**

Run:
```bash
cd backend
source venv/bin/activate
pytest
```

Expected: all tests pass.

- [ ] **Step 3: Start dev server and exercise every page**

Run:
```bash
cd /Users/ricardosalcedo/projects/ascaso-gallery
npm run dev
```

Load and visually confirm:
- Landing page (hero, featured artists, latest exhibition, news, art fairs)
- Artist detail (`/artists/carlos-medina`)
- Any exhibition detail route
- Any news detail route

Open the browser devtools network tab and confirm:
- Requests go to `https://ascaso-gallery-api.onrender.com/api/...`
- All return 200 with JSON
- No CORS errors

Stop the dev server.

- [ ] **Step 4: Build the frontend and verify it compiles**

Run:
```bash
npm run build
```

Expected: `dist/` rebuilt, no errors.

- [ ] **Step 5: Push and let Render deploy the frontend**

Run:
```bash
git push origin main
```

Render auto-deploys the frontend service. Watch the build log in the Render dashboard.

- [ ] **Step 6: Verify prod**

Open the production frontend URL. Confirm:
- Pages render
- Network tab shows requests to the backend API
- No CORS errors
- Golden-path navigation works (home → artist → back)

- [ ] **Step 7: No commit** (deploy-only).

---

## End-state checklist

- [ ] Backend live at `https://ascaso-gallery-api.onrender.com` with `/api/health` returning `{"status":"ok"}`
- [ ] All six resources CRUD-able via JWT-authed endpoints
- [ ] Upload endpoint tested against real Cloudinary account
- [ ] Seed command loaded baseline content
- [ ] Admin user created in prod
- [ ] Frontend pointed at the new API, JSON fallback still in place
- [ ] All backend tests green
- [ ] All frontend tests green
- [ ] Production frontend deployed and rendering dynamic content

## Deferred to future work (confirmed during brainstorming)

- React `/admin` route tree
- Signed direct-to-Cloudinary uploads
- Cloudinary orphan cleanup
- Refresh tokens / revocation list
- Cookie-based auth with CSRF
- Many-to-many artist ↔ exhibition linking
- GitHub Actions CI pipeline
- TanStack Query on the frontend
