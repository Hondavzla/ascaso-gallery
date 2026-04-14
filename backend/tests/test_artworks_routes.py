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
