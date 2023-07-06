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

    # API tokens
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

]
