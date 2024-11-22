from django.urls import include, path

from utilities.urls import get_model_urls
from . import views  # noqa F401

app_name = 'users'
urlpatterns = [

    path('tokens/', include(get_model_urls('users', 'token', detail=False))),
    path('tokens/<int:pk>/', include(get_model_urls('users', 'token'))),

    path('users/', include(get_model_urls('users', 'user', detail=False))),
    path('users/<int:pk>/', include(get_model_urls('users', 'user'))),

    path('groups/', include(get_model_urls('users', 'group', detail=False))),
    path('groups/<int:pk>/', include(get_model_urls('users', 'group'))),

    path('permissions/', include(get_model_urls('users', 'objectpermission', detail=False))),
    path('permissions/<int:pk>/', include(get_model_urls('users', 'objectpermission'))),

]
