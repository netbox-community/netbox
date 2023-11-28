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

    # IKE proposals
    path('ike-proposals/', views.IKEProposalListView.as_view(), name='ikeproposal_list'),
    path('ike-proposals/add/', views.IKEProposalEditView.as_view(), name='ikeproposal_add'),
    path('ike-proposals/import/', views.IKEProposalBulkImportView.as_view(), name='ikeproposal_import'),
    path('ike-proposals/edit/', views.IKEProposalBulkEditView.as_view(), name='ikeproposal_bulk_edit'),
    path('ike-proposals/delete/', views.IKEProposalBulkDeleteView.as_view(), name='ikeproposal_bulk_delete'),
    path('ike-proposals/<int:pk>/', include(get_model_urls('vpn', 'ikeproposal'))),

    # IKE policies
    path('ike-policys/', views.IKEPolicyListView.as_view(), name='ikepolicy_list'),
    path('ike-policys/add/', views.IKEPolicyEditView.as_view(), name='ikepolicy_add'),
    path('ike-policys/import/', views.IKEPolicyBulkImportView.as_view(), name='ikepolicy_import'),
    path('ike-policys/edit/', views.IKEPolicyBulkEditView.as_view(), name='ikepolicy_bulk_edit'),
    path('ike-policys/delete/', views.IKEPolicyBulkDeleteView.as_view(), name='ikepolicy_bulk_delete'),
    path('ike-policys/<int:pk>/', include(get_model_urls('vpn', 'ikepolicy'))),

    # IPSec proposals
    path('ipsec-proposals/', views.IPSecProposalListView.as_view(), name='ipsecproposal_list'),
    path('ipsec-proposals/add/', views.IPSecProposalEditView.as_view(), name='ipsecproposal_add'),
    path('ipsec-proposals/import/', views.IPSecProposalBulkImportView.as_view(), name='ipsecproposal_import'),
    path('ipsec-proposals/edit/', views.IPSecProposalBulkEditView.as_view(), name='ipsecproposal_bulk_edit'),
    path('ipsec-proposals/delete/', views.IPSecProposalBulkDeleteView.as_view(), name='ipsecproposal_bulk_delete'),
    path('ipsec-proposals/<int:pk>/', include(get_model_urls('vpn', 'ipsecproposal'))),

    # IPSec policies
    path('ipsec-policys/', views.IPSecPolicyListView.as_view(), name='ipsecpolicy_list'),
    path('ipsec-policys/add/', views.IPSecPolicyEditView.as_view(), name='ipsecpolicy_add'),
    path('ipsec-policys/import/', views.IPSecPolicyBulkImportView.as_view(), name='ipsecpolicy_import'),
    path('ipsec-policys/edit/', views.IPSecPolicyBulkEditView.as_view(), name='ipsecpolicy_bulk_edit'),
    path('ipsec-policys/delete/', views.IPSecPolicyBulkDeleteView.as_view(), name='ipsecpolicy_bulk_delete'),
    path('ipsec-policys/<int:pk>/', include(get_model_urls('vpn', 'ipsecpolicy'))),

    # IPSec profiles
    path('ipsec-profiles/', views.IPSecProfileListView.as_view(), name='ipsecprofile_list'),
    path('ipsec-profiles/add/', views.IPSecProfileEditView.as_view(), name='ipsecprofile_add'),
    path('ipsec-profiles/import/', views.IPSecProfileBulkImportView.as_view(), name='ipsecprofile_import'),
    path('ipsec-profiles/edit/', views.IPSecProfileBulkEditView.as_view(), name='ipsecprofile_bulk_edit'),
    path('ipsec-profiles/delete/', views.IPSecProfileBulkDeleteView.as_view(), name='ipsecprofile_bulk_delete'),
    path('ipsec-profiles/<int:pk>/', include(get_model_urls('vpn', 'ipsecprofile'))),

]
