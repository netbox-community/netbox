from typing import Dict

from django import template

from netbox.forms import SearchForm

register = template.Library()
search_form = SearchForm()


@register.inclusion_tag("search/searchbar.html")
def search_options(request) -> Dict:

    # Provide search options to template.
    return {
        'options': search_form.get_options(),
        'request': request,
    }
