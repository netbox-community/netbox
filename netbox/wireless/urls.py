from django.urls import path

from extras.views import ObjectChangeLogView, ObjectJournalView
from . import views
from .models import *

app_name = 'wireless'
urlpatterns = (

    # SSIDs
    path('ssids/', views.SSIDListView.as_view(), name='ssid_list'),
    path('ssids/add/', views.SSIDEditView.as_view(), name='ssid_add'),
    path('ssids/import/', views.SSIDBulkImportView.as_view(), name='ssid_import'),
    path('ssids/edit/', views.SSIDBulkEditView.as_view(), name='ssid_bulk_edit'),
    path('ssids/delete/', views.SSIDBulkDeleteView.as_view(), name='ssid_bulk_delete'),
    path('ssids/<int:pk>/', views.SSIDView.as_view(), name='ssid'),
    path('ssids/<int:pk>/edit/', views.SSIDEditView.as_view(), name='ssid_edit'),
    path('ssids/<int:pk>/delete/', views.SSIDDeleteView.as_view(), name='ssid_delete'),
    path('ssids/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='ssid_changelog', kwargs={'model': SSID}),
    path('ssids/<int:pk>/journal/', ObjectJournalView.as_view(), name='ssid_journal', kwargs={'model': SSID}),

)
