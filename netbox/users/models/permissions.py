from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models.features import CloningMixin
from netbox.registry import registry
from users.constants import RESERVED_ACTIONS
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'ObjectPermission',
)


class ObjectPermission(CloningMixin, models.Model):
    """
    A mapping of view, add, change, and/or delete permission for users and/or groups to an arbitrary set of objects
    identified by ORM query parameters.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    object_types = models.ManyToManyField(
        to='contenttypes.ContentType',
        related_name='object_permissions'
    )
    actions = ArrayField(
        base_field=models.CharField(max_length=30),
        help_text=_("The list of actions granted by this permission")
    )
    constraints = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('constraints'),
        help_text=_("Queryset filter matching the applicable objects of the selected type(s)")
    )

    clone_fields = (
        'description', 'enabled', 'object_types', 'actions', 'constraints',
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['name']
        indexes = (
            models.Index(fields=('name',)),  # Default ordering
        )
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')

    def __str__(self):
        return self.name

    @property
    def can_view(self):
        return 'view' in self.actions

    @property
    def can_add(self):
        return 'add' in self.actions

    @property
    def can_change(self):
        return 'change' in self.actions

    @property
    def can_delete(self):
        return 'delete' in self.actions

    def list_constraints(self):
        """
        Return all constraint sets as a list (even if only a single set is defined).
        """
        if type(self.constraints) is not list:
            return [self.constraints]
        return self.constraints

    def get_registered_actions(self):
        """
        Return a list of dicts for all registered actions:
            name: The action identifier
            help_text: Human-friendly description (first registration wins)
            enabled: Whether this action is enabled on this permission
            models: Sorted list of human-friendly model verbose names
        """
        enabled_actions = set(self.actions) - set(RESERVED_ACTIONS)

        action_info = {}
        action_models = {}
        for model_key, model_actions in registry['model_actions'].items():
            app_label, model_name = model_key.split('.')
            try:
                verbose_name = str(apps.get_model(app_label, model_name)._meta.verbose_name)
            except LookupError:
                verbose_name = model_key
            for action in model_actions:
                # First registration's help_text wins for shared action names
                if action.name not in action_info:
                    action_info[action.name] = action
                action_models.setdefault(action.name, []).append(verbose_name)

        return [
            {
                'name': name,
                'help_text': action_info[name].help_text,
                'enabled': name in enabled_actions,
                'models': sorted(action_models[name]),
            }
            for name in sorted(action_models)
        ]

    def get_additional_actions(self):
        """
        Return a sorted list of actions that are neither CRUD nor registered.
        These are manually-entered actions from the "Additional actions" field.
        """
        registered_names = set()
        for model_actions in registry['model_actions'].values():
            for action in model_actions:
                registered_names.add(action.name)

        return sorted(
            a for a in self.actions
            if a not in RESERVED_ACTIONS and a not in registered_names
        )

    def get_absolute_url(self):
        return reverse('users:objectpermission', args=[self.pk])
