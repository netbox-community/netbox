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
        # A ViewSet may map additional HTTP methods on its detail route to named actions by declaring a
        # `detail_route_mapping` (e.g. ScriptViewSet maps POST to its run() action). DRF's detail route
        # maps only the standard CRUD methods; absent this, such a handler must be declared as a raw HTTP
        # method (e.g. post()), which is bound to every route of the ViewSet and is invisible to both
        # per-action permissions and schema generation.
        detail_mapping = getattr(viewset, 'detail_route_mapping', {})

        routes = []
        for route in super().get_routes(viewset):
            # Route is a namedtuple, so _replace() is used to extend a mapping: assigning to it would
            # mutate the Route instances shared by all SimpleRouter subclasses.
            if not isinstance(route, Route):
                routes.append(route)
            elif route.detail:
                routes.append(route._replace(mapping={**route.mapping, **detail_mapping}))
            else:
                routes.append(route._replace(mapping={**route.mapping, **BULK_OPERATION_MAPPING}))

        return routes

    def get_api_root_view(self, api_urls=None):
        """
        Wrap DRF's DefaultRouter to return an alphabetized list of endpoints.
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in sorted(self.registry, key=lambda x: x[0]):
            api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict)
