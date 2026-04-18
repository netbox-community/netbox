"""
Declarative denormalization framework for NetBox models.

Replaces imperative save() overrides and signal handlers with declarative
specifications of how denormalized fields are computed. Benefits:

1. Models don't need save() overrides for denormalization
2. External tools can inspect the denormalization graph
3. Batch recomputation after merge/sync is a single call
4. The computation is separable from persistence (pure function)

Two kinds of denormalization are supported:

- **Self-denorm** (pre-save): Sets fields on the instance being saved.
  Example: ComponentModel._site = device.site

- **Propagation** (post-save): Updates fields on OTHER models when a
  source model changes. Example: Device.site changes → update all
  component _site fields. (Phase 4 will convert signal handlers to use this.)
"""
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

from django.db.models.signals import pre_save

logger = logging.getLogger('netbox.denorm')


@dataclass(frozen=True)
class DenormSpec:
    """
    Declares how a single denormalized field's value is computed.

    Use source_path for simple FK traversal (most common case).
    Use compute for arbitrary derivations.
    """
    field_name: str
    source_path: Optional[str] = None
    compute: Optional[Callable] = None
    depends_on: frozenset = field(default_factory=frozenset)

    def resolve(self, instance):
        """Compute the denormalized value from the instance."""
        if self.compute is not None:
            return self.compute(instance)
        if self.source_path is not None:
            obj = instance
            for attr in self.source_path.split('.'):
                obj = getattr(obj, attr, None)
                if obj is None:
                    return None
            return obj
        return None


class DenormRegistry:
    """
    Central registry of all pre-save denormalization rules.

    Models register their denormalized fields here. A pre_save signal
    handler calls compute_all() before each save, replacing the need
    for save() overrides.
    """

    def __init__(self):
        self._specs: dict[str, list[DenormSpec]] = defaultdict(list)

    def register(self, model_label: str, *specs: DenormSpec):
        for spec in specs:
            self._specs[model_label].append(spec)

    def get_specs(self, model_label: str) -> list[DenormSpec]:
        return self._specs.get(model_label, [])

    def has_specs(self, model_label: str) -> bool:
        return model_label in self._specs

    def compute_all(self, instance):
        """Compute and set all denormalized fields on an instance (pre-save)."""
        label = f'{instance._meta.app_label}.{instance._meta.model_name}'
        for spec in self._specs.get(label, []):
            value = spec.resolve(instance)
            field_name = spec.field_name
            # For FK fields, setattr on the descriptor name works correctly
            setattr(instance, field_name, value)

    def compute_if_changed(self, instance, changed_fields: set[str]):
        """Compute only denormalized fields affected by changed_fields."""
        label = f'{instance._meta.app_label}.{instance._meta.model_name}'
        for spec in self._specs.get(label, []):
            if not spec.depends_on or spec.depends_on & changed_fields:
                value = spec.resolve(instance)
                setattr(instance, spec.field_name, value)

    def batch_recompute(self, model, queryset=None, field_names=None,
                        select_related=None):
        """
        Batch recompute denormalized fields for a queryset.

        This is the key method for post-merge/sync consistency. Instead of
        replaying save() on each object, call this once per model.
        """
        label = f'{model._meta.app_label}.{model._meta.model_name}'
        specs = self._specs.get(label, [])
        if not specs:
            return 0

        if field_names:
            specs = [s for s in specs if s.field_name in field_names]

        if queryset is None:
            queryset = model.objects.all()

        if select_related:
            queryset = queryset.select_related(*select_related)

        update_fields = [s.field_name for s in specs]
        objects_to_update = []

        for obj in queryset.iterator():
            changed = False
            for spec in specs:
                old_value = getattr(obj, spec.field_name, None)
                new_value = spec.resolve(obj)
                if old_value != new_value:
                    setattr(obj, spec.field_name, new_value)
                    changed = True
            if changed:
                objects_to_update.append(obj)

            # Flush in batches to avoid memory issues
            if len(objects_to_update) >= 1000:
                model.objects.bulk_update(objects_to_update, update_fields)
                objects_to_update = []

        if objects_to_update:
            model.objects.bulk_update(objects_to_update, update_fields)

        return len(objects_to_update)

    def registered_models(self) -> set[str]:
        return set(self._specs.keys())

    def summary(self) -> dict:
        return {
            'models': len(self._specs),
            'total_fields': sum(len(v) for v in self._specs.values()),
            'by_model': {k: len(v) for k, v in sorted(self._specs.items())},
        }


# Global singleton
denorm_registry = DenormRegistry()


def _handle_pre_save(sender, instance, raw=False, **kwargs):
    """
    Pre-save signal handler that computes denormalized fields.
    Replaces explicit denorm logic in save() overrides.
    """
    if raw:
        return
    label = f'{sender._meta.app_label}.{sender._meta.model_name}'
    if denorm_registry.has_specs(label):
        denorm_registry.compute_all(instance)


def connect_denorm_signal():
    """Connect the pre_save handler. Called once at startup."""
    pre_save.connect(
        _handle_pre_save,
        dispatch_uid='netbox.denorm.pre_save',
    )
