from rest_framework.routers import Route

from netbox.api.routers import NetBoxRouter

from .views import ScriptViewSet

__all__ = (
    'ScriptRouter',
)


class ScriptRouter(NetBoxRouter):
    """
    Extend NetBoxRouter to map POST on the script detail route to ScriptViewSet.run(). DRF's detail route
    maps only the standard CRUD methods; absent this, run() must be declared as a raw post() method, which
    binds to every route of the ViewSet and is invisible to per-action permissions & schema generation.
    """
    def get_routes(self, viewset):
        if not issubclass(viewset, ScriptViewSet):
            return super().get_routes(viewset)

        # Extend the detail route template. Applied before super() expands the templates so that any
        # @action routes are untouched; _replace() avoids mutating the templates shared by all routers.
        routes = self.routes
        self.routes = [
            route._replace(mapping={**route.mapping, 'post': 'run'})
            if isinstance(route, Route) and route.detail else route
            for route in routes
        ]

        try:
            return super().get_routes(viewset)
        finally:
            self.routes = routes
