from django.urls import include, path

from utilities.urls import get_model_urls
from . import views  # noqa F401

app_name = 'vpn'
urlpatterns = [

    path('tunnel-groups/', include(get_model_urls('vpn', 'tunnelgroup', detail=False))),
    path('tunnel-groups/<int:pk>/', include(get_model_urls('vpn', 'tunnelgroup'))),

    path('tunnels/', include(get_model_urls('vpn', 'tunnel', detail=False))),
    path('tunnels/<int:pk>/', include(get_model_urls('vpn', 'tunnel'))),

    path('tunnel-terminations/', include(get_model_urls('vpn', 'tunneltermination', detail=False))),
    path('tunnel-terminations/<int:pk>/', include(get_model_urls('vpn', 'tunneltermination'))),

    path('ike-proposals/', include(get_model_urls('vpn', 'ikeproposal', detail=False))),
    path('ike-proposals/<int:pk>/', include(get_model_urls('vpn', 'ikeproposal'))),

    path('ike-policies/', include(get_model_urls('vpn', 'ikepolicy', detail=False))),
    path('ike-policies/<int:pk>/', include(get_model_urls('vpn', 'ikepolicy'))),

    path('ipsec-proposals/', include(get_model_urls('vpn', 'ipsecproposal', detail=False))),
    path('ipsec-proposals/<int:pk>/', include(get_model_urls('vpn', 'ipsecproposal'))),

    path('ipsec-policies/', include(get_model_urls('vpn', 'ipsecpolicy', detail=False))),
    path('ipsec-policies/<int:pk>/', include(get_model_urls('vpn', 'ipsecpolicy'))),

    path('ipsec-profiles/', include(get_model_urls('vpn', 'ipsecprofile', detail=False))),
    path('ipsec-profiles/<int:pk>/', include(get_model_urls('vpn', 'ipsecprofile'))),

    path('l2vpns/', include(get_model_urls('vpn', 'l2vpn', detail=False))),
    path('l2vpns/<int:pk>/', include(get_model_urls('vpn', 'l2vpn'))),

    path('l2vpn-terminations/', include(get_model_urls('vpn', 'l2vpntermination', detail=False))),
    path('l2vpn-terminations/<int:pk>/', include(get_model_urls('vpn', 'l2vpntermination'))),

]
