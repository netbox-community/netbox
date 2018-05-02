from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.display_activity, name='display'),
    url(r'^(\d+)/delete/(?P<pk>\d+)$', views.DeleteComment.as_view(), name='delete_comment'),
    url(r'^(\d+)/add', views.AddComment.as_view(), name='add_comment')
]
