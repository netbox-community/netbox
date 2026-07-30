from netbox.event_rules import EventRuleAction

__all__ = (
    'DummyRaisingAction',
)


class DummyRaisingAction(EventRuleAction):
    """
    Not wired into DummyPluginConfig.event_rule_actions (so it is not auto-registered on every
    test run); tests register/unregister it explicitly. Defined here rather than inline in a
    test module so that it is genuinely owned by a PluginConfig app, exercising the same
    plugin-vs-core distinction process_event_rules() makes for exception handling.
    """
    slug = 'dummy_plugin.raising_action'
    label = 'Dummy Raising Action'
    object_required = False

    def enqueue(self, **kwargs):
        raise RuntimeError("intentional failure for test")
