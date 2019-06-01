from django.urls import path

from extras.views import ObjectChangeLogView
from . import views
from .models import Secret, SecretRole

app_name = 'secrets'
urlpatterns = [

    # Secret roles
    path(r'secret-roles/', views.SecretRoleListView.as_view(), name='secretrole_list'),
    path(r'secret-roles/add/', views.SecretRoleCreateView.as_view(), name='secretrole_add'),
    path(r'secret-roles/import/', views.SecretRoleBulkImportView.as_view(), name='secretrole_import'),
    path(r'secret-roles/delete/', views.SecretRoleBulkDeleteView.as_view(), name='secretrole_bulk_delete'),
    path(r'secret-roles/<slug:slug>/edit/', views.SecretRoleEditView.as_view(), name='secretrole_edit'),
    path(r'secret-roles/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='secretrole_changelog', kwargs={'model': SecretRole}),

    # Secrets
    path(r'secrets/', views.SecretListView.as_view(), name='secret_list'),
    path(r'secrets/import/', views.SecretBulkImportView.as_view(), name='secret_import'),
    path(r'secrets/edit/', views.SecretBulkEditView.as_view(), name='secret_bulk_edit'),
    path(r'secrets/delete/', views.SecretBulkDeleteView.as_view(), name='secret_bulk_delete'),
    path(r'secrets/<int:pk>/', views.SecretView.as_view(), name='secret'),
    path(r'secrets/<int:pk>/edit/', views.secret_edit, name='secret_edit'),
    path(r'secrets/<int:pk>/delete/', views.SecretDeleteView.as_view(), name='secret_delete'),
    path(r'secrets/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='secret_changelog', kwargs={'model': Secret}),

]
