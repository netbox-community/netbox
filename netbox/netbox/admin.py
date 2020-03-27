from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User


class NetBoxAdminSite(AdminSite):
    """
    Custom admin site
    """
    site_header = 'NetBox Administration'
    site_title = 'NetBox'
    site_url = '/{}'.format(settings.BASE_PATH)
    index_template = 'admin/index.html'


admin_site = NetBoxAdminSite(name='admin')

# Register external models
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
