from rest_framework.routers import DefaultRouter, Route

# Additional HTTP methods mapped on the list route to support bulk operations
BULK_OPERATION_MAPPING = {
    'put': 'bulk_update',
    'patch': 'bulk_partial_update',
    'delete': 'bulk_destroy',
}


class NetBoxRouter(DefaultRouter):
    """
    Extend DRF's built-in DefaultRouter to:
    1. Support bulk operations
    2. Alphabetically order endpoints under the root view
    3. Map additional HTTP methods on the detail route to named actions
    """
    def get_routes(self, viewset):
        # A ViewSet may map extra HTTP methods on its detail route to named actions (e.g. ScriptViewSet
        # maps POST to run()), which DRF's standard CRUD mapping doesn't support
        detail_mapping = getattr(viewset, 'detail_route_mapping', {})

        # Extend the list & detail route templates. Applied before super() expands them so that @action
        # routes are untouched; _replace() avoids mutating the templates shared by all SimpleRouters.
        routes = self.routes
        self.routes = [
            route._replace(mapping={
                **route.mapping,
                **(detail_mapping if route.detail else BULK_OPERATION_MAPPING),
            }) if isinstance(route, Route) else route
            for route in routes
        ]

        try:
            return super().get_routes(viewset)
        finally:
            self.routes = routes

    def get_api_root_view(self, api_urls=None):
        """
        Wrap DRF's DefaultRouter to return an alphabetized list of endpoints.
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in sorted(self.registry, key=lambda x: x[0]):
            api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict)
