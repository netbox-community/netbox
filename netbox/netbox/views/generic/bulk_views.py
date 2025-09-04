import logging
import re
from copy import deepcopy

from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRel
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, router, transaction
from django.db.models import ManyToManyField, ProtectedError, RestrictedError
from django.db.models.fields.reverse_related import ManyToManyRel
from django.forms import ModelMultipleChoiceField, MultipleHiddenInput
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from mptt.models import MPTTModel

from core.exceptions import JobFailed
from core.models import ObjectType
from core.signals import clear_events
from extras.choices import CustomFieldUIEditableChoices
from extras.models import CustomField, ExportTemplate
from netbox.models.features import ChangeLoggingMixin
from netbox.object_actions import AddObject, BulkDelete, BulkEdit, BulkExport, BulkImport, BulkRename
from utilities.error_handlers import handle_protectederror
from utilities.exceptions import AbortRequest, PermissionsViolation
from utilities.export import TableExport
from utilities.forms import BulkDeleteForm, BulkRenameForm, restrict_form_fields
from utilities.forms.bulk_import import BulkImportForm
from utilities.htmx import htmx_partial
from utilities.jobs import is_background_request, process_request_as_job
from utilities.permissions import get_permission_for_model
from utilities.query import reapply_model_ordering
from utilities.request import safe_for_redirect
from utilities.tables import get_table_configs
from utilities.views import GetReturnURLMixin, get_action_url
from .base import BaseMultiObjectView
from .mixins import ActionsMixin, TableMixin
from .utils import get_prerequisite_model

__all__ = (
    'BulkComponentCreateView',
    'BulkCreateView',
    'BulkDeleteView',
    'BulkEditView',
    'BulkImportView',
    'BulkRenameView',
    'ObjectListView',
)


class ObjectListView(BaseMultiObjectView, ActionsMixin, TableMixin):
    """
    Display multiple objects, all the same type, as a table.

    Attributes:
        filterset: A django-filter FilterSet that is applied to the queryset
        filterset_form: The form class used to render filter options
        actions: An iterable of ObjectAction subclasses (see ActionsMixin)
    """
    template_name = 'generic/object_list.html'
    filterset = None
    filterset_form = None
    actions = (AddObject, BulkImport, BulkExport, BulkEdit, BulkRename, BulkDelete)

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'view')

    #
    # Export methods
    #

    def export_yaml(self):
        """
        Export the queryset of objects as concatenated YAML documents.
        """
        yaml_data = [obj.to_yaml() for obj in self.queryset]

        return '---\n'.join(yaml_data)

    def export_table(self, table, columns=None, filename=None, delimiter=None):
        """
        Export all table data in CSV format.

        Args:
            table: The Table instance to export
            columns: A list of specific columns to include. If None, all columns will be exported.
            filename: The name of the file attachment sent to the client. If None, will be determined automatically
                from the queryset model name.
            delimiter: The character used to separate columns (a comma is used by default)
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
            exclude_columns=exclude_columns,
            delimiter=delimiter,
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
            return template.render_to_response(queryset=self.queryset)
        except Exception as e:
            messages.error(
                request,
                _("There was an error rendering the selected export template ({template}): {error}").format(
                    template=template.name,
                    error=e
                )
            )
            # Strip the `export` param and redirect user to the filtered objects list
            query_params = request.GET.copy()
            query_params.pop('export')
            redirect_url = f'{request.path}?{query_params.urlencode()}'
            if safe_for_redirect(redirect_url):
                return redirect(redirect_url)
            return redirect(get_action_url(self.queryset.model, action='list'))

    #
    # Request handlers
    #

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return reapply_model_ordering(qs)

    def get(self, request):
        """
        GET request handler.

        Args:
            request: The current request
        """
        model = self.queryset.model
        object_type = ObjectType.objects.get_for_model(model)

        if self.filterset:
            self.queryset = self.filterset(request.GET, self.queryset, request=request).qs

        # Determine the available actions
        actions = self.get_permitted_actions(request.user)
        has_table_actions = any(action.multi for action in actions)

        if 'export' in request.GET:

            # Export the current table view
            if request.GET['export'] == 'table':
                table = self.get_table(self.queryset, request, has_table_actions)
                columns = [name for name, _ in table.selected_columns]
                delimiter = request.user.config.get('csv_delimiter')
                return self.export_table(table, columns, delimiter=delimiter)

            # Render an ExportTemplate
            elif request.GET['export']:
                template = get_object_or_404(ExportTemplate, object_types=object_type, name=request.GET['export'])
                return self.export_template(template, request)

            # Check for YAML export support on the model
            elif hasattr(model, 'to_yaml'):
                response = HttpResponse(self.export_yaml(), content_type='text/yaml')
                filename = 'netbox_{}.yaml'.format(self.queryset.model._meta.verbose_name_plural)
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
                return response

            # Fall back to default table/YAML export
            else:
                table = self.get_table(self.queryset, request, has_table_actions)
                delimiter = request.user.config.get('csv_delimiter')
                return self.export_table(table, delimiter=delimiter)

        # Render the objects table
        table = self.get_table(self.queryset, request, has_table_actions)

        # If this is an HTMX request, return only the rendered table HTML
        if htmx_partial(request):
            if request.GET.get('embedded', False):
                table.embedded = True
                # Hide selection checkboxes
                if 'pk' in table.base_columns:
                    table.columns.hide('pk')
            return render(request, 'htmx/table.html', {
                'table': table,
                'model': model,
                'actions': actions,
            })

        context = {
            'model': model,
            'table': table,
            'table_configs': get_table_configs(table, request.user),
            'actions': actions,
            'filter_form': self.filterset_form(request.GET) if self.filterset_form else None,
            'prerequisite_model': get_prerequisite_model(self.queryset),
            **self.get_extra_context(request),
        }

        return render(request, self.template_name, context)


class BulkCreateView(GetReturnURLMixin, BaseMultiObjectView):
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

    #
    # Request handlers
    #

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
            **self.get_extra_context(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkCreateView')
        model = self.queryset.model
        form = self.form(request.POST)
        model_form = self.model_form(request.POST)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                with transaction.atomic(using=router.db_for_write(model)):
                    new_objs = self._create_objects(form, request)

                    # Enforce object-level permissions
                    if self.queryset.filter(pk__in=[obj.pk for obj in new_objs]).count() != len(new_objs):
                        raise PermissionsViolation

                # If we make it to this point, validation has succeeded on all new objects.
                msg = f"Added {len(new_objs)} {model._meta.verbose_name_plural}"
                logger.info(msg)
                messages.success(request, msg)

                if '_addanother' in request.POST and safe_for_redirect(request.path):
                    return redirect(request.path)
                return redirect(self.get_return_url(request))

            except IntegrityError:
                pass

            except (AbortRequest, PermissionsViolation) as e:
                logger.debug(e.message)
                form.add_error(None, e.message)
                clear_events.send(sender=self)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'form': form,
            'model_form': model_form,
            'obj_type': model._meta.verbose_name,
            'return_url': self.get_return_url(request),
            **self.get_extra_context(request),
        })


class BulkImportView(GetReturnURLMixin, BaseMultiObjectView):
    """
    Import objects in bulk (CSV format).

    Attributes:
        model_form: The form used to create each imported object
    """
    template_name = 'generic/bulk_import.html'
    model_form = None
    related_object_forms = dict()

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

    def prep_related_object_data(self, parent, data):
        """
        Hook to modify the data for related objects before it's passed to the related object form (for example, to
        assign a parent object).
        """
        return data

    def _get_form_fields(self):
        form = self.model_form()
        required_fields = {}
        optional_fields = {}

        # Return only visible fields, with required fields listed first
        for field in form.visible_fields():
            if field.is_hidden:
                continue
            elif field.field.required:
                required_fields[field.name] = field.field
            else:
                optional_fields[field.name] = field.field

        return {**required_fields, **optional_fields}

    def _compile_form_errors(self, errors, index, prefix=None):
        error_messages = []
        for field_name, errors in errors.items():
            prefix = f'{prefix}.' if prefix else ''
            if field_name == '__all__':
                field_name = ''
            for err in errors:
                error_messages.append(f"Record {index} {prefix}{field_name}: {err}")
        return error_messages

    def _save_object(self, model_form, request):
        _action = 'Updated' if model_form.instance.pk else 'Created'

        # Save the primary object
        obj = self.save_object(model_form, request)

        # Enforce object-level permissions
        if not self.queryset.filter(pk=obj.pk).first():
            raise PermissionsViolation()

        # Iterate through the related object forms (if any), validating and saving each instance.
        for field_name, related_object_form in self.related_object_forms.items():

            related_obj_pks = []
            for i, rel_obj_data in enumerate(model_form.data.get(field_name, list())):
                rel_obj_data = self.prep_related_object_data(obj, rel_obj_data)
                f = related_object_form(rel_obj_data)

                for subfield_name, field in f.fields.items():
                    if subfield_name not in rel_obj_data and hasattr(field, 'initial'):
                        f.data[subfield_name] = field.initial

                if f.is_valid():
                    related_obj = f.save()
                    related_obj_pks.append(related_obj.pk)
                else:
                    # Replicate errors on the related object form to the import form for display and abort
                    raise ValidationError(
                        self._compile_form_errors(f.errors, index=i, prefix=f'{field_name}[{i}]')
                    )

            # Enforce object-level permissions on related objects
            model = related_object_form.Meta.model
            if model.objects.filter(pk__in=related_obj_pks).count() != len(related_obj_pks):
                raise ObjectDoesNotExist

        if is_background_request(request):
            request.job.logger.info(f'{_action} {obj}')

        return obj

    def save_object(self, object_form, request):
        """
        Provide a hook to modify the object immediately before saving it (e.g. to encrypt secret data).

        Args:
            object_form: The model form instance
            request: The current request
        """
        return object_form.save()

    def create_and_update_objects(self, form, request):
        saved_objects = []

        records = list(form.cleaned_data['data'])

        # Prefetch objects to be updated, if any
        prefetch_ids = [int(record['id']) for record in records if record.get('id')]
        prefetched_objects = {
            obj.pk: obj
            for obj in self.queryset.model.objects.filter(id__in=prefetch_ids)
        } if prefetch_ids else {}

        for i, record in enumerate(records, start=1):
            object_id = int(record.pop('id')) if record.get('id') else None

            # Determine whether this object is being created or updated
            if object_id:
                try:
                    instance = prefetched_objects[object_id]
                except KeyError:
                    form.add_error('data', _("Row {i}: Object with ID {id} does not exist").format(i=i, id=object_id))
                    raise ValidationError('')

                # Take a snapshot for change logging
                if instance.pk and hasattr(instance, 'snapshot'):
                    instance.snapshot()

            else:
                instance = self.queryset.model()

                # For newly created objects, apply any default custom field values
                custom_fields = CustomField.objects.filter(
                    object_types=ContentType.objects.get_for_model(self.queryset.model),
                    ui_editable=CustomFieldUIEditableChoices.YES
                )
                for cf in custom_fields:
                    field_name = f'cf_{cf.name}'
                    if field_name not in record:
                        record[field_name] = cf.default

            # Record changelog message (if any)
            instance._changelog_message = form.cleaned_data.get('changelog_message', '')

            # Instantiate the model form for the object
            model_form_kwargs = {
                'data': record,
                'instance': instance,
            }
            if hasattr(form, '_csv_headers'):
                model_form_kwargs['headers'] = form._csv_headers  # Add CSV headers
            model_form = self.model_form(**model_form_kwargs)

            # When updating, omit all form fields other than those specified in the record. (No
            # fields are required when modifying an existing object.)
            if object_id:
                unused_fields = [f for f in model_form.fields if f not in record]
                for field_name in unused_fields:
                    del model_form.fields[field_name]

            restrict_form_fields(model_form, request.user)

            if model_form.is_valid():
                obj = self._save_object(model_form, request)
                saved_objects.append(obj)
            else:
                # Raise model form errors
                raise ValidationError(
                    self._compile_form_errors(model_form.errors, index=i)
                )

        return saved_objects

    #
    # Request handlers
    #

    def get(self, request):
        model = self.model_form._meta.model
        form = BulkImportForm()
        if not issubclass(model, ChangeLoggingMixin):
            form.fields.pop('changelog_message')

        return render(request, self.template_name, {
            'model': model,
            'form': form,
            'fields': self._get_form_fields(),
            'return_url': self.get_return_url(request),
            **self.get_extra_context(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkImportView')
        model = self.model_form._meta.model
        form = BulkImportForm(request.POST, request.FILES)
        if not issubclass(model, ChangeLoggingMixin):
            form.fields.pop('changelog_message')

        if form.is_valid():
            logger.debug("Import form validation was successful")
            redirect_url = get_action_url(model, action='list')

            # If indicated, defer this request to a background job & redirect the user
            if form.cleaned_data['background_job']:
                job_name = _('Bulk import {count} {object_type}').format(
                    count=len(form.cleaned_data['data']),
                    object_type=model._meta.verbose_name_plural,
                )
                if process_request_as_job(self.__class__, request, name=job_name):
                    return redirect(redirect_url)

            try:
                # Iterate through data and bind each record to a new model form instance.
                with transaction.atomic(using=router.db_for_write(model)):
                    new_objects = self.create_and_update_objects(form, request)

                    # Enforce object-level permissions
                    if self.queryset.filter(pk__in=[obj.pk for obj in new_objects]).count() != len(new_objects):
                        raise PermissionsViolation

                msg = _('Imported {count} {object_type}').format(
                    count=len(new_objects),
                    object_type=model._meta.verbose_name_plural
                )
                logger.info(msg)

                # Handle background job
                if is_background_request(request):
                    request.job.logger.info(msg)
                    return

                messages.success(request, msg)
                return redirect(f"{redirect_url}?modified_by_request={request.id}")

            except (AbortRequest, PermissionsViolation, ValidationError) as e:
                err_messages = e.messages if type(e) is ValidationError else [e.message]
                for msg in err_messages:
                    logger.debug(msg)
                    form.add_error(None, msg)
                    if is_background_request(request):
                        request.job.logger.error(msg)
                        request.job.logger.warning("Bulk import aborted")
                clear_events.send(sender=self)
                if is_background_request(request):
                    raise JobFailed

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'model': model,
            'form': form,
            'fields': self._get_form_fields(),
            'return_url': self.get_return_url(request),
            **self.get_extra_context(request),
        })


class BulkEditView(GetReturnURLMixin, BaseMultiObjectView):
    """
    Edit objects in bulk.

    Attributes:
        filterset: FilterSet to apply when deleting by QuerySet
        form: The form class used to edit objects in bulk
    """
    template_name = 'generic/bulk_edit.html'
    filterset = None
    form = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'change')

    def post_save_operations(self, form, obj):
        """
        This method is called for each object in _update_objects. Override to perform additional object-level
        operations that are specific to a particular ModelForm.
        """
        # Add/remove tags
        if form.cleaned_data.get('add_tags', None):
            obj.tags.add(*form.cleaned_data['add_tags'])
        if form.cleaned_data.get('remove_tags', None):
            obj.tags.remove(*form.cleaned_data['remove_tags'])

    def _update_objects(self, form, request):
        custom_fields = getattr(form, 'custom_fields', {})
        standard_fields = [
            field for field in form.fields if field not in list(custom_fields) + ['pk']
        ]
        nullified_fields = request.POST.getlist('_nullify')
        updated_objects = []
        model_fields = {}
        m2m_fields = {}

        # Build list of model fields and m2m fields for later iteration
        for name in standard_fields:
            try:
                model_field = self.queryset.model._meta.get_field(name)
                if isinstance(model_field, (ManyToManyField, ManyToManyRel)):
                    m2m_fields[name] = model_field
                elif isinstance(model_field, GenericRel):
                    # Ignore generic relations (these may be used for other purposes in the form)
                    continue
                else:
                    model_fields[name] = model_field
            except FieldDoesNotExist:
                # This form field is used to modify a field rather than set its value directly
                model_fields[name] = None

        for obj in self.queryset.filter(pk__in=form.cleaned_data['pk']):

            # Take a snapshot of change-logged models
            if hasattr(obj, 'snapshot'):
                obj.snapshot()

            # Attach the changelog message (if any) to the object
            obj._changelog_message = form.cleaned_data.get('changelog_message')

            # Update standard fields. If a field is listed in _nullify, delete its value.
            for name, model_field in model_fields.items():
                # Handle nullification
                if name in form.nullable_fields and name in nullified_fields:
                    if type(model_field) is GenericForeignKey:
                        setattr(obj, name, None)
                    else:
                        setattr(obj, name, None if model_field.null else '')
                # Normal fields
                elif name in form.changed_data:
                    setattr(obj, name, form.cleaned_data[name])

            # Update custom fields
            for name, customfield in custom_fields.items():
                assert name.startswith('cf_')
                cf_name = name[3:]  # Strip cf_ prefix
                if name in form.nullable_fields and name in nullified_fields:
                    obj.custom_field_data[cf_name] = None
                elif name in form.changed_data:
                    obj.custom_field_data[cf_name] = customfield.serialize(form.cleaned_data[name])

            # Store M2M values for validation
            obj._m2m_values = {}
            for field in obj._meta.local_many_to_many:
                if value := form.cleaned_data.get(field.name):
                    obj._m2m_values[field.name] = list(value)
                elif field.name in nullified_fields:
                    obj._m2m_values[field.name] = []

            obj.full_clean()
            obj.save()
            updated_objects.append(obj)

            # Handle M2M fields after save
            for name, m2m_field in m2m_fields.items():
                if name in form.nullable_fields and name in nullified_fields:
                    getattr(obj, name).clear()
                elif form.cleaned_data[name]:
                    getattr(obj, name).set(form.cleaned_data[name])

            self.post_save_operations(form, obj)

            if is_background_request(request):
                request.job.logger.info(f"Updated {obj}")

        # Rebuild the tree for MPTT models
        if issubclass(self.queryset.model, MPTTModel):
            self.queryset.model.objects.rebuild()

        return updated_objects

    #
    # Request handlers
    #

    def get(self, request):
        return redirect(self.get_return_url(request))

    def post(self, request, **kwargs):
        logger = logging.getLogger('netbox.views.BulkEditView')
        model = self.queryset.model

        # If we are editing *all* objects in the queryset, replace the PK list with all matched objects.
        if request.POST.get('_all') and self.filterset is not None:
            pk_list = self.filterset(request.GET, self.queryset.values_list('pk', flat=True), request=request).qs
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

        post_data = request.POST.copy()
        post_data.setlist('pk', pk_list)
        form = self.form(post_data, initial=initial_data)
        restrict_form_fields(form, request.user)

        if '_apply' in request.POST:
            if form.is_valid():
                logger.debug("Form validation was successful")

                # If indicated, defer this request to a background job & redirect the user
                if form.cleaned_data['background_job']:
                    job_name = _('Bulk edit {count} {object_type}').format(
                        count=len(form.cleaned_data['pk']),
                        object_type=model._meta.verbose_name_plural,
                    )
                    if process_request_as_job(self.__class__, request, name=job_name):
                        return redirect(self.get_return_url(request))

                try:
                    with transaction.atomic(using=router.db_for_write(model)):
                        updated_objects = self._update_objects(form, request)

                        # Enforce object-level permissions
                        object_count = self.queryset.filter(pk__in=[obj.pk for obj in updated_objects]).count()
                        if object_count != len(updated_objects):
                            raise PermissionsViolation

                    msg = _('Updated {count} {object_type}').format(
                        count=len(updated_objects),
                        object_type=model._meta.verbose_name_plural,
                    )
                    logger.info(msg)

                    # Handle background job
                    if is_background_request(request):
                        request.job.logger.info(msg)
                        return

                    messages.success(self.request, msg)
                    return redirect(self.get_return_url(request))

                except (AbortRequest, PermissionsViolation, ValidationError) as e:
                    err_messages = e.messages if type(e) is ValidationError else [e.message]
                    for msg in err_messages:
                        logger.debug(msg)
                        form.add_error(None, msg)
                        if is_background_request(request):
                            request.job.logger.error(msg)
                    clear_events.send(sender=self)
                    if is_background_request(request):
                        raise JobFailed

            else:
                logger.debug("Form validation failed")

        # Retrieve objects being edited
        table = self.table(self.queryset.filter(pk__in=pk_list), orderable=False)
        if not table.rows:
            messages.warning(
                request,
                _("No {object_type} were selected.").format(object_type=model._meta.verbose_name_plural)
            )
            return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'model': model,
            'form': form,
            'table': table,
            'return_url': self.get_return_url(request),
            **self.get_extra_context(request),
        })


class BulkRenameView(GetReturnURLMixin, BaseMultiObjectView):
    """
    An extendable view for renaming objects in bulk.

    Attributes:
        field_name: The name of the object attribute for which the value is being updated (defaults to "name")
    """
    field_name = 'name'
    template_name = 'generic/bulk_rename.html'

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
                    obj.new_name = re.sub(find, replace, getattr(obj, self.field_name, ''))
                # Catch regex group reference errors
                except re.error:
                    obj.new_name = getattr(obj, self.field_name)
            else:
                obj.new_name = getattr(obj, self.field_name, '').replace(find, replace)
            renamed_pks.append(obj.pk)

        return renamed_pks

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkRenameView')

        if '_preview' in request.POST or '_apply' in request.POST:
            form = self.form(request.POST, initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

            if form.is_valid():
                try:
                    with transaction.atomic(using=router.db_for_write(self.queryset.model)):
                        renamed_pks = self._rename_objects(form, selected_objects)

                        if '_apply' in request.POST:
                            for obj in selected_objects:
                                setattr(obj, self.field_name, obj.new_name)
                                obj.save()

                            # Enforce constrained permissions
                            if self.queryset.filter(pk__in=renamed_pks).count() != len(selected_objects):
                                raise PermissionsViolation

                            messages.success(
                                request,
                                _("Renamed {count} {object_type}").format(
                                    count=len(selected_objects),
                                    object_type=self.queryset.model._meta.verbose_name_plural
                                )
                            )
                            return redirect(self.get_return_url(request))

                except IntegrityError as e:
                    messages.error(self.request, ", ".join(e.args))
                    clear_events.send(sender=self)

                except (AbortRequest, PermissionsViolation) as e:
                    logger.debug(e.message)
                    form.add_error(None, e.message)
                    clear_events.send(sender=self)

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

        return render(request, self.template_name, {
            'field_name': self.field_name,
            'form': form,
            'obj_type_plural': self.queryset.model._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': self.get_return_url(request),
        })


class BulkDeleteView(GetReturnURLMixin, BaseMultiObjectView):
    """
    Delete objects in bulk.

    Attributes:
        filterset: FilterSet to apply when deleting by QuerySet
        table: The table used to display devices being deleted
    """
    template_name = 'generic/bulk_delete.html'
    filterset = None
    table = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'delete')

    #
    # Request handlers
    #

    def get(self, request):
        return redirect(self.get_return_url(request))

    def post(self, request, **kwargs):
        logger = logging.getLogger('netbox.views.BulkDeleteView')
        model = self.queryset.model

        # Are we deleting *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all'):
            qs = model.objects.all()
            if self.filterset is not None:
                qs = self.filterset(request.GET, qs, request=request).qs
            pk_list = qs.only('pk').values_list('pk', flat=True)
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        if '_confirm' in request.POST:
            form = BulkDeleteForm(model, request.POST)
            if form.is_valid():
                logger.debug("Form validation was successful")

                # If indicated, defer this request to a background job & redirect the user
                if form.cleaned_data['background_job']:
                    job_name = _('Bulk delete {count} {object_type}').format(
                        count=len(form.cleaned_data['pk']),
                        object_type=model._meta.verbose_name_plural,
                    )
                    if process_request_as_job(self.__class__, request, name=job_name):
                        return redirect(self.get_return_url(request))

                # Delete objects
                queryset = self.queryset.filter(pk__in=pk_list)
                deleted_count = queryset.count()
                try:
                    with transaction.atomic(using=router.db_for_write(model)):
                        for obj in queryset:

                            # Take a snapshot of change-logged models
                            if hasattr(obj, 'snapshot'):
                                obj.snapshot()

                            # Attach the changelog message (if any) to the object
                            obj._changelog_message = form.cleaned_data.get('changelog_message')

                            # Delete the object
                            obj.delete()

                            if is_background_request(request):
                                request.job.logger.info(f"Deleted {obj}")

                    msg = _('Deleted {count} {object_type}').format(
                        count=deleted_count,
                        object_type=model._meta.verbose_name_plural
                    )
                    logger.info(msg)

                    # Handle background job
                    if is_background_request(request):
                        request.job.logger.info(msg)
                        return

                    messages.success(request, msg)

                except (ProtectedError, RestrictedError) as e:
                    logger.warning(f"Caught {type(e)} while attempting to delete objects")
                    if is_background_request(request):
                        request.job.logger.error(
                            _("Deletion failed due to the presence of one or more dependent objects.")
                        )
                        raise JobFailed
                    handle_protectederror(queryset, request, e)

                except AbortRequest as e:
                    logger.debug(e.message)
                    if is_background_request(request):
                        request.job.logger.error(e.message)
                        raise JobFailed
                    messages.error(request, mark_safe(e.message))

                return redirect(self.get_return_url(request))

            else:
                logger.debug("Form validation failed")

        else:
            form = BulkDeleteForm(model, initial={
                'pk': pk_list,
                'return_url': self.get_return_url(request),
            })

        # Retrieve objects being deleted
        table = self.table(self.queryset.filter(pk__in=pk_list), orderable=False)
        if not table.rows:
            messages.warning(
                request,
                _("No {object_type} were selected.").format(object_type=model._meta.verbose_name_plural)
            )
            return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'model': model,
            'form': form,
            'table': table,
            'return_url': self.get_return_url(request),
            **self.get_extra_context(request),
        })


#
# Device/VirtualMachine components
#

class BulkComponentCreateView(GetReturnURLMixin, BaseMultiObjectView):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a set of Devices or VirtualMachines.
    """
    template_name = 'generic/bulk_add_component.html'
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
            queryset = self.filterset(request.GET, self.parent_model.objects.only('pk'), request=request).qs
            pk_list = [obj.pk for obj in queryset]
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        selected_objects = self.parent_model.objects.filter(pk__in=pk_list)
        if not selected_objects:
            messages.warning(
                request,
                _("No {object_type} were selected.").format(object_type=self.parent_model._meta.verbose_name_plural)
            )
            return redirect(self.get_return_url(request))
        table = self.table(selected_objects, orderable=False)

        if '_create' in request.POST:
            form = self.form(request.POST)

            if form.is_valid():
                logger.debug("Form validation was successful")

                new_components = []
                data = deepcopy(form.cleaned_data)
                replication_data = {
                    field: data.pop(field) for field in form.replication_fields
                }

                try:
                    with transaction.atomic(using=router.db_for_write(self.queryset.model)):

                        for obj in data['pk']:

                            pattern_count = len(replication_data[form.replication_fields[0]])
                            for i in range(pattern_count):
                                component_data = {
                                    self.parent_field: obj.pk
                                }
                                component_data.update(data)
                                for field, values in replication_data.items():
                                    if values:
                                        component_data[field] = values[i]

                                component_form = self.model_form(component_data)
                                if component_form.is_valid():
                                    instance = component_form.save()
                                    logger.debug(f"Created {instance} on {instance.parent_object}")
                                    new_components.append(instance)
                                else:
                                    for field, errors in component_form.errors.as_data().items():
                                        for e in errors:
                                            form.add_error(field, '{}: {}'.format(obj, ', '.join(e)))

                        # Enforce object-level permissions
                        component_ids = [obj.pk for obj in new_components]
                        if self.queryset.filter(pk__in=component_ids).count() != len(new_components):
                            raise PermissionsViolation

                except IntegrityError:
                    clear_events.send(sender=self)

                except (AbortRequest, PermissionsViolation) as e:
                    logger.debug(e.message)
                    form.add_error(None, e.message)
                    clear_events.send(sender=self)

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
