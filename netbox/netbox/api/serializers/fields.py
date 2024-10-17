from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from utilities.views import get_viewname

__all__ = (
    'NetBoxAPIHyperlinkedIdentityField',
    'NetBoxURLHyperlinkedIdentityField',
)


class BaseNetBoxHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    Overrides HyperlinkedIdentityField to use standard NetBox view naming
    instead of passing in the view_name.  Initialize with a blank view_name
    and it will get replaced in the get_url call.  Derived classes must
    define a get_view_name.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(view_name="", *args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}

        view_name = self.get_view_name(obj)
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)

    def get_view_name(self, model):
        raise NotImplementedError(_('{class_name} must implement get_view_name()').format(
            class_name=self.__class__.__name__
        ))


class NetBoxAPIHyperlinkedIdentityField(BaseNetBoxHyperlinkedIdentityField):

    def get_view_name(self, model):
        return get_viewname(model=model, action='detail', rest_api=True)


class NetBoxURLHyperlinkedIdentityField(BaseNetBoxHyperlinkedIdentityField):

    def get_view_name(self, model):
        return get_viewname(model=model)
