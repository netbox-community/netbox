import re

import nh3
from django.utils.html import escape

from .constants import HTML_ALLOWED_ATTRIBUTES, HTML_ALLOWED_TAGS, IMAGE_URL_SCHEMES

__all__ = (
    'clean_html',
    'foreground_color',
    'highlight',
)

SCHEME_RE = re.compile(r'^([a-zA-Z][a-zA-Z0-9+.-]*):')

# Per the URL spec, browsers ignore leading/trailing C0 control characters & space, and strip any tab or
# newline characters appearing within a URL. We must normalize accordingly before checking the scheme.
URL_STRIP_CHARS = ''.join(chr(c) for c in range(0x21))
URL_REMOVE_CHARS = str.maketrans('', '', '\t\r\n')


def _attribute_filter(tag, attr, value):
    """Returns str to keep/modify attribute, None to remove it."""
    if tag == 'img' and attr == 'src':
        match = SCHEME_RE.match(value.strip(URL_STRIP_CHARS).translate(URL_REMOVE_CHARS))
        if match and match.group(1).lower() not in IMAGE_URL_SCHEMES:
            return None
    return value


def clean_html(html, schemes):
    """
    Sanitizes HTML based on a whitelist of allowed tags and attributes.
    Also takes a list of allowed URI schemes.
    """
    url_schemes = set(schemes)
    attribute_filter = None if url_schemes <= IMAGE_URL_SCHEMES else _attribute_filter
    return nh3.clean(
        html,
        tags=HTML_ALLOWED_TAGS,
        attributes=HTML_ALLOWED_ATTRIBUTES,
        url_schemes=url_schemes,
        attribute_filter=attribute_filter,
    )


def foreground_color(bg_color, dark='000000', light='ffffff'):
    """
    Return the ideal foreground color (dark or light) for a given background color in hexadecimal RGB format.

    :param dark: RBG color code for dark text
    :param light: RBG color code for light text
    """
    THRESHOLD = 150
    bg_color = bg_color.strip('#')
    r, g, b = [int(bg_color[c:c + 2], 16) for c in (0, 2, 4)]
    if r * 0.299 + g * 0.587 + b * 0.114 > THRESHOLD:
        return dark
    return light


def highlight(value, highlight, trim_pre=None, trim_post=None, trim_placeholder='...'):
    """
    Highlight a string within a string and optionally trim the pre/post portions of the original string.

    Args:
        value: The body of text being searched against
        highlight: The string of compiled regex pattern to highlight in `value`
        trim_pre: Maximum length of pre-highlight text to include
        trim_post: Maximum length of post-highlight text to include
        trim_placeholder: String value to swap in for trimmed pre/post text
    """
    # Split value on highlight string
    try:
        if type(highlight) is re.Pattern:
            pre, match, post = highlight.split(value, maxsplit=1)
        else:
            highlight = re.escape(highlight)
            pre, match, post = re.split(fr'({highlight})', value, maxsplit=1, flags=re.IGNORECASE)
    except ValueError:
        # Match not found
        return escape(value)

    # Trim pre/post sections to length
    if trim_pre and len(pre) > trim_pre:
        pre = trim_placeholder + pre[-trim_pre:]
    if trim_post and len(post) > trim_post:
        post = post[:trim_post] + trim_placeholder

    return f'{escape(pre)}<mark>{escape(match)}</mark>{escape(post)}'
