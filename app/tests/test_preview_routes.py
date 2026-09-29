from app.backstage_host import resolve_preview_route
from sample.models import SampleArticle, SampleHomePage, SampleSitePage


def test_home_page_preview_route():
    assert resolve_preview_route(SampleHomePage()) == "/"


def test_site_page_preview_route():
    assert resolve_preview_route(SampleSitePage()) == "/about"


def test_sample_article_preview_route_uses_slug():
    post = SampleArticle(slug="example-post")
    assert resolve_preview_route(post) == "/articles/example-post"
