from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'users'
urlpatterns = [

    # Account views
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('preferences/', views.UserConfigView.as_view(), name='preferences'),
    path('password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('api-tokens/', views.TokenListView.as_view(), name='token_list'),
    path('api-tokens/add/', views.TokenEditView.as_view(), name='token_add'),
    path('api-tokens/<int:pk>/', include(get_model_urls('users', 'token'))),

    # Tokens
    path('user-tokens/', views.UserTokenListView.as_view(), name='user_token_list'),
    path('user-tokens/add/', views.UserTokenEditView.as_view(), name='user_token_add'),
    path('user-tokens/import/', views.UserTokenBulkImportView.as_view(), name='user_token_import'),
    path('user-tokens/edit/', views.UserTokenBulkEditView.as_view(), name='user_token_bulk_edit'),
    path('user-tokens/delete/', views.UserTokenBulkDeleteView.as_view(), name='user_token_bulk_delete'),
    path('user-tokens/<int:pk>/', include(get_model_urls('users', 'user_token'))),

    # Users
    path('users/', views.UserListView.as_view(), name='netboxuser_list'),
    path('users/add/', views.UserEditView.as_view(), name='netboxuser_add'),
    path('users/edit/', views.UserBulkEditView.as_view(), name='netboxuser_bulk_edit'),
    path('users/import/', views.UserBulkImportView.as_view(), name='netboxuser_import'),
    path('users/delete/', views.UserBulkDeleteView.as_view(), name='netboxuser_bulk_delete'),
    path('users/<int:pk>/', include(get_model_urls('users', 'netboxuser'))),

    # Groups
    path('groups/', views.GroupListView.as_view(), name='netboxgroup_list'),
    path('groups/add/', views.GroupEditView.as_view(), name='netboxgroup_add'),
    path('groups/import/', views.GroupBulkImportView.as_view(), name='netboxgroup_import'),
    path('groups/delete/', views.GroupBulkDeleteView.as_view(), name='netboxgroup_bulk_delete'),
    path('groups/<int:pk>/', include(get_model_urls('users', 'netboxgroup'))),

    # Permissions
    path('permissions/', views.ObjectPermissionListView.as_view(), name='objectpermission_list'),
    path('permissions/add/', views.ObjectPermissionEditView.as_view(), name='objectpermission_add'),
    path('permissions/edit/', views.ObjectPermissionBulkEditView.as_view(), name='objectpermission_bulk_edit'),
    path('permissions/delete/', views.ObjectPermissionBulkDeleteView.as_view(), name='objectpermission_bulk_delete'),
    path('permissions/<int:pk>/', include(get_model_urls('users', 'objectpermission'))),

]
