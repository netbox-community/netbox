__all__ = (
    'assert_prechange_snapshot',
)


def assert_prechange_snapshot(instance):
    """
    Raise AssertionError if an update to `instance` is being recorded without a prechange snapshot.
    """
    # A snapshot read from the database by the pre_save fallback does not count
    if hasattr(instance, '_prechange_snapshot') and not instance.__dict__.get('_prechange_snapshot_from_db'):
        return
    raise AssertionError(
        f"{instance._meta.label} {instance.pk} was updated without calling snapshot() first; its change record "
        f"will have no prechange data."
    )
