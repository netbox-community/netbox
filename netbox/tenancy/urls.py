from django.urls import path

from extras.views import ObjectChangeLogView
from . import views
from .models import Tenant, TenantGroup

app_name = 'tenancy'
urlpatterns = [

    # Tenant groups
    path(r'tenant-groups/', views.TenantGroupListView.as_view(), name='tenantgroup_list'),
    path(r'tenant-groups/add/', views.TenantGroupCreateView.as_view(), name='tenantgroup_add'),
    path(r'tenant-groups/import/', views.TenantGroupBulkImportView.as_view(), name='tenantgroup_import'),
    path(r'tenant-groups/delete/', views.TenantGroupBulkDeleteView.as_view(), name='tenantgroup_bulk_delete'),
    path(r'tenant-groups/<slug:slug>/edit/', views.TenantGroupEditView.as_view(), name='tenantgroup_edit'),
    path(r'tenant-groups/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='tenantgroup_changelog', kwargs={'model': TenantGroup}),

    # Tenants
    path(r'tenants/', views.TenantListView.as_view(), name='tenant_list'),
    path(r'tenants/add/', views.TenantCreateView.as_view(), name='tenant_add'),
    path(r'tenants/import/', views.TenantBulkImportView.as_view(), name='tenant_import'),
    path(r'tenants/edit/', views.TenantBulkEditView.as_view(), name='tenant_bulk_edit'),
    path(r'tenants/delete/', views.TenantBulkDeleteView.as_view(), name='tenant_bulk_delete'),
    path(r'tenants/<slug:slug>/', views.TenantView.as_view(), name='tenant'),
    path(r'tenants/<slug:slug>/edit/', views.TenantEditView.as_view(), name='tenant_edit'),
    path(r'tenants/<slug:slug>/delete/', views.TenantDeleteView.as_view(), name='tenant_delete'),
    path(r'tenants/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='tenant_changelog', kwargs={'model': Tenant}),

]
