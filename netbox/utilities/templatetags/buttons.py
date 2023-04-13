from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse

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
    else:
        url = None

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
def add_button(model, action='add'):
    try:
        url = reverse(get_viewname(model, action))
    except NoReverseMatch:
        url = None

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/import.html')
def import_button(model, action='import'):
    try:
        url = reverse(get_viewname(model, action))
    except NoReverseMatch:
        url = None

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/export.html', takes_context=True)
def export_button(context, model):
    content_type = ContentType.objects.get_for_model(model)
    user = context['request'].user

    # Determine if the "all data" export returns CSV or YAML
    data_format = 'YAML' if hasattr(content_type.model_class(), 'to_yaml') else 'CSV'

    # Retrieve all export templates for this model
    export_templates = ExportTemplate.objects.restrict(user, 'view').filter(content_types=content_type)

    return {
        'perms': context['perms'],
        'content_type': content_type,
        'url_params': context['request'].GET.urlencode() if context['request'].GET else '',
        'export_templates': export_templates,
        'data_format': data_format,
    }


@register.inclusion_tag('buttons/bulk_edit.html')
def bulk_edit_button(model, action='bulk_edit', query_params=None):
    try:
        url = reverse(get_viewname(model, action))
        if query_params:
            url = f'{url}?{query_params.urlencode()}'
    except NoReverseMatch:
        url = None

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/bulk_delete.html')
def bulk_delete_button(model, action='bulk_delete', query_params=None):
    try:
        url = reverse(get_viewname(model, action))
        if query_params:
            url = f'{url}?{query_params.urlencode()}'
    except NoReverseMatch:
        url = None

    return {
        'url': url,
    }
