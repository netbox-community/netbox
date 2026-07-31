from netbox.event_rules import EventRuleAction

__all__ = (
    'DummyRaisingAction',
)


class DummyRaisingAction(EventRuleAction):
    """A plugin action for testing process_event_rules() exception handling. Registered per-test, not on load."""
    slug = 'dummy_plugin.raising_action'
    label = 'Dummy Raising Action'
    object_required = False

    def enqueue(self, **kwargs):
        raise RuntimeError("intentional failure for test")
