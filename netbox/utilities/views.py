from collections import OrderedDict
from django_tables2 import RequestConfig

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.db.models import ProtectedError
from django.forms import CharField, ModelMultipleChoiceField, MultipleHiddenInput, TypedChoiceField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateSyntaxError
from django.utils.http import is_safe_url
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


class ObjectListView(View):
    """
    List a series of objects.

    queryset: The queryset of objects to display
    filter: A django-filter FilterSet that is applied to the queryset
    filter_form: The form used to render filter options
    table: The django-tables2 Table used to render the objects list
    edit_permissions: Editing controls are displayed only if the user has these permissions
    template_name: The name of the template
    """
    queryset = None
    filter = None
    filter_form = None
    table = None
    edit_permissions = []
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

        # Construct the table based on the user's permissions
        table = self.table(self.queryset)
        if 'pk' in table.base_columns and any([request.user.has_perm(perm) for perm in self.edit_permissions]):
            table.base_columns['pk'].visible = True
        RequestConfig(request, paginate={'klass': EnhancedPaginator}).configure(table)

        context = {
            'table': table,
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


class ObjectEditView(View):
    """
    Create or edit a single object.

    model: The model of the object being edited
    form_class: The form used to create or edit the object
    fields_initial: A set of fields that will be prepopulated in the form from the request parameters
    template_name: The name of the template
    obj_list_url: The name of the URL used to display a list of this object type
    use_obj_view: If True, the user will be directed to a view of the object after it has been edited. Otherwise, the
                  user will be directed to the object's list view (defined as `obj_list_url`).
    """
    model = None
    form_class = None
    fields_initial = []
    template_name = 'utilities/obj_edit.html'
    obj_list_url = None
    use_obj_view = True

    def get_object(self, kwargs):
        # Look up object by slug or PK. Return None if neither was provided.
        if 'slug' in kwargs:
            return get_object_or_404(self.model, slug=kwargs['slug'])
        elif 'pk' in kwargs:
            return get_object_or_404(self.model, pk=kwargs['pk'])
        return self.model()

    def alter_obj(self, obj, args, kwargs):
        # Allow views to add extra info to an object before it is processed. For example, a parent object can be defined
        # given some parameter from the request URI.
        return obj

    def get_redirect_url(self, obj):
        # Determine where to redirect the user after updating an object (or aborting an update).
        if obj.pk and self.use_obj_view and hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        if obj and self.use_obj_view and hasattr(obj, 'get_parent_url'):
            return obj.get_parent_url()
        return reverse(self.obj_list_url)

    def get(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        obj = self.alter_obj(obj, args, kwargs)
        initial_data = {k: request.GET[k] for k in self.fields_initial if k in request.GET}
        form = self.form_class(instance=obj, initial=initial_data)

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'cancel_url': self.get_redirect_url(obj),
        })

    def post(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        obj = self.alter_obj(obj, args, kwargs)
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
                msg = u'{} <a href="{}">{}</a>'.format(msg, obj.get_absolute_url(), obj)
            else:
                msg = u'{} {}'.format(msg, obj)
            messages.success(request, msg)
            if obj_created:
                UserAction.objects.log_create(request.user, obj, msg)
            else:
                UserAction.objects.log_edit(request.user, obj, msg)

            if '_addanother' in request.POST:
                return redirect(request.path)
            return redirect(self.get_redirect_url(obj))

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'cancel_url': self.get_redirect_url(obj),
        })


class ObjectDeleteView(View):
    """
    Delete a single object.

    model: The model of the object being edited
    template_name: The name of the template
    redirect_url: Name of the URL to which the user is redirected after deleting the object
    """
    model = None
    template_name = 'utilities/obj_delete.html'
    redirect_url = None

    def get_object(self, kwargs):
        # Look up object by slug if one has been provided. Otherwise, use PK.
        if 'slug' in kwargs:
            return get_object_or_404(self.model, slug=kwargs['slug'])
        else:
            return get_object_or_404(self.model, pk=kwargs['pk'])

    def get_cancel_url(self, obj):
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        if hasattr(obj, 'get_parent_url'):
            return obj.get_parent_url()
        return reverse('home')

    def get(self, request, **kwargs):

        obj = self.get_object(kwargs)
        form = ConfirmationForm()

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.model._meta.verbose_name,
            'cancel_url': self.get_cancel_url(obj),
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
            if self.redirect_url:
                return redirect(self.redirect_url)
            elif hasattr(obj, 'get_parent_url'):
                return redirect(obj.get_parent_url())
            else:
                return redirect('home')

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.model._meta.verbose_name,
            'cancel_url': self.get_cancel_url(obj),
        })


class BulkAddView(View):
    """
    Create new objects in bulk.

    form: Form class
    model: The model of the objects being created
    template_name: The name of the template
    redirect_url: Name of the URL to which the user is redirected after creating the objects
    """
    form = None
    model = None
    template_name = None
    redirect_url = None

    def get(self, request):

        form = self.form()

        return render(request, self.template_name, {
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'cancel_url': reverse(self.redirect_url),
        })

    def post(self, request):

        form = self.form(request.POST)
        if form.is_valid():

            # The first field will be used as the pattern
            pattern_field = form.fields.keys()[0]
            pattern = form.cleaned_data[pattern_field]

            # All other fields will be copied as object attributes
            kwargs = {k: form.cleaned_data[k] for k in form.fields.keys()[1:]}

            new_objs = []
            try:
                with transaction.atomic():
                    for value in pattern:
                        obj = self.model(**kwargs)
                        setattr(obj, pattern_field, value)
                        obj.full_clean()
                        obj.save()
                        new_objs.append(obj)
            except ValidationError as e:
                form.add_error(None, e)

            if not form.errors:
                messages.success(request, u"Added {} {}.".format(len(new_objs), self.model._meta.verbose_name_plural))
                if '_addanother' in request.POST:
                    return redirect(request.path)
                return redirect(self.redirect_url)

        return render(request, self.template_name, {
            'form': form,
            'obj_type': self.model._meta.verbose_name,
            'cancel_url': reverse(self.redirect_url),
        })


class BulkImportView(View):
    """
    Import objects in bulk (CSV format).

    form: Form class
    table: The django-tables2 Table used to render the list of imported objects
    template_name: The name of the template
    obj_list_url: The name of the URL to use for the cancel button
    """
    form = None
    table = None
    template_name = None
    obj_list_url = None

    def get(self, request):

        return render(request, self.template_name, {
            'form': self.form(),
            'obj_list_url': self.obj_list_url,
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
            'obj_list_url': self.obj_list_url,
        })

    def save_obj(self, obj):
        obj.save()


class BulkEditView(View):
    """
    Edit objects in bulk.

    cls: The model of the objects being edited
    parent_cls: The model of the parent object (if any)
    form: The form class used to edit objects in bulk
    template_name: The name of the template
    default_redirect_url: Name of the URL to which the user is redirected after editing the objects
    """
    cls = None
    parent_cls = None
    form = None
    template_name = None
    default_redirect_url = None

    def get(self):
        return redirect(self.default_redirect_url)

    def post(self, request, **kwargs):

        # Attempt to derive parent object if a parent class has been given
        if self.parent_cls:
            parent_obj = get_object_or_404(self.parent_cls, **kwargs)
        else:
            parent_obj = None

        # Determine URL to redirect users upon modification of objects
        posted_redirect_url = request.POST.get('redirect_url')
        if posted_redirect_url and is_safe_url(url=posted_redirect_url, host=request.get_host()):
            redirect_url = posted_redirect_url
        elif parent_obj:
            redirect_url = parent_obj.get_absolute_url()
        elif self.default_redirect_url:
            redirect_url = reverse(self.default_redirect_url)
        else:
            raise ImproperlyConfigured('No redirect URL has been provided.')

        # Are we editing *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all'):
            pk_list = [int(pk) for pk in request.POST.get('pk_all').split(',') if pk]
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
                    elif form.cleaned_data[field]:
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
                return redirect(redirect_url)

        else:
            form = self.form(self.cls, initial={'pk': pk_list})

        selected_objects = self.cls.objects.filter(pk__in=pk_list)
        if not selected_objects:
            messages.warning(request, u"No {} were selected.".format(self.cls._meta.verbose_name_plural))
            return redirect(redirect_url)

        return render(request, self.template_name, {
            'form': form,
            'selected_objects': selected_objects,
            'cancel_url': redirect_url,
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
    form: The form class used to delete objects in bulk
    template_name: The name of the template
    default_redirect_url: Name of the URL to which the user is redirected after deleting the objects
    """
    cls = None
    parent_cls = None
    form = None
    template_name = 'utilities/confirm_bulk_delete.html'
    default_redirect_url = None

    def post(self, request, **kwargs):

        # Attempt to derive parent object if a parent class has been given
        if self.parent_cls:
            parent_obj = get_object_or_404(self.parent_cls, **kwargs)
        else:
            parent_obj = None

        # Determine URL to redirect users upon deletion of objects
        posted_redirect_url = request.POST.get('redirect_url')
        if posted_redirect_url and is_safe_url(url=posted_redirect_url, host=request.get_host()):
            redirect_url = posted_redirect_url
        elif parent_obj:
            redirect_url = parent_obj.get_absolute_url()
        elif self.default_redirect_url:
            redirect_url = reverse(self.default_redirect_url)
        else:
            raise ImproperlyConfigured('No redirect URL has been provided.')

        # Are we deleting *all* objects in the queryset or just a selected subset?
        if request.POST.get('_all'):
            pk_list = [int(pk) for pk in request.POST.get('pk_all').split(',') if pk]
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
                    return redirect(redirect_url)

                msg = u'Deleted {} {}'.format(deleted_count, self.cls._meta.verbose_name_plural)
                messages.success(request, msg)
                UserAction.objects.log_bulk_delete(request.user, ContentType.objects.get_for_model(self.cls), msg)
                return redirect(redirect_url)

        else:
            form = form_cls(initial={'pk': pk_list})

        selected_objects = self.cls.objects.filter(pk__in=pk_list)
        if not selected_objects:
            messages.warning(request, u"No {} were selected for deletion.".format(self.cls._meta.verbose_name_plural))
            return redirect(redirect_url)

        return render(request, self.template_name, {
            'form': form,
            'parent_obj': parent_obj,
            'obj_type_plural': self.cls._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'cancel_url': redirect_url,
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
