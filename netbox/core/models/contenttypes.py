from django.contrib.contenttypes.models import ContentType as ContentType_, ContentTypeManager as ContentTypeManager_
from django.db.models import Q

from netbox.registry import registry

__all__ = (
    'ContentType',
    'ContentTypeManager',
)


class ContentTypeManager(ContentTypeManager_):

    def public(self):
        """
        Filter the base queryset to return only ContentTypes corresponding to "public" models; those which are listed
        in registry['models'] and intended for reference by other objects.
        """
        q = Q()
        for app_label, models in registry['models'].items():
            q |= Q(app_label=app_label, model__in=models)
        return self.get_queryset().filter(q)


class ContentType(ContentType_):
    """
    Wrap Django's native ContentType model to use our custom manager.
    """
    objects = ContentTypeManager()

    class Meta:
        proxy = True
