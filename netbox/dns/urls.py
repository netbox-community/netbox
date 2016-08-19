from django.conf.urls import url

from . import views

urlpatterns = [

    # Zones
    url(r'^zones/$', views.ZoneListView.as_view(), name='zone_list'),
    url(r'^zones/add/$', views.ZoneEditView.as_view(), name='zone_add'),
    url(r'^zones/import/$', views.ZoneBulkImportView.as_view(), name='zone_import'),
    url(r'^zones/edit/$', views.ZoneBulkEditView.as_view(), name='zone_bulk_edit'),
    url(r'^zones/delete/$', views.ZoneBulkDeleteView.as_view(), name='zone_bulk_delete'),
    url(r'^zones/(?P<pk>\d+)/$', views.zone, name='zone'),
    url(r'^zones/(?P<pk>\d+)/edit/$', views.ZoneEditView.as_view(), name='zone_edit'),
    url(r'^zones/(?P<pk>\d+)/delete/$', views.ZoneDeleteView.as_view(), name='zone_delete'),

    # Records
    url(r'^records/$', views.RecordListView.as_view(), name='record_list'),
    url(r'^records/add/$', views.RecordEditView.as_view(), name='record_add'),
    url(r'^records/import/$', views.RecordBulkImportView.as_view(), name='record_import'),
    url(r'^records/edit/$', views.RecordBulkEditView.as_view(), name='record_bulk_edit'),
    url(r'^records/delete/$', views.RecordBulkDeleteView.as_view(), name='record_bulk_delete'),
    url(r'^records/(?P<pk>\d+)/$', views.record, name='record'),
    url(r'^records/(?P<pk>\d+)/edit/$', views.RecordEditView.as_view(), name='record_edit'),
    url(r'^records/(?P<pk>\d+)/delete/$', views.RecordDeleteView.as_view(), name='record_delete'),

    # BIND Exports
    url(r'^bind/forward/$', views.full_forward, name='full_forward'),
    url(r'^bind/reverse/$', views.full_reverse, name='full_reverse'),

]
