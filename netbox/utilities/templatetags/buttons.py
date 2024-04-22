from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse

from core.models import ObjectType
from extras.models import Bookmark, ExportTemplate
from utilities.querydict import prepare_cloned_fields
from utilities.views import get_viewname

__all__ = (
    'add_button',
    'bookmark_button',
    'bulk_delete_button',
    'bulk_edit_button',
    'clone_button',
    'delete_button',
    'edit_button',
    'export_button',
    'import_button',
    'sync_button',
)

register = template.Library()


#
# Instance buttons
#

@register.inclusion_tag('buttons/bookmark.html', takes_context=True)
def bookmark_button(context, instance):
    # Check if this user has already bookmarked the object
    content_type = ContentType.objects.get_for_model(instance)
    bookmark = Bookmark.objects.filter(
        object_type=content_type,
        object_id=instance.pk,
        user=context['request'].user
    ).first()

    # Compile form URL & data
    if bookmark:
        form_url = reverse('extras:bookmark_delete', kwargs={'pk': bookmark.pk})
        form_data = {
            'confirm': 'true',
        }
    else:
        form_url = reverse('extras:bookmark_add')
        form_data = {
            'object_type': content_type.pk,
            'object_id': instance.pk,
        }

    return {
        'bookmark': bookmark,
        'form_url': form_url,
        'form_data': form_data,
        'return_url': instance.get_absolute_url(),
    }


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


@register.inclusion_tag('buttons/sync.html')
def sync_button(instance):
    viewname = get_viewname(instance, 'sync')
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
    object_type = ObjectType.objects.get_for_model(model)
    user = context['request'].user

    # Determine if the "all data" export returns CSV or YAML
    data_format = 'YAML' if hasattr(object_type.model_class(), 'to_yaml') else 'CSV'

    # Retrieve all export templates for this model
    export_templates = ExportTemplate.objects.restrict(user, 'view').filter(object_types=object_type)

    return {
        'perms': context['perms'],
        'object_type': object_type,
        'url_params': context['request'].GET.urlencode() if context['request'].GET else '',
        'export_templates': export_templates,
        'data_format': data_format,
    }


@register.inclusion_tag('buttons/bulk_edit.html', takes_context=True)
def bulk_edit_button(context, model, action='bulk_edit', query_params=None):
    try:
        url = reverse(get_viewname(model, action))
        if query_params:
            url = f'{url}?{query_params.urlencode()}'
    except NoReverseMatch:
        url = None

    return {
        'htmx_navigation': context.get('htmx_navigation'),
        'url': url,
    }


@register.inclusion_tag('buttons/bulk_delete.html', takes_context=True)
def bulk_delete_button(context, model, action='bulk_delete', query_params=None):
    try:
        url = reverse(get_viewname(model, action))
        if query_params:
            url = f'{url}?{query_params.urlencode()}'
    except NoReverseMatch:
        url = None

    return {
        'htmx_navigation': context.get('htmx_navigation'),
        'url': url,
    }
