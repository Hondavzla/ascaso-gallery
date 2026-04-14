import pytest
from sqlalchemy.exc import IntegrityError


def test_exhibition_can_be_created(db):
    from app.models.exhibition import Exhibition
    e = Exhibition(
        slug='soto-retrospective',
        title='Soto Retrospective',
        subtitle='Kinetic Origins',
        status='current',
        dates='April 10 – June 15, 2026',
        hero_image_url='/e.jpg',
        description='desc',
        display_order=0,
    )
    db.session.add(e)
    db.session.commit()
    assert e.id is not None
    assert e.status == 'current'


def test_exhibition_slug_unique(db):
    from app.models.exhibition import Exhibition
    db.session.add(Exhibition(slug='dup', title='A', status='current'))
    db.session.commit()
    db.session.add(Exhibition(slug='dup', title='B', status='current'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
