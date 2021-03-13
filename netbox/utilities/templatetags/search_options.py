from typing import Dict
from netbox.forms import SearchForm
from django import template

register = template.Library()

search_form = SearchForm()


@register.inclusion_tag("search/searchbar.html")
def search_options() -> Dict:
    """Provide search options to template."""
    return {"options": search_form.options}
