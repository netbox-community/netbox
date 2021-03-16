from django.contrib.postgres.fields.array import ArrayContains

from dcim.utils import object_to_path_node


class PathContains(ArrayContains):

    def get_prep_lookup(self):
        self.rhs = [object_to_path_node(self.rhs)]
        return super().get_prep_lookup()
