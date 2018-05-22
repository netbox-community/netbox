from __future__ import unicode_literals

from django.conf.urls import url

from extras import views

app_name = 'extras'
urlpatterns = [

    # Tags
    url(r'^tags/$', views.TagListView.as_view(), name='tag_list'),
    url(r'^tags/(?P<slug>[\w-]+)/edit/$', views.TagEditView.as_view(), name='tag_edit'),
    url(r'^tags/(?P<slug>[\w-]+)/delete/$', views.TagDeleteView.as_view(), name='tag_delete'),
    url(r'^tags/delete/$', views.TagBulkDeleteView.as_view(), name='tag_bulk_delete'),

    # Image attachments
    url(r'^image-attachments/(?P<pk>\d+)/edit/$', views.ImageAttachmentEditView.as_view(), name='imageattachment_edit'),
    url(r'^image-attachments/(?P<pk>\d+)/delete/$', views.ImageAttachmentDeleteView.as_view(), name='imageattachment_delete'),

    # Reports
    url(r'^reports/$', views.ReportListView.as_view(), name='report_list'),
    url(r'^reports/(?P<name>[^/]+\.[^/]+)/$', views.ReportView.as_view(), name='report'),
    url(r'^reports/(?P<name>[^/]+\.[^/]+)/run/$', views.ReportRunView.as_view(), name='report_run'),

]
