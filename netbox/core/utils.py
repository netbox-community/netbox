__all__ = (
    'FakeTempDirectory',
)


class FakeTempDirectory:
    """
    Mimic tempfile.TemporaryDirectory to represent a real local path.
    """
    def __init__(self, name):
        self.name = name

    def cleanup(self):
        pass
