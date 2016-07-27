from django.conf.urls import url

from .views import *


urlpatterns = [

    # Tenant groups
    url(r'^tenant-groups/$', TenantGroupListView.as_view(), name='tenantgroup_list'),
    url(r'^tenant-groups/(?P<pk>\d+)/$', TenantGroupDetailView.as_view(), name='tenantgroup_detail'),

    # Tenants
    url(r'^tenants/$', TenantListView.as_view(), name='tenant_list'),
    url(r'^tenants/(?P<pk>\d+)/$', TenantDetailView.as_view(), name='tenant_detail'),

]
