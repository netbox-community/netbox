from netbox.tests.dummy_plugin.graphql import DummyModelType
from netbox.tests.dummy_plugin.models import DummyModel
from utilities.testing import APIViewTestCases


class DummyModelGraphQLTestCase(APIViewTestCases.GraphQLTestCase):
    model = DummyModel
    type_class = DummyModelType
    graphql_base_name = 'dummymodel'
    graphql_auto_filter_required = False
    graphql_object_permission_assertions = False

    @classmethod
    def setUpTestData(cls):
        DummyModel.objects.bulk_create((
            DummyModel(name='Dummy 1', number=1),
            DummyModel(name='Dummy 2', number=2),
            DummyModel(name='Dummy 3', number=3),
        ))
