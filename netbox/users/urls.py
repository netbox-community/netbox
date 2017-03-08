from django.conf.urls import url

from . import views


urlpatterns = [

    # User profiles
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/password/$', views.change_password, name='change_password'),
    url(r'^profile/api-tokens/$', views.TokenList.as_view(), name='api_tokens'),
    url(r'^profile/user-key/$', views.userkey, name='userkey'),
    url(r'^profile/user-key/edit/$', views.userkey_edit, name='userkey_edit'),
    url(r'^profile/recent-activity/$', views.recent_activity, name='recent_activity'),

]
