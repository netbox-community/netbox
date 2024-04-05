import logging
from collections import defaultdict
from copy import deepcopy

from django.contrib import messages
from django.db import router, transaction
from django.db.models import ProtectedError, RestrictedError
from django.db.models.deletion import Collector
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from extras.signals import clear_events
from utilities.error_handlers import handle_protectederror
from utilities.exceptions import AbortRequest, PermissionsViolation
from utilities.forms import ConfirmationForm, restrict_form_fields
from utilities.htmx import htmx_partial
from utilities.permissions import get_permission_for_model
from utilities.querydict import normalize_querydict, prepare_cloned_fields
from utilities.views import GetReturnURLMixin, get_viewname
from .base import BaseObjectView
from .mixins import ActionsMixin, TableMixin
from .utils import get_prerequisite_model

__all__ = (
    'ComponentCreateView',
    'ObjectChildrenView',
    'ObjectDeleteView',
    'ObjectEditView',
    'ObjectView',
)


class ObjectView(BaseObjectView):
    """
    Retrieve a single object for display.

    Note: If `template_name` is not specified, it will be determined automatically based on the queryset model.

    Attributes:
        tab: A ViewTab instance for the view
    """
    tab = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'view')

    def get_template_name(self):
        """
        Return self.template_name if defined. Otherwise, dynamically resolve the template name using the queryset
        model's `app_label` and `model_name`.
        """
        if self.template_name is not None:
            return self.template_name
        model_opts = self.queryset.model._meta
        return f'{model_opts.app_label}/{model_opts.model_name}.html'

    #
    # Request handlers
    #

    def get(self, request, **kwargs):
        """
        GET request handler. `*args` and `**kwargs` are passed to identify the object being queried.

        Args:
            request: The current request
        """
        instance = self.get_object(**kwargs)

        return render(request, self.get_template_name(), {
            'object': instance,
            'tab': self.tab,
            **self.get_extra_context(request, instance),
        })


class ObjectChildrenView(ObjectView, ActionsMixin, TableMixin):
    """
    Display a table of child objects associated with the parent object. For example, NetBox uses this to display
    the set of child IP addresses within a parent prefix.

    Attributes:
        child_model: The model class which represents the child objects
        table: The django-tables2 Table class used to render the child objects list
        filterset: A django-filter FilterSet that is applied to the queryset
        actions: A mapping of supported actions to their required permissions. When adding custom actions, bulk
            action names must be prefixed with `bulk_`. (See ActionsMixin.)
    """
    child_model = None
    table = None
    filterset = None

    def get_children(self, request, parent):
        """
        Return a QuerySet of child objects.

        Args:
            request: The current request
            parent: The parent object
        """
        raise NotImplementedError(_('{class_name} must implement get_children()').format(
            class_name=self.__class__.__name__
        ))

    def prep_table_data(self, request, queryset, parent):
        """
        Provides a hook for subclassed views to modify data before initializing the table.

        Args:
            request: The current request
            queryset: The filtered queryset of child objects
            parent: The parent object
        """
        return queryset

    #
    # Request handlers
    #

    def get(self, request, *args, **kwargs):
        """
        GET handler for rendering child objects.
        """
        instance = self.get_object(**kwargs)
        child_objects = self.get_children(request, instance)

        if self.filterset:
            child_objects = self.filterset(request.GET, child_objects, request=request).qs

        # Determine the available actions
        actions = self.get_permitted_actions(request.user, model=self.child_model)
        has_bulk_actions = any([a.startswith('bulk_') for a in actions])

        table_data = self.prep_table_data(request, child_objects, instance)
        table = self.get_table(table_data, request, has_bulk_actions)

        # If this is an HTMX request, return only the rendered table HTML
        if htmx_partial(request):
            return render(request, 'htmx/table.html', {
                'object': instance,
                'table': table,
            })

        return render(request, self.get_template_name(), {
            'object': instance,
            'child_model': self.child_model,
            'base_template': f'{instance._meta.app_label}/{instance._meta.model_name}.html',
            'table': table,
            'table_config': f'{table.name}_config',
            'actions': actions,
            'tab': self.tab,
            'return_url': request.get_full_path(),
            **self.get_extra_context(request, instance),
        })


class ObjectEditView(GetReturnURLMixin, BaseObjectView):
    """
    Create or edit a single object.

    Attributes:
        form: The form used to create or edit the object
    """
    template_name = 'generic/object_edit.html'
    form = None

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
        Return an object for editing. If no keyword arguments have been specified, this will be a new instance.
        """
        if not kwargs:
            # We're creating a new object
            return self.queryset.model()
        return super().get_object(**kwargs)

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

    def get_extra_addanother_params(self, request):
        """
        Return a dictionary of extra parameters to use on the Add Another button.
        """
        return {}

    #
    # Request handlers
    #

    def get(self, request, *args, **kwargs):
        """
        GET request handler.

        Args:
            request: The current request
        """
        obj = self.get_object(**kwargs)
        obj = self.alter_object(obj, request, args, kwargs)
        model = self.queryset.model

        initial_data = normalize_querydict(request.GET)
        form = self.form(instance=obj, initial=initial_data)
        restrict_form_fields(form, request.user)

        # If this is an HTMX request, return only the rendered form HTML
        if htmx_partial(request):
            return render(request, 'htmx/form.html', {
                'form': form,
            })

        return render(request, self.template_name, {
            'model': model,
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            'prerequisite_model': get_prerequisite_model(self.queryset),
            **self.get_extra_context(request, obj),
        })

    def post(self, request, *args, **kwargs):
        """
        POST request handler.

        Args:
            request: The current request
        """
        logger = logging.getLogger('netbox.views.ObjectEditView')
        obj = self.get_object(**kwargs)

        # Take a snapshot for change logging (if editing an existing object)
        if obj.pk and hasattr(obj, 'snapshot'):
            obj.snapshot()

        obj = self.alter_object(obj, request, args, kwargs)

        form = self.form(data=request.POST, files=request.FILES, instance=obj)
        restrict_form_fields(form, request.user)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                with transaction.atomic():
                    object_created = form.instance.pk is None
                    obj = form.save()

                    # Check that the new object conforms with any assigned object-level permissions
                    if not self.queryset.filter(pk=obj.pk).exists():
                        raise PermissionsViolation()

                msg = '{} {}'.format(
                    'Created' if object_created else 'Modified',
                    self.queryset.model._meta.verbose_name
                )
                logger.info(f"{msg} {obj} (PK: {obj.pk})")
                if hasattr(obj, 'get_absolute_url'):
                    msg = mark_safe(f'{msg} <a href="{obj.get_absolute_url()}">{escape(obj)}</a>')
                else:
                    msg = f'{msg} {obj}'
                messages.success(request, msg)

                if '_addanother' in request.POST:
                    redirect_url = request.path

                    # If cloning is supported, pre-populate a new instance of the form
                    params = prepare_cloned_fields(obj)
                    params.update(self.get_extra_addanother_params(request))
                    if params:
                        if 'return_url' in request.GET:
                            params['return_url'] = request.GET.get('return_url')
                        redirect_url += f"?{params.urlencode()}"

                    return redirect(redirect_url)

                return_url = self.get_return_url(request, obj)

                return redirect(return_url)

            except (AbortRequest, PermissionsViolation) as e:
                logger.debug(e.message)
                form.add_error(None, e.message)
                clear_events.send(sender=self)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            **self.get_extra_context(request, obj),
        })


class ObjectDeleteView(GetReturnURLMixin, BaseObjectView):
    """
    Delete a single object.
    """
    template_name = 'generic/object_delete.html'

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'delete')

    def _get_dependent_objects(self, obj):
        """
        Returns a dictionary mapping of dependent objects (organized by model) which will be deleted as a result of
        deleting the requested object.

        Args:
            obj: The object to return dependent objects for
        """
        using = router.db_for_write(obj._meta.model)
        collector = Collector(using=using)
        collector.collect([obj])

        # Compile a mapping of models to instances
        dependent_objects = defaultdict(list)
        for model, instance in collector.instances_with_model():
            # Omit the root object
            if instance != obj:
                dependent_objects[model].append(instance)

        return dict(dependent_objects)

    def _handle_protected_objects(self, obj, protected_objects, request, exc):
        """
        Handle a ProtectedError or RestrictedError exception raised while attempt to resolve dependent objects.
        """
        handle_protectederror(protected_objects, request, exc)

        if request.htmx:
            return HttpResponse(headers={
                'HX-Redirect': obj.get_absolute_url(),
            })
        else:
            return redirect(obj.get_absolute_url())

    #
    # Request handlers
    #

    def get(self, request, *args, **kwargs):
        """
        GET request handler.

        Args:
            request: The current request
        """
        obj = self.get_object(**kwargs)
        form = ConfirmationForm(initial=request.GET)

        try:
            dependent_objects = self._get_dependent_objects(obj)
        except ProtectedError as e:
            return self._handle_protected_objects(obj, e.protected_objects, request, e)
        except RestrictedError as e:
            return self._handle_protected_objects(obj, e.restricted_objects, request, e)

        # If this is an HTMX request, return only the rendered deletion form as modal content
        if htmx_partial(request):
            viewname = get_viewname(self.queryset.model, action='delete')
            form_url = reverse(viewname, kwargs={'pk': obj.pk})
            return render(request, 'htmx/delete_form.html', {
                'object': obj,
                'object_type': self.queryset.model._meta.verbose_name,
                'form': form,
                'form_url': form_url,
                'dependent_objects': dependent_objects,
                **self.get_extra_context(request, obj),
            })

        return render(request, self.template_name, {
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            'dependent_objects': dependent_objects,
            **self.get_extra_context(request, obj),
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

        # Take a snapshot of change-logged models
        if hasattr(obj, 'snapshot'):
            obj.snapshot()

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                obj.delete()

            except (ProtectedError, RestrictedError) as e:
                logger.info(f"Caught {type(e)} while attempting to delete objects")
                handle_protectederror([obj], request, e)
                return redirect(obj.get_absolute_url())

            except AbortRequest as e:
                logger.debug(e.message)
                messages.error(request, mark_safe(e.message))
                return redirect(obj.get_absolute_url())

            msg = 'Deleted {} {}'.format(self.queryset.model._meta.verbose_name, obj)
            logger.info(msg)
            messages.success(request, msg)

            return_url = form.cleaned_data.get('return_url')
            if return_url and return_url.startswith('/'):
                return redirect(return_url)
            return redirect(self.get_return_url(request, obj))

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            **self.get_extra_context(request, obj),
        })


#
# Device/VirtualMachine components
#

class ComponentCreateView(GetReturnURLMixin, BaseObjectView):
    """
    Add one or more components (e.g. interfaces, console ports, etc.) to a Device or VirtualMachine.
    """
    template_name = 'generic/object_edit.html'
    form = None
    model_form = None

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'add')

    def alter_object(self, instance, request):
        return instance

    def initialize_form(self, request):
        data = request.POST if request.method == 'POST' else None
        initial_data = normalize_querydict(request.GET)

        form = self.form(data=data, initial=initial_data)

        return form

    def get(self, request):
        form = self.initialize_form(request)
        instance = self.alter_object(self.queryset.model(), request)

        # If this is an HTMX request, return only the rendered form HTML
        if htmx_partial(request):
            return render(request, 'htmx/form.html', {
                'form': form,
            })

        return render(request, self.template_name, {
            'object': instance,
            'form': form,
            'return_url': self.get_return_url(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.views.ComponentCreateView')
        form = self.initialize_form(request)
        instance = self.alter_object(self.queryset.model(), request)

        # Note that the form instance is a replicated field base
        # This is needed to avoid running custom validators multiple times
        form.instance._replicated_base = hasattr(self.form, "replication_fields")

        if form.is_valid():
            new_components = []
            data = deepcopy(request.POST)
            pattern_count = len(form.cleaned_data[self.form.replication_fields[0]])

            for i in range(pattern_count):
                for field_name in self.form.replication_fields:
                    if form.cleaned_data.get(field_name):
                        data[field_name] = form.cleaned_data[field_name][i]

                if hasattr(form, 'get_iterative_data'):
                    data.update(form.get_iterative_data(i))

                component_form = self.model_form(data)

                if component_form.is_valid():
                    new_components.append(component_form)
                else:
                    form.errors.update(component_form.errors)
                    break

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

                        # Redirect user on success
                        if '_addanother' in request.POST:
                            return redirect(request.get_full_path())
                        else:
                            return redirect(self.get_return_url(request))

                except (AbortRequest, PermissionsViolation) as e:
                    logger.debug(e.message)
                    form.add_error(None, e.message)
                    clear_events.send(sender=self)

        return render(request, self.template_name, {
            'object': instance,
            'form': form,
            'return_url': self.get_return_url(request),
        })
