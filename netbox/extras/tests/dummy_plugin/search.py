from netbox.search import SearchIndex
from .models import DummyModel


class DummyModelIndex(SearchIndex):
    model = DummyModel
    queryset = DummyModel.objects.all()
    url = 'plugins:dummy_plugin:dummy_models'


indexes = (
    DummyModelIndex,
)
