def test_hash_password_returns_bcrypt():
    from app.services.auth import hash_password, verify_password
    h = hash_password('secret')
    assert h.startswith('$2')  # bcrypt prefix
    assert verify_password('secret', h) is True
    assert verify_password('wrong', h) is False


def test_hash_password_is_non_deterministic():
    from app.services.auth import hash_password
    assert hash_password('x') != hash_password('x')
