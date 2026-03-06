from django.db import router
from django.db.models import signals
from taggit.managers import _TaggableManager
from taggit.utils import require_instance_manager

__all__ = (
    'NetBoxTaggableManager',
)


class NetBoxTaggableManager(_TaggableManager):
    """
    Extends taggit's _TaggableManager to replace the per-tag get_or_create loop in add() with a
    single bulk_create() call, reducing SQL queries from O(N) to O(1) when assigning tags.
    """

    @require_instance_manager
    def add(self, *tags, through_defaults=None, tag_kwargs=None, **kwargs):
        self._remove_prefetched_objects()
        if tag_kwargs is None:
            tag_kwargs = {}
        db = router.db_for_write(self.through, instance=self.instance)

        tag_objs = self._to_tag_model_instances(tags, tag_kwargs)
        new_ids = {t.pk for t in tag_objs}

        # Determine which tags are not already assigned to this object
        lookup = self._lookup_kwargs()
        vals = set(
            self.through._default_manager.using(db)
            .values_list("tag_id", flat=True)
            .filter(**(lookup), tag_id__in=new_ids)
        )
        new_ids -= vals

        if not new_ids:
            return

        signals.m2m_changed.send(
            sender=self.through,
            action="pre_add",
            instance=self.instance,
            reverse=False,
            model=self.through.tag_model(),
            pk_set=new_ids,
            using=db,
        )

        # Use a single bulk INSERT instead of one get_or_create per tag.
        self.through._default_manager.using(db).bulk_create(
            [
                self.through(tag=tag, **lookup, **(through_defaults or {}))
                for tag in tag_objs
                if tag.pk in new_ids
            ],
            ignore_conflicts=True,
        )

        signals.m2m_changed.send(
            sender=self.through,
            action="post_add",
            instance=self.instance,
            reverse=False,
            model=self.through.tag_model(),
            pk_set=new_ids,
            using=db,
        )
