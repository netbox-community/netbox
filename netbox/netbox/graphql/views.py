from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.urls import reverse
from graphene_django.views import GraphQLView as GraphQLView_
from rest_framework.exceptions import AuthenticationFailed

from netbox.api.authentication import TokenAuthentication


class GraphQLView(GraphQLView_):
    """
    Extends graphene_django's GraphQLView to support DRF's token-based authentication.
    """
    def dispatch(self, request, *args, **kwargs):

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

            # If this is a human user, send a redirect to the login page
            if self.request_wants_html(request):
                return redirect_to_login(reverse('graphql'))

            return HttpResponseForbidden("No credentials provided.")

        return super().dispatch(request, *args, **kwargs)
