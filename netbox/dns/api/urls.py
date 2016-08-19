from django.conf.urls import url

from .views import *

urlpatterns = [

    # Zones
    url(r'^zones/$', ZoneListView.as_view(), name='zone_list'),
    url(r'^zones/(?P<pk>\d+)/$', ZoneDetailView.as_view(), name='zone_detail'),

    # Records
    url(r'^records/$', RecordListView.as_view(), name='record_list'),
    url(r'^records/(?P<pk>\d+)/$', RecordDetailView.as_view(), name='record_detail'),

    # BIND Exports
    url(r'^bind/forward/$', bind_forward, name='bind_forward'),
    url(r'^bind/reverse/$', bind_reverse, name='bind_reverse'),

]
