import logging
from copy import deepcopy

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import ProtectedError
from django.forms.widgets import HiddenInput
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe

from extras.signals import clear_webhooks
from utilities.error_handlers import handle_protectederror
from utilities.exceptions import AbortTransaction, PermissionsViolation
from utilities.forms import ConfirmationForm, ImportForm, restrict_form_fields
from utilities.htmx import is_htmx
from utilities.permissions import get_permission_for_model
from utilities.tables import configure_table
from utilities.utils import normalize_querydict, prepare_cloned_fields
from utilities.views import GetReturnURLMixin
from .base import GenericView

__all__ = (
    'ComponentCreateView',
    'ObjectChildrenView',
    'ObjectDeleteView',
    'ObjectEditView',
    'ObjectImportView',
    'ObjectView',
)


class ObjectView(GenericView):
    """
    Retrieve a single object for display.

    Note: If `template_name` is not specified, it will be determined automatically based on the queryset model.
    """

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'view')

    def get_object(self, **kwargs):
        """
        Return the object being viewed, identified by the keyword arguments passed. If no matching object is found,
        raise a 404 error.
        """
        return get_object_or_404(self.queryset, **kwargs)

    def get_template_name(self):
        """
        Return self.template_name if defined. Otherwise, dynamically resolve the template name using the queryset
        model's `app_label` and `model_name`.
        """
        if self.template_name is not None:
            return self.template_name
        model_opts = self.queryset.model._meta
        return f'{model_opts.app_label}/{model_opts.model_name}.html'

    def get_extra_context(self, request, instance):
        """
        Return any additional context data for the template.

        Args:
            request: The current request
            instance: The object being viewed
        """
        return {}

    def get(self, request, **kwargs):
        """
        GET request handler. `*args` and `**kwargs` are passed to identify the object being queried.

        Args:
            request: The current request
        """
        instance = self.get_object(**kwargs)

        return render(request, self.get_template_name(), {
            'object': instance,
            **self.get_extra_context(request, instance),
        })


class ObjectChildrenView(ObjectView):
    """
    Display a table of child objects associated with the parent object.

    Attributes:
        table: Table class used to render child objects list
    """
    child_model = None
    table = None
    filterset = None

    def get_children(self, request, parent):
        """
        Return a QuerySet of child objects.

        request: The current request
        parent: The parent object
        """
        raise NotImplementedError(f'{self.__class__.__name__} must implement get_children()')

    def prep_table_data(self, request, queryset, parent):
        """
        Provides a hook for subclassed views to modify data before initializing the table.

        Args:
            request: The current request
            queryset: The filtered queryset of child objects
            parent: The parent object
        """
        return queryset

    def get(self, request, *args, **kwargs):
        """
        GET handler for rendering child objects.
        """
        instance = self.get_object(**kwargs)
        child_objects = self.get_children(request, instance)

        if self.filterset:
            child_objects = self.filterset(request.GET, child_objects).qs

        permissions = {}
        for action in ('change', 'delete'):
            perm_name = get_permission_for_model(self.child_model, action)
            permissions[action] = request.user.has_perm(perm_name)

        table = self.table(self.prep_table_data(request, child_objects, instance), user=request.user)
        # Determine whether to display bulk action checkboxes
        if 'pk' in table.base_columns and (permissions['change'] or permissions['delete']):
            table.columns.show('pk')
        configure_table(table, request)

        # If this is an HTMX request, return only the rendered table HTML
        if is_htmx(request):
            return render(request, 'htmx/table.html', {
                'object': instance,
                'table': table,
            })

        return render(request, self.get_template_name(), {
            'object': instance,
            'table': table,
            'permissions': permissions,
            **self.get_extra_context(request, instance),
        })


class ObjectImportView(GetReturnURLMixin, GenericView):
    """
    Import a single object (YAML or JSON format).

    Attributes:
        model_form: The ModelForm used to create individual objects
        related_object_forms: A dictionary mapping of forms to be used for the creation of related (child) objects
    """
    template_name = 'generic/object_import.html'
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

    def _create_object(self, model_form):

        # Save the primary object
        obj = model_form.save()

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

        return obj

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
                        obj = self._create_object(model_form)

                except AbortTransaction:
                    clear_webhooks.send(sender=self)

                except PermissionsViolation:
                    msg = "Object creation failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)
                    clear_webhooks.send(sender=self)

            if not model_form.errors:
                logger.info(f"Import object {obj} (PK: {obj.pk})")
                msg = f'Imported object: <a href="{obj.get_absolute_url()}">{obj}</a>'
                messages.success(request, mark_safe(msg))

                if '_addanother' in request.POST:
                    return redirect(request.get_full_path())

                return_url = form.cleaned_data.get('return_url')
                if return_url is not None and is_safe_url(url=return_url, allowed_hosts=request.get_host()):
                    return redirect(return_url)
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


class ObjectEditView(GetReturnURLMixin, GenericView):
    """
    Create or edit a single object.

    Attributes:
        model_form: The form used to create or edit the object
    """
    template_name = 'generic/object_edit.html'
    model_form = None

    def dispatch(self, request, *args, **kwargs):
        # Determine required permission based on whether we are editing an existing object
        self._permission_action = 'change' if kwargs else 'add'

        return super().dispatch(request, *args, **kwargs)

    def get_required_permission(self):
        # self._permission_action is set by dispatch() to either "add" or "change" depending on whether
        # we are modifying an existing object or creating a new one.
        return get_permission_for_model(self.queryset.model, self._permission_action)

    def get_object(self, **kwargs):
        """
        Return an instance for editing. If a PK has been specified, this will be an existing object.

        Args:
            kwargs: URL path kwargs
        """
        if 'pk' in kwargs:
            obj = get_object_or_404(self.queryset, **kwargs)

            # Take a snapshot of change-logged models
            if hasattr(obj, 'snapshot'):
                obj.snapshot()

            return obj

        return self.queryset.model()

    def alter_object(self, obj, request, url_args, url_kwargs):
        """
        Provides a hook for views to modify an object before it is processed. For example, a parent object can be
        defined given some parameter from the request URL.

        Args:
            obj: The object being edited
            request: The current request
            url_args: URL path args
            url_kwargs: URL path kwargs
        """
        return obj

    def get(self, request, *args, **kwargs):
        """
        GET request handler.

        Args:
            request: The current request
        """
        obj = self.get_object(**kwargs)
        obj = self.alter_object(obj, request, args, kwargs)

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
        """
        POST request handler.

        Args:
            request: The current request
        """
        logger = logging.getLogger('netbox.views.ObjectEditView')
        obj = self.get_object(**kwargs)
        obj = self.alter_object(obj, request, args, kwargs)

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
                    redirect_url = request.path

                    # If the object has clone_fields, pre-populate a new instance of the form
                    params = prepare_cloned_fields(obj)
                    if 'return_url' in request.GET:
                        params['return_url'] = request.GET.get('return_url')
                    if params:
                        redirect_url += f"?{params.urlencode()}"

                    return redirect(redirect_url)

                return_url = self.get_return_url(request, obj)

                return redirect(return_url)

            except PermissionsViolation:
                msg = "Object save failed due to object-level permissions violation"
                logger.debug(msg)
                form.add_error(None, msg)
                clear_webhooks.send(sender=self)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })


class ObjectDeleteView(GetReturnURLMixin, GenericView):
    """
    Delete a single object.
    """
    template_name = 'generic/object_delete.html'

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'delete')

    def get_object(self, **kwargs):
        """
        Return an instance for deletion. If a PK has been specified, this will be an existing object.

        Args:
            kwargs: URL path kwargs
        """
        obj = get_object_or_404(self.queryset, **kwargs)

        # Take a snapshot of change-logged models
        if hasattr(obj, 'snapshot'):
            obj.snapshot()

        return obj

    def get(self, request, *args, **kwargs):
        """
        GET request handler.

        Args:
            request: The current request
        """
        obj = self.get_object(**kwargs)
        form = ConfirmationForm(initial=request.GET)

        # If this is an HTMX request, return only the rendered deletion form as modal content
        if is_htmx(request):
            viewname = f'{self.queryset.model._meta.app_label}:{self.queryset.model._meta.model_name}_delete'
            form_url = reverse(viewname, kwargs={'pk': obj.pk})
            return render(request, 'htmx/delete_form.html', {
                'object': obj,
                'object_type': self.queryset.model._meta.verbose_name,
                'form': form,
                'form_url': form_url,
            })

        return render(request, self.template_name, {
            'object': obj,
            'object_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })

    def post(self, request, *args, **kwargs):
        """
        POST request handler.

        Args:
            request: The current request
        """
        logger = logging.getLogger('netbox.views.ObjectDeleteView')
        obj = self.get_object(**kwargs)
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
            'object': obj,
            'object_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })


#
# Device/VirtualMachine components
#

class ComponentCreateView(GetReturnURLMixin, GenericView):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a Device or VirtualMachine.
    """
    template_name = 'dcim/component_create.html'
    form = None
    model_form = None
    patterned_fields = ('name', 'label')

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

    def alter_object(self, instance, request):
        return instance

    def initialize_forms(self, request):
        data = request.POST if request.method == 'POST' else None
        initial_data = normalize_querydict(request.GET)

        form = self.form(data=data, initial=request.GET)
        model_form = self.model_form(data=data, initial=initial_data)

        # These fields will be set from the pattern values
        for field_name in self.patterned_fields:
            model_form.fields[field_name].widget = HiddenInput()

        return form, model_form

    def get(self, request):
        form, model_form = self.initialize_forms(request)
        instance = self.alter_object(self.queryset.model, request)

        return render(request, self.template_name, {
            'obj': instance,
            'obj_type': self.queryset.model._meta.verbose_name,
            'replication_form': form,
            'form': model_form,
            'return_url': self.get_return_url(request),
        })

    def post(self, request):
        form, model_form = self.initialize_forms(request)
        instance = self.alter_object(self.queryset.model, request)

        self.validate_form(request, form)

        if form.is_valid() and not form.errors:
            if '_addanother' in request.POST:
                return redirect(request.get_full_path())
            else:
                return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'obj': instance,
            'obj_type': self.queryset.model._meta.verbose_name,
            'replication_form': form,
            'form': model_form,
            'return_url': self.get_return_url(request),
        })

    # TODO: Refactor this method for clarity & better error reporting
    def validate_form(self, request, form):
        """
        Validate form values and set errors on the form object as they are detected. If
        no errors are found, signal success messages.
        """
        logger = logging.getLogger('netbox.views.ComponentCreateView')
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

            if not form.errors and not component_form.errors:
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
                        # Return the newly created objects so overridden post methods can use the data as needed.
                        return new_objs

                except PermissionsViolation:
                    msg = "Component creation failed due to object-level permissions violation"
                    logger.debug(msg)
                    form.add_error(None, msg)
                    clear_webhooks.send(sender=self)

        return None
