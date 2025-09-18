from django.template import loader
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext as _

from core.models import ObjectType
from extras.models import ExportTemplate
from utilities.querydict import prepare_cloned_fields
from utilities.views import get_action_url

__all__ = (
    'AddObject',
    'BulkDelete',
    'BulkEdit',
    'BulkExport',
    'BulkImport',
    'BulkRename',
    'CloneObject',
    'DeleteObject',
    'EditObject',
    'ObjectAction',
)


class ObjectAction:
    """
    Base class for single- and multi-object operations.

    Params:
        name: The action name appended to the module for view resolution
        label: Human-friendly label for the rendered button
        template_name: Name of the HTML template which renders the button
        multi: Set to True if this action is performed by selecting multiple objects (i.e. using a table)
        permissions_required: The set of permissions a user must have to perform the action
        url_kwargs: The set of URL keyword arguments to pass when resolving the view's URL
    """
    name = ''
    label = None
    template_name = None
    multi = False
    permissions_required = set()
    url_kwargs = []

    @classmethod
    def get_url(cls, obj):
        kwargs = {
            kwarg: getattr(obj, kwarg) for kwarg in cls.url_kwargs
        }
        try:
            return get_action_url(obj, action=cls.name, kwargs=kwargs)
        except NoReverseMatch:
            return

    @classmethod
    def get_url_params(cls, context):
        request = context['request']
        params = request.GET.copy()
        if 'return_url' in context:
            params['return_url'] = context['return_url']
        return params

    @classmethod
    def get_context(cls, context, obj):
        """
        Return any additional context data needed to render the button.
        """
        return {}

    @classmethod
    def render(cls, context, obj, **kwargs):
        ctx = {
            'perms': context['perms'],
            'request': context['request'],
            'url': cls.get_url(obj),
            'url_params': cls.get_url_params(context),
            'label': cls.label,
            **cls.get_context(context, obj),
            **kwargs,
        }
        return loader.render_to_string(cls.template_name, ctx)


class AddObject(ObjectAction):
    """
    Create a new object.
    """
    name = 'add'
    label = _('Add')
    permissions_required = {'add'}
    template_name = 'buttons/add.html'


class CloneObject(ObjectAction):
    """
    Populate the new object form with select details from an existing object.
    """
    name = 'add'
    label = _('Clone')
    permissions_required = {'add'}
    template_name = 'buttons/clone.html'

    @classmethod
    def get_url(cls, obj):
        url = super().get_url(obj)
        param_string = prepare_cloned_fields(obj).urlencode()
        return f'{url}?{param_string}' if param_string else None


class EditObject(ObjectAction):
    """
    Edit a single object.
    """
    name = 'edit'
    label = _('Edit')
    permissions_required = {'change'}
    url_kwargs = ['pk']
    template_name = 'buttons/edit.html'


class DeleteObject(ObjectAction):
    """
    Delete a single object.
    """
    name = 'delete'
    label = _('Delete')
    permissions_required = {'delete'}
    url_kwargs = ['pk']
    template_name = 'buttons/delete.html'


class BulkImport(ObjectAction):
    """
    Import multiple objects at once.
    """
    name = 'bulk_import'
    label = _('Import')
    permissions_required = {'add'}
    template_name = 'buttons/import.html'


class BulkExport(ObjectAction):
    """
    Export multiple objects at once.
    """
    name = 'export'
    label = _('Export')
    permissions_required = {'view'}
    template_name = 'buttons/export.html'

    @classmethod
    def get_context(cls, context, model):
        object_type = ObjectType.objects.get_for_model(model)
        user = context['request'].user

        # Determine if the "all data" export returns CSV or YAML
        data_format = 'YAML' if hasattr(object_type.model_class(), 'to_yaml') else 'CSV'

        # Retrieve all export templates for this model
        export_templates = ExportTemplate.objects.restrict(user, 'view').filter(object_types=object_type)

        return {
            'object_type': object_type,
            'url_params': context['request'].GET.urlencode() if context['request'].GET else '',
            'export_templates': export_templates,
            'data_format': data_format,
        }


class BulkEdit(ObjectAction):
    """
    Change the value of one or more fields on a set of objects.
    """
    name = 'bulk_edit'
    label = _('Edit Selected')
    multi = True
    permissions_required = {'change'}
    template_name = 'buttons/bulk_edit.html'


class BulkRename(ObjectAction):
    """
    Rename multiple objects at once.
    """
    name = 'bulk_rename'
    label = _('Rename Selected')
    multi = True
    permissions_required = {'change'}
    template_name = 'buttons/bulk_rename.html'


class BulkDelete(ObjectAction):
    """
    Delete each of a set of objects.
    """
    name = 'bulk_delete'
    label = _('Delete Selected')
    multi = True
    permissions_required = {'delete'}
    template_name = 'buttons/bulk_delete.html'
