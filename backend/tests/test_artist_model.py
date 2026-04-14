import pytest
from sqlalchemy.exc import IntegrityError


def test_artist_can_be_created_with_jsonb_blocks(db):
    from app.models.artist import Artist
    a = Artist(
        slug='carlos-medina',
        name='Carlos Medina',
        medium='Sculpture',
        nationality='Venezuelan',
        eyebrow='Sculpture',
        hero_image_url='/x.jpg',
        featured=True,
        display_order=0,
        bio={'short': 's', 'full': ['p1', 'p2']},
        quote={'text': 't', 'attribution': 'CM', 'eyebrow': 'e'},
        awards=['A1', 'A2'],
        collections=['C1'],
        exhibitions_history=[{'year': 2024, 'items': ['x']}],
        monumental_works=[{'year': 2023, 'items': ['y']}],
    )
    db.session.add(a)
    db.session.commit()
    assert a.id is not None
    assert a.bio['short'] == 's'
    assert a.awards == ['A1', 'A2']
    assert a.created_at is not None


def test_artist_slug_unique(db):
    from app.models.artist import Artist
    db.session.add(Artist(slug='dup', name='A'))
    db.session.commit()
    db.session.add(Artist(slug='dup', name='B'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_artwork_belongs_to_artist(db):
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x', name='X')
    a.works.append(ArtWork(slug='w1', title='W1', image_url='/w1.jpg'))
    a.works.append(ArtWork(slug='w2', title='W2', image_url='/w2.jpg'))
    db.session.add(a)
    db.session.commit()
    assert len(a.works) == 2
    assert a.works[0].artist_id == a.id


def test_artwork_slug_unique_per_artist(db):
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x2', name='X')
    a.works.append(ArtWork(slug='dup', title='W', image_url='/w.jpg'))
    a.works.append(ArtWork(slug='dup', title='W2', image_url='/w2.jpg'))
    db.session.add(a)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_deleting_artist_cascades_to_artworks(db):
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x3', name='X')
    a.works.append(ArtWork(slug='w', title='W', image_url='/w.jpg'))
    db.session.add(a)
    db.session.commit()
    work_id = a.works[0].id

    db.session.delete(a)
    db.session.commit()

    assert db.session.get(ArtWork, work_id) is None
