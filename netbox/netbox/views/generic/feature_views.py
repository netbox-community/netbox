from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from extras import forms, tables
from extras.models import *

__all__ = (
    'ObjectChangeLogView',
    'ObjectJournalView',
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
            'active_tab': 'changelog',
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
        journalentry_table = tables.ObjectJournalTable(journalentries)
        journalentry_table.configure(request)

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
            'active_tab': 'journal',
        })
