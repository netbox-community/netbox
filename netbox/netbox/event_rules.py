from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.registry import registry
from utilities.choices import Choice

__all__ = (
    'EventRuleAction',
    'get_event_rule_action',
    'get_event_rule_action_choices',
    'register_event_rule_action',
)


class EventRuleAction:
    """
    Base class for a registered Event Rule action. Subclass this to add a new action type that an
    EventRule can dispatch to, whether defined in NetBox core or in a plugin.

    This module must not import any concrete Django models: it's imported by netbox.plugins (itself
    imported by netbox.settings, before the app registry is populated), so only registry-level
    bookkeeping belongs here. Subclasses that reference real models (e.g. NetBox's own
    WebhookAction/ScriptAction/NotificationAction) live in netbox.extras.event_rules instead, and are
    registered from ExtrasConfig.ready() once the app registry is available.

    Attributes:
        slug: A unique identifier for this action (e.g. "webhook", or "myplugin.run_check" for a
            plugin-provided action). A dotted namespace prefix is strongly recommended for
            plugin-provided actions to avoid collisions with other plugins or future core actions.
        label: The human-friendly name shown in the UI/API.
        description: An optional, longer description shown alongside the label (e.g. as a tooltip
            in the action_type dropdown).
        object_model: The model class (if any) which EventRule.action_object must be an instance of.
            May be left as None if this action never operates against a target object.
        object_required: Whether an action_object must be supplied for this action to be usable
            (default: False, matching object_model's default of None -- an action that declares
            an object_model should also set this to True). Independent of object_model: an action
            may declare an object_model but still treat the object as optional.
    """
    slug = None
    label = None
    description = None
    object_model = None
    object_required = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.slug:
            raise TypeError(f"{cls.__name__} must define a non-empty 'slug' attribute.")
        if not cls.label:
            raise TypeError(f"{cls.__name__} must define a 'label' attribute.")

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.slug}>"

    def get_object_queryset(self):
        """
        Return the queryset of objects eligible for selection as this action's action_object, or
        None if object_model is not set.
        """
        if self.object_model is None:
            return None
        return self.object_model.objects.all()

    def resolve_import_object(self, value):
        """
        Optional hook: resolve a CSV/bulk-import "action object" string to a model instance. Raise
        django.core.exceptions.ObjectDoesNotExist (or a subclass) if the value doesn't resolve.
        Return None (the default) if this action doesn't support bulk import.
        """
        return

    def _validate(self, *, action_object, action_data):
        """
        Entry point called from EventRule.clean(). Enforces the base object_required/object_model
        checks, then delegates to validate() for any action-specific validation.
        """
        if self.object_required and action_object is None:
            raise ValidationError({
                'action_object_id': _("This action requires a target object to be selected."),
            })
        if (
            action_object is not None and self.object_model is not None
            and not isinstance(action_object, self.object_model)
        ):
            raise ValidationError({
                'action_object_id': _("Selected object is not a valid {model}.").format(
                    model=self.object_model._meta.verbose_name
                ),
            })
        self.validate(action_object=action_object, action_data=action_data)

    def validate(self, *, action_object, action_data):
        """
        Optional hook: add custom validation, raising ValidationError on failure. No-op by
        default; no need to call super() -- _validate() above runs the base checks regardless.
        """
        pass

    def enqueue(self, *, event_rule, event_context, action_object, action_data):
        """
        Perform (or schedule) this action in response to a queued event. Implementations should
        not raise for conditions that are the fault of this EventRule's own configuration alone;
        log and return instead, so that other EventRules processed in the same batch are
        unaffected.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement enqueue()")


def register_event_rule_action(cls):
    """
    Register an EventRuleAction subclass. Can be used as a decorator, or called directly (e.g. when
    iterating a plugin's declared event_rule_actions):

        @register_event_rule_action
        class MyAction(EventRuleAction):
            slug = 'myplugin.my_action'
            ...

    Raises if the slug is already registered, so collisions are caught immediately rather than
    silently overwriting one another.
    """
    instance = cls()
    if instance.slug in registry['event_rule_actions']:
        raise ValidationError(f"An event rule action named {instance.slug} has already been registered!")
    registry['event_rule_actions'][instance.slug] = instance
    return cls


def get_event_rule_action(slug):
    return registry['event_rule_actions'].get(slug)


def get_event_rule_action_choices():
    return [
        Choice(action.slug, action.label, description=action.description)
        for action in registry['event_rule_actions'].values()
    ]
