import json

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from rest_framework.exceptions import AuthenticationFailed
from strawberry.django.views import GraphQLView

from netbox.api.authentication import TokenAuthentication
from netbox.config import get_config
from utilities.templatetags.builtins.tags import static_with_params


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
            return HttpResponseForbidden("No credentials provided.")

        return super().dispatch(request, *args, **kwargs)


@method_decorator(never_cache, name='dispatch')
class GraphiQLWorkerView(View):
    """
    Start one of the web workers used by GraphiQL's editor (Monaco).

    Browsers start workers only from the page's own origin, but static files may be served from
    elsewhere (e.g. S3). This script is served from NetBox's origin and imports the worker from its
    static URL. It is never cached, so a signed static URL is always current when Monaco restarts an
    idle worker.
    """
    workers = ('editor', 'graphql', 'json')

    def get(self, request, name):
        if not get_config().GRAPHQL_ENABLED or name not in self.workers:
            return HttpResponseNotFound()
        url = static_with_params(f'graphiql/{name}.worker.js', v=settings.RELEASE.version)
        return HttpResponse(f'importScripts({json.dumps(url)});', content_type='text/javascript')
