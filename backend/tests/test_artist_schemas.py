import pytest
from marshmallow import ValidationError


def test_artwork_schema_roundtrip():
    from app.schemas.artist import ArtWorkSchema
    data = {'slug': 'w1', 'title': 'W1', 'image_url': '/w.jpg', 'year': 2024, 'medium': 'bronze', 'display_order': 0}
    loaded = ArtWorkSchema().load(data)
    assert loaded['slug'] == 'w1'


def test_artwork_schema_requires_title_and_image():
    from app.schemas.artist import ArtWorkSchema
    with pytest.raises(ValidationError) as err:
        ArtWorkSchema().load({'slug': 'w'})
    assert 'title' in err.value.messages
    assert 'image_url' in err.value.messages


def test_artist_schema_allows_jsonb_blocks():
    from app.schemas.artist import ArtistSchema
    data = {
        'name': 'Carlos',
        'slug': 'carlos',
        'medium': 'Sculpture',
        'bio': {'short': 's', 'full': ['a', 'b']},
        'quote': {'text': 't', 'attribution': 'c', 'eyebrow': 'e'},
        'awards': ['x'],
        'collections': ['y'],
        'exhibitions_history': [{'year': 2024, 'items': ['foo']}],
        'monumental_works': [],
    }
    loaded = ArtistSchema().load(data)
    assert loaded['bio']['short'] == 's'
    assert loaded['awards'] == ['x']


def test_artist_schema_dump_includes_works():
    from app.schemas.artist import ArtistSchema
    from app.models.artist import Artist, ArtWork
    a = Artist(slug='x', name='X')
    a.works.append(ArtWork(slug='w1', title='W1', image_url='/w.jpg'))
    dumped = ArtistSchema().dump(a)
    assert dumped['slug'] == 'x'
    assert len(dumped['works']) == 1
    assert dumped['works'][0]['slug'] == 'w1'


def test_artist_summary_schema_omits_bio():
    from app.schemas.artist import ArtistSummarySchema
    from app.models.artist import Artist
    a = Artist(slug='x', name='X', medium='Sculpture', eyebrow='S', hero_image_url='/h.jpg', featured=True, display_order=1)
    dumped = ArtistSummarySchema().dump(a)
    assert set(dumped.keys()) == {'slug', 'name', 'medium', 'eyebrow', 'hero_image_url', 'featured', 'display_order'}
