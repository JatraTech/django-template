from backstage.registry.factory import _build_list_display
from sample.models import SampleArticle


def test_build_list_display_excludes_text_fields():
    columns = _build_list_display(SampleArticle)
    assert "content" not in columns
    assert "excerpt" not in columns
    assert "title" in columns
