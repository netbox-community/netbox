from cacheops.query import ManagerMixin, no_invalidation, _old_objs


# Monkey-patch cacheops' _pre_save() signal receiver. This is needed to mark the sending model's QuerySet as
# unrestricted.
def _pre_save(self, sender, instance, using, **kwargs):
    if not (instance.pk is None or instance._state.adding or no_invalidation.active):
        try:
            qs = sender.objects.using(using)
            if hasattr(qs, 'restrict'):
                qs = qs.unrestricted()
            _old_objs.__dict__[sender, instance.pk] = qs.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass


ManagerMixin._pre_save = _pre_save
