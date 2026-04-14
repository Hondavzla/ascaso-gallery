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
