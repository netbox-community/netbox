from rest_framework import routers

from . import views


router = routers.DefaultRouter()

# Tenants
router.register(r'tenant-groups', views.TenantGroupViewSet)
router.register(r'tenants', views.TenantViewSet)

urlpatterns = router.urls
