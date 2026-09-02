"""Offline HTML/text extraction tests."""

from backend.tools.web.extract import (
    decode_content,
    extract_html,
    extract_page,
    extract_plain_text,
)


def test_normal_html_extracts_title_headings_text():
    html = (
        "<html><head><title>My Title</title></head><body>"
        "<h1>Heading One</h1><h2>Sub</h2><p>Paragraph text here.</p>"
        "</body></html>"
    )
    ext = extract_html(html)
    assert ext.title == "My Title"
    assert "Heading One" in ext.headings
    assert "Paragraph text here." in ext.text


def test_malformed_html_does_not_crash():
    ext = extract_html("<html><body><p>Partial")
    assert ext.text
    assert ext.text.strip() == "Partial"


def test_malformed_nested_html_does_not_crash():
    ext = extract_html("<div><p>a</p><span><b>b")
    assert "a" in ext.text
    assert "b" in ext.text


def test_scripts_styles_templates_removed():
    html = (
        "<html><head><title>T</title><style>body{color:red}</style>"
        "<script>var x = 1;</script></head><body>"
        "<script>alert('evil')</script>"
        "<style>p{}</style>"
        "<template>template content</template>"
        "<noscript>noscript content</noscript>"
        "<p>Real content</p>"
        "</body></html>"
    )
    ext = extract_html(html)
    assert "Real content" in ext.text
    assert "alert" not in ext.text
    assert "var x" not in ext.text
    assert "template content" not in ext.text
    assert "noscript content" not in ext.text
    assert "color:red" not in ext.text


def test_nav_footer_aside_form_removed():
    html = (
        "<html><body><nav>Navigation</nav><footer>Footer</footer>"
        "<aside>Aside</aside><form>Form field</form>"
        "<p>Main content</p></body></html>"
    )
    ext = extract_html(html)
    assert "Main content" in ext.text
    for snippet in ("Navigation", "Footer", "Aside", "Form"):
        assert snippet not in ext.text


def test_html_entities_decoded():
    html = "<html><body><p>Fish &amp; Chips &lt;tag&gt; &#169; 2024</p></body></html>"
    ext = extract_html(html)
    assert "Fish & Chips <tag> © 2024" in ext.text


def test_missing_title_yields_empty_string():
    ext = extract_html("<html><body><p>No title</p></body></html>")
    assert ext.title == ""


def test_encoding_fallback_for_non_utf8(monkeypatch):
    # Simulate Latin-1 bytes that would fail strict UTF-8.
    content = "café déjà vu ñ".encode("latin-1")
    decoded = decode_content(content, "text/html; charset=iso-8859-1")
    assert "café" in decoded


def test_truncation_is_enforced():
    html = "<html><body><p>" + " ".join(["word"] * 5000) + "</p></body></html>"
    ext = extract_html(html, max_chars=100)
    assert ext.truncated is True
    assert len(ext.text) <= 100


def test_no_truncation_within_limit():
    html = "<html><body><p>Short text</p></body></html>"
    ext = extract_html(html, max_chars=1000)
    assert ext.truncated is False
    assert "Short text" in ext.text


def test_empty_page():
    ext = extract_html("")
    assert ext.title == ""
    assert ext.text == ""
    assert ext.headings == []


def test_extract_page_dispatches_on_content_type():
    assert extract_page(b"<title>X</title><p>hi</p>", "text/html").title == "X"
    plain = extract_page(b"plain text", "text/plain")
    assert plain.text == "plain text"
    assert plain.title == ""


def test_extract_plain_text_lowercases_title():
    ext = extract_plain_text("Hello world")
    assert ext.text == "Hello world"
    assert ext.title == ""
    assert ext.truncated is False
