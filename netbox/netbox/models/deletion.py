import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.db import router
from django.db.models.deletion import Collector

logger = logging.getLogger("netbox.models.deletion")


class CustomCollector(Collector):
    """
    Custom collector that handles GenericRelations correctly.
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
        """
        Override collect to first collect standard dependencies,
        then add GenericRelations to the dependency graph.
        """
        # Call parent collect first to get all standard dependencies
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

        # Track which GenericRelations we've already processed to prevent infinite recursion
        processed_relations = set()

        # Now add GenericRelations to the dependency graph
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
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name,
            self._meta.pk.attname,
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
