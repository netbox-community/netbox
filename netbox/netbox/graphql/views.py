from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed
from strawberry.django.views import GraphQLView

from netbox.api.authentication import TokenAuthentication
from netbox.config import get_config


class NetBoxGraphQLView(GraphQLView):
    """
    Extends strawberry's GraphQLView to support DRF's token-based authentication.
    """

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        config = get_config()

        # Enforce GRAPHQL_ENABLED
        if not config.GRAPHQL_ENABLED:
            return HttpResponseNotFound("The GraphQL API is not enabled.")

        # Attempt to authenticate the user using a DRF token, if provided
        if not request.user.is_authenticated:
            authenticator = TokenAuthentication()
            try:
                auth_info = authenticator.authenticate(request)
                if auth_info is not None:
                    request.user = auth_info[0]  # User object
            except AuthenticationFailed as exc:
                return HttpResponseForbidden(exc.detail)

        # Enforce LOGIN_REQUIRED
        if settings.LOGIN_REQUIRED and not request.user.is_authenticated:
            if request.accepts("text/html"):
                return redirect_to_login(reverse('graphql'))
            else:
                return HttpResponseForbidden("No credentials provided.")

        return super().dispatch(request, *args, **kwargs)
