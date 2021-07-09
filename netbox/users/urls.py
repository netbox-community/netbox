from django.urls import path

from . import views

app_name = 'user'
urlpatterns = [

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('preferences/', views.UserConfigView.as_view(), name='preferences'),
    path('password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('api-tokens/', views.TokenListView.as_view(), name='token_list'),
    path('api-tokens/add/', views.TokenEditView.as_view(), name='token_add'),
    path('api-tokens/<int:pk>/edit/', views.TokenEditView.as_view(), name='token_edit'),
    path('api-tokens/<int:pk>/delete/', views.TokenDeleteView.as_view(), name='token_delete'),

]
