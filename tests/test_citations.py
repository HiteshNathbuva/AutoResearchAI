"""Source registry and citation rendering tests."""

from backend.tools.web.models import WebSource
from backend.tools.web.sources import SOURCES_HEADER, SourceRegistry, render_sources_section


def test_source_ids_are_stable_and_sequential():
    registry = SourceRegistry()
    a = registry.add(url="http://a.example/", title="A")
    b = registry.add(url="http://b.example/", title="B")
    c = registry.add(url="http://c.example/", title="C")
    assert [a.source_id, b.source_id, c.source_id] == [1, 2, 3]


def test_url_deduplication_returns_same_id():
    registry = SourceRegistry()
    first = registry.add(url="http://a.example/index.html", title="First")
    dupe = registry.add(url="http://a.example/index.html", title="Duplicate")
    assert first.source_id == dupe.source_id
    assert len(registry) == 1


def test_dedup_ignores_fragment_and_case():
    registry = SourceRegistry()
    a = registry.add(url="http://a.example/page", title="a")
    b = registry.add(url="http://A.example/page#section", title="b")
    assert a.source_id == b.source_id
    assert len(registry) == 1


def test_source_rendering_uses_citation_ids():
    registry = SourceRegistry()
    registry.add(url="http://a.example/", title="Alpha")
    registry.add(url="http://b.example/", title="Beta")
    rendered = registry.render()
    assert "[1] Alpha — http://a.example/" in rendered
    assert "[2] Beta — http://b.example/" in rendered


def test_ordering_matches_insertion_order():
    registry = SourceRegistry()
    registry.add(url="http://z.example/", title="Zebra")
    registry.add(url="http://a.example/", title="Apple")
    ids = [source.source_id for source in registry.all()]
    assert ids == [1, 2]
    assert registry.all()[0].title == "Zebra"
    assert registry.all()[1].title == "Apple"


def test_render_sources_section_full():
    sources = [
        WebSource(source_id=1, url="http://a.example/", title="Alpha", domain="a.example"),
        WebSource(source_id=2, url="http://b.example/", title="Beta", domain="b.example"),
    ]
    section = render_sources_section(sources)
    assert section.startswith(SOURCES_HEADER)
    assert "[1] Alpha — http://a.example/" in section
    assert "[2] Beta — http://b.example/" in section


def test_render_empty_sources_section_returns_empty():
    assert render_sources_section([]) == ""


def test_cited_id_consistency():
    """Checks that rendered citation numbers match the actual sources."""
    registry = SourceRegistry()
    registry.add(url="http://a.example/", title="Alpha")
    registry.add(url="http://b.example/", title="Beta")
    rendered = registry.render()
    assert "[1] Alpha" in rendered
    assert "[2] Beta" in rendered
    # No citation higher than the number of sources.
    assert len(registry) == 2
    assert "[3]" not in rendered


def test_source_domain_is_derived_from_url():
    registry = SourceRegistry()
    source = registry.add(url="https://sub.example.com/path", title="t")
    assert source.domain == "sub.example.com"


def test_source_asdict_round_trips():
    registry = SourceRegistry()
    source = registry.add(url="http://a.example/", title="A", snippet="snippet")
    data = source.to_dict()
    restored = WebSource.from_dict(data)
    assert restored.to_dict() == data
