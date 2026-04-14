def test_create_app_returns_flask_instance():
    from app import create_app
    app = create_app('test')
    assert app is not None
    assert app.config['TESTING'] is True


def test_health_route_returns_ok():
    from app import create_app
    app = create_app('test')
    with app.test_client() as client:
        resp = client.get('/api/health')
        assert resp.status_code == 200
        assert resp.get_json() == {'status': 'ok'}


def test_unknown_config_name_raises():
    from app import create_app
    import pytest
    with pytest.raises(KeyError):
        create_app('bogus')
