import strawberry
import strawberry_django

# Extends a type the earlier dummy_plugin's schema imports, anchoring the cross-plugin ordering contract.


@strawberry.type
class SiteTypeBExtension:
    models = ['dcim.site']

    @strawberry_django.field
    def dummy_plugin_b_field(self) -> str:
        return 'dummy-plugin-b-value'


type_extensions = [
    SiteTypeBExtension,
]
