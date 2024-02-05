from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'users'
urlpatterns = [

    # Tokens
    path('tokens/', views.TokenListView.as_view(), name='token_list'),
    path('tokens/add/', views.TokenEditView.as_view(), name='token_add'),
    path('tokens/import/', views.TokenBulkImportView.as_view(), name='token_import'),
    path('tokens/edit/', views.TokenBulkEditView.as_view(), name='token_bulk_edit'),
    path('tokens/delete/', views.TokenBulkDeleteView.as_view(), name='token_bulk_delete'),
    path('tokens/<int:pk>/', include(get_model_urls('users', 'token'))),

    # Users
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserEditView.as_view(), name='user_add'),
    path('users/edit/', views.UserBulkEditView.as_view(), name='user_bulk_edit'),
    path('users/import/', views.UserBulkImportView.as_view(), name='user_import'),
    path('users/delete/', views.UserBulkDeleteView.as_view(), name='user_bulk_delete'),
    path('users/<int:pk>/', include(get_model_urls('users', 'user'))),

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
