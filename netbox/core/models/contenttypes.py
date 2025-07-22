from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext as _

from netbox.plugins import PluginConfig
from netbox.registry import registry
from utilities.string import title

__all__ = (
    'ObjectType',
    'ObjectTypeManager',
)


class ObjectTypeManager(ContentTypeManager):

    def public(self):
        """
        Filter the base queryset to return only ObjectTypes corresponding to "public" models; those which are intended
        for reference by other objects.
        """
        return self.get_queryset().filter(public=True)

    def with_feature(self, feature):
        """
        Return the ContentTypes only for models which are registered as supporting the specified feature. For example,
        we can find all ContentTypes for models which support event rules with:

            ObjectType.objects.with_feature('event_rules')
        """
        if feature not in registry['model_features']:
            raise KeyError(
                f"{feature} is not a registered model feature! Valid features are: {registry['model_features'].keys()}"
            )
        return self.get_queryset().filter(features__contains=[feature])


class ObjectType(ContentType):
    """
    Wrap Django's native ContentType model to use our custom manager.
    """
    contenttype_ptr = models.OneToOneField(
        on_delete=models.CASCADE,
        to='contenttypes.ContentType',
        parent_link=True,
        primary_key=True,
        serialize=False,
        related_name='object_type',
    )
    public = models.BooleanField(
        default=False,
    )
    features = ArrayField(
        base_field=models.CharField(max_length=50),
        blank=True,
        null=True,
    )

    objects = ObjectTypeManager()

    class Meta:
        verbose_name = _('object type')
        verbose_name_plural = _('object types')

    @property
    def app_labeled_name(self):
        # Override ContentType's "app | model" representation style.
        return f"{self.app_verbose_name} > {title(self.model_verbose_name)}"

    @property
    def app_verbose_name(self):
        if model := self.model_class():
            return model._meta.app_config.verbose_name

    @property
    def model_verbose_name(self):
        if model := self.model_class():
            return model._meta.verbose_name

    @property
    def model_verbose_name_plural(self):
        if model := self.model_class():
            return model._meta.verbose_name_plural

    @property
    def is_plugin_model(self):
        if not (model := self.model_class()):
            return  # Return null if model class is invalid
        return isinstance(model._meta.app_config, PluginConfig)
