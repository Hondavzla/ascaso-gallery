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
