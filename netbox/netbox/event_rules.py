import re

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from netbox.registry import registry
from utilities.choices import Choice
from utilities.string import enum_key

__all__ = (
    'EventRuleAction',
    'get_event_rule_action',
    'get_event_rule_action_choices',
    'get_event_rule_action_slugs',
    'register_event_rule_action',
)

# A slug must sanitize (via enum_key()) into a valid GraphQL enum member name, which rules out a
# leading digit or underscore. Hyphens are rejected outright rather than sanitized away, so that a
# slug always reads as it was written.
SLUG_RE = re.compile(r'^[a-z][a-z0-9_]*(\.[a-z0-9_]+)*$')


# This module must not import any concrete Django models: it's imported by netbox.plugins (itself
# imported by netbox.settings, before the app registry is populated), so only registry-level
# bookkeeping belongs here. Subclasses that reference real models (e.g. NetBox's own
# WebhookAction/ScriptAction/NotificationAction) live in netbox.extras.event_rules instead, and are
# registered from ExtrasConfig.ready() once the app registry is available.
class EventRuleAction:
    """
    Base class for a registered Event Rule action. Subclass this to add a new action type that an
    EventRule can dispatch to, whether defined in NetBox core or in a plugin.

    Registration instantiates the class once; that single instance serves every event rule, request,
    and background worker thread for the lifetime of the process. Implementations must therefore be
    stateless: enqueue() and validate() must not stash per-event data on self, as concurrent
    dispatches would race over it. Everything an action needs is passed in as arguments.

    Attributes:
        slug: A unique identifier for this action (e.g. "webhook", or "myplugin.run_check" for a
            plugin-provided action). Must begin with a lowercase letter, and may contain only
            letters, digits, underscores, and dot-separated segments thereafter -- no hyphens (use
            an underscore instead, e.g. "my_plugin.open_ticket"). A dotted namespace prefix is
            strongly recommended for plugin-provided actions to avoid collisions with other plugins
            or future core actions.
        label: The human-friendly name shown in the UI/API.
        description: An optional, longer description shown alongside the label (e.g. as a tooltip
            in the action_type dropdown).
        object_model: The model class (if any) which EventRule.action_object must be an instance of.
            May be left as None if this action never operates against a target object, in which
            case supplying an action_object is treated as a validation error.
        object_required: Whether an action_object must be supplied for this action to be usable.
            Defaults to False; set True (alongside object_model) when a target object is mandatory.
            An action may declare object_model but still treat the object as optional.
        object_label: The label for the object selection field on the event rule form. Defaults to
            object_model's verbose name.
    """
    slug = None
    label = None
    description = None
    object_model = None
    object_required = False
    object_label = None

    # Set per-instance by register_event_rule_action(); a subclass override is ignored. Determines
    # whether a dispatch-time exception from this action is isolated or propagates (see
    # process_event_rules() in extras.events).
    is_plugin_provided = True

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

    def get_object_label(self):
        """
        Return the label for this action's object selection field, or None if object_model is not
        set. Defaults to object_model's verbose name, unless object_label has been set explicitly.
        """
        if self.object_label:
            return self.object_label
        if self.object_model is None:
            return None
        return capfirst(self.object_model._meta.verbose_name)

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
        if action_object is not None:
            if self.object_model is None:
                raise ValidationError({
                    'action_object_id': _("This action does not operate against a target object."),
                })
            if not isinstance(action_object, self.object_model):
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


def register_event_rule_action(cls, *, is_plugin_provided=True):
    """
    Register an EventRuleAction subclass. Can be used as a decorator, or called directly (e.g. when
    iterating a plugin's declared event_rule_actions):

        @register_event_rule_action
        class MyAction(EventRuleAction):
            slug = 'myplugin.my_action'
            ...

    Raises ImproperlyConfigured if slug/label are missing, the slug is malformed, already
    registered, collides via enum_key() with another registered slug once both feed the GraphQL
    EventRuleActionEnum (see extras.graphql.enums), or object_required is set without an
    object_model to validate the object against. Checking slug/label here rather than at class
    definition means an intermediate base class shared by several concrete actions in a plugin can
    leave them unset.

    is_plugin_provided determines whether a dispatch-time exception from this action is isolated
    or propagates (see process_event_rules() in extras.events); defaults to True. NetBox's own
    core registrations (extras.apps.ExtrasConfig) pass False explicitly.
    """
    instance = cls()
    if not instance.slug:
        raise ImproperlyConfigured(f"{cls.__name__} must define a non-empty 'slug' attribute.")
    if not instance.label:
        raise ImproperlyConfigured(f"{cls.__name__} must define a 'label' attribute.")
    if instance.object_required and instance.object_model is None:
        # Unsatisfiable: an object is mandatory, yet any object supplied is rejected by _validate().
        raise ImproperlyConfigured(
            f"{cls.__name__} sets object_required but no object_model; a target object cannot be "
            f"required for an action which does not operate against one."
        )
    if not SLUG_RE.fullmatch(instance.slug):
        raise ImproperlyConfigured(
            f"Invalid event rule action slug {instance.slug!r}: must be lowercase, start with a "
            f"letter, and use only letters, digits, underscores, and dot-separated segments."
        )
    if instance.slug in registry['event_rule_actions']:
        raise ImproperlyConfigured(f"An event rule action named {instance.slug} has already been registered!")
    new_key = enum_key(instance.slug)
    for existing in registry['event_rule_actions'].values():
        if enum_key(existing.slug) == new_key:
            raise ImproperlyConfigured(
                f"Event rule action slug {instance.slug!r} collides with the already-registered "
                f"{existing.slug!r} once both are sanitized into a GraphQL enum member name."
            )
    instance.is_plugin_provided = is_plugin_provided
    registry['event_rule_actions'][instance.slug] = instance
    return cls


def get_event_rule_action(slug):
    return registry['event_rule_actions'].get(slug)


def get_event_rule_action_choices():
    return [
        Choice(action.slug, action.label, description=action.description)
        for action in registry['event_rule_actions'].values()
    ]


def get_event_rule_action_slugs():
    return list(registry['event_rule_actions'].keys())
