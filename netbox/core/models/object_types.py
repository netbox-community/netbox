import inspect
from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, models
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.plugins import PluginConfig
from netbox.registry import registry
from utilities.string import title

__all__ = (
    'ObjectType',
    'ObjectTypeManager',
    'ObjectTypeQuerySet',
)


class ObjectTypeQuerySet(models.QuerySet):

    def create(self, **kwargs):
        # If attempting to create a new ObjectType for a given app_label & model, replace those kwargs
        # with a reference to the ContentType (if one exists).
        if (app_label := kwargs.get('app_label')) and (model := kwargs.get('model')):
            try:
                kwargs['contenttype_ptr'] = ContentType.objects.get(app_label=app_label, model=model)
            except ObjectDoesNotExist:
                pass
        return super().create(**kwargs)


class ObjectTypeManager(models.Manager):

    def get_queryset(self):
        return ObjectTypeQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, app_label, model):
        """
        Retrieve an ObjectType by its application label & model name.

        This method exists to provide parity with ContentTypeManager.
        """
        return self.get(app_label=app_label, model=model)

    # TODO: Remove in NetBox v4.5
    def get_for_id(self, id):
        """
        Retrieve an ObjectType by its primary key (numeric ID).

        This method exists to provide parity with ContentTypeManager.
        """
        return self.get(pk=id)

    def _get_opts(self, model, for_concrete_model):
        if for_concrete_model:
            model = model._meta.concrete_model
        return model._meta

    def get_for_model(self, model, for_concrete_model=True):
        """
        Retrieve or create and return the ObjectType for a model.
        """
        from netbox.models.features import get_model_features, model_is_public

        # TODO: Remove this in NetBox v5.0
        # If the ObjectType table has not yet been provisioned (e.g. because we're in a pre-v4.4 migration),
        # fall back to ContentType.
        if 'core_objecttype' not in connection.introspection.table_names():
            ct = ContentType.objects.get_for_model(model, for_concrete_model=for_concrete_model)
            ct.features = get_model_features(ct.model_class())
            return ct

        if not inspect.isclass(model):
            model = model.__class__
        opts = self._get_opts(model, for_concrete_model)

        try:
            # Use .get() instead of .get_or_create() initially to ensure db_for_read is honored (Django bug #20401).
            ot = self.get(app_label=opts.app_label, model=opts.model_name)
        except self.model.DoesNotExist:
            # If the ObjectType doesn't exist, create it. (Use .get_or_create() to avoid race conditions.)
            ot = self.get_or_create(
                app_label=opts.app_label,
                model=opts.model_name,
                public=model_is_public(model),
                features=get_model_features(model),
            )[0]

        return ot

    def get_for_models(self, *models, for_concrete_models=True):
        """
        Retrieve or create the ObjectTypes for multiple models, returning a mapping {model: ObjectType}.

        This method exists to provide parity with ContentTypeManager.
        """
        from netbox.models.features import get_model_features, model_is_public
        results = {}

        # Compile the model and options mappings
        needed_models = defaultdict(set)
        needed_opts = defaultdict(list)
        for model in models:
            if not inspect.isclass(model):
                model = model.__class__
            opts = self._get_opts(model, for_concrete_models)
            needed_models[opts.app_label].add(opts.model_name)
            needed_opts[(opts.app_label, opts.model_name)].append(model)

        # Fetch existing ObjectType from the database
        condition = Q(
            *(
                Q(('app_label', app_label), ('model__in', model_names))
                for app_label, model_names in needed_models.items()
            ),
            _connector=Q.OR,
        )
        for ot in self.filter(condition):
            opts_models = needed_opts.pop((ot.app_label, ot.model), [])
            for model in opts_models:
                results[model] = ot

        # Create any missing ObjectTypes
        for (app_label, model_name), opts_models in needed_opts.items():
            for model in opts_models:
                results[model] = self.create(
                    app_label=app_label,
                    model=model_name,
                    public=model_is_public(model),
                    features=get_model_features(model),
                )

        return results

    def public(self):
        """
        Includes only ObjectTypes for "public" models.

        Filter the base queryset to return only ObjectTypes corresponding to public models; those which are intended
        for reference by other objects within the application.
        """
        return self.get_queryset().filter(public=True)

    def with_feature(self, feature):
        """
        Return ObjectTypes only for models which support the given feature.

        Only ObjectTypes which list the specified feature will be included. Supported features are declared in the
        application registry under `registry["model_features"]`. For example, we can find all ObjectTypes for models
        which support event rules with:

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
        ordering = ('app_label', 'model')
        indexes = [
            GinIndex(fields=['features']),
        ]

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
