import markdown
from markdown.inlinepatterns import SimpleTagPattern

__all__ = (
    'StrikethroughExtension',
)

STRIKE_RE = r'(~{2})(.+?)(~{2})'


class StrikethroughExtension(markdown.Extension):
    """
    A python-markdown extension which support strikethrough formatting (e.g. "~~text~~").
    """
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            SimpleTagPattern(STRIKE_RE, 'del'),
            'strikethrough',
            200
        )
