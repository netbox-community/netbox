from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import View

from core.choices import JobStatusChoices, ManagedFileRootPathChoices
from core.forms import ManagedFileForm
from core.models import Job
from core.tables import JobTable
from extras.dashboard.forms import DashboardWidgetAddForm, DashboardWidgetForm
from extras.dashboard.utils import get_widget_class
from netbox.views import generic
from utilities.forms import ConfirmationForm, get_field_value
from utilities.htmx import is_htmx
from utilities.rqworker import get_workers_for_queue
from utilities.templatetags.builtins.filters import render_markdown
from utilities.utils import copy_safe_request, count_related, get_viewname, normalize_querydict, shallow_compare_dict
from utilities.views import ContentTypePermissionRequiredMixin, register_model_view
from . import filtersets, forms, tables
from .forms.reports import ReportForm
from .models import *
from .reports import run_report
from .scripts import run_script


#
# Custom fields
#

class CustomFieldListView(generic.ObjectListView):
    queryset = CustomField.objects.all()
    filterset = filtersets.CustomFieldFilterSet
    filterset_form = forms.CustomFieldFilterForm
    table = tables.CustomFieldTable


@register_model_view(CustomField)
class CustomFieldView(generic.ObjectView):
    queryset = CustomField.objects.all()


@register_model_view(CustomField, 'edit')
class CustomFieldEditView(generic.ObjectEditView):
    queryset = CustomField.objects.all()
    form = forms.CustomFieldForm


@register_model_view(CustomField, 'delete')
class CustomFieldDeleteView(generic.ObjectDeleteView):
    queryset = CustomField.objects.all()


class CustomFieldBulkImportView(generic.BulkImportView):
    queryset = CustomField.objects.all()
    model_form = forms.CustomFieldImportForm


class CustomFieldBulkEditView(generic.BulkEditView):
    queryset = CustomField.objects.all()
    filterset = filtersets.CustomFieldFilterSet
    table = tables.CustomFieldTable
    form = forms.CustomFieldBulkEditForm


class CustomFieldBulkDeleteView(generic.BulkDeleteView):
    queryset = CustomField.objects.all()
    filterset = filtersets.CustomFieldFilterSet
    table = tables.CustomFieldTable


#
# Custom links
#

class CustomLinkListView(generic.ObjectListView):
    queryset = CustomLink.objects.all()
    filterset = filtersets.CustomLinkFilterSet
    filterset_form = forms.CustomLinkFilterForm
    table = tables.CustomLinkTable


@register_model_view(CustomLink)
class CustomLinkView(generic.ObjectView):
    queryset = CustomLink.objects.all()


@register_model_view(CustomLink, 'edit')
class CustomLinkEditView(generic.ObjectEditView):
    queryset = CustomLink.objects.all()
    form = forms.CustomLinkForm


@register_model_view(CustomLink, 'delete')
class CustomLinkDeleteView(generic.ObjectDeleteView):
    queryset = CustomLink.objects.all()


class CustomLinkBulkImportView(generic.BulkImportView):
    queryset = CustomLink.objects.all()
    model_form = forms.CustomLinkImportForm


class CustomLinkBulkEditView(generic.BulkEditView):
    queryset = CustomLink.objects.all()
    filterset = filtersets.CustomLinkFilterSet
    table = tables.CustomLinkTable
    form = forms.CustomLinkBulkEditForm


class CustomLinkBulkDeleteView(generic.BulkDeleteView):
    queryset = CustomLink.objects.all()
    filterset = filtersets.CustomLinkFilterSet
    table = tables.CustomLinkTable


#
# Export templates
#

class ExportTemplateListView(generic.ObjectListView):
    queryset = ExportTemplate.objects.all()
    filterset = filtersets.ExportTemplateFilterSet
    filterset_form = forms.ExportTemplateFilterForm
    table = tables.ExportTemplateTable
    template_name = 'extras/exporttemplate_list.html'
    actions = ('add', 'import', 'export', 'bulk_edit', 'bulk_delete', 'bulk_sync')


@register_model_view(ExportTemplate)
class ExportTemplateView(generic.ObjectView):
    queryset = ExportTemplate.objects.all()


@register_model_view(ExportTemplate, 'edit')
class ExportTemplateEditView(generic.ObjectEditView):
    queryset = ExportTemplate.objects.all()
    form = forms.ExportTemplateForm


@register_model_view(ExportTemplate, 'delete')
class ExportTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ExportTemplate.objects.all()


class ExportTemplateBulkImportView(generic.BulkImportView):
    queryset = ExportTemplate.objects.all()
    model_form = forms.ExportTemplateImportForm


class ExportTemplateBulkEditView(generic.BulkEditView):
    queryset = ExportTemplate.objects.all()
    filterset = filtersets.ExportTemplateFilterSet
    table = tables.ExportTemplateTable
    form = forms.ExportTemplateBulkEditForm


class ExportTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ExportTemplate.objects.all()
    filterset = filtersets.ExportTemplateFilterSet
    table = tables.ExportTemplateTable


class ExportTemplateBulkSyncDataView(generic.BulkSyncDataView):
    queryset = ExportTemplate.objects.all()


#
# Saved filters
#

class SavedFilterMixin:

    def get_queryset(self, request):
        """
        Return only shared SavedFilters, or those owned by the current user, unless
        this is a superuser.
        """
        queryset = SavedFilter.objects.all()
        user = request.user
        if user.is_superuser:
            return queryset
        if user.is_anonymous:
            return queryset.filter(shared=True)
        return queryset.filter(
            Q(shared=True) | Q(user=user)
        )


class SavedFilterListView(SavedFilterMixin, generic.ObjectListView):
    filterset = filtersets.SavedFilterFilterSet
    filterset_form = forms.SavedFilterFilterForm
    table = tables.SavedFilterTable


@register_model_view(SavedFilter)
class SavedFilterView(SavedFilterMixin, generic.ObjectView):
    queryset = SavedFilter.objects.all()


@register_model_view(SavedFilter, 'edit')
class SavedFilterEditView(SavedFilterMixin, generic.ObjectEditView):
    queryset = SavedFilter.objects.all()
    form = forms.SavedFilterForm

    def alter_object(self, obj, request, url_args, url_kwargs):
        if not obj.pk:
            obj.user = request.user
        return obj


@register_model_view(SavedFilter, 'delete')
class SavedFilterDeleteView(SavedFilterMixin, generic.ObjectDeleteView):
    queryset = SavedFilter.objects.all()


class SavedFilterBulkImportView(SavedFilterMixin, generic.BulkImportView):
    queryset = SavedFilter.objects.all()
    model_form = forms.SavedFilterImportForm


class SavedFilterBulkEditView(SavedFilterMixin, generic.BulkEditView):
    queryset = SavedFilter.objects.all()
    filterset = filtersets.SavedFilterFilterSet
    table = tables.SavedFilterTable
    form = forms.SavedFilterBulkEditForm


class SavedFilterBulkDeleteView(SavedFilterMixin, generic.BulkDeleteView):
    queryset = SavedFilter.objects.all()
    filterset = filtersets.SavedFilterFilterSet
    table = tables.SavedFilterTable


#
# Webhooks
#

class WebhookListView(generic.ObjectListView):
    queryset = Webhook.objects.all()
    filterset = filtersets.WebhookFilterSet
    filterset_form = forms.WebhookFilterForm
    table = tables.WebhookTable


@register_model_view(Webhook)
class WebhookView(generic.ObjectView):
    queryset = Webhook.objects.all()


@register_model_view(Webhook, 'edit')
class WebhookEditView(generic.ObjectEditView):
    queryset = Webhook.objects.all()
    form = forms.WebhookForm


@register_model_view(Webhook, 'delete')
class WebhookDeleteView(generic.ObjectDeleteView):
    queryset = Webhook.objects.all()


class WebhookBulkImportView(generic.BulkImportView):
    queryset = Webhook.objects.all()
    model_form = forms.WebhookImportForm


class WebhookBulkEditView(generic.BulkEditView):
    queryset = Webhook.objects.all()
    filterset = filtersets.WebhookFilterSet
    table = tables.WebhookTable
    form = forms.WebhookBulkEditForm


class WebhookBulkDeleteView(generic.BulkDeleteView):
    queryset = Webhook.objects.all()
    filterset = filtersets.WebhookFilterSet
    table = tables.WebhookTable


#
# Tags
#

class TagListView(generic.ObjectListView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    filterset = filtersets.TagFilterSet
    filterset_form = forms.TagFilterForm
    table = tables.TagTable


@register_model_view(Tag)
class TagView(generic.ObjectView):
    queryset = Tag.objects.all()

    def get_extra_context(self, request, instance):
        tagged_items = TaggedItem.objects.filter(tag=instance)
        taggeditem_table = tables.TaggedItemTable(
            data=tagged_items,
            orderable=False
        )
        taggeditem_table.configure(request)

        object_types = [
            {
                'content_type': ContentType.objects.get(pk=ti['content_type']),
                'item_count': ti['item_count']
            } for ti in tagged_items.values('content_type').annotate(item_count=Count('pk'))
        ]

        return {
            'taggeditem_table': taggeditem_table,
            'tagged_item_count': tagged_items.count(),
            'object_types': object_types,
        }


@register_model_view(Tag, 'edit')
class TagEditView(generic.ObjectEditView):
    queryset = Tag.objects.all()
    form = forms.TagForm


@register_model_view(Tag, 'delete')
class TagDeleteView(generic.ObjectDeleteView):
    queryset = Tag.objects.all()


class TagBulkImportView(generic.BulkImportView):
    queryset = Tag.objects.all()
    model_form = forms.TagImportForm


class TagBulkEditView(generic.BulkEditView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    table = tables.TagTable
    form = forms.TagBulkEditForm


class TagBulkDeleteView(generic.BulkDeleteView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    table = tables.TagTable


#
# Config contexts
#

class ConfigContextListView(generic.ObjectListView):
    queryset = ConfigContext.objects.all()
    filterset = filtersets.ConfigContextFilterSet
    filterset_form = forms.ConfigContextFilterForm
    table = tables.ConfigContextTable
    template_name = 'extras/configcontext_list.html'
    actions = ('add', 'bulk_edit', 'bulk_delete', 'bulk_sync')


@register_model_view(ConfigContext)
class ConfigContextView(generic.ObjectView):
    queryset = ConfigContext.objects.all()

    def get_extra_context(self, request, instance):
        # Gather assigned objects for parsing in the template
        assigned_objects = (
            ('Regions', instance.regions.all),
            ('Site Groups', instance.site_groups.all),
            ('Sites', instance.sites.all),
            ('Locations', instance.locations.all),
            ('Device Types', instance.device_types.all),
            ('Roles', instance.roles.all),
            ('Platforms', instance.platforms.all),
            ('Cluster Types', instance.cluster_types.all),
            ('Cluster Groups', instance.cluster_groups.all),
            ('Clusters', instance.clusters.all),
            ('Tenant Groups', instance.tenant_groups.all),
            ('Tenants', instance.tenants.all),
            ('Tags', instance.tags.all),
        )

        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('data_format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('data_format', 'json')
        else:
            format = 'json'

        return {
            'assigned_objects': assigned_objects,
            'format': format,
        }


@register_model_view(ConfigContext, 'edit')
class ConfigContextEditView(generic.ObjectEditView):
    queryset = ConfigContext.objects.all()
    form = forms.ConfigContextForm


class ConfigContextBulkEditView(generic.BulkEditView):
    queryset = ConfigContext.objects.all()
    filterset = filtersets.ConfigContextFilterSet
    table = tables.ConfigContextTable
    form = forms.ConfigContextBulkEditForm


@register_model_view(ConfigContext, 'delete')
class ConfigContextDeleteView(generic.ObjectDeleteView):
    queryset = ConfigContext.objects.all()


class ConfigContextBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigContext.objects.all()
    filterset = filtersets.ConfigContextFilterSet
    table = tables.ConfigContextTable


class ConfigContextBulkSyncDataView(generic.BulkSyncDataView):
    queryset = ConfigContext.objects.all()


class ObjectConfigContextView(generic.ObjectView):
    base_template = None
    template_name = 'extras/object_configcontext.html'

    def get_extra_context(self, request, instance):
        source_contexts = ConfigContext.objects.restrict(request.user, 'view').get_for_object(instance)

        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('data_format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('data_format', 'json')
        else:
            format = 'json'

        return {
            'rendered_context': instance.get_config_context(),
            'source_contexts': source_contexts,
            'format': format,
            'base_template': self.base_template,
        }


#
# Config templates
#

class ConfigTemplateListView(generic.ObjectListView):
    queryset = ConfigTemplate.objects.all()
    filterset = filtersets.ConfigTemplateFilterSet
    filterset_form = forms.ConfigTemplateFilterForm
    table = tables.ConfigTemplateTable
    template_name = 'extras/configtemplate_list.html'
    actions = ('add', 'import', 'export', 'bulk_edit', 'bulk_delete', 'bulk_sync')


@register_model_view(ConfigTemplate)
class ConfigTemplateView(generic.ObjectView):
    queryset = ConfigTemplate.objects.all()


@register_model_view(ConfigTemplate, 'edit')
class ConfigTemplateEditView(generic.ObjectEditView):
    queryset = ConfigTemplate.objects.all()
    form = forms.ConfigTemplateForm


@register_model_view(ConfigTemplate, 'delete')
class ConfigTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ConfigTemplate.objects.all()


class ConfigTemplateBulkImportView(generic.BulkImportView):
    queryset = ConfigTemplate.objects.all()
    model_form = forms.ConfigTemplateImportForm


class ConfigTemplateBulkEditView(generic.BulkEditView):
    queryset = ConfigTemplate.objects.all()
    filterset = filtersets.ConfigTemplateFilterSet
    table = tables.ConfigTemplateTable
    form = forms.ConfigTemplateBulkEditForm


class ConfigTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigTemplate.objects.all()
    filterset = filtersets.ConfigTemplateFilterSet
    table = tables.ConfigTemplateTable


class ConfigTemplateBulkSyncDataView(generic.BulkSyncDataView):
    queryset = ConfigTemplate.objects.all()


#
# Change logging
#

class ObjectChangeListView(generic.ObjectListView):
    queryset = ObjectChange.objects.all()
    filterset = filtersets.ObjectChangeFilterSet
    filterset_form = forms.ObjectChangeFilterForm
    table = tables.ObjectChangeTable
    template_name = 'extras/objectchange_list.html'
    actions = ('export',)


@register_model_view(ObjectChange)
class ObjectChangeView(generic.ObjectView):
    queryset = ObjectChange.objects.all()

    def get_extra_context(self, request, instance):
        related_changes = ObjectChange.objects.restrict(request.user, 'view').filter(
            request_id=instance.request_id
        ).exclude(
            pk=instance.pk
        )
        related_changes_table = tables.ObjectChangeTable(
            data=related_changes[:50],
            orderable=False
        )

        objectchanges = ObjectChange.objects.restrict(request.user, 'view').filter(
            changed_object_type=instance.changed_object_type,
            changed_object_id=instance.changed_object_id,
        )

        next_change = objectchanges.filter(time__gt=instance.time).order_by('time').first()
        prev_change = objectchanges.filter(time__lt=instance.time).order_by('-time').first()

        if not instance.prechange_data and instance.action in ['update', 'delete'] and prev_change:
            non_atomic_change = True
            prechange_data = prev_change.postchange_data
        else:
            non_atomic_change = False
            prechange_data = instance.prechange_data

        if prechange_data and instance.postchange_data:
            diff_added = shallow_compare_dict(
                prechange_data or dict(),
                instance.postchange_data or dict(),
                exclude=['last_updated'],
            )
            diff_removed = {
                x: prechange_data.get(x) for x in diff_added
            } if prechange_data else {}
        else:
            diff_added = None
            diff_removed = None

        return {
            'diff_added': diff_added,
            'diff_removed': diff_removed,
            'next_change': next_change,
            'prev_change': prev_change,
            'related_changes_table': related_changes_table,
            'related_changes_count': related_changes.count(),
            'non_atomic_change': non_atomic_change
        }


#
# Image attachments
#

@register_model_view(ImageAttachment, 'edit')
class ImageAttachmentEditView(generic.ObjectEditView):
    queryset = ImageAttachment.objects.all()
    form = forms.ImageAttachmentForm
    template_name = 'extras/imageattachment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the parent object based on URL kwargs
            content_type = get_object_or_404(ContentType, pk=request.GET.get('content_type'))
            instance.parent = get_object_or_404(content_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def get_return_url(self, request, obj=None):
        return obj.parent.get_absolute_url() if obj else super().get_return_url(request)

    def get_extra_addanother_params(self, request):
        return {
            'content_type': request.GET.get('content_type'),
            'object_id': request.GET.get('object_id'),
        }


@register_model_view(ImageAttachment, 'delete')
class ImageAttachmentDeleteView(generic.ObjectDeleteView):
    queryset = ImageAttachment.objects.all()

    def get_return_url(self, request, obj=None):
        return obj.parent.get_absolute_url() if obj else super().get_return_url(request)


#
# Journal entries
#

class JournalEntryListView(generic.ObjectListView):
    queryset = JournalEntry.objects.all()
    filterset = filtersets.JournalEntryFilterSet
    filterset_form = forms.JournalEntryFilterForm
    table = tables.JournalEntryTable
    actions = ('export', 'bulk_edit', 'bulk_delete')


@register_model_view(JournalEntry)
class JournalEntryView(generic.ObjectView):
    queryset = JournalEntry.objects.all()


@register_model_view(JournalEntry, 'edit')
class JournalEntryEditView(generic.ObjectEditView):
    queryset = JournalEntry.objects.all()
    form = forms.JournalEntryForm

    def alter_object(self, obj, request, args, kwargs):
        if not obj.pk:
            obj.created_by = request.user
        return obj

    def get_return_url(self, request, instance):
        if not instance.assigned_object:
            return reverse('extras:journalentry_list')
        obj = instance.assigned_object
        viewname = get_viewname(obj, 'journal')
        return reverse(viewname, kwargs={'pk': obj.pk})


@register_model_view(JournalEntry, 'delete')
class JournalEntryDeleteView(generic.ObjectDeleteView):
    queryset = JournalEntry.objects.all()

    def get_return_url(self, request, instance):
        obj = instance.assigned_object
        viewname = get_viewname(obj, 'journal')
        return reverse(viewname, kwargs={'pk': obj.pk})


class JournalEntryBulkEditView(generic.BulkEditView):
    queryset = JournalEntry.objects.all()
    filterset = filtersets.JournalEntryFilterSet
    table = tables.JournalEntryTable
    form = forms.JournalEntryBulkEditForm


class JournalEntryBulkDeleteView(generic.BulkDeleteView):
    queryset = JournalEntry.objects.all()
    filterset = filtersets.JournalEntryFilterSet
    table = tables.JournalEntryTable


#
# Dashboard & widgets
#

class DashboardResetView(LoginRequiredMixin, View):
    template_name = 'extras/dashboard/reset.html'

    def get(self, request):
        get_object_or_404(Dashboard.objects.all(), user=request.user)
        form = ConfirmationForm()

        return render(request, self.template_name, {
            'form': form,
            'return_url': reverse('home'),
        })

    def post(self, request):
        dashboard = get_object_or_404(Dashboard.objects.all(), user=request.user)
        form = ConfirmationForm(request.POST)

        if form.is_valid():
            dashboard.delete()
            messages.success(request, _("Your dashboard has been reset."))
            return redirect(reverse('home'))

        return render(request, self.template_name, {
            'form': form,
            'return_url': reverse('home'),
        })


class DashboardWidgetAddView(LoginRequiredMixin, View):
    template_name = 'extras/dashboard/widget_add.html'

    def get(self, request):
        if not is_htmx(request):
            return redirect('home')

        initial = request.GET or {
            'widget_class': 'extras.NoteWidget',
        }
        widget_form = DashboardWidgetAddForm(initial=initial)
        widget_name = get_field_value(widget_form, 'widget_class')
        widget_class = get_widget_class(widget_name)
        config_form = widget_class.ConfigForm(initial=widget_class.default_config, prefix='config')

        return render(request, self.template_name, {
            'widget_class': widget_class,
            'widget_form': widget_form,
            'config_form': config_form,
        })

    def post(self, request):
        widget_form = DashboardWidgetAddForm(request.POST)
        config_form = None
        widget_class = None

        if widget_form.is_valid():
            widget_class = get_widget_class(widget_form.cleaned_data['widget_class'])
            config_form = widget_class.ConfigForm(request.POST, prefix='config')

            if config_form.is_valid():
                data = widget_form.cleaned_data
                data.pop('widget_class')
                data['config'] = config_form.cleaned_data
                widget = widget_class(**data)
                request.user.dashboard.add_widget(widget)
                request.user.dashboard.save()
                messages.success(request, f'Added widget {widget.id}')

                return HttpResponse(headers={
                    'HX-Redirect': reverse('home'),
                })

        return render(request, self.template_name, {
            'widget_class': widget_class,
            'widget_form': widget_form,
            'config_form': config_form,
        })


class DashboardWidgetConfigView(LoginRequiredMixin, View):
    template_name = 'extras/dashboard/widget_config.html'

    def get(self, request, id):
        if not is_htmx(request):
            return redirect('home')

        widget = request.user.dashboard.get_widget(id)
        widget_form = DashboardWidgetForm(initial=widget.form_data)
        config_form = widget.ConfigForm(initial=widget.form_data.get('config'), prefix='config')

        return render(request, self.template_name, {
            'widget_class': widget.__class__,
            'widget_form': widget_form,
            'config_form': config_form,
            'form_url': reverse('extras:dashboardwidget_config', kwargs={'id': id})
        })

    def post(self, request, id):
        widget = request.user.dashboard.get_widget(id)
        widget_form = DashboardWidgetForm(request.POST)
        config_form = widget.ConfigForm(request.POST, prefix='config')

        if widget_form.is_valid() and config_form.is_valid():
            data = widget_form.cleaned_data
            data['config'] = config_form.cleaned_data
            request.user.dashboard.config[str(id)].update(data)
            request.user.dashboard.save()
            messages.success(request, f'Updated widget {widget.id}')

            return HttpResponse(headers={
                'HX-Redirect': reverse('home'),
            })

        return render(request, self.template_name, {
            'widget_form': widget_form,
            'config_form': config_form,
            'form_url': reverse('extras:dashboardwidget_config', kwargs={'id': id})
        })


class DashboardWidgetDeleteView(LoginRequiredMixin, View):
    template_name = 'generic/object_delete.html'

    def get(self, request, id):
        if not is_htmx(request):
            return redirect('home')

        widget = request.user.dashboard.get_widget(id)
        form = ConfirmationForm(initial=request.GET)

        return render(request, 'htmx/delete_form.html', {
            'object_type': widget.__class__.__name__,
            'object': widget,
            'form': form,
            'form_url': reverse('extras:dashboardwidget_delete', kwargs={'id': id})
        })

    def post(self, request, id):
        form = ConfirmationForm(request.POST)

        if form.is_valid():
            request.user.dashboard.delete_widget(id)
            request.user.dashboard.save()
            messages.success(request, f'Deleted widget {id}')
        else:
            messages.error(request, f'Error deleting widget: {form.errors[0]}')

        return redirect(reverse('home'))


#
# Reports
#

@register_model_view(ReportModule, 'edit')
class ReportModuleCreateView(generic.ObjectEditView):
    queryset = ReportModule.objects.all()
    form = ManagedFileForm

    def alter_object(self, obj, *args, **kwargs):
        obj.file_root = ManagedFileRootPathChoices.REPORTS
        return obj


@register_model_view(ReportModule, 'delete')
class ReportModuleDeleteView(generic.ObjectDeleteView):
    queryset = ReportModule.objects.all()
    default_return_url = 'extras:report_list'


class ReportListView(ContentTypePermissionRequiredMixin, View):
    """
    Retrieve all the available reports from disk and the recorded Job (if any) for each.
    """
    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request):
        report_modules = ReportModule.objects.restrict(request.user)

        return render(request, 'extras/report_list.html', {
            'model': ReportModule,
            'report_modules': report_modules,
        })


class ReportView(ContentTypePermissionRequiredMixin, View):
    """
    Display a single Report and its associated Job (if any).
    """
    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request, module, name):
        module = get_object_or_404(ReportModule.objects.restrict(request.user), file_path__startswith=module)
        report = module.reports[name]()

        object_type = ContentType.objects.get(app_label='extras', model='reportmodule')
        report.result = Job.objects.filter(
            object_type=object_type,
            object_id=module.pk,
            name=report.name,
            status__in=JobStatusChoices.TERMINAL_STATE_CHOICES
        ).first()

        return render(request, 'extras/report.html', {
            'module': module,
            'report': report,
            'form': ReportForm(scheduling_enabled=report.scheduling_enabled),
        })

    def post(self, request, module, name):
        if not request.user.has_perm('extras.run_report'):
            return HttpResponseForbidden()

        module = get_object_or_404(ReportModule.objects.restrict(request.user), file_path__startswith=module)
        report = module.reports[name]()
        form = ReportForm(request.POST, scheduling_enabled=report.scheduling_enabled)

        if form.is_valid():

            # Allow execution only if RQ worker process is running
            if not get_workers_for_queue('default'):
                messages.error(request, "Unable to run report: RQ worker process not running.")
                return render(request, 'extras/report.html', {
                    'report': report,
                })

            # Run the Report. A new Job is created.
            job = Job.enqueue(
                run_report,
                instance=module,
                name=report.class_name,
                user=request.user,
                schedule_at=form.cleaned_data.get('schedule_at'),
                interval=form.cleaned_data.get('interval'),
                job_timeout=report.job_timeout
            )

            return redirect('extras:report_result', job_pk=job.pk)

        return render(request, 'extras/report.html', {
            'module': module,
            'report': report,
            'form': form,
        })


class ReportSourceView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request, module, name):
        module = get_object_or_404(ReportModule.objects.restrict(request.user), file_path__startswith=module)
        report = module.reports[name]()

        return render(request, 'extras/report/source.html', {
            'module': module,
            'report': report,
            'tab': 'source',
        })


class ReportJobsView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request, module, name):
        module = get_object_or_404(ReportModule.objects.restrict(request.user), file_path__startswith=module)
        report = module.reports[name]()

        object_type = ContentType.objects.get(app_label='extras', model='reportmodule')
        jobs = Job.objects.filter(
            object_type=object_type,
            object_id=module.pk,
            name=report.name
        )

        jobs_table = JobTable(
            data=jobs,
            orderable=False,
            user=request.user
        )
        jobs_table.configure(request)

        return render(request, 'extras/report/jobs.html', {
            'module': module,
            'report': report,
            'table': jobs_table,
            'tab': 'jobs',
        })


class ReportResultView(ContentTypePermissionRequiredMixin, View):
    """
    Display a Job pertaining to the execution of a Report.
    """
    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request, job_pk):
        object_type = ContentType.objects.get_by_natural_key(app_label='extras', model='reportmodule')
        job = get_object_or_404(Job.objects.all(), pk=job_pk, object_type=object_type)

        module = job.object
        report = module.reports[job.name]

        # If this is an HTMX request, return only the result HTML
        if is_htmx(request):
            response = render(request, 'extras/htmx/report_result.html', {
                'report': report,
                'job': job,
            })
            if job.completed or not job.started:
                response.status_code = 286
            return response

        return render(request, 'extras/report_result.html', {
            'report': report,
            'job': job,
        })


#
# Scripts
#

@register_model_view(ScriptModule, 'edit')
class ScriptModuleCreateView(generic.ObjectEditView):
    queryset = ScriptModule.objects.all()
    form = ManagedFileForm

    def alter_object(self, obj, *args, **kwargs):
        obj.file_root = ManagedFileRootPathChoices.SCRIPTS
        return obj


@register_model_view(ScriptModule, 'delete')
class ScriptModuleDeleteView(generic.ObjectDeleteView):
    queryset = ScriptModule.objects.all()
    default_return_url = 'extras:script_list'


class ScriptListView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request):
        script_modules = ScriptModule.objects.restrict(request.user)

        return render(request, 'extras/script_list.html', {
            'model': ScriptModule,
            'script_modules': script_modules,
        })


class ScriptView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request, module, name):
        print(module)
        module = get_object_or_404(ScriptModule.objects.restrict(request.user), file_path__startswith=module)
        script = module.scripts[name]()
        form = script.as_form(initial=normalize_querydict(request.GET))

        # Look for a pending Job (use the latest one by creation timestamp)
        object_type = ContentType.objects.get(app_label='extras', model='scriptmodule')
        script.result = Job.objects.filter(
            object_type=object_type,
            object_id=module.pk,
            name=script.name,
        ).exclude(
            status__in=JobStatusChoices.TERMINAL_STATE_CHOICES
        ).first()

        return render(request, 'extras/script.html', {
            'module': module,
            'script': script,
            'form': form,
        })

    def post(self, request, module, name):
        if not request.user.has_perm('extras.run_script'):
            return HttpResponseForbidden()

        module = get_object_or_404(ScriptModule.objects.restrict(request.user), file_path__startswith=module)
        script = module.scripts[name]()
        form = script.as_form(request.POST, request.FILES)

        # Allow execution only if RQ worker process is running
        if not get_workers_for_queue('default'):
            messages.error(request, "Unable to run script: RQ worker process not running.")

        elif form.is_valid():
            job = Job.enqueue(
                run_script,
                instance=module,
                name=script.class_name,
                user=request.user,
                schedule_at=form.cleaned_data.pop('_schedule_at'),
                interval=form.cleaned_data.pop('_interval'),
                data=form.cleaned_data,
                request=copy_safe_request(request),
                job_timeout=script.job_timeout,
                commit=form.cleaned_data.pop('_commit')
            )

            return redirect('extras:script_result', job_pk=job.pk)

        return render(request, 'extras/script.html', {
            'module': module,
            'script': script,
            'form': form,
        })


class ScriptSourceView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request, module, name):
        module = get_object_or_404(ScriptModule.objects.restrict(request.user), file_path__startswith=module)
        script = module.scripts[name]()

        return render(request, 'extras/script/source.html', {
            'module': module,
            'script': script,
            'tab': 'source',
        })


class ScriptJobsView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request, module, name):
        module = get_object_or_404(ScriptModule.objects.restrict(request.user), file_path__startswith=module)
        script = module.scripts[name]()

        object_type = ContentType.objects.get(app_label='extras', model='scriptmodule')
        jobs = Job.objects.filter(
            object_type=object_type,
            object_id=module.pk,
            name=script.class_name
        )

        jobs_table = JobTable(
            data=jobs,
            orderable=False,
            user=request.user
        )
        jobs_table.configure(request)

        return render(request, 'extras/script/jobs.html', {
            'module': module,
            'script': script,
            'table': jobs_table,
            'tab': 'jobs',
        })


class ScriptResultView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request, job_pk):
        object_type = ContentType.objects.get_by_natural_key(app_label='extras', model='scriptmodule')
        job = get_object_or_404(Job.objects.all(), pk=job_pk, object_type=object_type)

        module = job.object
        script = module.scripts[job.name]()

        # If this is an HTMX request, return only the result HTML
        if is_htmx(request):
            response = render(request, 'extras/htmx/script_result.html', {
                'script': script,
                'job': job,
            })
            if job.completed or not job.started:
                response.status_code = 286
            return response

        return render(request, 'extras/script_result.html', {
            'script': script,
            'job': job,
        })


#
# Markdown
#

class RenderMarkdownView(View):

    def post(self, request):
        form = forms.RenderMarkdownForm(request.POST)
        if not form.is_valid():
            HttpResponseBadRequest()
        rendered = render_markdown(form.cleaned_data['text'])

        return HttpResponse(rendered)
