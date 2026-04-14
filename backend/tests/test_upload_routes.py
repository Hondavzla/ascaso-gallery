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
