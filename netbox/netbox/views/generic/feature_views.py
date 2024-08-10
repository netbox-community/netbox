from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.generic import View

from core.models import Job
from core.tables import JobTable
from extras import forms, tables
from extras.models import *
from utilities.permissions import get_permission_for_model
from utilities.views import GetReturnURLMixin, ViewTab
from .base import BaseMultiObjectView

__all__ = (
    'BulkSyncDataView',
    'ObjectChangeLogView',
    'ObjectJobsView',
    'ObjectJournalView',
    'ObjectSyncDataView',
)


class ObjectChangeLogView(View):
    """
    Present a history of changes made to a particular object. The model class must be passed as a keyword argument
    when referencing this view in a URL path. For example:

        path('sites/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='site_changelog', kwargs={'model': Site}),

    Attributes:
        base_template: The name of the template to extend. If not provided, "{app}/{model}.html" will be used.
    """
    base_template = None
    tab = ViewTab(
        label=_('Changelog'),
        permission='extras.view_objectchange',
        weight=10000
    )

    def get(self, request, model, **kwargs):

        # Handle QuerySet restriction of parent object if needed
        if hasattr(model.objects, 'restrict'):
            obj = get_object_or_404(model.objects.restrict(request.user, 'view'), **kwargs)
        else:
            obj = get_object_or_404(model, **kwargs)

        # Gather all changes for this object (and its related objects)
        content_type = ContentType.objects.get_for_model(model)
        objectchanges = ObjectChange.objects.restrict(request.user, 'view').prefetch_related(
            'user', 'changed_object_type'
        ).filter(
            Q(changed_object_type=content_type, changed_object_id=obj.pk) |
            Q(related_object_type=content_type, related_object_id=obj.pk)
        )
        objectchanges_table = tables.ObjectChangeTable(
            data=objectchanges,
            orderable=False,
            user=request.user
        )
        objectchanges_table.configure(request)

        # Default to using "<app>/<model>.html" as the template, if it exists. Otherwise,
        # fall back to using base.html.
        if self.base_template is None:
            self.base_template = f"{model._meta.app_label}/{model._meta.model_name}.html"

        return render(request, 'extras/object_changelog.html', {
            'object': obj,
            'table': objectchanges_table,
            'base_template': self.base_template,
            'tab': self.tab,
        })


class ObjectJournalView(View):
    """
    Show all journal entries for an object. The model class must be passed as a keyword argument when referencing this
    view in a URL path. For example:

        path('sites/<int:pk>/journal/', ObjectJournalView.as_view(), name='site_journal', kwargs={'model': Site}),

    Attributes:
        base_template: The name of the template to extend. If not provided, "{app}/{model}.html" will be used.
    """
    base_template = None
    tab = ViewTab(
        label=_('Journal'),
        badge=lambda obj: obj.journal_entries.count(),
        permission='extras.view_journalentry',
        weight=9000
    )

    def get(self, request, model, **kwargs):

        # Handle QuerySet restriction of parent object if needed
        if hasattr(model.objects, 'restrict'):
            obj = get_object_or_404(model.objects.restrict(request.user, 'view'), **kwargs)
        else:
            obj = get_object_or_404(model, **kwargs)

        # Gather all changes for this object (and its related objects)
        content_type = ContentType.objects.get_for_model(model)
        journalentries = JournalEntry.objects.restrict(request.user, 'view').prefetch_related('created_by').filter(
            assigned_object_type=content_type,
            assigned_object_id=obj.pk
        )
        journalentry_table = tables.JournalEntryTable(journalentries, user=request.user)
        journalentry_table.configure(request)
        journalentry_table.columns.hide('assigned_object_type')
        journalentry_table.columns.hide('assigned_object')

        if request.user.has_perm('extras.add_journalentry'):
            form = forms.JournalEntryForm(
                initial={
                    'assigned_object_type': ContentType.objects.get_for_model(obj),
                    'assigned_object_id': obj.pk
                }
            )
        else:
            form = None

        # Default to using "<app>/<model>.html" as the template, if it exists. Otherwise,
        # fall back to using base.html.
        if self.base_template is None:
            self.base_template = f"{model._meta.app_label}/{model._meta.model_name}.html"

        return render(request, 'extras/object_journal.html', {
            'object': obj,
            'form': form,
            'table': journalentry_table,
            'base_template': self.base_template,
            'tab': self.tab,
        })


class ObjectJobsView(View):
    """
    Render a list of all Job assigned to an object. For example:

        path('data-sources/<int:pk>/jobs/', ObjectJobsView.as_view(), name='datasource_jobs', kwargs={'model': DataSource}),

    Attributes:
        base_template: The name of the template to extend. If not provided, "{app}/{model}.html" will be used.
    """
    base_template = None
    tab = ViewTab(
        label=_('Jobs'),
        badge=lambda obj: obj.jobs.count(),
        permission='core.view_job',
        weight=11000
    )

    def get_object(self, request, **kwargs):
        return get_object_or_404(self.model.objects.restrict(request.user, 'view'), **kwargs)

    def get_jobs(self, instance):
        object_type = ContentType.objects.get_for_model(instance)
        return Job.objects.filter(
            object_type=object_type,
            object_id=instance.id
        )

    def get(self, request, model, **kwargs):
        self.model = model
        obj = self.get_object(request, **kwargs)

        # Gather all Jobs for this object
        jobs = self.get_jobs(obj)
        jobs_table = JobTable(
            data=jobs,
            orderable=False,
            user=request.user
        )
        jobs_table.configure(request)

        # Default to using "<app>/<model>.html" as the template, if it exists. Otherwise,
        # fall back to using base.html.
        if self.base_template is None:
            self.base_template = f"{model._meta.app_label}/{model._meta.model_name}.html"

        return render(request, 'core/object_jobs.html', {
            'object': obj,
            'table': jobs_table,
            'base_template': self.base_template,
            'tab': self.tab,
        })


class ObjectSyncDataView(View):

    def post(self, request, model, **kwargs):
        """
        Synchronize data from the DataFile associated with this object.
        """
        qs = model.objects.all()
        if hasattr(model.objects, 'restrict'):
            qs = qs.restrict(request.user, 'sync')
        obj = get_object_or_404(qs, **kwargs)

        if not obj.data_file:
            messages.error(request, _("Unable to synchronize data: No data file set."))
            return redirect(obj.get_absolute_url())

        obj.sync(save=True)
        messages.success(request, _("Synchronized data for {object_type} {object}.").format(
            object_type=model._meta.verbose_name,
            object=obj
        ))

        return redirect(obj.get_absolute_url())


class BulkSyncDataView(GetReturnURLMixin, BaseMultiObjectView):
    """
    Synchronize multiple instances of a model inheriting from SyncedDataMixin.
    """
    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'sync')

    def post(self, request):
        selected_objects = self.queryset.filter(
            pk__in=request.POST.getlist('pk'),
            data_file__isnull=False
        )

        with transaction.atomic():
            for obj in selected_objects:
                obj.sync(save=True)

            messages.success(request, _("Synced {count} {object_type}").format(
                count=len(selected_objects),
                object_type=self.queryset.model._meta.verbose_name_plural
            ))

        return redirect(self.get_return_url(request))
