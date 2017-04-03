from django.conf.urls import url

from extras import views


urlpatterns = [

    # Image attachments
    url(r'^image-attachments/(?P<pk>\d+)/edit/$', views.ImageAttachmentEditView.as_view(), name='imageattachment_edit'),
    url(r'^image-attachments/(?P<pk>\d+)/delete/$', views.ImageAttachmentDeleteView.as_view(), name='imageattachment_delete'),

]
