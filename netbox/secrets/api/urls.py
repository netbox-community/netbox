from django.conf.urls import url

from .views import *


urlpatterns = [

    # Secret roles
    url(r'^secret-roles/$', SecretRoleViewSet.as_view({'get': 'list'}), name='secretrole_list'),
    url(r'^secret-roles/(?P<pk>\d+)/$', SecretRoleViewSet.as_view({'get': 'retrieve'}), name='secretrole_detail'),

    # Secrets
    url(r'^secrets/$', SecretListView.as_view(), name='secret_list'),
    url(r'^secrets/(?P<pk>\d+)/$', SecretDetailView.as_view(), name='secret_detail'),

    # Miscellaneous
    url(r'^generate-keys/$', RSAKeyGeneratorView.as_view(), name='generate_keys'),

]
