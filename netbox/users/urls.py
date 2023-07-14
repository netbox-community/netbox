from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'users'
urlpatterns = [

    # User
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('preferences/', views.UserConfigView.as_view(), name='preferences'),
    path('password/', views.ChangePasswordView.as_view(), name='change_password'),

    # Users
    path('users/', views.NetBoxUserListView.as_view(), name='netboxuser_list'),
    path('users/add/', views.NetBoxUserEditView.as_view(), name='netboxuser_add'),
    path('users/edit/', views.NetBoxUserBulkEditView.as_view(), name='netboxuser_bulk_edit'),
    path('users/delete/', views.NetBoxUserBulkDeleteView.as_view(), name='netboxuser_bulk_delete'),
    path('users/<int:pk>/', include(get_model_urls('users', 'netboxuser'))),

    # Groups
    path('groups/', views.NetBoxGroupListView.as_view(), name='netboxgroup_list'),
    path('groups/add/', views.NetBoxGroupEditView.as_view(), name='netboxgroup_add'),
    path('groups/import/', views.NetBoxGroupBulkImportView.as_view(), name='netboxgroup_import'),
    path('groups/delete/', views.NetBoxGroupBulkDeleteView.as_view(), name='netboxgroup_bulk_delete'),
    path('groups/<int:pk>/', include(get_model_urls('users', 'netboxgroup'))),

    # Permissions
    path('permissions/', views.ObjectPermissionListView.as_view(), name='objectpermission_list'),
    path('permissions/add/', views.ObjectPermissionEditView.as_view(), name='objectpermission_add'),
    path('permissions/edit/', views.ObjectPermissionBulkEditView.as_view(), name='objectpermission_bulk_edit'),
    path('permissions/delete/', views.ObjectPermissionBulkDeleteView.as_view(), name='objectpermission_bulk_delete'),
    path('permissions/<int:pk>/', include(get_model_urls('users', 'objectpermission'))),

    # API tokens
    path('api-tokens/', views.TokenListView.as_view(), name='token_list'),
    path('api-tokens/add/', views.TokenEditView.as_view(), name='token_add'),
    path('api-tokens/<int:pk>/', include(get_model_urls('users', 'token'))),

]
