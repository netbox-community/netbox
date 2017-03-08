from django.conf.urls import url

from . import views


urlpatterns = [

    # User profiles
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/password/$', views.change_password, name='change_password'),
    url(r'^profile/api-tokens/$', views.TokenListView.as_view(), name='token_list'),
    url(r'^profile/api-tokens/add/$', views.TokenEditView.as_view(), name='token_add'),
    url(r'^profile/api-tokens/(?P<pk>\d+)/edit/$', views.TokenEditView.as_view(), name='token_edit'),
    url(r'^profile/api-tokens/(?P<pk>\d+)/delete/$', views.TokenDeleteView.as_view(), name='token_delete'),
    url(r'^profile/user-key/$', views.userkey, name='userkey'),
    url(r'^profile/user-key/edit/$', views.userkey_edit, name='userkey_edit'),
    url(r'^profile/recent-activity/$', views.recent_activity, name='recent_activity'),

]
