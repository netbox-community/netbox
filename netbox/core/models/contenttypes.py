from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext as _

from netbox.plugins import PluginConfig
from netbox.registry import registry
from utilities.string import title

__all__ = (
    'ObjectType',
    'ObjectTypeManager',
)


class ObjectTypeQuerySet(models.QuerySet):

    def create(self, **kwargs):
        # If attempting to create a new ObjectType for a given app_label & model, replace those kwargs
        # with a reference to the ContentType (if one exists).
        if (app_label := kwargs.get('app_label')) and (model := kwargs.get('model')):
            try:
                kwargs['contenttype_ptr'] = ContentType.objects.get(app_label=app_label, model=model)
                kwargs.pop('app_label')
                kwargs.pop('model')
            except ObjectDoesNotExist:
                pass
        return super().create(**kwargs)


class ObjectTypeManager(models.Manager):

    def get_queryset(self):
        return ObjectTypeQuerySet(self.model, using=self._db)

    def create(self, **kwargs):
        return self.get_queryset().create(**kwargs)

    def _get_opts(self, model, for_concrete_model):
        if for_concrete_model:
            model = model._meta.concrete_model
        return model._meta

    def get_by_natural_key(self, app_label, model):
        return self.get(app_label=app_label, model=model)

    def get_for_id(self, id):
        return self.get(pk=id)

    def get_for_model(self, model, for_concrete_model=True):
        from netbox.models.features import get_model_features, model_is_public
        opts = self._get_opts(model, for_concrete_model)

        try:
            # Start with get() and not get_or_create() in order to use
            # the db_for_read (see #20401).
            ot = self.get(app_label=opts.app_label, model=opts.model_name)
        except self.model.DoesNotExist:
            # Not found in the database; we proceed to create it. This time
            # use get_or_create to take care of any race conditions.
            ot, __ = self.get_or_create(
                app_label=opts.app_label,
                model=opts.model_name,
                public=model_is_public(model),
                features=get_model_features(model.__class__),
            )
        return ot

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
        default=list,
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
