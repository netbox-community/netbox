"""
Declarative instantiation framework for NetBox models.

Captures the pattern where creating a parent model (Device, Module)
automatically creates child components from templates. Benefits:

1. External tools can introspect what gets created when a Device is made
2. The instantiation logic is documented as structured data
3. Instantiation can be replayed or suppressed during merge/sync

Usage:

    # What components does creating a Device create?
    specs = instantiation_registry.get_for_source('dcim.device')

    # Export all instantiation rules
    schema = instantiation_registry.export()
"""
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

logger = logging.getLogger('netbox.instantiation')


@dataclass(frozen=True)
class InstantiationSpec:
    """
    Declares that creating source_model automatically creates
    instances of target_model from a template queryset.

    Attributes:
        source_model: The parent model being created (e.g. 'dcim.device').
        target_model: The child model being instantiated (e.g. 'dcim.consoleport').
        template_relation: The queryset path from the type to templates
            (e.g. 'device_type.consoleporttemplates').
        handler: Callable that performs the instantiation. Receives
            (instance, template_queryset).
        bulk_create: Whether bulk_create is used (False for MPTT models).
        post_instantiate: Optional callback after all components created
            (e.g. update_interface_bridges).
        description: Human-readable explanation.
    """
    source_model: str
    target_model: str
    template_relation: str
    handler: Optional[Callable] = None
    bulk_create: bool = True
    post_instantiate: Optional[Callable] = None
    description: str = ''

    def get_template_queryset(self, instance):
        """Traverse the template_relation path to get the template QS."""
        obj = instance
        for attr in self.template_relation.split('.'):
            obj = getattr(obj, attr)
        if callable(obj):
            return obj()
        return obj

    def export(self) -> dict:
        return {
            'source_model': self.source_model,
            'target_model': self.target_model,
            'template_relation': self.template_relation,
            'bulk_create': self.bulk_create,
            'description': self.description,
        }


class InstantiationRegistry:
    """
    Central registry of all automatic component instantiation rules.
    """

    def __init__(self):
        self._specs: dict[str, list[InstantiationSpec]] = defaultdict(list)

    def register(self, *specs: InstantiationSpec):
        for spec in specs:
            self._specs[spec.source_model].append(spec)

    def get_for_source(self, model_label: str) -> list[InstantiationSpec]:
        return list(self._specs.get(model_label, []))

    def registered_sources(self) -> set[str]:
        return set(self._specs.keys())

    def export(self) -> dict:
        return {
            'sources': sorted(self._specs.keys()),
            'total_rules': sum(len(v) for v in self._specs.values()),
            'rules': [
                spec.export()
                for specs in self._specs.values()
                for spec in specs
            ],
        }

    def summary(self) -> dict:
        return {
            'source_models': len(self._specs),
            'total_rules': sum(len(v) for v in self._specs.values()),
            'by_source': {k: len(v) for k, v in sorted(self._specs.items())},
        }


# Global singleton
instantiation_registry = InstantiationRegistry()
