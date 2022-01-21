from django.views.generic import View

from utilities.views import ObjectPermissionRequiredMixin


class BaseObjectView(ObjectPermissionRequiredMixin, View):
    """
    Base view class for reusable generic views.

    Attributes:
        queryset: Django QuerySet from which the object(s) will be fetched
        template_name: The name of the HTML template file to render
    """
    queryset = None
    template_name = None

    def get_extra_context(self, request, instance):
        """
        Return any additional context data to include when rendering the template.

        Args:
            request: The current request
            instance: The object being viewed
        """
        return {}


class BaseMultiObjectView(ObjectPermissionRequiredMixin, View):
    """
    Base view class for reusable generic views.

    Attributes:
        queryset: Django QuerySet from which the object(s) will be fetched
        template_name: The name of the HTML template file to render
    """
    queryset = None
    template_name = None

    def get_extra_context(self, request):
        """
        Return any additional context data to include when rendering the template.

        Args:
            request: The current request
        """
        return {}
