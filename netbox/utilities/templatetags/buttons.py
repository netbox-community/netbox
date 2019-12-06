from django import template
from django.urls import reverse

from extras.models import ExportTemplate

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

    # Populate form field values
    params = {}
    for field_name in getattr(instance, 'clone_fields', []):
        field = instance._meta.get_field(field_name)
        field_value = field.value_from_object(instance)

        # Swap out False with URL-friendly value
        if field_value is False:
            field_value = ''

        # Omit empty values
        if field_value not in (None, ''):
            params[field_name] = field_value

        # TODO: Tag replication

    # Append parameters to URL
    param_string = '&'.join(['{}={}'.format(k, v) for k, v in params.items()])
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
