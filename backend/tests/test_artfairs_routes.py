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
