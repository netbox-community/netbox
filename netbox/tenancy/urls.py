from django.urls import path

from extras.views import ObjectChangeLogView
from . import views
from .models import Tenant, TenantGroup

app_name = 'tenancy'
urlpatterns = [

    # Tenant groups
    path('tenant-groups/', views.TenantGroupListView.as_view(), name='tenantgroup_list'),
    path('tenant-groups/add/', views.TenantGroupEditView.as_view(), name='tenantgroup_add'),
    path('tenant-groups/import/', views.TenantGroupBulkImportView.as_view(), name='tenantgroup_import'),
    path('tenant-groups/delete/', views.TenantGroupBulkDeleteView.as_view(), name='tenantgroup_bulk_delete'),
    path('tenant-groups/<slug:slug>/edit/', views.TenantGroupEditView.as_view(), name='tenantgroup_edit'),
    path('tenant-groups/<slug:slug>/delete/', views.TenantGroupDeleteView.as_view(), name='tenantgroup_delete'),
    path('tenant-groups/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='tenantgroup_changelog', kwargs={'model': TenantGroup}),

    # Tenants
    path('tenants/', views.TenantListView.as_view(), name='tenant_list'),
    path('tenants/add/', views.TenantEditView.as_view(), name='tenant_add'),
    path('tenants/import/', views.TenantBulkImportView.as_view(), name='tenant_import'),
    path('tenants/edit/', views.TenantBulkEditView.as_view(), name='tenant_bulk_edit'),
    path('tenants/delete/', views.TenantBulkDeleteView.as_view(), name='tenant_bulk_delete'),
    path('tenants/<slug:slug>/', views.TenantView.as_view(), name='tenant'),
    path('tenants/<slug:slug>/edit/', views.TenantEditView.as_view(), name='tenant_edit'),
    path('tenants/<slug:slug>/delete/', views.TenantDeleteView.as_view(), name='tenant_delete'),
    path('tenants/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='tenant_changelog', kwargs={'model': Tenant}),

]
