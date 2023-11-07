from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'vpn'
urlpatterns = [

    # Tunnels
    path('tunnels/', views.TunnelListView.as_view(), name='tunnel_list'),
    path('tunnels/add/', views.TunnelEditView.as_view(), name='tunnel_add'),
    path('tunnels/import/', views.TunnelBulkImportView.as_view(), name='tunnel_import'),
    path('tunnels/edit/', views.TunnelBulkEditView.as_view(), name='tunnel_bulk_edit'),
    path('tunnels/delete/', views.TunnelBulkDeleteView.as_view(), name='tunnel_bulk_delete'),
    path('tunnels/<int:pk>/', include(get_model_urls('vpn', 'tunnel'))),

    # Tunnel terminations
    path('tunnel-terminations/', views.TunnelTerminationListView.as_view(), name='tunneltermination_list'),
    path('tunnel-terminations/add/', views.TunnelTerminationEditView.as_view(), name='tunneltermination_add'),
    path('tunnel-terminations/import/', views.TunnelTerminationBulkImportView.as_view(), name='tunneltermination_import'),
    path('tunnel-terminations/edit/', views.TunnelTerminationBulkEditView.as_view(), name='tunneltermination_bulk_edit'),
    path('tunnel-terminations/delete/', views.TunnelTerminationBulkDeleteView.as_view(), name='tunneltermination_bulk_delete'),
    path('tunnel-terminations/<int:pk>/', include(get_model_urls('vpn', 'tunneltermination'))),

    # IPSec profiles
    path('ipsec-profiles/', views.IPSecProfileListView.as_view(), name='ipsecprofile_list'),
    path('ipsec-profiles/add/', views.IPSecProfileEditView.as_view(), name='ipsecprofile_add'),
    path('ipsec-profiles/import/', views.IPSecProfileBulkImportView.as_view(), name='ipsecprofile_import'),
    path('ipsec-profiles/edit/', views.IPSecProfileBulkEditView.as_view(), name='ipsecprofile_bulk_edit'),
    path('ipsec-profiles/delete/', views.IPSecProfileBulkDeleteView.as_view(), name='ipsecprofile_bulk_delete'),
    path('ipsec-profiles/<int:pk>/', include(get_model_urls('vpn', 'ipsecprofile'))),

]
