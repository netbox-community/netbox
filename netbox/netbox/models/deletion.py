import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.db import router
from django.db.models.deletion import CASCADE, Collector
from django.utils.translation import gettext as _

logger = logging.getLogger("netbox.models.deletion")


class CountOnly:
    """
    A stand-in for a list of dependent instances that reports a count without holding any
    instances. Used on the delete-confirmation page for high-cardinality relations (e.g. a
    JobsMixin object's jobs) which we deliberately do not materialize (see #22812). It is a
    lenient, empty iterable: `len()` returns the true row count, but iterating yields nothing,
    so it slots into the same `{model: <iterable>}` mapping as real instance lists and renders
    as a non-expandable row.
    """
    # Template flag: distinguishes a count-only entry (no instances to list) from a real list,
    # so the confirmation page can render it without an expand/collapse affordance.
    count_only = True

    def __init__(self, count):
        self.count = count

    def __len__(self):
        return self.count

    def __iter__(self):
        return iter(())


class ConfirmCollector(Collector):
    """
    A display-only Collector used to enumerate the objects that would be deleted along with a
    given object, for rendering the delete confirmation page. It behaves like Django's stock
    Collector (preserving the full FK cascade graph and its ProtectedError/RestrictedError
    behavior) except that it does not descend into the `jobs` GenericRelation. A JobsMixin
    object can accumulate thousands of Jobs, each carrying large data/log_entries payloads;
    materializing them all just to render a confirmation page can exhaust memory (see #22812).
    Instead, the related Jobs are counted and recorded in `generic_relation_counts`.

    This is intentionally specific to Job, the only high-cardinality GenericRelation in the
    data model; it is not a general count-out over every GenericRelation. If another relation
    ever needs the same treatment, extend the check in collect() (and the matching write-path
    batching in JobsMixin/ScriptModule.delete) rather than assuming this already handles it.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generic_relation_counts = {}

    def collect(self, objs, source=None, *args, **kwargs):
        """
        Override collect() to count the `jobs` GenericRelation rather than descend into it.

        Django's Collector offers no per-relation skip hook, so we intercept the one call it
        makes when cascading into a GenericRelation: collect(sub_objs, source=model, ...), where
        `sub_objs` is a queryset of the related model. When that model is Job, we count the rows
        instead of collecting (and thus instantiating) them, and forward every other call to the
        stock implementation untouched. A directly-deleted Job (top-level call, source=None)
        still collects normally.
        """
        from core.models import Job

        if source is not None and getattr(objs, 'model', None) is Job:
            # Django calls this branch for the jobs relation even when there are none; only record
            # a count when there are actually jobs, so jobless objects don't get a spurious
            # "0 jobs" row on the delete-confirmation page.
            count = objs.count()
            if count:
                self.generic_relation_counts[Job] = self.generic_relation_counts.get(Job, 0) + count
            return None
        return super().collect(objs, source=source, *args, **kwargs)


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
        for _model, instances in list(self.data.items()):
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
        if self._get_pk_val() is None:
            raise ValueError(
                _("{object_name} object can't be deleted because its {pk_attname} attribute is set to None.").format(
                    object_name=self._meta.object_name,
                    pk_attname=self._meta.pk.attname,
                )
            )

        # Pass origin=self (matching Django's Model.delete) so signal receivers can tell that
        # cascaded child objects are being deleted as part of deleting this object.
        collector = CustomCollector(using=using, origin=self)
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
