from django.urls import include, path

from utilities.urls import get_model_urls
from . import views  # noqa F401

app_name = 'wireless'
urlpatterns = (

    path('wireless-lan-groups/', include(get_model_urls('wireless', 'wirelesslangroup', detail=False))),
    path('wireless-lan-groups/<int:pk>/', include(get_model_urls('wireless', 'wirelesslangroup'))),

    path('wireless-lans/', include(get_model_urls('wireless', 'wirelesslan', detail=False))),
    path('wireless-lans/<int:pk>/', include(get_model_urls('wireless', 'wirelesslan'))),

    path('wireless-links/', include(get_model_urls('wireless', 'wirelesslink', detail=False))),
    path('wireless-links/<int:pk>/', include(get_model_urls('wireless', 'wirelesslink'))),

)
