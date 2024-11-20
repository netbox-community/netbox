from django.urls import include, path

from utilities.urls import get_model_urls
from . import views  # noqa F401

app_name = 'ipam'
urlpatterns = [

    path('asn-ranges/', include(get_model_urls('ipam', 'asnrange', detail=False))),
    path('asn-ranges/<int:pk>/', include(get_model_urls('ipam', 'asnrange'))),

    path('asns/', include(get_model_urls('ipam', 'asn', detail=False))),
    path('asns/<int:pk>/', include(get_model_urls('ipam', 'asn'))),

    path('vrfs/', include(get_model_urls('ipam', 'vrf', detail=False))),
    path('vrfs/<int:pk>/', include(get_model_urls('ipam', 'vrf'))),

    path('route-targets/', include(get_model_urls('ipam', 'routetarget', detail=False))),
    path('route-targets/<int:pk>/', include(get_model_urls('ipam', 'routetarget'))),

    path('rirs/', include(get_model_urls('ipam', 'rir', detail=False))),
    path('rirs/<int:pk>/', include(get_model_urls('ipam', 'rir'))),

    path('aggregates/', include(get_model_urls('ipam', 'aggregate', detail=False))),
    path('aggregates/<int:pk>/', include(get_model_urls('ipam', 'aggregate'))),

    path('roles/', include(get_model_urls('ipam', 'role', detail=False))),
    path('roles/<int:pk>/', include(get_model_urls('ipam', 'role'))),

    path('prefixes/', include(get_model_urls('ipam', 'prefix', detail=False))),
    path('prefixes/<int:pk>/', include(get_model_urls('ipam', 'prefix'))),

    path('ip-ranges/', include(get_model_urls('ipam', 'iprange', detail=False))),
    path('ip-ranges/<int:pk>/', include(get_model_urls('ipam', 'iprange'))),

    path('ip-addresses/', include(get_model_urls('ipam', 'ipaddress', detail=False))),
    path('ip-addresses/<int:pk>/', include(get_model_urls('ipam', 'ipaddress'))),

    path('fhrp-groups/', include(get_model_urls('ipam', 'fhrpgroup', detail=False))),
    path('fhrp-groups/<int:pk>/', include(get_model_urls('ipam', 'fhrpgroup'))),

    path('fhrp-group-assignments/', include(get_model_urls('ipam', 'fhrpgroupassignment', detail=False))),
    path('fhrp-group-assignments/<int:pk>/', include(get_model_urls('ipam', 'fhrpgroupassignment'))),

    path('vlan-groups/', include(get_model_urls('ipam', 'vlangroup', detail=False))),
    path('vlan-groups/<int:pk>/', include(get_model_urls('ipam', 'vlangroup'))),

    path('vlans/', include(get_model_urls('ipam', 'vlan', detail=False))),
    path('vlans/<int:pk>/', include(get_model_urls('ipam', 'vlan'))),

    path('vlan-translation-policies/', include(get_model_urls('ipam', 'vlantranslationpolicy', detail=False))),
    path('vlan-translation-policies/<int:pk>/', include(get_model_urls('ipam', 'vlantranslationpolicy'))),

    path('vlan-translation-rules/', include(get_model_urls('ipam', 'vlantranslationrule', detail=False))),
    path('vlan-translation-rules/<int:pk>/', include(get_model_urls('ipam', 'vlantranslationrule'))),

    path('service-templates/', include(get_model_urls('ipam', 'servicetemplate', detail=False))),
    path('service-templates/<int:pk>/', include(get_model_urls('ipam', 'servicetemplate'))),

    path('services/', include(get_model_urls('ipam', 'service', detail=False))),
    path('services/<int:pk>/', include(get_model_urls('ipam', 'service'))),
]
