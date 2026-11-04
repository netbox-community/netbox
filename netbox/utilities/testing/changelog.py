import sys

__all__ = (
    'PRECHANGE_SNAPSHOT_EXEMPT',
    'assert_prechange_snapshot',
)

# Call sites permitted to record an update without first calling snapshot(), as (module, function qualname)
PRECHANGE_SNAPSHOT_EXEMPT = {
    # Known issues; remove each entry once fixed
    ('dcim.models.cables', 'Cable.save'),  # The second save() when creating a Cable records a spurious update
    ('dcim.signals', 'update_mac_address_interface'),
    ('netbox.models.features', 'SyncedDataMixin.sync'),
    ('wireless.signals', 'update_connected_interfaces'),
}


def assert_prechange_snapshot(instance):
    """
    Raise AssertionError if an update to `instance` is being recorded without a prechange snapshot, unless a call
    site in PRECHANGE_SNAPSHOT_EXEMPT is on the stack.
    """
    if hasattr(instance, '_prechange_snapshot'):
        return
    frame = sys._getframe(1)
    while frame is not None:
        if (frame.f_globals.get('__name__'), frame.f_code.co_qualname) in PRECHANGE_SNAPSHOT_EXEMPT:
            return
        frame = frame.f_back
    raise AssertionError(
        f"{instance._meta.label} {instance.pk} was updated without calling snapshot() first; its change record "
        f"will have no prechange data."
    )
