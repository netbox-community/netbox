from netbox.event_rules import EventRuleAction

__all__ = (
    'DummyRaisingAction',
)


class DummyRaisingAction(EventRuleAction):
    """A stand-in plugin action for testing process_event_rules()'s exception handling. Not auto-registered."""
    slug = 'dummy_plugin.raising_action'
    label = 'Dummy Raising Action'
    object_required = False

    def enqueue(self, **kwargs):
        raise RuntimeError("intentional failure for test")
