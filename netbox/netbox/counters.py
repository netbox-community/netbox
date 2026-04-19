"""
Declarative counter cache registry for NetBox models.

Wraps the existing CounterCacheField system to make counter
relationships introspectable. Benefits:

1. External tools know which models have auto-updating counts
2. The full counter dependency graph is machine-readable
3. Counter recomputation after merge can be driven from declarations

The actual counting is still performed by utilities/counters.py.
This module provides the structured metadata.
"""
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger('netbox.counters')


@dataclass(frozen=True)
class CounterSpec:
    """
    Declares a counter cache relationship.

    Attributes:
        child_model: The model being counted (e.g. 'dcim.interface').
        parent_model: The model holding the count (e.g. 'dcim.device').
        fk_field: FK field on child pointing to parent (e.g. 'device').
        counter_name: Name of the counter cache field on parent.
        description: Human-readable explanation.
    """
    child_model: str
    parent_model: str
    fk_field: str
    counter_name: Optional[str] = None
    description: str = ''

    def export(self) -> dict:
        return {
            'child_model': self.child_model,
            'parent_model': self.parent_model,
            'fk_field': self.fk_field,
            'counter_name': self.counter_name,
            'description': self.description,
        }


class CounterRegistry:
    """Central registry of all counter cache relationships."""

    def __init__(self):
        self._specs: list[CounterSpec] = []

    def register(self, *specs: CounterSpec):
        self._specs.extend(specs)

    def get_for_parent(self, model_label: str) -> list[CounterSpec]:
        return [s for s in self._specs if s.parent_model == model_label]

    def get_for_child(self, model_label: str) -> list[CounterSpec]:
        return [s for s in self._specs if s.child_model == model_label]

    def connect_all(self):
        """
        Resolve parent model classes from registered specs and wire up
        counter cache signals via connect_counters().
        """
        from django.apps import apps
        from utilities.counters import connect_counters

        parent_labels = sorted(set(spec.parent_model for spec in self._specs))
        parent_models = [apps.get_model(label) for label in parent_labels]
        connect_counters(*parent_models)

    def export(self) -> dict:
        parents = sorted(set(s.parent_model for s in self._specs))
        return {
            'parent_models': parents,
            'total_counters': len(self._specs),
            'counters': [s.export() for s in self._specs],
        }

    def summary(self) -> dict:
        by_parent = defaultdict(int)
        for s in self._specs:
            by_parent[s.parent_model] += 1
        return {
            'total_counters': len(self._specs),
            'parent_models': len(by_parent),
            'by_parent': dict(sorted(by_parent.items())),
        }


# Global singleton
counter_registry = CounterRegistry()


# ──────────────────────────────────────────────────────────────────────
# Register all counter cache relationships
# These mirror the connect_counters() calls in app configs
# ──────────────────────────────────────────────────────────────────────

_COUNTER_RELATIONSHIPS = [
    ('dcim.consoleport', 'dcim.device', 'device', 'Console port count on device'),
    ('dcim.consoleserverport', 'dcim.device', 'device', 'Console server port count on device'),
    ('dcim.powerport', 'dcim.device', 'device', 'Power port count on device'),
    ('dcim.poweroutlet', 'dcim.device', 'device', 'Power outlet count on device'),
    ('dcim.interface', 'dcim.device', 'device', 'Interface count on device'),
    ('dcim.frontport', 'dcim.device', 'device', 'Front port count on device'),
    ('dcim.rearport', 'dcim.device', 'device', 'Rear port count on device'),
    ('dcim.devicebay', 'dcim.device', 'device', 'Device bay count on device'),
    ('dcim.modulebay', 'dcim.device', 'device', 'Module bay count on device'),
    ('dcim.inventoryitem', 'dcim.device', 'device', 'Inventory item count on device'),
    ('dcim.consoleporttemplate', 'dcim.devicetype', 'device_type', 'Console port template count'),
    ('dcim.consoleserverporttemplate', 'dcim.devicetype', 'device_type', 'Console server port template count'),
    ('dcim.powerporttemplate', 'dcim.devicetype', 'device_type', 'Power port template count'),
    ('dcim.poweroutlettemplate', 'dcim.devicetype', 'device_type', 'Power outlet template count'),
    ('dcim.interfacetemplate', 'dcim.devicetype', 'device_type', 'Interface template count'),
    ('dcim.frontporttemplate', 'dcim.devicetype', 'device_type', 'Front port template count'),
    ('dcim.rearporttemplate', 'dcim.devicetype', 'device_type', 'Rear port template count'),
    ('dcim.devicebaytemplate', 'dcim.devicetype', 'device_type', 'Device bay template count'),
    ('dcim.modulebaytemplate', 'dcim.devicetype', 'device_type', 'Module bay template count'),
    ('dcim.inventoryitemtemplate', 'dcim.devicetype', 'device_type', 'Inventory item template count'),
    ('dcim.device', 'dcim.devicetype', 'device_type', 'Device count on device type'),
    ('dcim.module', 'dcim.moduletype', 'module_type', 'Module count on module type'),
    ('dcim.rack', 'dcim.racktype', 'rack_type', 'Rack count on rack type'),
    ('dcim.device', 'dcim.virtualchassis', 'virtual_chassis', 'Device count on virtual chassis'),
    ('virtualization.vminterface', 'virtualization.virtualmachine', 'virtual_machine', 'VM interface count'),
    ('virtualization.virtualdisk', 'virtualization.virtualmachine', 'virtual_machine', 'Virtual disk count'),
]

for child, parent, fk, desc in _COUNTER_RELATIONSHIPS:
    counter_registry.register(CounterSpec(
        child_model=child,
        parent_model=parent,
        fk_field=fk,
        description=desc,
    ))
