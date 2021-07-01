import logging
import re
from copy import deepcopy

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist, ValidationError
from django.db import transaction, IntegrityError
from django.db.models import ManyToManyField, ProtectedError
from django.forms import Form, ModelMultipleChoiceField, MultipleHiddenInput, Textarea
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.views.generic import View
from django_tables2.export import TableExport

from extras.models import CustomField, ExportTemplate
from utilities.error_handlers import handle_protectederror
from utilities.exceptions import AbortTransaction, PermissionsViolation
from utilities.forms import (
    BootstrapMixin, BulkRenameForm, ConfirmationForm, CSVDataField, ImportForm, TableConfigForm, restrict_form_fields,
)
from utilities.permissions import get_permission_for_model
from utilities.tables import paginate_table
from utilities.utils import csv_format, normalize_querydict, prepare_cloned_fields
from utilities.views import GetReturnURLMixin, ObjectPermissionRequiredMixin


class ObjectView(ObjectPermissionRequiredMixin, View):
    """
    Retrieve a single object for display.

    queryset: The base queryset for retrieving the object
    template_name: Name of the template to use
    """
    queryset = None
    template_name = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'view')

    def get_template_name(self):
        """
        Return self.template_name if set. Otherwise, resolve the template path by model app_label and name.
        """
        if self.template_name is not None:
            return self.template_name
        model_opts = self.queryset.model._meta
        return f'{model_opts.app_label}/{model_opts.model_name}.html'

    def get_extra_context(self, request, instance):
        """
        Return any additional context data for the template.

        request: The current request
        instance: The object being viewed
        """
        return {}

    def get(self, request, *args, **kwargs):
        """
        Generic GET handler for accessing an object by PK or slug
        """
        instance = get_object_or_404(self.queryset, **kwargs)

        return render(request, self.get_template_name(), {
            'object': instance,
            **self.get_extra_context(request, instance),
        })


class ObjectListView(ObjectPermissionRequiredMixin, View):
    """
    List a series of objects.

    queryset: The queryset of objects to display. Note: Prefetching related objects is not necessary, as the
      table will prefetch objects as needed depending on the columns being displayed.
    filter: A django-filter FilterSet that is applied to the queryset
    filter_form: The form used to render filter options
    table: The django-tables2 Table used to render the objects list
    template_name: The name of the template
    """
    queryset = None
    filterset = None
    filterset_form = None
    table = None
    template_name = 'generic/object_list.html'
    action_buttons = ('add', 'import', 'export')

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'view')

    def queryset_to_yaml(self):
        """
        Export the queryset of objects as concatenated YAML documents.
        """
        yaml_data = [obj.to_yaml() for obj in self.queryset]

        return '---\n'.join(yaml_data)

    def queryset_to_csv(self):
        """
        Export the queryset of objects as comma-separated value (CSV), using the model's to_csv() method.
        """
        csv_data = []
        custom_fields = []

        # Start with the column headers
        headers = self.queryset.model.csv_headers.copy()

        # Add custom field headers, if any
        if hasattr(self.queryset.model, 'custom_field_data'):
            for custom_field in CustomField.objects.get_for_model(self.queryset.model):
                headers.append(custom_field.name)
                custom_fields.append(custom_field.name)

        csv_data.append(','.join(headers))

        # Iterate through the queryset appending each object
        for obj in self.queryset:
            data = obj.to_csv()

            for custom_field in custom_fields:
                data += (obj.cf.get(custom_field, ''),)

            csv_data.append(csv_format(data))

        return '\n'.join(csv_data)

    def get(self, request):

        model = self.queryset.model
        content_type = ContentType.objects.get_for_model(model)

        if self.filterset:
            self.queryset = self.filterset(request.GET, self.queryset).qs

        # Check for export rendering (except for table-based)
        if 'export' in request.GET and request.GET['export'] != 'table':

            # An export template has been specified
            if request.GET['export']:
                et = get_object_or_404(ExportTemplate, content_type=content_type, name=request.GET['export'])
                try:
                    return et.render_to_response(self.queryset)
                except Exception as e:
                    messages.error(
                        request,
                        "There was an error rendering the selected export template ({}): {}".format(
                            et.name, e
                        )
                    )

            # Check for YAML export support
            elif hasattr(model, 'to_yaml'):
                response = HttpResponse(self.queryset_to_yaml(), content_type='text/yaml')
                filename = 'netbox_{}.yaml'.format(self.queryset.model._meta.verbose_name_plural)
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
                return response

            # Fall back to built-in CSV formatting if export requested but no template specified
            elif 'export' in request.GET and hasattr(model, 'to_csv'):
                response = HttpResponse(self.queryset_to_csv(), content_type='text/csv')
                filename = 'netbox_{}.csv'.format(self.queryset.model._meta.verbose_name_plural)
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
                return response

        # Compile a dictionary indicating which permissions are available to the current user for this model
        permissions = {}
        for action in ('add', 'change', 'delete', 'view'):
            perm_name = get_permission_for_model(model, action)
            permissions[action] = request.user.has_perm(perm_name)

        # Construct the objects table
        table = self.table(self.queryset, user=request.user)
        if 'pk' in table.base_columns and (permissions['change'] or permissions['delete']):
            table.columns.show('pk')

        # Handle table-based export
        if request.GET.get('export') == 'table':
            exclude_columns = {'pk'}
            exclude_columns.update({
                name for name, _ in table.available_columns
            })
            exporter = TableExport(
                export_format=TableExport.CSV,
                table=table,
                exclude_columns=exclude_columns,
                dataset_kwargs={},
            )
            return exporter.response(
                filename=f'netbox_{self.queryset.model._meta.verbose_name_plural}.csv'
            )

        # Paginate the objects table
        paginate_table(table, request)

        context = {
            'content_type': content_type,
            'table': table,
            'permissions': permissions,
            'action_buttons': self.action_buttons,
            'table_config_form': TableConfigForm(table=table),
            'filter_form': self.filterset_form(request.GET, label_suffix='') if self.filterset_form else None,
        }
        context.update(self.extra_context())

        return render(request, self.template_name, context)

    def extra_context(self):
        return {}


class ObjectEditView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Create or edit a single object.

    queryset: The base queryset for the object being modified
    model_form: The form used to create or edit the object
    template_name: The name of the template
    """
    queryset = None
    model_form = None
    template_name = 'generic/object_edit.html'

    def get_required_permission(self):
        # self._permission_action is set by dispatch() to either "add" or "change" depending on whether
        # we are modifying an existing object or creating a new one.
        return get_permission_for_model(self.queryset.model, self._permission_action)

    def get_object(self, kwargs):
        # Look up an existing object by slug or PK, if provided.
        if 'slug' in kwargs:
            obj = get_object_or_404(self.queryset, slug=kwargs['slug'])
        elif 'pk' in kwargs:
            obj = get_object_or_404(self.queryset, pk=kwargs['pk'])
        # Otherwise, return a new instance.
        else:
            return self.queryset.model()

        # Take a snapshot of change-logged models
        if hasattr(obj, 'snapshot'):
            obj.snapshot()

        return obj

    def alter_obj(self, obj, request, url_args, url_kwargs):
        # Allow views to add extra info to an object before it is processed. For example, a parent object can be defined
        # given some parameter from the request URL.
        return obj

    def dispatch(self, request, *args, **kwargs):
        # Determine required permission based on whether we are editing an existing object
        self._permission_action = 'change' if kwargs else 'add'

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = self.alter_obj(self.get_object(kwargs), request, args, kwargs)

        initial_data = normalize_querydict(request.GET)
        form = self.model_form(instance=obj, initial=initial_data)
        restrict_form_fields(form, request.user)

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })

    def post(self, request, *args, **kwargs):
        logger = logging.getLogger('netbox.views.ObjectEditView')
        obj = self.alter_obj(self.get_object(kwargs), request, args, kwargs)
        form = self.model_form(
            data=request.POST,
            files=request.FILES,
            instance=obj
        )
        restrict_form_fields(form, request.user)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                with transaction.atomic():
                    object_created = form.instance.pk is None
                    obj = form.save()

                    # Check that the new object conforms with any assigned object-level permissions
                    if not self.queryset.filter(pk=obj.pk).first():
                        raise PermissionsViolation()

                msg = '{} {}'.format(
                    'Created' if object_created else 'Modified',
                    self.queryset.model._meta.verbose_name
                )
                logger.info(f"{msg} {obj} (PK: {obj.pk})")
                if hasattr(obj, 'get_absolute_url'):
                    msg = '{} <a href="{}">{}</a>'.format(msg, obj.get_absolute_url(), escape(obj))
                else:
                    msg = '{} {}'.format(msg, escape(obj))
                messages.success(request, mark_safe(msg))

                if '_addanother' in request.POST:

                    # If the object has clone_fields, pre-populate a new instance of the form
                    if hasattr(obj, 'clone_fields'):
                        url = '{}?{}'.format(request.path, prepare_cloned_fields(obj))
                        return redirect(url)

                    return redirect(request.get_full_path())

                return_url = form.cleaned_data.get('return_url')
                if return_url is not None and is_safe_url(url=return_url, allowed_hosts=request.get_host()):
                    return redirect(return_url)
                else:
                    return redirect(self.get_return_url(request, obj))

            except PermissionsViolation:
                msg = "Object save failed due to object-level permissions violation"
                logger.debug(msg)
                form.add_error(None, msg)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })


class ObjectDeleteView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Delete a single object.

    queryset: The base queryset for the object being deleted
    template_name: The name of the template
    """
    queryset = None
    template_name = 'generic/object_delete.html'

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'delete')

    def get_object(self, kwargs):
        # Look up object by slug if one has been provided. Otherwise, use PK.
        if 'slug' in kwargs:
            obj = get_object_or_404(self.queryset, slug=kwargs['slug'])
        else:
            obj = get_object_or_404(self.queryset, pk=kwargs['pk'])

        # Take a snapshot of change-logged models
        if hasattr(obj, 'snapshot'):
            obj.snapshot()

        return obj

    def get(self, request, **kwargs):
        obj = self.get_object(kwargs)
        form = ConfirmationForm(initial=request.GET)

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.queryset.model._meta.verbose_name,
            'return_url': self.get_return_url(request, obj),
        })

    def post(self, request, **kwargs):
        logger = logging.getLogger('netbox.views.ObjectDeleteView')
        obj = self.get_object(kwargs)
        form = ConfirmationForm(request.POST)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                obj.delete()
            except ProtectedError as e:
                logger.info("Caught ProtectedError while attempting to delete object")
                handle_protectederror([obj], request, e)
                return redirect(obj.get_absolute_url())

            msg = 'Deleted {} {}'.format(self.queryset.model._meta.verbose_name, obj)
            logger.info(msg)
            messages.success(request, msg)

            return_url = form.cleaned_data.get('return_url')
            if return_url is not None and is_safe_url(url=return_url, allowed_hosts=request.get_host()):
                return redirect(return_url)
            else:
                return redirect(self.get_return_url(request, obj))

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.queryset.model._meta.verbose_name,
            'return_url': self.get_return_url(request, obj),
        })


class BulkCreateView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Create new objects in bulk.

    queryset: Base queryset for the objects being created
    form: Form class which provides the `pattern` field
    model_form: The ModelForm used to create individual objects
    pattern_target: Name of the field to be evaluated as a pattern (if any)
    template_name: The name of the template
    """
    queryset = None
    form = None
    model_form = None
    pattern_target = ''
    template_name = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

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
            pattern = form.cleaned_data['pattern']
            new_objs = []

            try:
                with transaction.atomic():

                    # Create objects from the expanded. Abort the transaction on the first validation error.
                    for value in pattern:

                        # Reinstantiate the model form each time to avoid overwriting the same instance. Use a mutable
                        # copy of the POST QueryDict so that we can update the target field value.
                        model_form = self.model_form(request.POST.copy())
                        model_form.data[self.pattern_target] = value

                        # Validate each new object independently.
                        if model_form.is_valid():
                            obj = model_form.save()
                            logger.debug(f"Created {obj} (PK: {obj.pk})")
                            new_objs.append(obj)
                        else:
                            # Copy any errors on the pattern target field to the pattern form.
                            errors = model_form.errors.as_data()
                            if errors.get(self.pattern_target):
                                form.add_error('pattern', errors[self.pattern_target])
                            # Raise an IntegrityError to break the for loop and abort the transaction.
                            raise IntegrityError()

                    # Enforce object-level permissions
                    if self.queryset.filter(pk__in=[obj.pk for obj in new_objs]).count() != len(new_objs):
                        raise PermissionsViolation

                    # If we make it to this point, validation has succeeded on all new objects.
                    msg = "Added {} {}".format(len(new_objs), model._meta.verbose_name_plural)
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


class ObjectImportView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Import a single object (YAML or JSON format).

    queryset: Base queryset for the objects being created
    model_form: The ModelForm used to create individual objects
    related_object_forms: A dictionary mapping of forms to be used for the creation of related (child) objects
    template_name: The name of the template
    """
    queryset = None
    model_form = None
    related_object_forms = dict()
    template_name = 'generic/object_import.html'

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

    def get(self, request):
        form = ImportForm()

        return render(request, self.template_name, {
            'form': form,
            'obj_type': self.queryset.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.views.ObjectImportView')
        form = ImportForm(request.POST)

        if form.is_valid():
            logger.debug("Import form validation was successful")

            # Initialize model form
            data = form.cleaned_data['data']
            model_form = self.model_form(data)
            restrict_form_fields(model_form, request.user)

            # Assign default values for any fields which were not specified. We have to do this manually because passing
            # 'initial=' to the form on initialization merely sets default values for the widgets. Since widgets are not
            # used for YAML/JSON import, we first bind the imported data normally, then update the form's data with the
            # applicable field defaults as needed prior to form validation.
            for field_name, field in model_form.fields.items():
                if field_name not in data and hasattr(field, 'initial'):
                    model_form.data[field_name] = field.initial

            if model_form.is_valid():

                try:
                    with transaction.atomic():

                        # Save the primary object
                        obj = model_form.save()

                        # Enforce object-level permissions
                        if not self.queryset.filter(pk=obj.pk).first():
                            raise PermissionsViolation()

                        logger.debug(f"Created {obj} (PK: {obj.pk})")

                        # Iterate through the related object forms (if any), validating and saving each instance.
                        for field_name, related_object_form in self.related_object_forms.items():
                            logger.debug("Processing form for related objects: {related_object_form}")

                            related_obj_pks = []
                            for i, rel_obj_data in enumerate(data.get(field_name, list())):

                                f = related_object_form(obj, rel_obj_data)

                                for subfield_name, field in f.fields.items():
                                    if subfield_name not in rel_obj_data and hasattr(field, 'initial'):
                                        f.data[subfield_name] = field.initial

                                if f.is_valid():
                                    related_obj = f.save()
                                    related_obj_pks.append(related_obj.pk)
                                else:
                                    # Replicate errors on the related object form to the primary form for display
                                    for subfield_name, errors in f.errors.items():
                                        for err in errors:
                                            err_msg = "{}[{}] {}: {}".format(field_name, i, subfield_name, err)
                                            model_form.add_error(None, err_msg)
                                    raise AbortTransaction()

                            # Enforce object-level permissions on related objects
                            model = related_object_form.Meta.model
                            if model.objects.filter(pk__in=related_obj_pks).count() != len(related_obj_pks):
                                raise ObjectDoesNotExist

                except AbortTransaction:
                    pass

                except PermissionsViolation:
                    msg = "Object creation failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)

            if not model_form.errors:
                logger.info(f"Import object {obj} (PK: {obj.pk})")
                messages.success(request, mark_safe('Imported object: <a href="{}">{}</a>'.format(
                    obj.get_absolute_url(), obj
                )))

                if '_addanother' in request.POST:
                    return redirect(request.get_full_path())

                return_url = form.cleaned_data.get('return_url')
                if return_url is not None and is_safe_url(url=return_url, allowed_hosts=request.get_host()):
                    return redirect(return_url)
                else:
                    return redirect(self.get_return_url(request, obj))

            else:
                logger.debug("Model form validation failed")

                # Replicate model form errors for display
                for field, errors in model_form.errors.items():
                    for err in errors:
                        if field == '__all__':
                            form.add_error(None, err)
                        else:
                            form.add_error(None, "{}: {}".format(field, err))

        else:
            logger.debug("Import form validation failed")

        return render(request, self.template_name, {
            'form': form,
            'obj_type': self.queryset.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })


class BulkImportView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Import objects in bulk (CSV format).

    queryset: Base queryset for the model
    model_form: The form used to create each imported object
    table: The django-tables2 Table used to render the list of imported objects
    template_name: The name of the template
    widget_attrs: A dict of attributes to apply to the import widget (e.g. to require a session key)
    """
    queryset = None
    model_form = None
    table = None
    template_name = 'generic/object_bulk_import.html'
    widget_attrs = {}

    def _import_form(self, *args, **kwargs):

        class ImportForm(BootstrapMixin, Form):
            csv = CSVDataField(
                from_form=self.model_form,
                widget=Textarea(attrs=self.widget_attrs)
            )

        return ImportForm(*args, **kwargs)

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
        new_objs = []
        form = self._import_form(request.POST)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                # Iterate through CSV data and bind each row to a new model form instance.
                with transaction.atomic():
                    headers, records = form.cleaned_data['csv']
                    for row, data in enumerate(records, start=1):
                        obj_form = self.model_form(data, headers=headers)
                        restrict_form_fields(obj_form, request.user)

                        if obj_form.is_valid():
                            obj = self._save_obj(obj_form, request)
                            new_objs.append(obj)
                        else:
                            for field, err in obj_form.errors.items():
                                form.add_error('csv', "Row {} {}: {}".format(row, field, err[0]))
                            raise ValidationError("")

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
                pass

            except PermissionsViolation:
                msg = "Object import failed due to object-level permissions violation"
                logger.debug(msg)
                form.add_error(None, msg)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'form': form,
            'fields': self.model_form().fields,
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })


class BulkEditView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Edit objects in bulk.

    queryset: Custom queryset to use when retrieving objects (e.g. to select related objects)
    filter: FilterSet to apply when deleting by QuerySet
    table: The table used to display devices being edited
    form: The form class used to edit objects in bulk
    template_name: The name of the template
    """
    queryset = None
    filterset = None
    table = None
    form = None
    template_name = 'generic/object_bulk_edit.html'

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'change')

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

        if '_apply' in request.POST:
            form = self.form(model, request.POST)
            restrict_form_fields(form, request.user)

            if form.is_valid():
                logger.debug("Form validation was successful")
                custom_fields = form.custom_fields if hasattr(form, 'custom_fields') else []
                standard_fields = [
                    field for field in form.fields if field not in custom_fields + ['pk']
                ]
                nullified_fields = request.POST.getlist('_nullify')

                try:

                    with transaction.atomic():

                        updated_objects = []
                        for obj in self.queryset.filter(pk__in=form.cleaned_data['pk']):

                            # Take a snapshot of change-logged models
                            if hasattr(obj, 'snapshot'):
                                obj.snapshot()

                            # Update standard fields. If a field is listed in _nullify, delete its value.
                            for name in standard_fields:

                                try:
                                    model_field = model._meta.get_field(name)
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
                                elif form.cleaned_data[name] not in (None, '', []):
                                    setattr(obj, name, form.cleaned_data[name])

                            # Update custom fields
                            for name in custom_fields:
                                if name in form.nullable_fields and name in nullified_fields:
                                    obj.custom_field_data[name] = None
                                elif form.cleaned_data.get(name) not in (None, ''):
                                    obj.custom_field_data[name] = form.cleaned_data[name]

                            obj.full_clean()
                            obj.save()
                            updated_objects.append(obj)
                            logger.debug(f"Saved {obj} (PK: {obj.pk})")

                            # Add/remove tags
                            if form.cleaned_data.get('add_tags', None):
                                obj.tags.add(*form.cleaned_data['add_tags'])
                            if form.cleaned_data.get('remove_tags', None):
                                obj.tags.remove(*form.cleaned_data['remove_tags'])

                        # Enforce object-level permissions
                        if self.queryset.filter(pk__in=[obj.pk for obj in updated_objects]).count() != len(updated_objects):
                            raise PermissionsViolation

                    if updated_objects:
                        msg = 'Updated {} {}'.format(len(updated_objects), model._meta.verbose_name_plural)
                        logger.info(msg)
                        messages.success(self.request, msg)

                    return redirect(self.get_return_url(request))

                except ValidationError as e:
                    messages.error(self.request, "{} failed validation: {}".format(obj, e))

                except PermissionsViolation:
                    msg = "Object update failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)

            else:
                logger.debug("Form validation failed")

        else:
            # Include the PK list as initial data for the form
            initial_data = {'pk': pk_list}

            # Check for other contextual data needed for the form. We avoid passing all of request.GET because the
            # filter values will conflict with the bulk edit form fields.
            # TODO: Find a better way to accomplish this
            if 'device' in request.GET:
                initial_data['device'] = request.GET.get('device')
            elif 'device_type' in request.GET:
                initial_data['device_type'] = request.GET.get('device_type')

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


class BulkRenameView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    An extendable view for renaming objects in bulk.
    """
    queryset = None
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

    def post(self, request):
        logger = logging.getLogger('netbox.views.BulkRenameView')

        if '_preview' in request.POST or '_apply' in request.POST:
            form = self.form(request.POST, initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

            if form.is_valid():
                try:
                    with transaction.atomic():
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

                        if '_apply' in request.POST:
                            for obj in selected_objects:
                                obj.name = obj.new_name
                                obj.save()

                            # Enforce constrained permissions
                            if self.queryset.filter(pk__in=renamed_pks).count() != len(selected_objects):
                                raise PermissionsViolation

                            messages.success(request, "Renamed {} {}".format(
                                len(selected_objects),
                                self.queryset.model._meta.verbose_name_plural
                            ))
                            return redirect(self.get_return_url(request))

                except PermissionsViolation:
                    msg = "Object update failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

        return render(request, self.template_name, {
            'form': form,
            'obj_type_plural': self.queryset.model._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': self.get_return_url(request),
        })


class BulkDeleteView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Delete objects in bulk.

    queryset: Custom queryset to use when retrieving objects (e.g. to select related objects)
    filter: FilterSet to apply when deleting by QuerySet
    table: The table used to display devices being deleted
    form: The form class used to delete objects in bulk
    template_name: The name of the template
    """
    queryset = None
    filterset = None
    table = None
    form = None
    template_name = 'generic/object_bulk_delete.html'

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'delete')

    def get(self, request):
        return redirect(self.get_return_url(request))

    def post(self, request, **kwargs):
        logger = logging.getLogger('netbox.views.BulkDeleteView')
        model = self.queryset.model

        # Are we deleting *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all'):
            if self.filterset is not None:
                pk_list = [obj.pk for obj in self.filterset(request.GET, model.objects.only('pk')).qs]
            else:
                pk_list = model.objects.values_list('pk', flat=True)
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

# TODO: Replace with BulkCreateView
class ComponentCreateView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a Device or VirtualMachine.
    """
    queryset = None
    form = None
    model_form = None
    template_name = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

    def get(self, request):

        form = self.form(initial=request.GET)

        return render(request, self.template_name, {
            'component_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.views.ComponentCreateView')
        form = self.form(request.POST, initial=request.GET)

        if form.is_valid():

            new_components = []
            data = deepcopy(request.POST)

            names = form.cleaned_data['name_pattern']
            labels = form.cleaned_data.get('label_pattern')
            for i, name in enumerate(names):
                label = labels[i] if labels else None
                # Initialize the individual component form
                data['name'] = name
                data['label'] = label
                if hasattr(form, 'get_iterative_data'):
                    data.update(form.get_iterative_data(i))
                component_form = self.model_form(data)

                if component_form.is_valid():
                    new_components.append(component_form)
                else:
                    for field, errors in component_form.errors.as_data().items():
                        # Assign errors on the child form's name/label field to name_pattern/label_pattern on the parent form
                        if field == 'name':
                            field = 'name_pattern'
                        elif field == 'label':
                            field = 'label_pattern'
                        for e in errors:
                            form.add_error(field, '{}: {}'.format(name, ', '.join(e)))

            if not form.errors:

                try:

                    with transaction.atomic():

                        # Create the new components
                        new_objs = []
                        for component_form in new_components:
                            obj = component_form.save()
                            new_objs.append(obj)

                        # Enforce object-level permissions
                        if self.queryset.filter(pk__in=[obj.pk for obj in new_objs]).count() != len(new_objs):
                            raise PermissionsViolation

                    messages.success(request, "Added {} {}".format(
                        len(new_components), self.queryset.model._meta.verbose_name_plural
                    ))
                    if '_addanother' in request.POST:
                        return redirect(request.get_full_path())
                    else:
                        return redirect(self.get_return_url(request))

                except PermissionsViolation:
                    msg = "Component creation failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)

        return render(request, self.template_name, {
            'component_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request),
        })


class BulkComponentCreateView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a set of Devices or VirtualMachines.
    """
    parent_model = None
    parent_field = None
    form = None
    queryset = None
    model_form = None
    filterset = None
    table = None
    template_name = 'generic/object_bulk_add_component.html'

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
        table = self.table(selected_objects)

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
                    pass

                except PermissionsViolation:
                    msg = "Component creation failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)

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
