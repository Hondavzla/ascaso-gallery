import json
import os
from datetime import datetime
from pathlib import Path

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import AdminUser, Artist, ArtWork, Exhibition, NewsArticle, ArtFair
from app.services.auth import hash_password


# ---------------- create-admin (unchanged from T16) ----------------


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


# ---------------- seed ----------------


def _fixtures_dir() -> Path:
    override = os.environ.get('FIXTURES_DIR')
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / 'fixtures'


def _parse_date(value):
    """Accept ISO date ('2025-10-15') or datetime strings; return datetime or None."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_year_from_start(value):
    """Extract year from an ISO date string like '2025-12-02'."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).year
    except ValueError:
        return None


def _upsert_artist_summary(payload: dict) -> Artist:
    """Upsert a minimal Artist row from the index.json summary shape."""
    slug = payload['slug']
    artist = Artist.query.filter_by(slug=slug).first() or Artist(slug=slug)
    artist.name = payload.get('name') or artist.name
    artist.medium = payload.get('medium') or artist.medium
    # Summary uses 'image', detail uses 'heroImage'
    if payload.get('image') and not artist.hero_image_url:
        artist.hero_image_url = payload['image']
    db.session.add(artist)
    db.session.flush()
    return artist


def _upsert_artist_detail(payload: dict) -> Artist:
    """Upsert a rich Artist row from a detail JSON file and attach works."""
    slug = payload['slug']
    artist = Artist.query.filter_by(slug=slug).first() or Artist(slug=slug)

    artist.name = payload.get('name', artist.name)
    artist.medium = payload.get('medium') or artist.medium
    artist.nationality = payload.get('nationality')
    artist.eyebrow = payload.get('eyebrow')
    # Detail uses camelCase 'heroImage'; summary uses 'image'
    hero = payload.get('heroImage') or payload.get('hero_image_url') or payload.get('image')
    if hero:
        artist.hero_image_url = hero
    artist.display_order = payload.get('display_order', artist.display_order or 0)
    artist.bio = payload.get('bio')
    artist.quote = payload.get('quote')
    artist.awards = payload.get('awards')
    artist.collections = payload.get('collections')
    # Frontend uses 'exhibitions' and 'monumentalWorks'; DB uses the _history / snake_case names
    artist.exhibitions_history = payload.get('exhibitions') or payload.get('exhibitions_history')
    artist.monumental_works = payload.get('monumentalWorks') or payload.get('monumental_works')

    db.session.add(artist)
    db.session.flush()

    # Upsert artworks by (artist_id, slug) per the unique constraint from §2 of the spec
    existing_works = {w.slug: w for w in artist.works}
    for i, w in enumerate(payload.get('works') or []):
        w_slug = w['slug']
        work = existing_works.get(w_slug) or ArtWork(artist_id=artist.id, slug=w_slug)
        work.title = w['title']
        # Frontend uses 'image' for artwork; DB uses 'image_url'
        work.image_url = w.get('image') or w.get('image_url') or ''
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

    # 1) Summaries from index.json — minimal rows for every listed artist
    index_path = artists_dir / 'index.json'
    if index_path.exists():
        for summary in json.loads(index_path.read_text()):
            _upsert_artist_summary(summary)
            count += 1

    # 2) Detail files — enrich existing rows (may also create new ones if not in index)
    for f in sorted(artists_dir.glob('*.json')):
        if f.name == 'index.json':
            continue
        payload = json.loads(f.read_text())
        _upsert_artist_detail(payload)

    return count


def _seed_exhibitions(dir: Path) -> int:
    path = dir / 'exhibitions.json'
    if not path.exists():
        return 0
    rows = json.loads(path.read_text())
    count = 0
    for payload in rows:
        slug = payload['slug']
        row = Exhibition.query.filter_by(slug=slug).first() or Exhibition(slug=slug)
        row.title = payload.get('title', row.title)
        row.subtitle = payload.get('subtitle')
        row.status = payload.get('status', row.status or 'current')
        row.dates = payload.get('dateLabel') or payload.get('dates')
        row.hero_image_url = payload.get('image') or payload.get('hero_image_url')
        row.description = payload.get('description')
        row.display_order = payload.get('display_order', row.display_order or 0)
        db.session.add(row)
        count += 1
    return count


def _seed_news(dir: Path) -> int:
    path = dir / 'news.json'
    if not path.exists():
        return 0
    rows = json.loads(path.read_text())
    count = 0
    for payload in rows:
        slug = payload['slug']
        row = NewsArticle.query.filter_by(slug=slug).first() or NewsArticle(slug=slug)
        row.title = payload.get('title', row.title)
        row.excerpt = payload.get('excerpt')
        row.content = payload.get('content')
        row.hero_image_url = payload.get('image') or payload.get('hero_image_url')
        row.external_url = payload.get('url') or payload.get('external_url')
        row.source = payload.get('source')
        row.published_at = _parse_date(payload.get('date') or payload.get('published_at'))
        db.session.add(row)
        count += 1
    return count


def _seed_artfairs(dir: Path) -> int:
    path = dir / 'artfairs.json'
    if not path.exists():
        return 0
    rows = json.loads(path.read_text())
    count = 0
    for payload in rows:
        slug = payload['slug']
        row = ArtFair.query.filter_by(slug=slug).first() or ArtFair(slug=slug)
        row.name = payload.get('name', row.name)
        row.dates = payload.get('dateLabel') or payload.get('dates')
        row.location = payload.get('location')
        row.booth = payload.get('booth')
        row.description = payload.get('description')
        row.hero_image_url = payload.get('image') or payload.get('hero_image_url')
        # year is required (not nullable) — derive from startDate when the JSON doesn't provide one
        year = payload.get('year') or _parse_year_from_start(payload.get('startDate'))
        if year is None:
            raise click.ClickException(f'Art fair {slug}: cannot determine year (missing both year and startDate)')
        row.year = year
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
@click.option('--wipe', is_flag=True, help='Delete existing content rows before seeding (never touches admin_users)')
@with_appcontext
def seed(wipe):
    """Load JSON fixtures into the database."""
    if wipe:
        # Order matters for FK: artworks → artists, then everything else
        ArtWork.query.delete()
        Artist.query.delete()
        Exhibition.query.delete()
        NewsArticle.query.delete()
        ArtFair.query.delete()
        db.session.commit()

    dir = _fixtures_dir()
    n_artists = _seed_artists(dir)
    n_exhibitions = _seed_exhibitions(dir)
    n_news = _seed_news(dir)
    n_fairs = _seed_artfairs(dir)
    _apply_featured(dir)

    db.session.commit()
    click.echo(
        f'Seeded {n_artists} artists, {n_exhibitions} exhibitions, {n_news} news, {n_fairs} art fairs'
    )


def register_cli(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(seed)
