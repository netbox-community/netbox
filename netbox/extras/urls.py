from django.conf.urls import url

from extras import views
from extras.models import Tag
from utilities.urls import cached


app_name = 'extras'
urlpatterns = [

    # Tags
    url(r'^tags/$', cached(views.TagListView.as_view()), name='tag_list'),
    url(r'^tags/delete/$', views.TagBulkDeleteView.as_view(), name='tag_bulk_delete'),
    url(r'^tags/(?P<slug>[\w-]+)/$', cached(views.TagView.as_view()), name='tag'),
    url(r'^tags/(?P<slug>[\w-]+)/edit/$', views.TagEditView.as_view(), name='tag_edit'),
    url(r'^tags/(?P<slug>[\w-]+)/delete/$', views.TagDeleteView.as_view(), name='tag_delete'),
    url(r'^tags/(?P<slug>[\w-]+)/changelog/$', cached(views.ObjectChangeLogView.as_view()), name='tag_changelog', kwargs={'model': Tag}),

    # Config contexts
    url(r'^config-contexts/$', cached(views.ConfigContextListView.as_view()), name='configcontext_list'),
    url(r'^config-contexts/add/$', cached(views.ConfigContextCreateView.as_view()), name='configcontext_add'),
    url(r'^config-contexts/edit/$', views.ConfigContextBulkEditView.as_view(), name='configcontext_bulk_edit'),
    url(r'^config-contexts/delete/$', views.ConfigContextBulkDeleteView.as_view(), name='configcontext_bulk_delete'),
    url(r'^config-contexts/(?P<pk>\d+)/$', cached(views.ConfigContextView.as_view()), name='configcontext'),
    url(r'^config-contexts/(?P<pk>\d+)/edit/$', views.ConfigContextEditView.as_view(), name='configcontext_edit'),
    url(r'^config-contexts/(?P<pk>\d+)/delete/$', views.ConfigContextDeleteView.as_view(), name='configcontext_delete'),

    # Image attachments
    url(r'^image-attachments/(?P<pk>\d+)/edit/$', views.ImageAttachmentEditView.as_view(), name='imageattachment_edit'),
    url(r'^image-attachments/(?P<pk>\d+)/delete/$', views.ImageAttachmentDeleteView.as_view(), name='imageattachment_delete'),

    # Reports
    url(r'^reports/$', cached(views.ReportListView.as_view()), name='report_list'),
    url(r'^reports/(?P<name>[^/]+\.[^/]+)/$', cached(views.ReportView.as_view()), name='report'),
    url(r'^reports/(?P<name>[^/]+\.[^/]+)/run/$', views.ReportRunView.as_view(), name='report_run'),

    # Change logging
    url(r'^changelog/$', cached(views.ObjectChangeListView.as_view()), name='objectchange_list'),
    url(r'^changelog/(?P<pk>\d+)/$', cached(views.ObjectChangeView.as_view()), name='objectchange'),

]
