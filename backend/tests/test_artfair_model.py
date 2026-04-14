def test_artfair_can_be_created(db):
    from app.models.artfair import ArtFair
    f = ArtFair(
        slug='art-miami-2026',
        name='Art Miami 2026',
        dates='December 3–8, 2026',
        location='Miami, FL',
        booth='AM125',
        description='desc',
        hero_image_url='/f.jpg',
        year=2026,
    )
    db.session.add(f)
    db.session.commit()
    assert f.id is not None
    assert f.year == 2026
