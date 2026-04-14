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
