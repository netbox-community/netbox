from django import template
from django.urls import reverse

from extras.models import ExportTemplate
from utilities.utils import prepare_cloned_fields

register = template.Library()


def _get_viewname(instance, action):
    """
    Return the appropriate viewname for adding, editing, or deleting an instance.
    """

    # Validate action
    assert action in ('add', 'edit', 'delete')
    viewname = "{}:{}_{}".format(
        instance._meta.app_label, instance._meta.model_name, action
    )

    return viewname


#
# Instance buttons
#

@register.inclusion_tag('buttons/clone.html')
def clone_button(instance):
    url = reverse(_get_viewname(instance, 'add'))

    # Populate cloned field values
    param_string = prepare_cloned_fields(instance)
    if param_string:
        url = f'{url}?{param_string}'

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/edit.html')
def edit_button(instance):
    viewname = _get_viewname(instance, 'edit')
    url = reverse(viewname, kwargs={'pk': instance.pk})

    return {
        'url': url,
    }


@register.inclusion_tag('buttons/delete.html')
def delete_button(instance):
    viewname = _get_viewname(instance, 'delete')
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
def export_button(context, content_type=None):
    add_exporttemplate_link = None

    if content_type is not None:
        user = context['request'].user
        export_templates = ExportTemplate.objects.restrict(user, 'view').filter(content_type=content_type)
        if user.is_staff and user.has_perm('extras.add_exporttemplate'):
            add_exporttemplate_link = f"{reverse('admin:extras_exporttemplate_add')}?content_type={content_type.pk}"
    else:
        export_templates = []

    return {
        'url_params': context['request'].GET,
        'export_templates': export_templates,
        'add_exporttemplate_link': add_exporttemplate_link,
    }
