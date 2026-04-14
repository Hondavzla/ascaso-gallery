from app.models import AdminUser
from app.services.auth import verify_password


def test_create_admin_creates_user(app, db):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['create-admin', '--email', 'new@x.com', '--password', 'secret'])
    assert result.exit_code == 0
    assert 'created' in result.output.lower()
    u = AdminUser.query.filter_by(email='new@x.com').first()
    assert u is not None
    assert verify_password('secret', u.password_hash)


def test_create_admin_rejects_duplicate(app, db):
    runner = app.test_cli_runner()
    runner.invoke(args=['create-admin', '--email', 'dup@x.com', '--password', 'a'])
    result = runner.invoke(args=['create-admin', '--email', 'dup@x.com', '--password', 'b'])
    assert result.exit_code != 0
    assert 'already exists' in result.output.lower()
