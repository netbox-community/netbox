from django.contrib import admin

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
    list_display = ('id', 'is_active', 'created', 'comment')
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
