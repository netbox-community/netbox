from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [

    # Account views
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('preferences/', views.UserConfigView.as_view(), name='preferences'),
    path('password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('api-tokens/', views.UserTokenListView.as_view(), name='usertoken_list'),
    path('api-tokens/add/', views.UserTokenEditView.as_view(), name='usertoken_add'),
    path('api-tokens/<int:pk>/', views.UserTokenView.as_view(), name='usertoken'),
    path('api-tokens/<int:pk>/edit/', views.UserTokenEditView.as_view(), name='usertoken_edit'),
    path('api-tokens/<int:pk>/delete/', views.UserTokenDeleteView.as_view(), name='usertoken_delete'),

]
