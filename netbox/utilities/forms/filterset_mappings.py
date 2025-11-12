# Mapping of filter form classes to their corresponding FilterSet classes
# This enables the FilterModifierMixin to verify which lookups are actually supported
# by checking the FilterSet's auto-generated lookup filters.
#
# Usage:
#   from utilities.forms.filterset_mappings import FILTERSET_MAPPINGS
#   from .forms.filtersets import XFilterForm
#   from .filtersets import XFilterSet
#   FILTERSET_MAPPINGS[XFilterForm] = XFilterSet

FILTERSET_MAPPINGS = {}
