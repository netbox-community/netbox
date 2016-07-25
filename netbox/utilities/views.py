from django_tables2 import RequestConfig

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.db.models import ProtectedError
from django.forms import ModelMultipleChoiceField, MultipleHiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateSyntaxError
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic import View

from extras.models import ExportTemplate, UserAction

from .error_handlers import handle_protectederror
from .forms import ConfirmationForm
from .paginator import EnhancedPaginator


class ObjectListView(View):
    queryset = None
    filter = None
    filter_form = None
    table = None
    edit_permissions = []
    template_name = None
    redirect_on_single_result = True

    def get(self, request, *args, **kwargs):

        model = self.queryset.model
        object_ct = ContentType.objects.get_for_model(model)

        if self.filter:
            self.queryset = self.filter(request.GET, self.queryset).qs

        # Check for export template rendering
        if request.GET.get('export'):
            et = get_object_or_404(ExportTemplate, content_type=object_ct, name=request.GET.get('export'))
            try:
                response = et.to_response(context_dict={'queryset': self.queryset.all()},
                                          filename='netbox_{}'.format(self.queryset.model._meta.verbose_name_plural))
                return response
            except TemplateSyntaxError:
                messages.error(request, "There was an error rendering the selected export template ({})."
                               .format(et.name))
        # Fall back to built-in CSV export
        elif 'export' in request.GET and hasattr(model, 'to_csv'):
            output = '\n'.join([obj.to_csv() for obj in self.queryset.all()])
            response = HttpResponse(
                output,
                content_type='text/csv'
            )
            response['Content-Disposition'] = 'attachment; filename="netbox_{}.csv"'\
                .format(self.queryset.model._meta.verbose_name_plural)
            return response

        # Attempt to redirect automatically if the search query returns a single result
        if self.redirect_on_single_result and self.queryset.count() == 1 and request.GET:
            try:
                return HttpResponseRedirect(self.queryset[0].get_absolute_url())
            except AttributeError:
                pass

        # Provide a hook to tweak the queryset based on the request immediately prior to rendering the object list
        self.queryset = self.alter_queryset(request)

        # Construct the table based on the user's permissions
        table = self.table(self.queryset)
        table.model = model
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
    model = None
    form_class = None
    fields_initial = []
    template_name = 'utilities/obj_edit.html'
    success_url = None
    cancel_url = None

    def get_object(self, kwargs):
        # Look up object by slug if one has been provided. Otherwise, use PK.
        if 'slug' in kwargs:
            return get_object_or_404(self.model, slug=kwargs['slug'])
        else:
            return get_object_or_404(self.model, pk=kwargs['pk'])

    def get(self, request, *args, **kwargs):

        if kwargs:
            obj = self.get_object(kwargs)
            form = self.form_class(instance=obj)
        else:
            obj = None
            form = self.form_class(initial={k: request.GET.get(k) for k in self.fields_initial})

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'cancel_url': obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else reverse(self.cancel_url),
        })

    def post(self, request, *args, **kwargs):

        # Validate object if editing an existing object
        obj = self.get_object(kwargs) if kwargs else None

        form = self.form_class(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj_created = not obj.pk
            obj.save()

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
            elif self.success_url:
                return redirect(self.success_url)
            else:
                return redirect(obj.get_absolute_url())

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'cancel_url': obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else reverse(self.cancel_url),
        })


class ObjectDeleteView(View):
    model = None
    template_name = 'utilities/obj_delete.html'
    redirect_url = None

    def get_object(self, kwargs):
        # Look up object by slug if one has been provided. Otherwise, use PK.
        if 'slug' in kwargs:
            return get_object_or_404(self.model, slug=kwargs['slug'])
        else:
            return get_object_or_404(self.model, pk=kwargs['pk'])

    def get(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        form = ConfirmationForm()

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.model._meta.verbose_name,
            'cancel_url': obj.get_absolute_url(),
        })

    def post(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            try:
                obj.delete()
                msg = u'Deleted {} {}'.format(self.model._meta.verbose_name, obj)
                messages.success(request, msg)
                UserAction.objects.log_delete(request.user, obj, msg)
                return redirect(self.redirect_url)
            except ProtectedError, e:
                handle_protectederror(obj, request, e)
                return redirect(obj.get_absolute_url())

        return render(request, self.template_name, {
            'obj': obj,
            'form': form,
            'obj_type': self.model._meta.verbose_name,
            'cancel_url': obj.get_absolute_url(),
        })


class BulkImportView(View):
    form = None
    table = None
    template_name = None
    obj_list_url = None

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, {
            'form': self.form(),
            'obj_list_url': self.obj_list_url,
        })

    def post(self, request, *args, **kwargs):

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
    cls = None
    form = None
    template_name = None
    default_redirect_url = None

    def get(self, request, *args, **kwargs):
        return redirect(self.default_redirect_url)

    def post(self, request, *args, **kwargs):

        posted_redirect_url = request.POST.get('redirect_url')
        if posted_redirect_url and is_safe_url(url=posted_redirect_url, host=request.get_host()):
            redirect_url = posted_redirect_url
        else:
            redirect_url = reverse(self.default_redirect_url)

        if request.POST.get('_all'):
            pk_list = [x for x in request.POST.get('pk_all').split(',') if x]
        else:
            pk_list = request.POST.getlist('pk')

        if '_apply' in request.POST:
            form = self.form(request.POST)
            if form.is_valid():
                updated_count = self.update_objects(pk_list, form)
                if updated_count:
                    msg = u'Updated {} {}'.format(updated_count, self.cls._meta.verbose_name_plural)
                    messages.success(self.request, msg)
                    UserAction.objects.log_bulk_edit(request.user, ContentType.objects.get_for_model(self.cls), msg)
                return redirect(redirect_url)

        else:
            form = self.form(initial={'pk': pk_list})

        selected_objects = self.cls.objects.filter(pk__in=pk_list)
        if not selected_objects:
            messages.warning(request, "No {} were selected.".format(self.cls._meta.verbose_name_plural))
            return redirect(redirect_url)

        return render(request, self.template_name, {
            'form': form,
            'selected_objects': selected_objects,
            'cancel_url': redirect_url,
        })

    def update_objects(self, obj_list, form):
        """
        This method provides the update logic (must be overridden by subclasses).
        """
        raise NotImplementedError()


class BulkDeleteView(View):
    cls = None
    parent_cls = None
    form = None
    template_name = 'utilities/confirm_bulk_delete.html'
    default_redirect_url = None

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(BulkDeleteView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

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
            pk_list = [x for x in request.POST.get('pk_all').split(',') if x]
        else:
            pk_list = request.POST.getlist('pk')

        form_cls = self.get_form()

        if '_confirm' in request.POST:
            form = form_cls(request.POST)
            if form.is_valid():

                # Delete objects
                queryset = self.cls.objects.filter(pk__in=pk_list)
                try:
                    deleted_count = queryset.delete()[1][self.cls._meta.label]
                except ProtectedError, e:
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
            messages.warning(request, "No {} were selected for deletion.".format(self.cls._meta.verbose_name_plural))
            return redirect(redirect_url)

        return render(request, self.template_name, {
            'form': form,
            'parent_obj': parent_obj,
            'obj_type_plural': self.cls._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'cancel_url': redirect_url,
        })

    def get_form(self):
        """Provide a standard bulk delete form if none has been specified for the view"""

        class BulkDeleteForm(ConfirmationForm):
            pk = ModelMultipleChoiceField(queryset=self.cls.objects.all(), widget=MultipleHiddenInput)

        if self.form:
            return self.form
        return BulkDeleteForm
