from __future__ import unicode_literals

from rest_framework import routers

from . import views


class TenancyRootView(routers.APIRootView):
    """
    Tenancy API root view
    """
    def get_view_name(self):
        return 'Tenancy'


router = routers.DefaultRouter()
router.APIRootView = TenancyRootView

# Field choices
router.register(r'_choices', views.TenancyFieldChoicesViewSet, base_name='field-choice')

# Tenants
router.register(r'tenant-groups', views.TenantGroupViewSet)
router.register(r'tenants', views.TenantViewSet)

app_name = 'tenancy-api'
urlpatterns = router.urls
