from django.db import router
from django.db.models import signals
from taggit.managers import TaggableManager, _TaggableManager
from taggit.utils import require_instance_manager

__all__ = (
    'NetBoxTaggableManager',
    'NetBoxTaggableManagerField',
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
            .filter(**lookup, tag_id__in=new_ids)
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


class NetBoxTaggableManagerField(TaggableManager):
    """
    Subclass of taggit's TaggableManager that interpolates `%(app_label)s` and `%(class)s` in
    `related_name`. taggit's contribute_to_class() bypasses Django's RelatedField, which is what
    normally performs this substitution, so without this two taggable models that share a class
    name (e.g. from different plugins) collide on Tag's reverse accessor.
    """
    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        if not cls._meta.abstract and self.remote_field.related_name:
            self.remote_field.related_name = self.remote_field.related_name % {
                'class': cls.__name__.lower(),
                'app_label': cls._meta.app_label.lower(),
            }

    def deconstruct(self):
        # Emit the upstream taggit path and omit related_name so existing migrations remain
        # equivalent and no AlterField is produced for every TagsMixin consumer. related_name
        # has no effect on the database schema; it is reapplied on model load. Only safe while
        # this subclass adds no field attributes that affect schema — if that changes, restore
        # the real path so migrations capture the diff.
        name, _path, args, kwargs = super().deconstruct()
        kwargs.pop('related_name', None)
        return name, 'taggit.managers.TaggableManager', args, kwargs
