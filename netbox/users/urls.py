from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'users'
urlpatterns = [

    # User
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('preferences/', views.UserConfigView.as_view(), name='preferences'),
    path('password/', views.ChangePasswordView.as_view(), name='change_password'),

    # Users
    path('users/', views.NetBoxUserListView.as_view(), name='user_list'),
    path('users/add/', views.NetBoxUserEditView.as_view(), name='user_add'),
    path('users/add/', views.NetBoxUserEditView.as_view(), name='netboxuser_add'),
    path('users/import/', views.NetBoxUserBulkImportView.as_view(), name='netboxuser_import'),
    path('users/edit/', views.NetBoxUserBulkEditView.as_view(), name='netboxuser_bulk_edit'),
    path('users/delete/', views.NetBoxUserBulkDeleteView.as_view(), name='netboxuser_bulk_delete'),
    path('users/<int:pk>/', include(get_model_urls('users', 'netboxuser'))),

    # API tokens
    path('api-tokens/', views.TokenListView.as_view(), name='token_list'),
    path('api-tokens/add/', views.TokenEditView.as_view(), name='token_add'),
    path('api-tokens/<int:pk>/', include(get_model_urls('users', 'token'))),

]
