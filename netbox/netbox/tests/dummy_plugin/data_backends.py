from contextlib import contextmanager

from netbox.data_backends import DataBackend


class DummyBackend(DataBackend):
    name = 'dummy'
    label = 'Dummy'
    is_local = True

    @contextmanager
    def fetch(self):
        yield '/tmp'


backends = (
    DummyBackend,
)
