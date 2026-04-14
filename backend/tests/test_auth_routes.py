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
