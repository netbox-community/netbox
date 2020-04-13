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

# Tenants
router.register('tenant-groups', views.TenantGroupViewSet)
router.register('tenants', views.TenantViewSet)

app_name = 'tenancy-api'
urlpatterns = router.urls
