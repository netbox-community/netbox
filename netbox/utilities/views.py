from collections import OrderedDict
from django_tables2 import RequestConfig

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.db.models import ProtectedError
from django.forms import CharField, ModelMultipleChoiceField, MultipleHiddenInput, TypedChoiceField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateSyntaxError
from django.utils.html import escape
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.views.generic import View

from extras.forms import CustomFieldForm
from extras.models import CustomField, CustomFieldValue, ExportTemplate, UserAction

from .error_handlers import handle_protectederror
from .forms import ConfirmationForm
from .paginator import EnhancedPaginator


class CustomFieldQueryset:
    """
    Annotate custom fields on objects within a QuerySet.
    """

    def __init__(self, queryset, custom_fields):
        self.queryset = queryset
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

    def get_return_url(self, request, obj):
        query_param = request.GET.get('return_url')
        if query_param and is_safe_url(url=query_param, host=request.get_host()):
            return query_param
        elif obj.pk and hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        elif self.default_return_url is not None:
            return reverse(self.default_return_url)
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
        object_ct = ContentType.objects.get_for_model(model)

        if self.filter:
            self.queryset = self.filter(request.GET, self.queryset).qs

        # If this type of object has one or more custom fields, prefetch any relevant custom field values
        custom_fields = CustomField.objects.filter(obj_type=ContentType.objects.get_for_model(model))\
            .prefetch_related('choices')
        if custom_fields:
            self.queryset = self.queryset.prefetch_related('custom_field_values')

        # Check for export template rendering
        if request.GET.get('export'):
            et = get_object_or_404(ExportTemplate, content_type=object_ct, name=request.GET.get('export'))
            queryset = CustomFieldQueryset(self.queryset, custom_fields) if custom_fields else self.queryset
            try:
                response = et.to_response(context_dict={'queryset': queryset},
                                          filename='netbox_{}'.format(model._meta.verbose_name_plural))
                return response
            except TemplateSyntaxError:
                messages.error(request, u"There was an error rendering the selected export template ({})."
                               .format(et.name))
        # Fall back to built-in CSV export
        elif 'export' in request.GET and hasattr(model, 'to_csv'):
            output = '\n'.join([obj.to_csv() for obj in self.queryset])
            response = HttpResponse(
                output,
                content_type='text/csv'
            )
            response['Content-Disposition'] = 'attachment; filename="netbox_{}.csv"'\
                .format(self.queryset.model._meta.verbose_name_plural)
            return response

        # Provide a hook to tweak the queryset based on the request immediately prior to rendering the object list
        self.queryset = self.alter_queryset(request)

        # Compile user model permissions for access from within the template
        perm_base_name = '{}.{{}}_{}'.format(model._meta.app_label, model._meta.model_name)
        permissions = {p: request.user.has_perm(perm_base_name.format(p)) for p in ['add', 'change', 'delete']}

        # Construct the table based on the user's permissions
        table = self.table(self.queryset)
        if 'pk' in table.base_columns and (permissions['change'] or permissions['delete']):
            table.base_columns['pk'].visible = True

        # Apply the request context
        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(table)

        context = {
            'table': table,
            'permissions': permissions,
            'filter_form': self.filter_form(request.GET, label_suffix='') if self.filter_form else None,
            'export_templates': ExportTemplate.objects.filter(content_type=object_ct),
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
    form_class: The form used to create or edit the object
    template_name: The name of the template
    default_return_url: The name of the URL used to display a list of this object type
    """
    model = None
    form_class = None
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
        form = self.form_class(instance=obj, initial=initial_data)

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })

    def post(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        obj = self.alter_obj(obj, request, args, kwargs)
        form = self.form_class(request.POST, instance=obj)

        if form.is_valid():
            obj = form.save(commit=False)
            obj_created = not obj.pk
            obj.save()
            form.save_m2m()
            if isinstance(form, CustomFieldForm):
                form.save_custom_fields()

            msg = u'Created ' if obj_created else u'Modified '
            msg += self.model._meta.verbose_name
            if hasattr(obj, 'get_absolute_url'):
                msg = u'{} <a href="{}">{}</a>'.format(msg, obj.get_absolute_url(), escape(obj))
            else:
                msg = u'{} {}'.format(msg, escape(obj))
            messages.success(request, mark_safe(msg))
            if obj_created:
                UserAction.objects.log_create(request.user, obj, msg)
            else:
                UserAction.objects.log_edit(request.user, obj, msg)

            if '_addanother' in request.POST:
                return redirect(request.path)

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

    model: The model of the object being edited
    template_name: The name of the template
    default_return_url: Name of the URL to which the user is redirected after deleting the object
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

            msg = u'Deleted {} {}'.format(self.model._meta.verbose_name, obj)
            messages.success(request, msg)
            UserAction.objects.log_delete(request.user, obj, msg)

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


class BulkAddView(View):
    """
    Create new objects in bulk.

    form: Form class
    model_form: The ModelForm used to create individual objects
    template_name: The name of the template
    default_return_url: Name of the URL to which the user is redirected after creating the objects
    """
    form = None
    model_form = None
    template_name = None
    default_return_url = 'home'

    def get(self, request):

        form = self.form()

        return render(request, self.template_name, {
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'form': form,
            'return_url': reverse(self.default_return_url),
        })

    def post(self, request):

        model = self.model_form._meta.model
        form = self.form(request.POST)
        if form.is_valid():

            # Read the pattern field and target from the form's pattern_map
            pattern_field, pattern_target = form.pattern_map
            pattern = form.cleaned_data[pattern_field]
            model_form_data = form.cleaned_data

            new_objs = []
            try:
                with transaction.atomic():
                    # Validate and save each object individually
                    for value in pattern:
                        model_form_data[pattern_target] = value
                        model_form = self.model_form(model_form_data)
                        if model_form.is_valid():
                            obj = model_form.save()
                            new_objs.append(obj)
                        else:
                            for error in model_form.errors.as_data().values():
                                form.add_error(None, error)
                    # Abort the creation of all objects if errors exist
                    if form.errors:
                        raise ValidationError("Validation of one or more model forms failed.")
            except ValidationError:
                pass

            if not form.errors:
                msg = u"Added {} {}".format(len(new_objs), model._meta.verbose_name_plural)
                messages.success(request, msg)
                UserAction.objects.log_bulk_create(request.user, ContentType.objects.get_for_model(model), msg)
                if '_addanother' in request.POST:
                    return redirect(request.path)
                return redirect(self.default_return_url)

        return render(request, self.template_name, {
            'form': form,
            'obj_type': model._meta.verbose_name,
            'return_url': reverse(self.default_return_url),
        })


class BulkImportView(View):
    """
    Import objects in bulk (CSV format).

    form: Form class
    table: The django-tables2 Table used to render the list of imported objects
    template_name: The name of the template
    default_return_url: The name of the URL to use for the cancel button
    """
    form = None
    table = None
    template_name = None
    default_return_url = None

    def get(self, request):

        return render(request, self.template_name, {
            'form': self.form(),
            'return_url': self.default_return_url,
        })

    def post(self, request):

        form = self.form(request.POST)
        if form.is_valid():
            new_objs = []
            try:
                with transaction.atomic():
                    for obj in form.cleaned_data['csv']:
                        self.save_obj(obj)
                        new_objs.append(obj)

                obj_table = self.table(new_objs)
                if new_objs:
                    msg = u'Imported {} {}'.format(len(new_objs), new_objs[0]._meta.verbose_name_plural)
                    messages.success(request, msg)
                    UserAction.objects.log_import(request.user, ContentType.objects.get_for_model(new_objs[0]), msg)

                return render(request, "import_success.html", {
                    'table': obj_table,
                })

            except IntegrityError as e:
                form.add_error('csv', "Record {}: {}".format(len(new_objs) + 1, e.__cause__))

        return render(request, self.template_name, {
            'form': form,
            'return_url': self.default_return_url,
        })

    def save_obj(self, obj):
        obj.save()


class BulkEditView(View):
    """
    Edit objects in bulk.

    cls: The model of the objects being edited
    parent_cls: The model of the parent object (if any)
    filter: FilterSet to apply when deleting by QuerySet
    form: The form class used to edit objects in bulk
    template_name: The name of the template
    default_return_url: Name of the URL to which the user is redirected after editing the objects (can be overridden by
                        POSTing return_url)
    """
    cls = None
    parent_cls = None
    filter = None
    form = None
    template_name = None
    default_return_url = 'home'

    def get(self):
        return redirect(self.default_return_url)

    def post(self, request, **kwargs):

        # Attempt to derive parent object if a parent class has been given
        if self.parent_cls:
            parent_obj = get_object_or_404(self.parent_cls, **kwargs)
        else:
            parent_obj = None

        # Determine URL to redirect users upon modification of objects
        posted_return_url = request.POST.get('return_url')
        if posted_return_url and is_safe_url(url=posted_return_url, host=request.get_host()):
            return_url = posted_return_url
        elif parent_obj:
            return_url = parent_obj.get_absolute_url()
        else:
            return_url = reverse(self.default_return_url)

        # Are we editing *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all') and self.filter is not None:
            pk_list = [obj.pk for obj in self.filter(request.GET, self.cls.objects.only('pk')).qs]
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        if '_apply' in request.POST:
            form = self.form(self.cls, request.POST)
            if form.is_valid():

                custom_fields = form.custom_fields if hasattr(form, 'custom_fields') else []
                standard_fields = [field for field in form.fields if field not in custom_fields and field != 'pk']

                # Update standard fields. If a field is listed in _nullify, delete its value.
                nullified_fields = request.POST.getlist('_nullify')
                fields_to_update = {}
                for field in standard_fields:
                    if field in form.nullable_fields and field in nullified_fields:
                        if isinstance(form.fields[field], CharField):
                            fields_to_update[field] = ''
                        else:
                            fields_to_update[field] = None
                    elif form.cleaned_data[field] not in (None, ''):
                        fields_to_update[field] = form.cleaned_data[field]
                updated_count = self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)

                # Update custom fields for objects
                if custom_fields:
                    objs_updated = self.update_custom_fields(pk_list, form, custom_fields, nullified_fields)
                    if objs_updated and not updated_count:
                        updated_count = objs_updated

                if updated_count:
                    msg = u'Updated {} {}'.format(updated_count, self.cls._meta.verbose_name_plural)
                    messages.success(self.request, msg)
                    UserAction.objects.log_bulk_edit(request.user, ContentType.objects.get_for_model(self.cls), msg)
                return redirect(return_url)

        else:
            initial_data = request.POST.copy()
            initial_data['pk'] = pk_list
            form = self.form(self.cls, initial=initial_data)

        selected_objects = self.cls.objects.filter(pk__in=pk_list)
        if not selected_objects:
            messages.warning(request, u"No {} were selected.".format(self.cls._meta.verbose_name_plural))
            return redirect(return_url)

        return render(request, self.template_name, {
            'form': form,
            'selected_objects': selected_objects,
            'return_url': return_url,
        })

    def update_custom_fields(self, pk_list, form, fields, nullified_fields):
        obj_type = ContentType.objects.get_for_model(self.cls)
        objs_updated = False

        for name in fields:

            field = form.fields[name].model

            # Setting the field to null
            if name in form.nullable_fields and name in nullified_fields:

                # Delete all CustomFieldValues for instances of this field belonging to the selected objects.
                CustomFieldValue.objects.filter(field=field, obj_type=obj_type, obj_id__in=pk_list).delete()
                objs_updated = True

            # Updating the value of the field
            elif form.cleaned_data[name] not in [None, u'']:

                # Check for zero value (bulk editing)
                if isinstance(form.fields[name], TypedChoiceField) and form.cleaned_data[name] == 0:
                    serialized_value = field.serialize_value(None)
                else:
                    serialized_value = field.serialize_value(form.cleaned_data[name])

                # Gather any pre-existing CustomFieldValues for the objects being edited.
                existing_cfvs = CustomFieldValue.objects.filter(field=field, obj_type=obj_type, obj_id__in=pk_list)

                # Determine which objects have an existing CFV to update and which need a new CFV created.
                update_list = [cfv['obj_id'] for cfv in existing_cfvs.values()]
                create_list = list(set(pk_list) - set(update_list))

                # Creating/updating CFVs
                if serialized_value:
                    existing_cfvs.update(serialized_value=serialized_value)
                    CustomFieldValue.objects.bulk_create([
                        CustomFieldValue(field=field, obj_type=obj_type, obj_id=pk, serialized_value=serialized_value)
                        for pk in create_list
                    ])

                # Deleting CFVs
                else:
                    existing_cfvs.delete()

                objs_updated = True

        return len(pk_list) if objs_updated else 0


class BulkDeleteView(View):
    """
    Delete objects in bulk.

    cls: The model of the objects being deleted
    parent_cls: The model of the parent object (if any)
    filter: FilterSet to apply when deleting by QuerySet
    form: The form class used to delete objects in bulk
    template_name: The name of the template
    default_return_url: Name of the URL to which the user is redirected after deleting the objects (can be overriden by
                        POSTing return_url)
    """
    cls = None
    parent_cls = None
    filter = None
    form = None
    template_name = 'utilities/confirm_bulk_delete.html'
    default_return_url = 'home'

    def post(self, request, **kwargs):

        # Attempt to derive parent object if a parent class has been given
        if self.parent_cls:
            parent_obj = get_object_or_404(self.parent_cls, **kwargs)
        else:
            parent_obj = None

        # Determine URL to redirect users upon deletion of objects
        posted_return_url = request.POST.get('return_url')
        if posted_return_url and is_safe_url(url=posted_return_url, host=request.get_host()):
            return_url = posted_return_url
        elif parent_obj:
            return_url = parent_obj.get_absolute_url()
        else:
            return_url = reverse(self.default_return_url)

        # Are we deleting *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all') and self.filter is not None:
            pk_list = [obj.pk for obj in self.filter(request.GET, self.cls.objects.only('pk')).qs]
        else:
            pk_list = [int(pk) for pk in request.POST.getlist('pk')]

        form_cls = self.get_form()

        if '_confirm' in request.POST:
            form = form_cls(request.POST)
            if form.is_valid():

                # Delete objects
                queryset = self.cls.objects.filter(pk__in=pk_list)
                try:
                    deleted_count = queryset.delete()[1][self.cls._meta.label]
                except ProtectedError as e:
                    handle_protectederror(list(queryset), request, e)
                    return redirect(return_url)

                msg = u'Deleted {} {}'.format(deleted_count, self.cls._meta.verbose_name_plural)
                messages.success(request, msg)
                UserAction.objects.log_bulk_delete(request.user, ContentType.objects.get_for_model(self.cls), msg)
                return redirect(return_url)

        else:
            form = form_cls(initial={'pk': pk_list, 'return_url': return_url})

        selected_objects = self.cls.objects.filter(pk__in=pk_list)
        if not selected_objects:
            messages.warning(request, u"No {} were selected for deletion.".format(self.cls._meta.verbose_name_plural))
            return redirect(return_url)

        return render(request, self.template_name, {
            'form': form,
            'parent_obj': parent_obj,
            'obj_type_plural': self.cls._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': return_url,
        })

    def get_form(self):
        """
        Provide a standard bulk delete form if none has been specified for the view
        """

        class BulkDeleteForm(ConfirmationForm):
            pk = ModelMultipleChoiceField(queryset=self.cls.objects.all(), widget=MultipleHiddenInput)

        if self.form:
            return self.form
        return BulkDeleteForm
