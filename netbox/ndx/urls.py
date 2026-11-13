from django.urls import include, path

from utilities.urls import get_model_urls

from . import views

app_name = 'ndx'
urlpatterns = [
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('catalog/import/', views.CatalogImportView.as_view(), name='catalog_import'),
    path('catalog/<str:vendor_slug>/<str:slug>/', views.CatalogEntryView.as_view(), name='catalog_entry'),

    path('sync/', views.SyncStatusView.as_view(), name='sync_status'),
    path('sync/run/', views.SyncView.as_view(), name='sync'),
    path('sync/apply/', views.ApplyUpdatesView.as_view(), name='apply_updates'),

    path('import-records/', include(get_model_urls('ndx', 'importrecord', detail=False))),
    path('import-records/<int:pk>/', include(get_model_urls('ndx', 'importrecord'))),
]
