from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'account'
urlpatterns = [

    # Account views
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscriptions'),
    path('preferences/', views.UserConfigView.as_view(), name='preferences'),
    path('password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('api-tokens/', views.UserTokenListView.as_view(), name='usertoken_list'),
    path('api-tokens/add/', views.UserTokenEditView.as_view(), name='usertoken_add'),
    path('api-tokens/<int:pk>/', include(get_model_urls('account', 'usertoken'))),

]
