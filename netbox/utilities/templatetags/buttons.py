from django import template
from django.urls import reverse

from extras.models import ExportTemplate
from utilities.utils import prepare_cloned_fields

register = template.Library()


@register.inclusion_tag('buttons/add.html')
def add_button(url):
    return {
        'add_url': url,
    }


@register.inclusion_tag('buttons/import.html')
def import_button(url):
    return {
        'import_url': url,
    }


@register.inclusion_tag('buttons/clone.html')
def clone_button(url, instance):

    url = reverse(url)
    param_string = prepare_cloned_fields(instance)
    if param_string:
        url = '{}?{}'.format(url, param_string)

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/export.html', takes_context=True)
def export_button(context, content_type=None):
    export_templates = ExportTemplate.objects.filter(content_type=content_type)
    return {
        'url_params': context['request'].GET,
        'export_templates': export_templates,
    }
