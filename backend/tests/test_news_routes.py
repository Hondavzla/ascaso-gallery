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
