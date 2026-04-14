import os
from datetime import timedelta


def test_dev_config_defaults_to_sqlite(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'x')
    monkeypatch.setenv('JWT_SECRET_KEY', 'y')
    monkeypatch.delenv('DATABASE_URL', raising=False)
    from app.config import DevConfig
    cfg = DevConfig()
    assert cfg.SQLALCHEMY_DATABASE_URI == 'sqlite:///dev.db'
    assert cfg.DEBUG is True
    assert cfg.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert cfg.MAX_CONTENT_LENGTH == 15 * 1024 * 1024
    assert cfg.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=12)


def test_test_config_uses_memory_sqlite():
    from app.config import TestConfig
    cfg = TestConfig()
    assert cfg.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    assert cfg.TESTING is True
    assert cfg.SECRET_KEY == 'test-secret'


def test_prod_config_reads_database_url(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'x')
    monkeypatch.setenv('JWT_SECRET_KEY', 'y')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@h/db')
    from importlib import reload
    import app.config as cfg_mod
    reload(cfg_mod)
    assert cfg_mod.ProdConfig.SQLALCHEMY_DATABASE_URI == 'postgresql://u:p@h/db'
    assert cfg_mod.ProdConfig.DEBUG is False
