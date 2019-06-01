from django.urls import path

from . import views

app_name = 'user'
urlpatterns = [

    path(r'profile/', views.ProfileView.as_view(), name='profile'),
    path(r'password/', views.ChangePasswordView.as_view(), name='change_password'),
    path(r'api-tokens/', views.TokenListView.as_view(), name='token_list'),
    path(r'api-tokens/add/', views.TokenEditView.as_view(), name='token_add'),
    path(r'api-tokens/<int:pk>/edit/', views.TokenEditView.as_view(), name='token_edit'),
    path(r'api-tokens/<int:pk>/delete/', views.TokenDeleteView.as_view(), name='token_delete'),
    path(r'user-key/', views.UserKeyView.as_view(), name='userkey'),
    path(r'user-key/edit/', views.UserKeyEditView.as_view(), name='userkey_edit'),
    path(r'session-key/delete/', views.SessionKeyDeleteView.as_view(), name='sessionkey_delete'),

]
