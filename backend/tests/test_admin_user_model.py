def test_admin_user_can_be_created(db):
    from app.models.admin_user import AdminUser
    user = AdminUser(email='a@b.com', password_hash='hashed')
    db.session.add(user)
    db.session.commit()
    assert user.id is not None
    assert user.created_at is not None


def test_admin_user_email_is_unique(db):
    from app.models.admin_user import AdminUser
    db.session.add(AdminUser(email='dup@x.com', password_hash='h1'))
    db.session.commit()
    db.session.add(AdminUser(email='dup@x.com', password_hash='h2'))
    import pytest
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
