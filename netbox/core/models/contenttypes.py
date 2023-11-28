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

    def with_feature(self, feature):
        """
        Return the ContentTypes only for models which are registered as supporting the specified feature. For example,
        we can find all ContentTypes for models which support webhooks with

            ContentType.objects.with_feature('event_rules')
        """
        if feature not in registry['model_features']:
            raise KeyError(
                f"{feature} is not a registered model feature! Valid features are: {registry['model_features'].keys()}"
            )

        q = Q()
        for app_label, models in registry['model_features'][feature].items():
            q |= Q(app_label=app_label, model__in=models)

        return self.get_queryset().filter(q)


class ContentType(ContentType_):
    """
    Wrap Django's native ContentType model to use our custom manager.
    """
    objects = ContentTypeManager()

    class Meta:
        proxy = True
