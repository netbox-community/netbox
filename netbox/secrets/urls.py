from __future__ import unicode_literals

from django.conf.urls import url

from extras.views import ObjectChangeLogView
from . import views
from .models import Secret, SecretRole

app_name = 'secrets'
urlpatterns = [

    # Secret roles
    url(r'^secret-roles/$', views.SecretRoleListView.as_view(), name='secretrole_list'),
    url(r'^secret-roles/add/$', views.SecretRoleCreateView.as_view(), name='secretrole_add'),
    url(r'^secret-roles/import/$', views.SecretRoleBulkImportView.as_view(), name='secretrole_import'),
    url(r'^secret-roles/delete/$', views.SecretRoleBulkDeleteView.as_view(), name='secretrole_bulk_delete'),
    url(r'^secret-roles/(?P<slug>[\w-]+)/edit/$', views.SecretRoleEditView.as_view(), name='secretrole_edit'),
    url(r'^secret-roles/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='secretrole_changelog', kwargs={'model': SecretRole}),

    # Secrets
    url(r'^secrets/$', views.SecretListView.as_view(), name='secret_list'),
    url(r'^secrets/import/$', views.SecretBulkImportView.as_view(), name='secret_import'),
    url(r'^secrets/edit/$', views.SecretBulkEditView.as_view(), name='secret_bulk_edit'),
    url(r'^secrets/delete/$', views.SecretBulkDeleteView.as_view(), name='secret_bulk_delete'),
    url(r'^secrets/(?P<pk>\d+)/$', views.SecretView.as_view(), name='secret'),
    url(r'^secrets/(?P<pk>\d+)/edit/$', views.secret_edit, name='secret_edit'),
    url(r'^secrets/(?P<pk>\d+)/delete/$', views.SecretDeleteView.as_view(), name='secret_delete'),
    url(r'^secrets/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='secret_changelog', kwargs={'model': Secret}),

]
