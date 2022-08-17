class CabledObjectMixin:

    def resolve_cable_end(self, info):
        # Handle empty values
        return self.cable_end or None
