from django.conf.urls import include, url

from rest_framework import routers

from views import TenantViewSet, TenantGroupViewSet


router = routers.DefaultRouter()
router.register(r'tenant-groups', TenantGroupViewSet)
router.register(r'tenants', TenantViewSet)

urlpatterns = [

    url(r'', include(router.urls)),

]
