from typing import Dict
from netbox.forms import SearchForm
from django import template

register = template.Library()

search_form = None


@register.inclusion_tag("search/searchbar.html")
def search_options(request) -> Dict:
    global search_form

    if not search_form:
        search_form = SearchForm()

    """Provide search options to template."""
    return {
        'options': search_form.get_options(),
        'request': request,
    }
