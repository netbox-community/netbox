from netbox.search import SearchIndex
from .models import DummyModel


class DummyModelIndex(SearchIndex):
    model = DummyModel
    queryset = DummyModel.objects.all()


indexes = (
    DummyModelIndex,
)
