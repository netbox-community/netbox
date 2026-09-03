from django.apps import AppConfig


class GraphQLConfig(AppConfig):
    name = 'netbox.graphql'
    label = 'netbox_graphql'

    def ready(self):
        # Runs after every plugin's ready(), so schema errors fail django.setup() instead of the first request.
        from netbox.graphql import schema  # noqa: F401
        from netbox.graphql.utils import validate_extension_targets

        validate_extension_targets()
