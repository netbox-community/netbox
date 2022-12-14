from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'wireless'
urlpatterns = (

    # Wireless LAN groups
    path('wireless-lan-groups/', views.WirelessLANGroupListView.as_view(), name='wirelesslangroup_list'),
    path('wireless-lan-groups/add/', views.WirelessLANGroupEditView.as_view(), name='wirelesslangroup_add'),
    path('wireless-lan-groups/import/', views.WirelessLANGroupBulkImportView.as_view(), name='wirelesslangroup_import'),
    path('wireless-lan-groups/edit/', views.WirelessLANGroupBulkEditView.as_view(), name='wirelesslangroup_bulk_edit'),
    path('wireless-lan-groups/delete/', views.WirelessLANGroupBulkDeleteView.as_view(), name='wirelesslangroup_bulk_delete'),
    path('wireless-lan-groups/<int:pk>/', include(get_model_urls('wireless', 'wirelesslangroup'))),

    # Wireless LANs
    path('wireless-lans/', views.WirelessLANListView.as_view(), name='wirelesslan_list'),
    path('wireless-lans/add/', views.WirelessLANEditView.as_view(), name='wirelesslan_add'),
    path('wireless-lans/import/', views.WirelessLANBulkImportView.as_view(), name='wirelesslan_import'),
    path('wireless-lans/edit/', views.WirelessLANBulkEditView.as_view(), name='wirelesslan_bulk_edit'),
    path('wireless-lans/delete/', views.WirelessLANBulkDeleteView.as_view(), name='wirelesslan_bulk_delete'),
    path('wireless-lans/<int:pk>/', include(get_model_urls('wireless', 'wirelesslan'))),

    # Wireless links
    path('wireless-links/', views.WirelessLinkListView.as_view(), name='wirelesslink_list'),
    path('wireless-links/add/', views.WirelessLinkEditView.as_view(), name='wirelesslink_add'),
    path('wireless-links/import/', views.WirelessLinkBulkImportView.as_view(), name='wirelesslink_import'),
    path('wireless-links/edit/', views.WirelessLinkBulkEditView.as_view(), name='wirelesslink_bulk_edit'),
    path('wireless-links/delete/', views.WirelessLinkBulkDeleteView.as_view(), name='wirelesslink_bulk_delete'),
    path('wireless-links/<int:pk>/', include(get_model_urls('wireless', 'wirelesslink'))),

)
