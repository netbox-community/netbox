from django.test import SimpleTestCase, tag

from utilities.html import clean_html

TEST_SCHEMES = ['file', 'ftp', 'ssh', 'http', 'https']


class CleanHTMLURLPolicyTestCase(SimpleTestCase):

    @tag('regression')
    def test_img_src_disallowed_schemes(self):
        """
        file:/ftp:/ssh: image sources are stripped while non-src attributes survive.
        (Core regression: these schemes are in ALLOWED_URL_SCHEMES but forbidden for images.)
        """
        html = (
            '<img src="file:///etc" alt="a">'
            '<img src="ftp://host/i.png" alt="b">'
            '<img src="ssh://host/i.png" alt="c">'
        )
        result = clean_html(html, TEST_SCHEMES)
        self.assertNotIn('file:///', result)
        self.assertNotIn('ftp://', result)
        self.assertNotIn('ssh://', result)
        self.assertIn('alt="a"', result)
        self.assertIn('alt="b"', result)
        self.assertIn('alt="c"', result)

    @tag('regression')
    def test_img_src_leading_whitespace(self):
        """Disallowed schemes hidden behind leading whitespace are still stripped."""
        html = '<img src=" ssh://host/i.png">'
        result = clean_html(html, TEST_SCHEMES)
        self.assertNotIn('ssh://', result)

    @tag('regression')
    def test_img_src_embedded_control_characters(self):
        """Disallowed schemes obscured by tab/newline/control characters are still stripped."""
        html = (
            '<img src="ss&#9;h://host/i.png">'
            '<img src="fi&#13;le:///etc">'
            '<img src="&#1;ftp://host/i.png">'
        )
        result = clean_html(html, TEST_SCHEMES)
        self.assertNotIn('h://host', result)
        self.assertNotIn('le:///etc', result)
        self.assertNotIn('ftp://host', result)

    @tag('regression')
    def test_img_src_http_https_and_relative(self):
        """http/https/relative image sources are retained."""
        html = (
            '<img src="https://example.com/i1.png">'
            '<img src="http://example.com/i2.png">'
            '<img src="/rel.png">'
            '<img src="rel.png">'
            '<img src="//cdn.example.com/i3.png">'
        )
        result = clean_html(html, TEST_SCHEMES)
        self.assertIn('example.com/i1.png', result)
        self.assertIn('example.com/i2.png', result)
        self.assertIn('src="/rel.png"', result)
        self.assertIn('src="rel.png"', result)
        self.assertIn('src="//cdn.example.com/i3.png"', result)

    @tag('regression')
    def test_link_href_preserves_all_schemes(self):
        """a[href] behavior is unchanged — all configured schemes remain allowed."""
        html = (
            '<a href="ssh://host">s</a>'
            '<a href="file:///etc">f</a>'
            '<a href="ftp://host">f</a>'
            '<a href="https://example.com">h</a>'
        )
        result = clean_html(html, TEST_SCHEMES)
        self.assertIn('href="ssh://host"', result)
        self.assertIn('href="file:///etc"', result)
        self.assertIn('href="ftp://host"', result)
        self.assertIn('href="https://example.com"', result)

    @tag('regression')
    def test_mixed_content(self):
        """Different policies for img vs a in the same input."""
        html = '<a href="ssh://host">L</a><img src="ssh://host/i.png">'
        result = clean_html(html, TEST_SCHEMES)
        self.assertIn('href="ssh://host"', result)
        self.assertNotIn('ssh://host/i.png', result)

    @tag('regression')
    def test_javascript_url_blocked(self):
        """nh3's url_schemes filtering still applies with the attribute filter in place."""
        html = '<a href="javascript:alert(1)">x</a><img src="javascript:alert(1)">'
        result = clean_html(html, ['https', 'mailto'])
        self.assertNotIn('javascript:', result)

    @tag('regression')
    def test_img_src_respects_allowed_url_schemes(self):
        """Image sources must respect ALLOWED_URL_SCHEMES, not just IMAGE_URL_SCHEMES."""
        html = '<img src="http://example.com/i.png">'
        result = clean_html(html, ['https', 'mailto'])
        self.assertNotIn('http://example.com', result)
