from datetime import datetime

from app.models import Artist, ArtWork, Exhibition, NewsArticle, ArtFair


def _write_fixtures(tmp_path):
    """Build a synthetic fixtures dir with all the shapes the real seed must handle."""
    fixtures = tmp_path / 'fixtures'
    (fixtures / 'artists').mkdir(parents=True)

    # Artist index with 2 summaries — one will have a detail file, the other won't
    (fixtures / 'artists' / 'index.json').write_text('''
    [
      {"slug": "carlos-medina", "name": "Carlos Medina", "medium": "Sculpture", "image": "/images/carlos.jpg", "hasDetailPage": true},
      {"slug": "minimal-artist", "name": "Minimal Artist", "medium": "Painting", "image": "/images/minimal.jpg", "hasDetailPage": false}
    ]
    ''')

    # Rich detail file (like src/data/artists/carlos-medina.json)
    (fixtures / 'artists' / 'carlos-medina.json').write_text('''
    {
      "slug": "carlos-medina",
      "name": "Carlos Medina",
      "medium": "Sculpture",
      "heroImage": "/images/carlos-detail.jpg",
      "eyebrow": "Sculpture",
      "bio": {"short": "s", "full": ["p1", "p2"]},
      "quote": {"text": "t", "attribution": "CM", "eyebrow": "El Artista"},
      "works": [
        {"slug": "w1", "title": "W1", "image": "/w1.jpg"},
        {"slug": "w2", "title": "W2", "image": "/w2.jpg"}
      ],
      "exhibitions": [{"year": 2024, "items": ["Solo at Ascaso"]}],
      "monumentalWorks": [{"year": 2023, "items": ["Brickell"]}],
      "awards": ["Award 1"],
      "collections": ["Collection 1"]
    }
    ''')

    (fixtures / 'exhibitions.json').write_text('''
    [{
      "slug": "forms-in-space",
      "title": "Forms in Space",
      "subtitle": "Contemporary",
      "status": "current",
      "startDate": "2025-12-04",
      "endDate": "2026-02-09",
      "dateLabel": "December 4 – February 9",
      "image": "/images/e.jpeg",
      "eyebrow": "On View"
    }]
    ''')

    (fixtures / 'news.json').write_text('''
    [{
      "slug": "press-one",
      "date": "2025-10-15",
      "title": "Press One",
      "excerpt": "excerpt",
      "image": "/images/n.jpg",
      "url": "https://example.com/press",
      "source": "ArtDaily"
    }]
    ''')

    (fixtures / 'artfairs.json').write_text('''
    [{
      "slug": "art-miami-2025",
      "name": "Art Miami 2025",
      "startDate": "2025-12-02",
      "endDate": "2025-12-07",
      "dateLabel": "December 2 – 7, 2025",
      "booth": "AM125",
      "description": "desc",
      "image": "/images/f.jpg",
      "eyebrow": "Last Art Fair"
    }]
    ''')

    (fixtures / 'landing.json').write_text('{"featuredArtistSlugs": ["carlos-medina"]}')
    return fixtures


def test_seed_loads_all_fixtures(app, db, monkeypatch, tmp_path):
    fixtures = _write_fixtures(tmp_path)
    monkeypatch.setenv('FIXTURES_DIR', str(fixtures))
    runner = app.test_cli_runner()
    result = runner.invoke(args=['seed'])
    assert result.exit_code == 0, result.output

    # Both artists present
    assert Artist.query.count() == 2
    carlos = Artist.query.filter_by(slug='carlos-medina').first()
    minimal = Artist.query.filter_by(slug='minimal-artist').first()
    assert carlos is not None
    assert minimal is not None

    # Carlos enriched from detail file (camelCase → snake_case mapping)
    assert carlos.hero_image_url == '/images/carlos-detail.jpg'  # detail overrides summary
    assert carlos.bio == {'short': 's', 'full': ['p1', 'p2']}
    assert carlos.quote['attribution'] == 'CM'
    assert carlos.awards == ['Award 1']
    assert carlos.collections == ['Collection 1']
    assert carlos.exhibitions_history == [{'year': 2024, 'items': ['Solo at Ascaso']}]
    assert carlos.monumental_works == [{'year': 2023, 'items': ['Brickell']}]
    assert carlos.eyebrow == 'Sculpture'
    assert carlos.featured is True  # from landing.json featuredArtistSlugs

    # Minimal artist only has summary fields
    assert minimal.hero_image_url == '/images/minimal.jpg'
    assert minimal.featured is False
    assert minimal.bio is None

    # Works attached to carlos
    assert len(carlos.works) == 2
    slugs = sorted([w.slug for w in carlos.works])
    assert slugs == ['w1', 'w2']
    w1 = next(w for w in carlos.works if w.slug == 'w1')
    assert w1.image_url == '/w1.jpg'  # 'image' → 'image_url' mapping

    # Exhibition: eyebrow/startDate/endDate dropped, dateLabel → dates, image → hero_image_url
    assert Exhibition.query.count() == 1
    e = Exhibition.query.first()
    assert e.dates == 'December 4 – February 9'
    assert e.hero_image_url == '/images/e.jpeg'
    assert e.status == 'current'

    # News: url → external_url, date → published_at, image → hero_image_url, source preserved
    assert NewsArticle.query.count() == 1
    n = NewsArticle.query.first()
    assert n.external_url == 'https://example.com/press'
    assert n.source == 'ArtDaily'
    assert n.hero_image_url == '/images/n.jpg'
    assert n.published_at == datetime(2025, 10, 15)

    # ArtFair: dateLabel → dates, startDate → year, image → hero_image_url, eyebrow/endDate dropped
    assert ArtFair.query.count() == 1
    f = ArtFair.query.first()
    assert f.year == 2025
    assert f.dates == 'December 2 – 7, 2025'
    assert f.hero_image_url == '/images/f.jpg'
    assert f.booth == 'AM125'


def test_seed_is_idempotent(app, db, monkeypatch, tmp_path):
    fixtures = _write_fixtures(tmp_path)
    monkeypatch.setenv('FIXTURES_DIR', str(fixtures))
    runner = app.test_cli_runner()
    runner.invoke(args=['seed'])
    runner.invoke(args=['seed'])  # second run should upsert, not duplicate

    assert Artist.query.count() == 2
    carlos = Artist.query.filter_by(slug='carlos-medina').first()
    assert len(carlos.works) == 2  # artwork upsert also idempotent
    assert Exhibition.query.count() == 1
    assert NewsArticle.query.count() == 1
    assert ArtFair.query.count() == 1


def test_seed_wipe_clears_first(app, db, monkeypatch, tmp_path):
    db.session.add(Artist(slug='ghost', name='Ghost'))
    db.session.commit()

    fixtures = _write_fixtures(tmp_path)
    monkeypatch.setenv('FIXTURES_DIR', str(fixtures))
    runner = app.test_cli_runner()
    result = runner.invoke(args=['seed', '--wipe'])
    assert result.exit_code == 0

    assert Artist.query.filter_by(slug='ghost').first() is None
    assert Artist.query.count() == 2  # from fixtures, not ghost


def test_seed_does_not_touch_admin_users(app, db, monkeypatch, tmp_path):
    from app.models import AdminUser
    db.session.add(AdminUser(email='admin@x.com', password_hash='hashed'))
    db.session.commit()

    fixtures = _write_fixtures(tmp_path)
    monkeypatch.setenv('FIXTURES_DIR', str(fixtures))
    runner = app.test_cli_runner()
    runner.invoke(args=['seed', '--wipe'])

    # Admin user survives even --wipe
    assert AdminUser.query.filter_by(email='admin@x.com').first() is not None
