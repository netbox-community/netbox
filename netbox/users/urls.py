from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'user'
urlpatterns = [

    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^password/$', views.ChangePasswordView.as_view(), name='change_password'),
    url(r'^api-tokens/$', views.TokenListView.as_view(), name='token_list'),
    url(r'^api-tokens/add/$', views.TokenEditView.as_view(), name='token_add'),
    url(r'^api-tokens/(?P<pk>\d+)/edit/$', views.TokenEditView.as_view(), name='token_edit'),
    url(r'^api-tokens/(?P<pk>\d+)/delete/$', views.TokenDeleteView.as_view(), name='token_delete'),
    url(r'^user-key/$', views.UserKeyView.as_view(), name='userkey'),
    url(r'^user-key/edit/$', views.UserKeyEditView.as_view(), name='userkey_edit'),
    url(r'^session-key/delete/$', views.SessionKeyDeleteView.as_view(), name='sessionkey_delete'),
    url(r'^recent-activity/$', views.RecentActivityView.as_view(), name='recent_activity'),

]
