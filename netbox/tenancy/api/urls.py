from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'tenant-groups', views.TenantGroupViewSet)
router.register(r'tenants', views.TenantViewSet)
