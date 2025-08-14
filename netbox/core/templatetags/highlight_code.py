from django import template
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

register = template.Library()


@register.simple_tag
def highlight_code(value, filename: str):
    """
    Highlight code using Pygments.
    """
    if not value:
        return ''
    try:
        lexer = get_lexer_for_filename(filename)
    except ClassNotFound:
        return mark_safe(f"<pre>{value}</pre>")  # Fallback to plain text if no lexer was found
    return mark_safe(
        highlight(
            value,
            lexer,
            HtmlFormatter(
                 linenos="inline", classprefix="pygments-", style="solarized-light"
            ),
        )
    )
