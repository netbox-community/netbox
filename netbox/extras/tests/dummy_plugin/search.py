from netbox.search import SearchIndex
from .models import DummyModel


class DummyModelIndex(SearchIndex):
    model = DummyModel
    fields = (
        ('name', 100),
    )


indexes = (
    DummyModelIndex,
)
