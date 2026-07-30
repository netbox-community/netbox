from netbox.event_rules import EventRuleAction

__all__ = (
    'DummyRaisingAction',
)


class DummyRaisingAction(EventRuleAction):
    """
    Defined here (a real PluginConfig app), not inline in a test module, so it genuinely exercises
    process_event_rules()'s plugin-vs-core exception handling. Not auto-registered; tests
    register/unregister it explicitly.
    """
    slug = 'dummy_plugin.raising_action'
    label = 'Dummy Raising Action'
    object_required = False

    def enqueue(self, **kwargs):
        raise RuntimeError("intentional failure for test")
