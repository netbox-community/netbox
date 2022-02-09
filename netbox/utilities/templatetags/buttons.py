from django import template
from django.urls import reverse

from extras.models import ExportTemplate
from utilities.utils import get_viewname, prepare_cloned_fields

register = template.Library()


#
# Instance buttons
#

@register.inclusion_tag('buttons/clone.html')
def clone_button(instance):
    url = reverse(get_viewname(instance, 'add'))

    # Populate cloned field values
    param_string = prepare_cloned_fields(instance).urlencode()
    if param_string:
        url = f'{url}?{param_string}'

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/edit.html')
def edit_button(instance):
    viewname = get_viewname(instance, 'edit')
    url = reverse(viewname, kwargs={'pk': instance.pk})

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/delete.html')
def delete_button(instance):
    viewname = get_viewname(instance, 'delete')
    url = reverse(viewname, kwargs={'pk': instance.pk})

    return {
        'url': url,
    }


#
# List buttons
#

@register.inclusion_tag('buttons/add.html')
def add_button(url):
    url = reverse(url)

    return {
        'add_url': url,
    }


@register.inclusion_tag('buttons/import.html')
def import_button(url):

    return {
        'import_url': url,
    }


@register.inclusion_tag('buttons/export.html', takes_context=True)
def export_button(context, content_type):
    user = context['request'].user

    # Determine if the "all data" export returns CSV or YAML
    data_format = 'YAML' if hasattr(content_type.model_class(), 'to_yaml') else 'CSV'

    # Retrieve all export templates for this model
    export_templates = ExportTemplate.objects.restrict(user, 'view').filter(content_type=content_type)

    return {
        'perms': context['perms'],
        'content_type': content_type,
        'url_params': context['request'].GET.urlencode() if context['request'].GET else '',
        'export_templates': export_templates,
        'data_format': data_format,
    }
