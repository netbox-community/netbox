from graphene_django.views import GraphQLView as GraphQLView_
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings


class GraphQLView(GraphQLView_):
    """
    Extends grpahene_django's GraphQLView to support DRF's token-based authentication.
    """
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraphQLView, cls).as_view(*args, **kwargs)

        # Apply DRF permission and authentication classes
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = api_view(['GET', 'POST'])(view)

        return view
