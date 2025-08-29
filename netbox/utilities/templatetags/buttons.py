from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from core.models import ObjectType
from extras.models import Bookmark, ExportTemplate, Subscription
from netbox.models.features import NotificationsMixin
from utilities.querydict import prepare_cloned_fields
from utilities.views import get_action_url

__all__ = (
    'action_buttons',
    'add_button',
    'bookmark_button',
    'bulk_delete_button',
    'bulk_edit_button',
    'clone_button',
    'delete_button',
    'edit_button',
    'export_button',
    'import_button',
    'subscribe_button',
    'sync_button',
)

register = template.Library()


@register.simple_tag(takes_context=True)
def action_buttons(context, actions, obj, multi=False, **kwargs):
    buttons = [
        action.render(context, obj, **kwargs)
        for action in actions if action.multi == multi
    ]
    return mark_safe(''.join(buttons))


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


@register.inclusion_tag('buttons/subscribe.html', takes_context=True)
def subscribe_button(context, instance):
    # Skip for objects which don't support notifications
    if not (issubclass(instance.__class__, NotificationsMixin)):
        return {}

    # Check if this user has already subscribed to the object
    content_type = ContentType.objects.get_for_model(instance)
    subscription = Subscription.objects.filter(
        object_type=content_type,
        object_id=instance.pk,
        user=context['request'].user
    ).first()

    # Compile form URL & data
    if subscription:
        form_url = reverse('extras:subscription_delete', kwargs={'pk': subscription.pk})
        form_data = {
            'confirm': 'true',
        }
    else:
        form_url = reverse('extras:subscription_add')
        form_data = {
            'object_type': content_type.pk,
            'object_id': instance.pk,
        }

    return {
        'subscription': subscription,
        'form_url': form_url,
        'form_data': form_data,
        'return_url': instance.get_absolute_url(),
    }


#
# Legacy object buttons
#

# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/clone.html')
def clone_button(instance):
    # Resolve URL path
    try:
        url = get_action_url(instance, action='add')
    except NoReverseMatch:
        return {
            'url': None,
        }

    # Populate cloned field values and return full URL
    param_string = prepare_cloned_fields(instance).urlencode()
    return {
        'url': f'{url}?{param_string}' if param_string else None,
    }


# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/edit.html')
def edit_button(instance):
    url = get_action_url(instance, action='edit', kwargs={'pk': instance.pk})

    return {
        'url': url,
        'label': _('Edit'),
    }


# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/delete.html')
def delete_button(instance):
    url = get_action_url(instance, action='delete', kwargs={'pk': instance.pk})

    return {
        'url': url,
        'label': _('Delete'),
    }


# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/sync.html')
def sync_button(instance):
    url = get_action_url(instance, action='sync', kwargs={'pk': instance.pk})

    return {
        'label': _('Sync'),
        'url': url,
    }


#
# Legacy list buttons
#

# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/add.html')
def add_button(model, action='add', return_url=None):
    try:
        url = get_action_url(model, action=action)
    except NoReverseMatch:
        url = None

    return {
        'url': url,
        'label': _('Add'),
        'return_url': return_url,
    }


# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/import.html')
def import_button(model, action='bulk_import'):
    try:
        url = get_action_url(model, action=action)
    except NoReverseMatch:
        url = None

    return {
        'url': url,
        'label': _('Import'),
    }


# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/export.html', takes_context=True)
def export_button(context, model):
    object_type = ObjectType.objects.get_for_model(model)
    user = context['request'].user

    # Determine if the "all data" export returns CSV or YAML
    data_format = 'YAML' if hasattr(object_type.model_class(), 'to_yaml') else 'CSV'

    # Retrieve all export templates for this model
    export_templates = ExportTemplate.objects.restrict(user, 'view').filter(object_types=object_type)

    return {
        'label': _('Export'),
        'perms': context['perms'],
        'object_type': object_type,
        'url_params': context['request'].GET.urlencode() if context['request'].GET else '',
        'export_templates': export_templates,
        'data_format': data_format,
    }


# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/bulk_edit.html', takes_context=True)
def bulk_edit_button(context, model, action='bulk_edit', query_params=None):
    try:
        url = get_action_url(model, action=action)
        if query_params:
            url = f'{url}?{query_params.urlencode()}'
    except NoReverseMatch:
        url = None

    return {
        'label': _('Edit Selected'),
        'url': url,
        'htmx_navigation': context.get('htmx_navigation'),
    }


# TODO: Remove in NetBox v4.7
@register.inclusion_tag('buttons/bulk_delete.html', takes_context=True)
def bulk_delete_button(context, model, action='bulk_delete', query_params=None):
    try:
        url = get_action_url(model, action=action)
        if query_params:
            url = f'{url}?{query_params.urlencode()}'
    except NoReverseMatch:
        url = None

    return {
        'label': _('Delete Selected'),
        'url': url,
        'htmx_navigation': context.get('htmx_navigation'),
    }
