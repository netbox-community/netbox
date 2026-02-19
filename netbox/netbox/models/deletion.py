import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.db import router
from django.db.models.deletion import CASCADE, Collector

logger = logging.getLogger("netbox.models.deletion")


class CustomCollector(Collector):
    """
    Override Django's stock Collector to handle GenericRelations and ensure proper ordering of cascading deletions.
    """

    def collect(
        self,
        objs,
        source=None,
        nullable=False,
        collect_related=True,
        source_attr=None,
        reverse_dependency=False,
        keep_parents=False,
        fail_on_restricted=True,
    ):
        # By default, Django will force the deletion of dependent objects before the parent only if the ForeignKey field
        # is not nullable. We want to ensure proper ordering regardless, so if the ForeignKey has `on_delete=CASCADE`
        # applied, we set `nullable` to False when calling `collect()`.
        if objs and source and source_attr:
            model = objs[0].__class__
            field = model._meta.get_field(source_attr)
            if field.remote_field.on_delete == CASCADE:
                nullable = False

        super().collect(
            objs,
            source=source,
            nullable=nullable,
            collect_related=collect_related,
            source_attr=source_attr,
            reverse_dependency=reverse_dependency,
            keep_parents=keep_parents,
            fail_on_restricted=fail_on_restricted,
        )

        # Add GenericRelations to the dependency graph
        processed_relations = set()
        for _, instances in list(self.data.items()):
            for instance in instances:
                # Get all GenericRelations for this model
                for field in instance._meta.private_fields:
                    if isinstance(field, GenericRelation):
                        # Create a unique key for this relation
                        relation_key = f"{instance._meta.model_name}.{field.name}"
                        if relation_key in processed_relations:
                            continue
                        processed_relations.add(relation_key)

                        # Add the model that the generic relation points to as a dependency
                        self.add_dependency(field.related_model, instance, reverse_dependency=True)


class DeleteMixin:
    """
    Mixin to override the model delete function to use our custom collector.
    """

    def delete(self, using=None, keep_parents=False):
        """
        Override delete to use our custom collector.
        """
        using = using or router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, (
            f"{self._meta.object_name} object can't be deleted because its "
            f"{self._meta.pk.attname} attribute is set to None."
        )

        collector = CustomCollector(using=using)
        collector.collect([self], keep_parents=keep_parents)

        return collector.delete()

    delete.alters_data = True

    @classmethod
    def verify_mro(cls, instance):
        """
        Verify that this mixin is first in the MRO.
        """
        mro = instance.__class__.__mro__
        if mro.index(cls) != 0:
            raise RuntimeError(f"{cls.__name__} must be first in the MRO. Current MRO: {mro}")
