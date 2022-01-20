from django.views.generic import View

from utilities.views import ObjectPermissionRequiredMixin


class GenericView(ObjectPermissionRequiredMixin, View):
    """
    Base view class for reusable generic views.

    Attributes:
        queryset: Django QuerySet from which the object(s) will be fetched
        template_name: The name of the HTML template file to render
    """
    queryset = None
    template_name = None
