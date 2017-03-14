from django.conf.urls import url

from . import views


urlpatterns = [

    # User profiles
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^user-key/$', views.userkey, name='userkey'),
    url(r'^user-key/edit/$', views.userkey_edit, name='userkey_edit'),
    url(r'^recent-activity/$', views.recent_activity, name='recent_activity'),

]
