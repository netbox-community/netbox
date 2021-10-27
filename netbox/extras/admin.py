from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from netbox.config import get_config, PARAMS
from .forms import ConfigRevisionForm
from .models import ConfigRevision, JobResult


@admin.register(ConfigRevision)
class ConfigRevisionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Rack Elevations', {
            'fields': ('RACK_ELEVATION_DEFAULT_UNIT_HEIGHT', 'RACK_ELEVATION_DEFAULT_UNIT_WIDTH'),
        }),
        ('IPAM', {
            'fields': ('ENFORCE_GLOBAL_UNIQUE', 'PREFER_IPV4'),
        }),
        ('Security', {
            'fields': ('ALLOWED_URL_SCHEMES',),
        }),
        ('Banners', {
            'fields': ('BANNER_LOGIN', 'BANNER_TOP', 'BANNER_BOTTOM'),
        }),
        ('Pagination', {
            'fields': ('PAGINATE_COUNT', 'MAX_PAGE_SIZE'),
        }),
        ('NAPALM', {
            'fields': ('NAPALM_USERNAME', 'NAPALM_PASSWORD', 'NAPALM_TIMEOUT', 'NAPALM_ARGS'),
        }),
        ('Miscellaneous', {
            'fields': ('MAINTENANCE_MODE', 'MAPS_URL'),
        }),
        ('Config Revision', {
            'fields': ('comment',),
        })
    ]
    form = ConfigRevisionForm
    list_display = ('id', 'is_active', 'created', 'comment', 'restore_link')
    ordering = ('-id',)
    readonly_fields = ('data',)

    def get_changeform_initial_data(self, request):
        """
        Populate initial form data from the most recent ConfigRevision.
        """
        latest_revision = ConfigRevision.objects.last()
        initial = latest_revision.data if latest_revision else {}
        initial.update(super().get_changeform_initial_data(request))

        return initial

    # Permissions

    def has_add_permission(self, request):
        # Only superusers may modify the configuration.
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # ConfigRevisions cannot be modified once created.
        return False

    def has_delete_permission(self, request, obj=None):
        # Only inactive ConfigRevisions may be deleted (must be superuser).
        return request.user.is_superuser and (
            obj is None or not obj.is_active()
        )

    # List display methods

    def restore_link(self, obj):
        if obj.is_active():
            return ''
        return format_html(
            '<a href="{url}" class="button">Restore</a>',
            url=reverse('admin:extras_configrevision_restore', args=(obj.pk,))
        )
    restore_link.short_description = "Actions"

    # URLs

    def get_urls(self):
        urls = [
            path('<int:pk>/restore/', self.admin_site.admin_view(self.restore), name='extras_configrevision_restore'),
        ]

        return urls + super().get_urls()

    # Views

    def restore(self, request, pk):
        # Get the ConfigRevision being restored
        candidate_config = get_object_or_404(ConfigRevision, pk=pk)

        if request.method == 'POST':
            candidate_config.activate()
            self.message_user(request, f"Restored configuration revision #{pk}")

            return redirect(reverse('admin:extras_configrevision_changelist'))

        # Get the current ConfigRevision
        config_version = get_config().version
        current_config = ConfigRevision.objects.filter(pk=config_version).first()

        params = []
        for param in PARAMS:
            params.append((
                param.name,
                current_config.data.get(param.name, None),
                candidate_config.data.get(param.name, None)
            ))

        context = self.admin_site.each_context(request)
        context.update({
            'object': candidate_config,
            'params': params,
        })

        return TemplateResponse(request, 'admin/extras/configrevision/restore.html', context)


#
# Reports & scripts
#

@admin.register(JobResult)
class JobResultAdmin(admin.ModelAdmin):
    list_display = [
        'obj_type', 'name', 'created', 'completed', 'user', 'status',
    ]
    fields = [
        'obj_type', 'name', 'created', 'completed', 'user', 'status', 'data', 'job_id'
    ]
    list_filter = [
        'status',
    ]
    readonly_fields = fields

    def has_add_permission(self, request):
        return False
