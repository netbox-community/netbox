"""
Declarative cascade framework for NetBox models.

Replaces imperative signal handlers and save() overrides that propagate
field values to related models. Benefits:

1. External tools can introspect the cascade graph — no AST/regex parsing
2. The full impact of any model change is machine-readable
3. Cascades can be suppressed during bulk import or merge replay
4. Batch recomputation after merge is driven from the same declarations

Two kinds of cascade are supported:

- **BulkCascade**: Updates fields on related models via QuerySet.update().
  Example: Device.site changes → update _site on all components.

- **SaveCascade**: Loads related objects and calls save() on each.
  Example: RackType saved → copy attrs to each Rack and save().
  These produce ObjectChange records.

Usage:

    # Introspect: what happens when I change Device.site?
    effects = cascade_registry.get_for_source('dcim.device', changed_fields={'site'})

    # Export all cascades as structured data
    schema = cascade_registry.export()
"""
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from django.db.models.signals import post_delete, post_save, pre_delete

logger = logging.getLogger('netbox.cascades')


class CascadeTiming(str, Enum):
    POST_SAVE = 'post_save'
    POST_DELETE = 'post_delete'
    PRE_DELETE = 'pre_delete'


class CascadeMethod(str, Enum):
    BULK_UPDATE = 'bulk_update'
    INDIVIDUAL_SAVE = 'individual_save'
    CUSTOM = 'custom'


@dataclass(frozen=True)
class CascadeSpec:
    """
    Declares a single cascade: when source_model is saved/deleted,
    propagate changes to target_model.

    Attributes:
        source_model: App-label.model_name that triggers this cascade.
        target_model: App-label.model_name that gets updated.
        trigger_fields: Fields on source that trigger this cascade.
            None means any change triggers it.
        field_mapping: Dict mapping target field names to source field paths.
            Paths are dot-separated attribute traversal from the instance.
            Example: {'_site': 'site', '_location': 'location'}
        filter_spec: How to find target objects. A callable that receives
            the source instance and returns a QuerySet filter dict.
        method: How the update is performed.
        timing: When the cascade fires.
        only_on_create: Only fire when source object is first created.
        skip_on_create: Skip when source object is first created.
        handler: For CUSTOM method, the callable that performs the cascade.
            Receives (instance, **kwargs). Used for complex cascades that
            can't be expressed as field mappings.
        description: Human-readable explanation for documentation/export.
    """
    source_model: str
    target_model: str
    trigger_fields: Optional[frozenset] = None
    field_mapping: Optional[dict] = None
    filter_spec: Optional[Callable] = None
    method: CascadeMethod = CascadeMethod.BULK_UPDATE
    timing: CascadeTiming = CascadeTiming.POST_SAVE
    only_on_create: bool = False
    skip_on_create: bool = True
    handler: Optional[Callable] = None
    description: str = ''

    def get_filter(self, instance) -> dict:
        """Build the QuerySet filter for finding target objects."""
        if self.filter_spec:
            return self.filter_spec(instance)
        return {}

    def get_update_values(self, instance) -> dict:
        """Resolve field_mapping paths to concrete values from instance."""
        if not self.field_mapping:
            return {}
        values = {}
        for target_field, source_path in self.field_mapping.items():
            obj = instance
            for attr in source_path.split('.'):
                obj = getattr(obj, attr, None)
                if obj is None:
                    break
            values[target_field] = obj
        return values

    def export(self) -> dict:
        """Export as a plain dict for machine-readable schema."""
        return {
            'source_model': self.source_model,
            'target_model': self.target_model,
            'trigger_fields': sorted(self.trigger_fields) if self.trigger_fields else None,
            'field_mapping': self.field_mapping,
            'method': self.method.value,
            'timing': self.timing.value,
            'only_on_create': self.only_on_create,
            'skip_on_create': self.skip_on_create,
            'description': self.description,
        }


class CascadeRegistry:
    """
    Central registry of all cross-model cascades.

    Query methods let callers understand the full impact of any model
    change without executing it. The dispatch handler executes cascades
    from the registry on save/delete.

    Supports mixin sentinels: pseudo-labels like ``__mixin:SyncedDataMixin__``
    that match any model whose MRO includes the registered mixin class. This
    lets a single registration cover every concrete model inheriting that mixin.
    """

    def __init__(self):
        self._specs: dict[str, list[CascadeSpec]] = defaultdict(list)
        self._mixin_sentinels: dict[str, type] = {}

    def register(self, *specs: CascadeSpec):
        for spec in specs:
            self._specs[spec.source_model].append(spec)

    def register_mixin_sentinel(self, sentinel_label: str, mixin_class: type):
        self._mixin_sentinels[sentinel_label] = mixin_class

    def _sentinel_labels_for(self, instance) -> list[str]:
        mro = type(instance).__mro__
        return [label for label, cls in self._mixin_sentinels.items() if cls in mro]

    def get_for_source(
        self,
        model_label: str,
        changed_fields: Optional[set[str]] = None,
        timing: Optional[CascadeTiming] = None,
        instance=None,
    ) -> list[CascadeSpec]:
        """Get cascades triggered by a change to source model.

        If *instance* is provided, also includes cascades registered under
        matching mixin sentinel labels.
        """
        specs = list(self._specs.get(model_label, []))
        if instance is not None:
            for sentinel_label in self._sentinel_labels_for(instance):
                specs.extend(self._specs.get(sentinel_label, []))
        if timing:
            specs = [s for s in specs if s.timing == timing]
        if changed_fields is not None:
            specs = [
                s for s in specs
                if s.trigger_fields is None or s.trigger_fields & changed_fields
            ]
        return specs

    def get_for_target(self, model_label: str) -> list[CascadeSpec]:
        """Get all cascades that affect a given target model."""
        result = []
        for specs in self._specs.values():
            for spec in specs:
                if spec.target_model == model_label:
                    result.append(spec)
        return result

    def get_all(self) -> list[CascadeSpec]:
        result = []
        for specs in self._specs.values():
            result.extend(specs)
        return result

    def registered_sources(self) -> set[str]:
        return set(self._specs.keys())

    def impact_of(self, model_label: str, changed_fields: Optional[set[str]] = None) -> dict:
        """
        Compute the full impact graph of changing a model.
        Returns a dict of target_model -> list of field updates.
        Useful for the datamodel-service.
        """
        impact = defaultdict(list)
        for spec in self.get_for_source(model_label, changed_fields):
            impact[spec.target_model].append({
                'trigger_fields': sorted(spec.trigger_fields) if spec.trigger_fields else None,
                'updated_fields': sorted(spec.field_mapping.keys()) if spec.field_mapping else None,
                'method': spec.method.value,
                'description': spec.description,
            })
        return dict(impact)

    def export(self) -> dict:
        """Export the full registry as structured data."""
        return {
            'sources': sorted(self._specs.keys()),
            'total_cascades': sum(len(v) for v in self._specs.values()),
            'cascades': [
                spec.export()
                for specs in self._specs.values()
                for spec in specs
            ],
        }

    def summary(self) -> dict:
        return {
            'source_models': len(self._specs),
            'total_cascades': sum(len(v) for v in self._specs.values()),
            'by_source': {k: len(v) for k, v in sorted(self._specs.items())},
        }


# Global singleton
cascade_registry = CascadeRegistry()

# Thread-local suppression
_suppressed = False


def set_cascades_suppressed(suppressed: bool):
    """Enable/disable cascade execution globally (for bulk import/merge)."""
    global _suppressed
    _suppressed = suppressed


def are_cascades_suppressed() -> bool:
    return _suppressed


def _resolve_model(model_label: str):
    """Resolve 'app_label.model_name' to a Django model class."""
    from django.apps import apps
    app_label, model_name = model_label.split('.')
    return apps.get_model(app_label, model_name)


def _execute_cascade(spec: CascadeSpec, instance, **kwargs):
    """Execute a single cascade spec against an instance."""
    if are_cascades_suppressed():
        return

    created = kwargs.get('created', False)
    if spec.only_on_create and not created:
        return
    if spec.skip_on_create and created:
        return

    if spec.method == CascadeMethod.CUSTOM:
        if spec.handler:
            spec.handler(instance, **kwargs)
        return

    target_model = _resolve_model(spec.target_model)
    filter_kwargs = spec.get_filter(instance)
    update_values = spec.get_update_values(instance)

    if not filter_kwargs or not update_values:
        return

    if spec.method == CascadeMethod.BULK_UPDATE:
        count = target_model.objects.filter(**filter_kwargs).update(**update_values)
        logger.debug(
            f'Cascade {spec.source_model} -> {spec.target_model}: '
            f'updated {count} rows'
        )
    elif spec.method == CascadeMethod.INDIVIDUAL_SAVE:
        for obj in target_model.objects.filter(**filter_kwargs):
            for field_name, value in update_values.items():
                setattr(obj, field_name, value)
            obj.save()


def _handle_post_save(sender, instance, created, raw=False, **kwargs):
    """Post-save signal handler that executes cascades from the registry."""
    if raw:
        return

    label = f'{sender._meta.app_label}.{sender._meta.model_name}'
    specs = cascade_registry.get_for_source(label, timing=CascadeTiming.POST_SAVE, instance=instance)
    for spec in specs:
        _execute_cascade(spec, instance, created=created, **kwargs)


def _handle_post_delete(sender, instance, **kwargs):
    """Post-delete signal handler that executes cascades from the registry."""
    label = f'{sender._meta.app_label}.{sender._meta.model_name}'
    specs = cascade_registry.get_for_source(label, timing=CascadeTiming.POST_DELETE, instance=instance)
    for spec in specs:
        _execute_cascade(spec, instance, **kwargs)


def _handle_pre_delete(sender, instance, **kwargs):
    """Pre-delete signal handler that executes cascades from the registry."""
    label = f'{sender._meta.app_label}.{sender._meta.model_name}'
    specs = cascade_registry.get_for_source(label, timing=CascadeTiming.PRE_DELETE, instance=instance)
    for spec in specs:
        _execute_cascade(spec, instance, **kwargs)


def connect_cascade_signals():
    """Connect cascade dispatch handlers. Called once at startup."""
    post_save.connect(
        _handle_post_save,
        dispatch_uid='netbox.cascades.post_save',
    )
    post_delete.connect(
        _handle_post_delete,
        dispatch_uid='netbox.cascades.post_delete',
    )
    pre_delete.connect(
        _handle_pre_delete,
        dispatch_uid='netbox.cascades.pre_delete',
    )
