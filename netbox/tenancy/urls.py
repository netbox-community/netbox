from __future__ import unicode_literals

from django.conf.urls import url

from extras.views import ObjectChangeLogView
from . import views
from .models import Tenant, TenantGroup

app_name = 'tenancy'
urlpatterns = [

    # Tenant groups
    url(r'^tenant-groups/$', views.TenantGroupListView.as_view(), name='tenantgroup_list'),
    url(r'^tenant-groups/add/$', views.TenantGroupCreateView.as_view(), name='tenantgroup_add'),
    url(r'^tenant-groups/import/$', views.TenantGroupBulkImportView.as_view(), name='tenantgroup_import'),
    url(r'^tenant-groups/delete/$', views.TenantGroupBulkDeleteView.as_view(), name='tenantgroup_bulk_delete'),
    url(r'^tenant-groups/(?P<slug>[\w-]+)/edit/$', views.TenantGroupEditView.as_view(), name='tenantgroup_edit'),
    url(r'^tenant-groups/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='tenantgroup_changelog', kwargs={'model': TenantGroup}),

    # Tenants
    url(r'^tenants/$', views.TenantListView.as_view(), name='tenant_list'),
    url(r'^tenants/add/$', views.TenantCreateView.as_view(), name='tenant_add'),
    url(r'^tenants/import/$', views.TenantBulkImportView.as_view(), name='tenant_import'),
    url(r'^tenants/edit/$', views.TenantBulkEditView.as_view(), name='tenant_bulk_edit'),
    url(r'^tenants/delete/$', views.TenantBulkDeleteView.as_view(), name='tenant_bulk_delete'),
    url(r'^tenants/(?P<slug>[\w-]+)/$', views.TenantView.as_view(), name='tenant'),
    url(r'^tenants/(?P<slug>[\w-]+)/edit/$', views.TenantEditView.as_view(), name='tenant_edit'),
    url(r'^tenants/(?P<slug>[\w-]+)/delete/$', views.TenantDeleteView.as_view(), name='tenant_delete'),
    url(r'^tenants/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='tenant_changelog', kwargs={'model': Tenant}),

]
