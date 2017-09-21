from __future__ import unicode_literals

from django.conf.urls import url

from extras import views


app_name = 'extras'
urlpatterns = [

    # Image attachments
    url(r'^image-attachments/(?P<pk>\d+)/edit/$', views.ImageAttachmentEditView.as_view(), name='imageattachment_edit'),
    url(r'^image-attachments/(?P<pk>\d+)/delete/$', views.ImageAttachmentDeleteView.as_view(), name='imageattachment_delete'),

    # Reports
    url(r'^reports/$', views.ReportListView.as_view(), name='report_list'),

]
