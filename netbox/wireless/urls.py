from django.urls import path

from extras.views import ObjectChangeLogView, ObjectJournalView
from . import views
from .models import *

app_name = 'wireless'
urlpatterns = (

    # Wireless LANs
    path('wireless-lans/', views.WirelessLANListView.as_view(), name='wirelesslan_list'),
    path('wireless-lans/add/', views.WirelessLANEditView.as_view(), name='wirelesslan_add'),
    path('wireless-lans/import/', views.WirelessLANBulkImportView.as_view(), name='wirelesslan_import'),
    path('wireless-lans/edit/', views.WirelessLANBulkEditView.as_view(), name='wirelesslan_bulk_edit'),
    path('wireless-lans/delete/', views.WirelessLANBulkDeleteView.as_view(), name='wirelesslan_bulk_delete'),
    path('wireless-lans/<int:pk>/', views.WirelessLANView.as_view(), name='wirelesslan'),
    path('wireless-lans/<int:pk>/edit/', views.WirelessLANEditView.as_view(), name='wirelesslan_edit'),
    path('wireless-lans/<int:pk>/delete/', views.WirelessLANDeleteView.as_view(), name='wirelesslan_delete'),
    path('wireless-lans/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='wirelesslan_changelog', kwargs={'model': WirelessLAN}),
    path('wireless-lans/<int:pk>/journal/', ObjectJournalView.as_view(), name='wirelesslan_journal', kwargs={'model': WirelessLAN}),

    # Wireless links
    path('wireless-links/', views.WirelessLinkListView.as_view(), name='wirelesslink_list'),
    path('wireless-links/add/', views.WirelessLinkEditView.as_view(), name='wirelesslink_add'),
    path('wireless-links/import/', views.WirelessLinkBulkImportView.as_view(), name='wirelesslink_import'),
    path('wireless-links/edit/', views.WirelessLinkBulkEditView.as_view(), name='wirelesslink_bulk_edit'),
    path('wireless-links/delete/', views.WirelessLinkBulkDeleteView.as_view(), name='wirelesslink_bulk_delete'),
    path('wireless-links/<int:pk>/', views.WirelessLinkView.as_view(), name='wirelesslink'),
    path('wireless-links/<int:pk>/edit/', views.WirelessLinkEditView.as_view(), name='wirelesslink_edit'),
    path('wireless-links/<int:pk>/delete/', views.WirelessLinkDeleteView.as_view(), name='wirelesslink_delete'),
    path('wireless-links/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='wirelesslink_changelog', kwargs={'model': WirelessLink}),
    path('wireless-links/<int:pk>/journal/', ObjectJournalView.as_view(), name='wirelesslink_journal', kwargs={'model': WirelessLink}),

)
