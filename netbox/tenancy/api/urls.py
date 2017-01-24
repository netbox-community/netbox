from django.conf.urls import url

from .views import *


urlpatterns = [

    # Tenant groups
    url(r'^tenant-groups/$', TenantGroupViewSet.as_view({'get': 'list'}), name='tenantgroup_list'),
    url(r'^tenant-groups/(?P<pk>\d+)/$', TenantGroupViewSet.as_view({'get': 'retrieve'}), name='tenantgroup_detail'),

    # Tenants
    url(r'^tenants/$', TenantViewSet.as_view({'get': 'list'}), name='tenant_list'),
    url(r'^tenants/(?P<pk>\d+)/$', TenantViewSet.as_view({'get': 'retrieve'}), name='tenant_detail'),

]
