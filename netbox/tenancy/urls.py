from django.urls import include, path

from utilities.urls import get_model_urls
from . import views  # noqa F401

app_name = 'tenancy'
urlpatterns = [

    path('tenant-groups/', include(get_model_urls('tenancy', 'tenantgroup', detail=False))),
    path('tenant-groups/<int:pk>/', include(get_model_urls('tenancy', 'tenantgroup'))),

    path('tenants/', include(get_model_urls('tenancy', 'tenant', detail=False))),
    path('tenants/<int:pk>/', include(get_model_urls('tenancy', 'tenant'))),

    path('contact-groups/', include(get_model_urls('tenancy', 'contactgroup', detail=False))),
    path('contact-groups/<int:pk>/', include(get_model_urls('tenancy', 'contactgroup'))),

    path('contact-roles/', include(get_model_urls('tenancy', 'contactrole', detail=False))),
    path('contact-roles/<int:pk>/', include(get_model_urls('tenancy', 'contactrole'))),

    path('contacts/', include(get_model_urls('tenancy', 'contact', detail=False))),
    path('contacts/<int:pk>/', include(get_model_urls('tenancy', 'contact'))),

    path('contact-assignments/', include(get_model_urls('tenancy', 'contactassignment', detail=False))),
    path('contact-assignments/<int:pk>/', include(get_model_urls('tenancy', 'contactassignment'))),

]
