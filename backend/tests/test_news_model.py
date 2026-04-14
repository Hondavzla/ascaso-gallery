from datetime import datetime


def test_news_article_published(db):
    from app.models.news import NewsArticle
    n = NewsArticle(
        slug='opening',
        title='Opening Night',
        excerpt='x',
        content='body',
        hero_image_url='/n.jpg',
        published_at=datetime(2026, 4, 1),
    )
    db.session.add(n)
    db.session.commit()
    assert n.id is not None
    assert n.published_at.year == 2026


def test_news_article_draft_has_null_published_at(db):
    from app.models.news import NewsArticle
    n = NewsArticle(slug='draft', title='Draft', published_at=None)
    db.session.add(n)
    db.session.commit()
    assert n.published_at is None
