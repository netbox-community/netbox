from django.urls import path

from extras.views import ObjectChangeLogView, ObjectJournalView
from utilities.views import SlugRedirectView
from . import views
from .models import *

app_name = 'tenancy'
urlpatterns = [

    # Tenant groups
    path('tenant-groups/', views.TenantGroupListView.as_view(), name='tenantgroup_list'),
    path('tenant-groups/add/', views.TenantGroupEditView.as_view(), name='tenantgroup_add'),
    path('tenant-groups/import/', views.TenantGroupBulkImportView.as_view(), name='tenantgroup_import'),
    path('tenant-groups/edit/', views.TenantGroupBulkEditView.as_view(), name='tenantgroup_bulk_edit'),
    path('tenant-groups/delete/', views.TenantGroupBulkDeleteView.as_view(), name='tenantgroup_bulk_delete'),
    path('tenant-groups/<int:pk>/', views.TenantGroupView.as_view(), name='tenantgroup'),
    path('tenant-groups/<int:pk>/edit/', views.TenantGroupEditView.as_view(), name='tenantgroup_edit'),
    path('tenant-groups/<int:pk>/delete/', views.TenantGroupDeleteView.as_view(), name='tenantgroup_delete'),
    path('tenant-groups/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='tenantgroup_changelog', kwargs={'model': TenantGroup}),

    # Tenants
    path('tenants/', views.TenantListView.as_view(), name='tenant_list'),
    path('tenants/add/', views.TenantEditView.as_view(), name='tenant_add'),
    path('tenants/import/', views.TenantBulkImportView.as_view(), name='tenant_import'),
    path('tenants/edit/', views.TenantBulkEditView.as_view(), name='tenant_bulk_edit'),
    path('tenants/delete/', views.TenantBulkDeleteView.as_view(), name='tenant_bulk_delete'),
    path('tenants/<int:pk>/', views.TenantView.as_view(), name='tenant'),
    path('tenants/<slug:slug>/', SlugRedirectView.as_view(), kwargs={'model': Tenant}),
    path('tenants/<int:pk>/edit/', views.TenantEditView.as_view(), name='tenant_edit'),
    path('tenants/<int:pk>/delete/', views.TenantDeleteView.as_view(), name='tenant_delete'),
    path('tenants/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='tenant_changelog', kwargs={'model': Tenant}),
    path('tenants/<int:pk>/journal/', ObjectJournalView.as_view(), name='tenant_journal', kwargs={'model': Tenant}),

    # Contact groups
    path('contact-groups/', views.ContactGroupListView.as_view(), name='contactgroup_list'),
    path('contact-groups/add/', views.ContactGroupEditView.as_view(), name='contactgroup_add'),
    path('contact-groups/import/', views.ContactGroupBulkImportView.as_view(), name='contactgroup_import'),
    path('contact-groups/edit/', views.ContactGroupBulkEditView.as_view(), name='contactgroup_bulk_edit'),
    path('contact-groups/delete/', views.ContactGroupBulkDeleteView.as_view(), name='contactgroup_bulk_delete'),
    path('contact-groups/<int:pk>/', views.ContactGroupView.as_view(), name='contactgroup'),
    path('contact-groups/<int:pk>/edit/', views.ContactGroupEditView.as_view(), name='contactgroup_edit'),
    path('contact-groups/<int:pk>/delete/', views.ContactGroupDeleteView.as_view(), name='contactgroup_delete'),
    path('contact-groups/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='contactgroup_changelog', kwargs={'model': ContactGroup}),

    # Contact roles
    path('contact-roles/', views.ContactRoleListView.as_view(), name='contactrole_list'),
    path('contact-roles/add/', views.ContactRoleEditView.as_view(), name='contactrole_add'),
    path('contact-roles/import/', views.ContactRoleBulkImportView.as_view(), name='contactrole_import'),
    path('contact-roles/edit/', views.ContactRoleBulkEditView.as_view(), name='contactrole_bulk_edit'),
    path('contact-roles/delete/', views.ContactRoleBulkDeleteView.as_view(), name='contactrole_bulk_delete'),
    path('contact-roles/<int:pk>/', views.ContactRoleView.as_view(), name='contactrole'),
    path('contact-roles/<int:pk>/edit/', views.ContactRoleEditView.as_view(), name='contactrole_edit'),
    path('contact-roles/<int:pk>/delete/', views.ContactRoleDeleteView.as_view(), name='contactrole_delete'),
    path('contact-roles/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='contactrole_changelog', kwargs={'model': ContactRole}),

    # Contacts
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/add/', views.ContactEditView.as_view(), name='contact_add'),
    path('contacts/import/', views.ContactBulkImportView.as_view(), name='contact_import'),
    path('contacts/edit/', views.ContactBulkEditView.as_view(), name='contact_bulk_edit'),
    path('contacts/delete/', views.ContactBulkDeleteView.as_view(), name='contact_bulk_delete'),
    path('contacts/<int:pk>/', views.ContactView.as_view(), name='contact'),
    path('contacts/<slug:slug>/', SlugRedirectView.as_view(), kwargs={'model': Contact}),
    path('contacts/<int:pk>/edit/', views.ContactEditView.as_view(), name='contact_edit'),
    path('contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),
    path('contacts/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='contact_changelog', kwargs={'model': Contact}),
    path('contacts/<int:pk>/journal/', ObjectJournalView.as_view(), name='contact_journal', kwargs={'model': Contact}),

]
