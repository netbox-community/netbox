from rest_framework.routers import DefaultRouter, Route


class NetBoxRouter(DefaultRouter):
    """
    Extend DRF's built-in DefaultRouter to:
    1. Support bulk operations
    2. Alphabetically order endpoints under the root view
    3. Support mapping additional HTTP methods on the detail route to named actions
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Update the list view mappings to support bulk operations
        self.routes[0].mapping.update({
            'put': 'bulk_update',
            'patch': 'bulk_partial_update',
            'delete': 'bulk_destroy',
        })

    def get_routes(self, viewset):
        routes = super().get_routes(viewset)

        # A ViewSet may map additional HTTP methods on its detail route to named actions by declaring a
        # `detail_route_mapping` (e.g. {'post': 'run'}). DRF's detail route maps only the standard CRUD
        # methods; without this, such a handler must be declared as a raw HTTP method (e.g. post()), which
        # is bound to every route of the ViewSet and is invisible to both per-action permissions and schema
        # generation.
        if mapping := getattr(viewset, 'detail_route_mapping', None):
            routes = [
                route._replace(mapping={**route.mapping, **mapping})
                if isinstance(route, Route) and route.detail else route
                for route in routes
            ]

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
