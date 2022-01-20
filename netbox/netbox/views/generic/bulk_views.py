import logging
import re
from copy import deepcopy

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import transaction, IntegrityError
from django.db.models import ManyToManyField, ProtectedError
from django.forms import Form, ModelMultipleChoiceField, MultipleHiddenInput, Textarea
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_tables2.export import TableExport

from extras.models import ExportTemplate
from extras.signals import clear_webhooks
from utilities.error_handlers import handle_protectederror
from utilities.exceptions import PermissionsViolation
from utilities.forms import (
    BootstrapMixin, BulkRenameForm, ConfirmationForm, CSVDataField, CSVFileField, restrict_form_fields,
)
from utilities.htmx import is_htmx
from utilities.permissions import get_permission_for_model
from utilities.tables import configure_table
from utilities.views import GetReturnURLMixin
from .base import GenericView

__all__ = (
    'BulkComponentCreateView',
    'BulkCreateView',
    'BulkDeleteView',
    'BulkEditView',
    'BulkImportView',
    'BulkRenameView',
    'ObjectListView',
)


class ObjectListView(GenericView):
    """
    Display multiple objects, all of the same type, as a table.

    Attributes:
        filterset: A django-filter FilterSet that is applied to the queryset
        filterset_form: The form class used to render filter options
        table: The django-tables2 Table used to render the objects list
        action_buttons: A list of buttons to include at the top of the page
    """
    template_name = 'generic/object_list.html'
    filterset = None
    filterset_form = None
    table = None
    action_buttons = ('add', 'import', 'export')

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'view')

    def get_table(self, request, permissions):
        """
        Return the django-tables2 Table instance to be used for rendering the objects list.

        Args:
            request: The current request
            permissions: A dictionary mapping of the view, add, change, and delete permissions to booleans indicating
                whether the user has each
        """
        table = self.table(self.queryset, user=request.user)
        if 'pk' in table.base_columns and (permissions['change'] or permissions['delete']):
            table.columns.show('pk')

        return table

    def get_extra_context(self, request):
        """
        Return any additional context data for the template.

        Agrs:
            request: The current request
        """
        return {}

    def get(self, request):
        """
        GET request handler.

        Args:
            request: The current request
        """
        model = self.queryset.model
        content_type = ContentType.objects.get_for_model(model)

        if self.filterset:
            self.queryset = self.filterset(request.GET, self.queryset).qs

        # Compile a dictionary indicating which permissions are available to the current user for this model
        permissions = {}
        for action in ('add', 'change', 'delete', 'view'):
            perm_name = get_permission_for_model(model, action)
            permissions[action] = request.user.has_perm(perm_name)

        if 'export' in request.GET:

            # Export the current table view
            if request.GET['export'] == 'table':
                table = self.get_table(request, permissions)
                columns = [name for name, _ in table.selected_columns]
                return self.export_table(table, columns)

            # Render an ExportTemplate
            elif request.GET['export']:
                template = get_object_or_404(ExportTemplate, content_type=content_type, name=request.GET['export'])
                return self.export_template(template, request)

            # Check for YAML export support on the model
            elif hasattr(model, 'to_yaml'):
                response = HttpResponse(self.export_yaml(), content_type='text/yaml')
                filename = 'netbox_{}.yaml'.format(self.queryset.model._meta.verbose_name_plural)
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
                return response

            # Fall back to default table/YAML export
            else:
                table = self.get_table(request, permissions)
                return self.export_table(table)

        # Render the objects table
        table = self.get_table(request, permissions)
        configure_table(table, request)

        # If this is an HTMX request, return only the rendered table HTML
        if is_htmx(request):
            return render(request, 'htmx/table.html', {
                'table': table,
            })

        context = {
            'content_type': content_type,
            'table': table,
            'permissions': permissions,
            'action_buttons': self.action_buttons,
            'filter_form': self.filterset_form(request.GET, label_suffix='') if self.filterset_form else None,
        }
        context.update(self.get_extra_context(request))

        return render(request, self.template_name, context)

    #
    # Export methods
    #

    def export_yaml(self):
        """
        Export the queryset of objects as concatenated YAML documents.
        """
        yaml_data = [obj.to_yaml() for obj in self.queryset]

        return '---\n'.join(yaml_data)

    def export_table(self, table, columns=None, filename=None):
        """
        Export all table data in CSV format.

        Args:
            table: The Table instance to export
            columns: A list of specific columns to include. If None, all columns will be exported.
            filename: The name of the file attachment sent to the client. If None, will be determined automatically
                from the queryset model name.
        """
        exclude_columns = {'pk', 'actions'}
        if columns:
            all_columns = [col_name for col_name, _ in table.selected_columns + table.available_columns]
            exclude_columns.update({
                col for col in all_columns if col not in columns
            })
        exporter = TableExport(
            export_format=TableExport.CSV,
            table=table,
            exclude_columns=exclude_columns
        )
        return exporter.response(
            filename=filename or f'netbox_{self.queryset.model._meta.verbose_name_plural}.csv'
        )

    def export_template(self, template, request):
        """
        Render an ExportTemplate using the current queryset.

        Args:
            template: ExportTemplate instance
            request: The current request
        """
        try:
            return template.render_to_response(self.queryset)
        except Exception as e:
            messages.error(request, f"There was an error rendering the selected export template ({template.name}): {e}")
            return redirect(request.path)


class BulkCreateView(GetReturnURLMixin, GenericView):
    """
    Create new objects in bulk.

    form: Form class which provides the `pattern` field
    model_form: The ModelForm used to create individual objects
    pattern_target: Name of the field to be evaluated as a pattern (if any)
    """
    form = None
    model_form = None
    pattern_target = ''

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

    def _create_objects(self, form, request):
        new_objects = []

        # Create objects from the expanded. Abort the transaction on the first validation error.
        for value in form.cleaned_data['pattern']:

            # Reinstantiate the model form each time to avoid overwriting the same instance. Use a mutable
            # copy of the POST QueryDict so that we can update the target field value.
            model_form = self.model_form(request.POST.copy())
            model_form.data[self.pattern_target] = value

            # Validate each new object independently.
            if model_form.is_valid():
                obj = model_form.save()
                new_objects.append(obj)
            else:
                # Copy any errors on the pattern target field to the pattern form.
                errors = model_form.errors.as_data()
                if errors.get(self.pattern_target):
                    form.add_error('pattern', errors[self.pattern_target])
                # Raise an IntegrityError to break the for loop and abort the transaction.
                raise IntegrityError()

        return new_objects

    def get(self, request):
        # Set initial values for visible form fields from query args
        initial = {}
        for field in getattr(self.model_form._meta, 'fields', []):
            if request.GET.get(field):
                initial[field] = request.GET[field]

        form = self.form()
        model_form = self.model_form(initial=initial)

        return render(request, self.template_name, {
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'form': form,
            'model_form': model_form,
            'return_url': self.get_return_url(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkCreateView')
        model = self.queryset.model
        form = self.form(request.POST)
        model_form = self.model_form(request.POST)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                with transaction.atomic():
                    new_objs = self._create_objects(form, request)

                    # Enforce object-level permissions
                    if self.queryset.filter(pk__in=[obj.pk for obj in new_objs]).count() != len(new_objs):
                        raise PermissionsViolation

                # If we make it to this point, validation has succeeded on all new objects.
                msg = f"Added {len(new_objs)} {model._meta.verbose_name_plural}"
                logger.info(msg)
                messages.success(request, msg)

                if '_addanother' in request.POST:
                    return redirect(request.path)
                return redirect(self.get_return_url(request))

            except IntegrityError:
                pass

            except PermissionsViolation:
                msg = "Object creation failed due to object-level permissions violation"
                logger.debug(msg)
                form.add_error(None, msg)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'form': form,
            'model_form': model_form,
            'obj_type': model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })


class BulkImportView(GetReturnURLMixin, GenericView):
    """
    Import objects in bulk (CSV format).

    Attributes:
        model_form: The form used to create each imported object
        table: The django-tables2 Table used to render the list of imported objects
        widget_attrs: A dict of attributes to apply to the import widget (e.g. to require a session key)
    """
    template_name = 'generic/object_bulk_import.html'
    model_form = None
    table = None
    widget_attrs = {}

    def _import_form(self, *args, **kwargs):

        class ImportForm(BootstrapMixin, Form):
            csv = CSVDataField(
                from_form=self.model_form,
                widget=Textarea(attrs=self.widget_attrs)
            )
            csv_file = CSVFileField(
                label="CSV file",
                from_form=self.model_form,
                required=False
            )

            def clean(self):
                csv_rows = self.cleaned_data['csv'][1] if 'csv' in self.cleaned_data else None
                csv_file = self.files.get('csv_file')

                # Check that the user has not submitted both text data and a file
                if csv_rows and csv_file:
                    raise ValidationError(
                        "Cannot process CSV text and file attachment simultaneously. Please choose only one import "
                        "method."
                    )

        return ImportForm(*args, **kwargs)

    def _create_objects(self, form, request):
        new_objs = []
        if request.FILES:
            headers, records = form.cleaned_data['csv_file']
        else:
            headers, records = form.cleaned_data['csv']

        for row, data in enumerate(records, start=1):
            obj_form = self.model_form(data, headers=headers)
            restrict_form_fields(obj_form, request.user)

            if obj_form.is_valid():
                obj = self._save_obj(obj_form, request)
                new_objs.append(obj)
            else:
                for field, err in obj_form.errors.items():
                    form.add_error('csv', f'Row {row} {field}: {err[0]}')
                raise ValidationError("")

        return new_objs

    def _save_obj(self, obj_form, request):
        """
        Provide a hook to modify the object immediately before saving it (e.g. to encrypt secret data).
        """
        return obj_form.save()

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

    def get(self, request):

        return render(request, self.template_name, {
            'form': self._import_form(),
            'fields': self.model_form().fields,
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkImportView')
        form = self._import_form(request.POST, request.FILES)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                # Iterate through CSV data and bind each row to a new model form instance.
                with transaction.atomic():
                    new_objs = self._create_objects(form, request)

                    # Enforce object-level permissions
                    if self.queryset.filter(pk__in=[obj.pk for obj in new_objs]).count() != len(new_objs):
                        raise PermissionsViolation

                # Compile a table containing the imported objects
                obj_table = self.table(new_objs)

                if new_objs:
                    msg = 'Imported {} {}'.format(len(new_objs), new_objs[0]._meta.verbose_name_plural)
                    logger.info(msg)
                    messages.success(request, msg)

                    return render(request, "import_success.html", {
                        'table': obj_table,
                        'return_url': self.get_return_url(request),
                    })

            except ValidationError:
                clear_webhooks.send(sender=self)

            except PermissionsViolation:
                msg = "Object import failed due to object-level permissions violation"
                logger.debug(msg)
                form.add_error(None, msg)
                clear_webhooks.send(sender=self)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'form': form,
            'fields': self.model_form().fields,
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })


class BulkEditView(GetReturnURLMixin, GenericView):
    """
    Edit objects in bulk.

    Attributes:
        filterset: FilterSet to apply when deleting by QuerySet
        table: The table used to display devices being edited
        form: The form class used to edit objects in bulk
    """
    template_name = 'generic/object_bulk_edit.html'
    filterset = None
    table = None
    form = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'change')

    def _update_objects(self, form, request):
        custom_fields = getattr(form, 'custom_fields', [])
        standard_fields = [
            field for field in form.fields if field not in list(custom_fields) + ['pk']
        ]
        nullified_fields = request.POST.getlist('_nullify')
        updated_objects = []

        for obj in self.queryset.filter(pk__in=form.cleaned_data['pk']):

            # Take a snapshot of change-logged models
            if hasattr(obj, 'snapshot'):
                obj.snapshot()

            # Update standard fields. If a field is listed in _nullify, delete its value.
            for name in standard_fields:

                try:
                    model_field = self.queryset.model._meta.get_field(name)
                except FieldDoesNotExist:
                    # This form field is used to modify a field rather than set its value directly
                    model_field = None

                # Handle nullification
                if name in form.nullable_fields and name in nullified_fields:
                    if isinstance(model_field, ManyToManyField):
                        getattr(obj, name).set([])
                    else:
                        setattr(obj, name, None if model_field.null else '')

                # ManyToManyFields
                elif isinstance(model_field, ManyToManyField):
                    if form.cleaned_data[name]:
                        getattr(obj, name).set(form.cleaned_data[name])
                # Normal fields
                elif name in form.changed_data:
                    setattr(obj, name, form.cleaned_data[name])

            # Update custom fields
            for name in custom_fields:
                if name in form.nullable_fields and name in nullified_fields:
                    obj.custom_field_data[name] = None
                elif name in form.changed_data:
                    obj.custom_field_data[name] = form.fields[name].prepare_value(form.cleaned_data[name])

            obj.full_clean()
            obj.save()
            updated_objects.append(obj)

            # Add/remove tags
            if form.cleaned_data.get('add_tags', None):
                obj.tags.add(*form.cleaned_data['add_tags'])
            if form.cleaned_data.get('remove_tags', None):
                obj.tags.remove(*form.cleaned_data['remove_tags'])

        return updated_objects

    def get(self, request):
        return redirect(self.get_return_url(request))

    def post(self, request, **kwargs):
        logger = logging.getLogger('netbox.views.BulkEditView')
        model = self.queryset.model

        # If we are editing *all* objects in the queryset, replace the PK list with all matched objects.
        if request.POST.get('_all') and self.filterset is not None:
            pk_list = self.filterset(request.GET, self.queryset.values_list('pk', flat=True)).qs
        else:
            pk_list = request.POST.getlist('pk')

        # Include the PK list as initial data for the form
        initial_data = {'pk': pk_list}

        # Check for other contextual data needed for the form. We avoid passing all of request.GET because the
        # filter values will conflict with the bulk edit form fields.
        # TODO: Find a better way to accomplish this
        if 'device' in request.GET:
            initial_data['device'] = request.GET.get('device')
        elif 'device_type' in request.GET:
            initial_data['device_type'] = request.GET.get('device_type')
        elif 'virtual_machine' in request.GET:
            initial_data['virtual_machine'] = request.GET.get('virtual_machine')

        if '_apply' in request.POST:
            form = self.form(model, request.POST, initial=initial_data)
            restrict_form_fields(form, request.user)

            if form.is_valid():
                logger.debug("Form validation was successful")

                try:

                    with transaction.atomic():
                        updated_objects = self._update_objects(form, request)

                        # Enforce object-level permissions
                        object_count = self.queryset.filter(pk__in=[obj.pk for obj in updated_objects]).count()
                        if object_count != len(updated_objects):
                            raise PermissionsViolation

                    if updated_objects:
                        msg = f'Updated {len(updated_objects)} {model._meta.verbose_name_plural}'
                        logger.info(msg)
                        messages.success(self.request, msg)

                    return redirect(self.get_return_url(request))

                except ValidationError as e:
                    messages.error(self.request, ", ".join(e.messages))
                    clear_webhooks.send(sender=self)

                except PermissionsViolation:
                    msg = "Object update failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)
                    clear_webhooks.send(sender=self)

            else:
                logger.debug("Form validation failed")

        else:
            form = self.form(model, initial=initial_data)
            restrict_form_fields(form, request.user)

        # Retrieve objects being edited
        table = self.table(self.queryset.filter(pk__in=pk_list), orderable=False)
        if not table.rows:
            messages.warning(request, "No {} were selected.".format(model._meta.verbose_name_plural))
            return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'form': form,
            'table': table,
            'obj_type_plural': model._meta.verbose_name_plural,
            'return_url': self.get_return_url(request),
        })


class BulkRenameView(GetReturnURLMixin, GenericView):
    """
    An extendable view for renaming objects in bulk.
    """
    template_name = 'generic/object_bulk_rename.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a new Form class from BulkRenameForm
        class _Form(BulkRenameForm):
            pk = ModelMultipleChoiceField(
                queryset=self.queryset,
                widget=MultipleHiddenInput()
            )

        self.form = _Form

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'change')

    def _rename_objects(self, form, selected_objects):
        renamed_pks = []

        for obj in selected_objects:

            # Take a snapshot of change-logged models
            if hasattr(obj, 'snapshot'):
                obj.snapshot()

            find = form.cleaned_data['find']
            replace = form.cleaned_data['replace']
            if form.cleaned_data['use_regex']:
                try:
                    obj.new_name = re.sub(find, replace, obj.name)
                # Catch regex group reference errors
                except re.error:
                    obj.new_name = obj.name
            else:
                obj.new_name = obj.name.replace(find, replace)
            renamed_pks.append(obj.pk)

        return renamed_pks

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkRenameView')

        if '_preview' in request.POST or '_apply' in request.POST:
            form = self.form(request.POST, initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

            if form.is_valid():
                try:
                    with transaction.atomic():
                        renamed_pks = self._rename_objects(form, selected_objects)

                        if '_apply' in request.POST:
                            for obj in selected_objects:
                                obj.name = obj.new_name
                                obj.save()

                            # Enforce constrained permissions
                            if self.queryset.filter(pk__in=renamed_pks).count() != len(selected_objects):
                                raise PermissionsViolation

                            model_name = self.queryset.model._meta.verbose_name_plural
                            messages.success(request, f"Renamed {len(selected_objects)} {model_name}")
                            return redirect(self.get_return_url(request))

                except PermissionsViolation:
                    msg = "Object update failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)
                    clear_webhooks.send(sender=self)

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

        return render(request, self.template_name, {
            'form': form,
            'obj_type_plural': self.queryset.model._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': self.get_return_url(request),
        })


class BulkDeleteView(GetReturnURLMixin, GenericView):
    """
    Delete objects in bulk.

    filterset: FilterSet to apply when deleting by QuerySet
    table: The table used to display devices being deleted
    form: The form class used to delete objects in bulk
    """
    template_name = 'generic/object_bulk_delete.html'
    filterset = None
    table = None
    form = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'delete')

    def get(self, request):
        return redirect(self.get_return_url(request))

    def post(self, request, **kwargs):
        logger = logging.getLogger('netbox.views.BulkDeleteView')
        model = self.queryset.model

        # Are we deleting *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all'):
            qs = model.objects.all()
            if self.filterset is not None:
                qs = self.filterset(request.GET, qs).qs
            pk_list = qs.only('pk').values_list('pk', flat=True)
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        form_cls = self.get_form()

        if '_confirm' in request.POST:
            form = form_cls(request.POST)
            if form.is_valid():
                logger.debug("Form validation was successful")

                # Delete objects
                queryset = self.queryset.filter(pk__in=pk_list)
                deleted_count = queryset.count()
                try:
                    for obj in queryset:
                        # Take a snapshot of change-logged models
                        if hasattr(obj, 'snapshot'):
                            obj.snapshot()
                        obj.delete()
                except ProtectedError as e:
                    logger.info("Caught ProtectedError while attempting to delete objects")
                    handle_protectederror(queryset, request, e)
                    return redirect(self.get_return_url(request))

                msg = f"Deleted {deleted_count} {model._meta.verbose_name_plural}"
                logger.info(msg)
                messages.success(request, msg)
                return redirect(self.get_return_url(request))

            else:
                logger.debug("Form validation failed")

        else:
            form = form_cls(initial={
                'pk': pk_list,
                'return_url': self.get_return_url(request),
            })

        # Retrieve objects being deleted
        table = self.table(self.queryset.filter(pk__in=pk_list), orderable=False)
        if not table.rows:
            messages.warning(request, "No {} were selected for deletion.".format(model._meta.verbose_name_plural))
            return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'form': form,
            'obj_type_plural': model._meta.verbose_name_plural,
            'table': table,
            'return_url': self.get_return_url(request),
        })

    def get_form(self):
        """
        Provide a standard bulk delete form if none has been specified for the view
        """
        class BulkDeleteForm(ConfirmationForm):
            pk = ModelMultipleChoiceField(queryset=self.queryset, widget=MultipleHiddenInput)

        if self.form:
            return self.form

        return BulkDeleteForm


#
# Device/VirtualMachine components
#

class BulkComponentCreateView(GetReturnURLMixin, GenericView):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a set of Devices or VirtualMachines.
    """
    template_name = 'generic/object_bulk_add_component.html'
    parent_model = None
    parent_field = None
    form = None
    model_form = None
    filterset = None
    table = None

    def get_required_permission(self):
        return f'dcim.add_{self.queryset.model._meta.model_name}'

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkComponentCreateView')
        parent_model_name = self.parent_model._meta.verbose_name_plural
        model_name = self.queryset.model._meta.verbose_name_plural

        # Are we editing *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all') and self.filterset is not None:
            pk_list = [obj.pk for obj in self.filterset(request.GET, self.parent_model.objects.only('pk')).qs]
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        selected_objects = self.parent_model.objects.filter(pk__in=pk_list)
        if not selected_objects:
            messages.warning(request, "No {} were selected.".format(self.parent_model._meta.verbose_name_plural))
            return redirect(self.get_return_url(request))
        table = self.table(selected_objects, orderable=False)

        if '_create' in request.POST:
            form = self.form(request.POST)

            if form.is_valid():
                logger.debug("Form validation was successful")

                new_components = []
                data = deepcopy(form.cleaned_data)

                try:
                    with transaction.atomic():

                        for obj in data['pk']:

                            names = data['name_pattern']
                            labels = data['label_pattern'] if 'label_pattern' in data else None
                            for i, name in enumerate(names):
                                label = labels[i] if labels else None

                                component_data = {
                                    self.parent_field: obj.pk,
                                    'name': name,
                                    'label': label
                                }
                                component_data.update(data)
                                component_form = self.model_form(component_data)
                                if component_form.is_valid():
                                    instance = component_form.save()
                                    logger.debug(f"Created {instance} on {instance.parent_object}")
                                    new_components.append(instance)
                                else:
                                    for field, errors in component_form.errors.as_data().items():
                                        for e in errors:
                                            form.add_error(field, '{} {}: {}'.format(obj, name, ', '.join(e)))

                        # Enforce object-level permissions
                        if self.queryset.filter(pk__in=[obj.pk for obj in new_components]).count() != len(new_components):
                            raise PermissionsViolation

                except IntegrityError:
                    clear_webhooks.send(sender=self)

                except PermissionsViolation:
                    msg = "Component creation failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)
                    clear_webhooks.send(sender=self)

                if not form.errors:
                    msg = "Added {} {} to {} {}.".format(
                        len(new_components),
                        model_name,
                        len(form.cleaned_data['pk']),
                        parent_model_name
                    )
                    logger.info(msg)
                    messages.success(request, msg)

                    return redirect(self.get_return_url(request))

            else:
                logger.debug("Form validation failed")

        else:
            form = self.form(initial={'pk': pk_list})

        return render(request, self.template_name, {
            'form': form,
            'parent_model_name': parent_model_name,
            'model_name': model_name,
            'table': table,
            'return_url': self.get_return_url(request),
        })
