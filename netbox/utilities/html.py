import re

from django.utils.html import escape

__all__ = (
    'highlight',
)


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
    except ValueError as e:
        # Match not found
        return escape(value)

    # Trim pre/post sections to length
    if trim_pre and len(pre) > trim_pre:
        pre = trim_placeholder + pre[-trim_pre:]
    if trim_post and len(post) > trim_post:
        post = post[:trim_post] + trim_placeholder

    return f'{escape(pre)}<mark>{escape(match)}</mark>{escape(post)}'
