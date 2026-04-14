import pytest
from marshmallow import ValidationError


@pytest.fixture
def app():
    from app import create_app
    app = create_app('test')

    @app.get('/_boom/404')
    def boom_404():
        from flask import abort
        abort(404)

    @app.get('/_boom/500')
    def boom_500():
        raise RuntimeError('hidden detail')

    @app.get('/_boom/validation')
    def boom_validation():
        raise ValidationError({'name': ['Missing data for required field.']})

    return app


def test_404_returns_json_envelope(app):
    client = app.test_client()
    resp = client.get('/_boom/404')
    assert resp.status_code == 404
    body = resp.get_json()
    assert body['error']['code'] == 'not_found'
    assert 'request_id' in body['error']


def test_500_hides_internal_detail(app):
    client = app.test_client()
    resp = client.get('/_boom/500')
    assert resp.status_code == 500
    body = resp.get_json()
    assert body['error']['code'] == 'internal_error'
    assert body['error']['message'] == 'An unexpected error occurred'
    assert 'hidden detail' not in resp.get_data(as_text=True)


def test_validation_error_returns_422_with_details(app):
    client = app.test_client()
    resp = client.get('/_boom/validation')
    assert resp.status_code == 422
    body = resp.get_json()
    assert body['error']['code'] == 'validation_error'
    assert body['error']['details'] == {'name': ['Missing data for required field.']}
