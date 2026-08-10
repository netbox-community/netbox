from rest_framework.routers import DefaultRouter


class NetBoxRouter(DefaultRouter):
    """
    Extend DRF's built-in DefaultRouter to:
    1. Support bulk operations
    2. Alphabetically order endpoints under the root view
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Update the list view mappings to support bulk operations
        self.routes[0].mapping.update({
            'put': 'bulk_update',
            'patch': 'bulk_partial_update',
            'delete': 'bulk_destroy',
        })

    def get_api_root_view(self, api_urls=None):
        """
        Wrap DRF's DefaultRouter to return an alphabetized list of endpoints.
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in sorted(self.registry, key=lambda x: x[0]):
            api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict)
