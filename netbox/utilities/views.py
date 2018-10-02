from __future__ import unicode_literals

from collections import OrderedDict
from copy import deepcopy
import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Count, ProtectedError
from django.forms import CharField, Form, ModelMultipleChoiceField, MultipleHiddenInput, Textarea
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME
from django.views.generic import View
from django_tables2 import RequestConfig

from extras.models import CustomField, CustomFieldValue, ExportTemplate
from utilities.utils import queryset_to_csv
from utilities.forms import BootstrapMixin, CSVDataField
from .constants import M2M_FIELD_TYPES
from .error_handlers import handle_protectederror
from .forms import ConfirmationForm
from .paginator import EnhancedPaginator


class CustomFieldQueryset:
    """
    Annotate custom fields on objects within a QuerySet.
    """

    def __init__(self, queryset, custom_fields):
        self.queryset = queryset
        self.model = queryset.model
        self.custom_fields = custom_fields

    def __iter__(self):
        for obj in self.queryset:
            values_dict = {cfv.field_id: cfv.value for cfv in obj.custom_field_values.all()}
            obj.custom_fields = OrderedDict([(field, values_dict.get(field.pk)) for field in self.custom_fields])
            yield obj


class GetReturnURLMixin(object):
    """
    Provides logic for determining where a user should be redirected after processing a form.
    """
    default_return_url = None

    def get_return_url(self, request, obj=None):

        # First, see if `return_url` was specified as a query parameter. Use it only if it's considered safe.
        query_param = request.GET.get('return_url')
        if query_param and is_safe_url(url=query_param, host=request.get_host()):
            return query_param

        # Next, check if the object being modified (if any) has an absolute URL.
        elif obj is not None and obj.pk and hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()

        # Fall back to the default URL (if specified) for the view.
        elif self.default_return_url is not None:
            return reverse(self.default_return_url)

        # If all else fails, return home. Ideally this should never happen.
        return reverse('home')


class ObjectListView(View):
    """
    List a series of objects.

    queryset: The queryset of objects to display
    filter: A django-filter FilterSet that is applied to the queryset
    filter_form: The form used to render filter options
    table: The django-tables2 Table used to render the objects list
    template_name: The name of the template
    """
    queryset = None
    filter = None
    filter_form = None
    table = None
    template_name = None

    def get(self, request):

        model = self.queryset.model
        content_type = ContentType.objects.get_for_model(model)

        if self.filter:
            self.queryset = self.filter(request.GET, self.queryset).qs

        # If this type of object has one or more custom fields, prefetch any relevant custom field values
        custom_fields = CustomField.objects.filter(obj_type=ContentType.objects.get_for_model(model))\
            .prefetch_related('choices')
        if custom_fields:
            self.queryset = self.queryset.prefetch_related('custom_field_values')

        # Check for export template rendering
        if request.GET.get('export'):
            et = get_object_or_404(ExportTemplate, content_type=content_type, name=request.GET.get('export'))
            queryset = CustomFieldQueryset(self.queryset, custom_fields) if custom_fields else self.queryset
            try:
                return et.render_to_response(queryset)
            except TemplateSyntaxError:
                messages.error(
                    request,
                    "There was an error rendering the selected export template ({}).".format(et.name)
                )
        # Fall back to built-in CSV export if no template was specified
        elif 'export' in request.GET and hasattr(model, 'to_csv'):
            return queryset_to_csv(self.queryset)

        # Provide a hook to tweak the queryset based on the request immediately prior to rendering the object list
        self.queryset = self.alter_queryset(request)

        # Compile user model permissions for access from within the template
        perm_base_name = '{}.{{}}_{}'.format(model._meta.app_label, model._meta.model_name)
        permissions = {p: request.user.has_perm(perm_base_name.format(p)) for p in ['add', 'change', 'delete']}

        # Construct the table based on the user's permissions
        table = self.table(self.queryset)
        if 'pk' in table.base_columns and (permissions['change'] or permissions['delete']):
            table.columns.show('pk')

        # Construct queryset for tags list
        if hasattr(model, 'tags'):
            tags = model.tags.annotate(count=Count('taggit_taggeditem_items')).order_by('name')
        else:
            tags = None

        # Apply the request context
        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(table)

        context = {
            'content_type': content_type,
            'table': table,
            'permissions': permissions,
            'filter_form': self.filter_form(request.GET, label_suffix='') if self.filter_form else None,
            'tags': tags,
        }
        context.update(self.extra_context())

        return render(request, self.template_name, context)

    def alter_queryset(self, request):
        # .all() is necessary to avoid caching queries
        return self.queryset.all()

    def extra_context(self):
        return {}


class ObjectEditView(GetReturnURLMixin, View):
    """
    Create or edit a single object.

    model: The model of the object being edited
    model_form: The form used to create or edit the object
    template_name: The name of the template
    """
    model = None
    model_form = None
    template_name = 'utilities/obj_edit.html'

    def get_object(self, kwargs):
        # Look up object by slug or PK. Return None if neither was provided.
        if 'slug' in kwargs:
            return get_object_or_404(self.model, slug=kwargs['slug'])
        elif 'pk' in kwargs:
            return get_object_or_404(self.model, pk=kwargs['pk'])
        return self.model()

    def alter_obj(self, obj, request, url_args, url_kwargs):
        # Allow views to add extra info to an object before it is processed. For example, a parent object can be defined
        # given some parameter from the request URL.
        return obj

    def get(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        obj = self.alter_obj(obj, request, args, kwargs)
        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}
        form = self.model_form(instance=obj, initial=initial_data)

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })

    def post(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        obj = self.alter_obj(obj, request, args, kwargs)
        form = self.model_form(request.POST, request.FILES, instance=obj)

        if form.is_valid():
            obj_created = not form.instance.pk
            obj = form.save()

            msg = '{} {}'.format(
                'Created' if obj_created else 'Modified',
                self.model._meta.verbose_name
            )
            if hasattr(obj, 'get_absolute_url'):
                msg = '{} <a href="{}">{}</a>'.format(msg, obj.get_absolute_url(), escape(obj))
            else:
                msg = '{} {}'.format(msg, escape(obj))
            messages.success(request, mark_safe(msg))

            if '_addanother' in request.POST:
                return redirect(request.get_full_path())

            return_url = form.cleaned_data.get('return_url')
            if return_url is not None and is_safe_url(url=return_url, host=request.get_host()):
                return redirect(return_url)
            else:
                return redirect(self.get_return_url(request, obj))

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })


class ObjectDeleteView(GetReturnURLMixin, View):
    """
    Delete a single object.

    model: The model of the object being deleted
    template_name: The name of the template
    """
    model = None
    template_name = 'utilities/obj_delete.html'

    def get_object(self, kwargs):
        # Look up object by slug if one has been provided. Otherwise, use PK.
        if 'slug' in kwargs:
            return get_object_or_404(self.model, slug=kwargs['slug'])
        else:
            return get_object_or_404(self.model, pk=kwargs['pk'])

    def get(self, request, **kwargs):

        obj = self.get_object(kwargs)
        form = ConfirmationForm(initial=request.GET)

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.model._meta.verbose_name,
            'return_url': self.get_return_url(request, obj),
        })

    def post(self, request, **kwargs):

        obj = self.get_object(kwargs)
        form = ConfirmationForm(request.POST)
        if form.is_valid():

            try:
                obj.delete()
            except ProtectedError as e:
                handle_protectederror(obj, request, e)
                return redirect(obj.get_absolute_url())

            msg = 'Deleted {} {}'.format(self.model._meta.verbose_name, obj)
            messages.success(request, msg)

            return_url = form.cleaned_data.get('return_url')
            if return_url is not None and is_safe_url(url=return_url, host=request.get_host()):
                return redirect(return_url)
            else:
                return redirect(self.get_return_url(request, obj))

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.model._meta.verbose_name,
            'return_url': self.get_return_url(request, obj),
        })


class BulkCreateView(GetReturnURLMixin, View):
    """
    Create new objects in bulk.

    form: Form class which provides the `pattern` field
    model_form: The ModelForm used to create individual objects
    pattern_target: Name of the field to be evaluated as a pattern (if any)
    template_name: The name of the template
    """
    form = None
    model_form = None
    pattern_target = ''
    template_name = None

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

        model = self.model_form._meta.model
        form = self.form(request.POST)
        model_form = self.model_form(request.POST)

        if form.is_valid():

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
                            new_objs.append(obj)
                        else:
                            # Copy any errors on the pattern target field to the pattern form.
                            errors = model_form.errors.as_data()
                            if errors.get(self.pattern_target):
                                form.add_error('pattern', errors[self.pattern_target])
                            # Raise an IntegrityError to break the for loop and abort the transaction.
                            raise IntegrityError()

                    # If we make it to this point, validation has succeeded on all new objects.
                    msg = "Added {} {}".format(len(new_objs), model._meta.verbose_name_plural)
                    messages.success(request, msg)

                    if '_addanother' in request.POST:
                        return redirect(request.path)
                    return redirect(self.get_return_url(request))

            except IntegrityError:
                pass

        return render(request, self.template_name, {
            'form': form,
            'model_form': model_form,
            'obj_type': model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })


class BulkImportView(GetReturnURLMixin, View):
    """
    Import objects in bulk (CSV format).

    model_form: The form used to create each imported object
    table: The django-tables2 Table used to render the list of imported objects
    template_name: The name of the template
    widget_attrs: A dict of attributes to apply to the import widget (e.g. to require a session key)
    """
    model_form = None
    table = None
    template_name = 'utilities/obj_import.html'
    widget_attrs = {}

    def _import_form(self, *args, **kwargs):

        fields = self.model_form().fields.keys()
        required_fields = [name for name, field in self.model_form().fields.items() if field.required]

        class ImportForm(BootstrapMixin, Form):
            csv = CSVDataField(fields=fields, required_fields=required_fields, widget=Textarea(attrs=self.widget_attrs))

        return ImportForm(*args, **kwargs)

    def _save_obj(self, obj_form):
        """
        Provide a hook to modify the object immediately before saving it (e.g. to encrypt secret data).
        """
        return obj_form.save()

    def get(self, request):

        return render(request, self.template_name, {
            'form': self._import_form(),
            'fields': self.model_form().fields,
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })

    def post(self, request):

        new_objs = []
        form = self._import_form(request.POST)

        if form.is_valid():

            try:

                # Iterate through CSV data and bind each row to a new model form instance.
                with transaction.atomic():
                    for row, data in enumerate(form.cleaned_data['csv'], start=1):
                        obj_form = self.model_form(data)
                        if obj_form.is_valid():
                            obj = self._save_obj(obj_form)
                            new_objs.append(obj)
                        else:
                            for field, err in obj_form.errors.items():
                                form.add_error('csv', "Row {} {}: {}".format(row, field, err[0]))
                            raise ValidationError("")

                # Compile a table containing the imported objects
                obj_table = self.table(new_objs)

                if new_objs:
                    msg = 'Imported {} {}'.format(len(new_objs), new_objs[0]._meta.verbose_name_plural)
                    messages.success(request, msg)

                    return render(request, "import_success.html", {
                        'table': obj_table,
                        'return_url': self.get_return_url(request),
                    })

            except ValidationError:
                pass

        return render(request, self.template_name, {
            'form': form,
            'fields': self.model_form().fields,
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })


class BulkEditView(GetReturnURLMixin, View):
    """
    Edit objects in bulk.

    queryset: Custom queryset to use when retrieving objects (e.g. to select related objects)
    parent_model: The model of the parent object (if any)
    filter: FilterSet to apply when deleting by QuerySet
    table: The table used to display devices being edited
    form: The form class used to edit objects in bulk
    template_name: The name of the template
    """
    queryset = None
    parent_model = None
    filter = None
    table = None
    form = None
    template_name = 'utilities/obj_bulk_edit.html'

    def get(self, request):
        return redirect(self.get_return_url(request))

    def post(self, request, **kwargs):

        model = self.queryset.model

        # Attempt to derive parent object if a parent class has been given
        if self.parent_model:
            parent_obj = get_object_or_404(self.parent_model, **kwargs)
        else:
            parent_obj = None

        # Are we editing *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all') and self.filter is not None:
            pk_list = [obj.pk for obj in self.filter(request.GET, model.objects.only('pk')).qs]
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        if '_apply' in request.POST:
            form = self.form(model, parent_obj, request.POST)
            if form.is_valid():

                custom_fields = form.custom_fields if hasattr(form, 'custom_fields') else []
                standard_fields = [field for field in form.fields if field not in custom_fields and field != 'pk']
                nullified_fields = request.POST.getlist('_nullify')

                try:

                    with transaction.atomic():

                        updated_count = 0
                        for obj in model.objects.filter(pk__in=pk_list):

                            # Update standard fields. If a field is listed in _nullify, delete its value.
                            for name in standard_fields:
                                if name in form.nullable_fields and name in nullified_fields:
                                    setattr(obj, name, '' if isinstance(form.fields[name], CharField) else None)
                                elif form.cleaned_data[name] not in (None, ''):
                                    setattr(obj, name, form.cleaned_data[name])
                            obj.full_clean()
                            obj.save()

                            # Update custom fields
                            obj_type = ContentType.objects.get_for_model(model)
                            for name in custom_fields:
                                field = form.fields[name].model
                                if name in form.nullable_fields and name in nullified_fields:
                                    CustomFieldValue.objects.filter(
                                        field=field, obj_type=obj_type, obj_id=obj.pk
                                    ).delete()
                                elif form.cleaned_data[name] not in [None, '']:
                                    try:
                                        cfv = CustomFieldValue.objects.get(
                                            field=field, obj_type=obj_type, obj_id=obj.pk
                                        )
                                    except CustomFieldValue.DoesNotExist:
                                        cfv = CustomFieldValue(
                                            field=field, obj_type=obj_type, obj_id=obj.pk
                                        )
                                    cfv.value = form.cleaned_data[name]
                                    cfv.save()

                            # Add/remove tags
                            if form.cleaned_data.get('add_tags', None):
                                obj.tags.add(*form.cleaned_data['add_tags'])
                            if form.cleaned_data.get('remove_tags', None):
                                obj.tags.remove(*form.cleaned_data['remove_tags'])

                            updated_count += 1

                    if updated_count:
                        msg = 'Updated {} {}'.format(updated_count, model._meta.verbose_name_plural)
                        messages.success(self.request, msg)

                    return redirect(self.get_return_url(request))

                except ValidationError as e:
                    messages.error(self.request, "{} failed validation: {}".format(obj, e))

        else:
            initial_data = request.POST.copy()
            initial_data['pk'] = pk_list
            form = self.form(model, parent_obj, initial=initial_data)

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


class BulkDeleteView(GetReturnURLMixin, View):
    """
    Delete objects in bulk.

    queryset: Custom queryset to use when retrieving objects (e.g. to select related objects)
    parent_model: The model of the parent object (if any)
    filter: FilterSet to apply when deleting by QuerySet
    table: The table used to display devices being deleted
    form: The form class used to delete objects in bulk
    template_name: The name of the template
    """
    queryset = None
    parent_model = None
    filter = None
    table = None
    form = None
    template_name = 'utilities/obj_bulk_delete.html'

    def get(self, request):
        return redirect(self.get_return_url(request))

    def post(self, request, **kwargs):

        model = self.queryset.model

        # Attempt to derive parent object if a parent class has been given
        if self.parent_model:
            parent_obj = get_object_or_404(self.parent_model, **kwargs)
        else:
            parent_obj = None

        # Are we deleting *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all'):
            if self.filter is not None:
                pk_list = [obj.pk for obj in self.filter(request.GET, model.objects.only('pk')).qs]
            else:
                pk_list = model.objects.values_list('pk', flat=True)
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        form_cls = self.get_form()

        if '_confirm' in request.POST:
            form = form_cls(request.POST)
            if form.is_valid():

                # Delete objects
                queryset = model.objects.filter(pk__in=pk_list)
                try:
                    deleted_count = queryset.delete()[1][model._meta.label]
                except ProtectedError as e:
                    handle_protectederror(list(queryset), request, e)
                    return redirect(self.get_return_url(request))

                msg = 'Deleted {} {}'.format(deleted_count, model._meta.verbose_name_plural)
                messages.success(request, msg)
                return redirect(self.get_return_url(request))

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
            'parent_obj': parent_obj,
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

class ComponentCreateView(View):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a Device or VirtualMachine.
    """
    parent_model = None
    parent_field = None
    model = None
    form = None
    model_form = None
    template_name = None

    def get(self, request, pk):

        parent = get_object_or_404(self.parent_model, pk=pk)
        form = self.form(parent, initial=request.GET)

        return render(request, self.template_name, {
            'parent': parent,
            'component_type': self.model._meta.verbose_name,
            'form': form,
            'return_url': parent.get_absolute_url(),
        })

    def post(self, request, pk):

        parent = get_object_or_404(self.parent_model, pk=pk)

        form = self.form(parent, request.POST)
        if form.is_valid():

            new_components = []
            data = deepcopy(request.POST)
            data[self.parent_field] = parent.pk

            for name in form.cleaned_data['name_pattern']:

                # Initialize the individual component form
                data['name'] = name
                component_form = self.model_form(data)

                if component_form.is_valid():
                    new_components.append(component_form)
                else:
                    for field, errors in component_form.errors.as_data().items():
                        # Assign errors on the child form's name field to name_pattern on the parent form
                        if field == 'name':
                            field = 'name_pattern'
                        for e in errors:
                            form.add_error(field, '{}: {}'.format(name, ', '.join(e)))

            if not form.errors:

                # Create the new components
                for component_form in new_components:
                    component_form.save()

                messages.success(request, "Added {} {} to {}.".format(
                    len(new_components), self.model._meta.verbose_name_plural, parent
                ))
                if '_addanother' in request.POST:
                    return redirect(request.path)
                else:
                    return redirect(parent.get_absolute_url())

        return render(request, self.template_name, {
            'parent': parent,
            'component_type': self.model._meta.verbose_name,
            'form': form,
            'return_url': parent.get_absolute_url(),
        })


class BulkComponentCreateView(GetReturnURLMixin, View):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a set of Devices or VirtualMachines.
    """
    parent_model = None
    parent_field = None
    form = None
    model = None
    model_form = None
    filter = None
    table = None
    template_name = 'utilities/obj_bulk_add_component.html'

    def post(self, request):

        # Are we editing *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all') and self.filter is not None:
            pk_list = [obj.pk for obj in self.filter(request.GET, self.model.objects.only('pk')).qs]
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

                new_components = []
                data = deepcopy(form.cleaned_data)
                for obj in data['pk']:

                    names = data['name_pattern']
                    for name in names:
                        component_data = {
                            self.parent_field: obj.pk,
                            'name': name,
                        }
                        component_data.update(data)
                        component_form = self.model_form(component_data)
                        if component_form.is_valid():
                            new_components.append(component_form.save(commit=False))
                        else:
                            for field, errors in component_form.errors.as_data().items():
                                for e in errors:
                                    form.add_error(field, '{} {}: {}'.format(obj, name, ', '.join(e)))

                if not form.errors:
                    self.model.objects.bulk_create(new_components)

                    messages.success(request, "Added {} {} to {} {}.".format(
                        len(new_components),
                        self.model._meta.verbose_name_plural,
                        len(form.cleaned_data['pk']),
                        self.parent_model._meta.verbose_name_plural
                    ))
                    return redirect(self.get_return_url(request))

        else:
            form = self.form(initial={'pk': pk_list})

        return render(request, self.template_name, {
            'form': form,
            'component_name': self.model._meta.verbose_name_plural,
            'table': table,
            'return_url': self.get_return_url(request),
        })


@requires_csrf_token
def server_error(request, template_name=ERROR_500_TEMPLATE_NAME):
    """
    Custom 500 handler to provide additional context when rendering 500.html.
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>Server Error (500)</h1>', content_type='text/html')
    type_, error, traceback = sys.exc_info()

    return HttpResponseServerError(template.render({
        'exception': str(type_),
        'error': error,
    }))
