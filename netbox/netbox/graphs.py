"""
Declarative graph recomputation framework for NetBox models.

Captures derived graph structures (cable paths, prefix hierarchy,
wireless links) as structured declarations. Benefits:

1. External tools understand which model changes trigger graph rebuilds
2. Recomputation can be batched after merge/sync
3. The graph dependency structure is machine-readable

Usage:

    # What graph operations does saving a Cable trigger?
    specs = graph_registry.get_for_trigger('dcim.cable')

    # Export all graph rules
    schema = graph_registry.export()
"""
import importlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger('netbox.graphs')


class GraphType(str, Enum):
    CABLE_PATH = 'cable_path'
    PREFIX_HIERARCHY = 'prefix_hierarchy'
    WIRELESS_PATH = 'wireless_path'


@dataclass(frozen=True)
class GraphSpec:
    """
    Declares a graph recomputation rule.

    Attributes:
        trigger_model: Model whose save/delete triggers recomputation.
        graph_type: Category of graph operation.
        trigger_event: 'post_save', 'post_delete', or 'both'.
        trigger_fields: Fields on trigger_model that cause recompute.
            None means any change triggers it.
        affected_model: The derived model that gets recomputed.
        handler: String reference to the handler function.
        description: Human-readable explanation.
    """
    trigger_model: str
    graph_type: GraphType
    trigger_event: str = 'post_save'
    trigger_fields: Optional[frozenset] = None
    affected_model: Optional[str] = None
    handler: str = ''
    description: str = ''

    def export(self) -> dict:
        return {
            'trigger_model': self.trigger_model,
            'graph_type': self.graph_type.value,
            'trigger_event': self.trigger_event,
            'trigger_fields': sorted(self.trigger_fields) if self.trigger_fields else None,
            'affected_model': self.affected_model,
            'handler': self.handler,
            'description': self.description,
        }


class GraphRegistry:
    """
    Central registry of all graph recomputation rules.
    """

    def __init__(self):
        self._specs: dict[str, list[GraphSpec]] = defaultdict(list)

    def register(self, *specs: GraphSpec):
        for spec in specs:
            self._specs[spec.trigger_model].append(spec)

    def get_for_trigger(
        self,
        model_label: str,
        graph_type: Optional[GraphType] = None,
    ) -> list[GraphSpec]:
        specs = list(self._specs.get(model_label, []))
        if graph_type:
            specs = [s for s in specs if s.graph_type == graph_type]
        return specs

    def get_by_type(self, graph_type: GraphType) -> list[GraphSpec]:
        result = []
        for specs in self._specs.values():
            for spec in specs:
                if spec.graph_type == graph_type:
                    result.append(spec)
        return result

    def registered_triggers(self) -> set[str]:
        return set(self._specs.keys())

    def export(self) -> dict:
        return {
            'triggers': sorted(self._specs.keys()),
            'total_rules': sum(len(v) for v in self._specs.values()),
            'by_type': {
                gt.value: len(self.get_by_type(gt))
                for gt in GraphType
            },
            'rules': [
                spec.export()
                for specs in self._specs.values()
                for spec in specs
            ],
        }

    def summary(self) -> dict:
        return {
            'trigger_models': len(self._specs),
            'total_rules': sum(len(v) for v in self._specs.values()),
            'by_type': {
                gt.value: len(self.get_by_type(gt))
                for gt in GraphType
            },
        }


# Global singleton
graph_registry = GraphRegistry()


# ──────────────────────────────────────────────────────────────────────
# Cable path graph registrations
# ──────────────────────────────────────────────────────────────────────

graph_registry.register(
    GraphSpec(
        trigger_model='dcim.cable',
        graph_type=GraphType.CABLE_PATH,
        trigger_event='custom:trace_paths',
        trigger_fields=frozenset({'status'}),
        affected_model='dcim.cablepath',
        handler='dcim.signals.update_connected_endpoints',
        description=(
            'Retrace cable paths when cable status or terminations change. '
            'Connected via custom trace_paths signal in dcim/signals.py, '
            'not dispatched by GraphRegistry.'
        ),
    ),
    GraphSpec(
        trigger_model='dcim.cable',
        graph_type=GraphType.CABLE_PATH,
        trigger_event='post_delete',
        affected_model='dcim.cablepath',
        handler='dcim.signals.retrace_cable_paths',
        description='Retrace cable paths when cable is deleted',
    ),
    GraphSpec(
        trigger_model='dcim.portmapping',
        graph_type=GraphType.CABLE_PATH,
        trigger_event='both',
        affected_model='dcim.cablepath',
        handler='dcim.signals.update_passthrough_port_paths',
        description='Retrace cable paths through port mappings on create/delete',
    ),
    GraphSpec(
        trigger_model='dcim.cabletermination',
        graph_type=GraphType.CABLE_PATH,
        trigger_event='post_delete',
        affected_model='dcim.cablepath',
        handler='dcim.signals.retrace_paths_on_termination_delete',
        description='Retrace cable paths when cable termination is deleted',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Prefix hierarchy graph registrations
# ──────────────────────────────────────────────────────────────────────

graph_registry.register(
    GraphSpec(
        trigger_model='ipam.prefix',
        graph_type=GraphType.PREFIX_HIERARCHY,
        trigger_event='post_save',
        trigger_fields=frozenset({'prefix', 'vrf'}),
        affected_model='ipam.prefix',
        handler='ipam.signals.handle_prefix_saved',
        description='Recompute prefix hierarchy (_depth, _children) on save',
    ),
    GraphSpec(
        trigger_model='ipam.prefix',
        graph_type=GraphType.PREFIX_HIERARCHY,
        trigger_event='post_delete',
        affected_model='ipam.prefix',
        handler='ipam.signals.handle_prefix_deleted',
        description='Recompute prefix hierarchy on delete',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Wireless link path registrations
# ──────────────────────────────────────────────────────────────────────

graph_registry.register(
    GraphSpec(
        trigger_model='wireless.wirelesslink',
        graph_type=GraphType.WIRELESS_PATH,
        trigger_event='post_save',
        affected_model='dcim.cablepath',
        handler='wireless.signals.create_wireless_cable_paths',
        description='Create cable paths for wireless link interfaces on creation',
    ),
    GraphSpec(
        trigger_model='wireless.wirelesslink',
        graph_type=GraphType.WIRELESS_PATH,
        trigger_event='post_delete',
        affected_model='dcim.cablepath',
        handler='wireless.signals.delete_wireless_cable_paths',
        description='Delete cable paths when wireless link is deleted',
    ),
    GraphSpec(
        trigger_model='circuits.circuittermination',
        graph_type=GraphType.CABLE_PATH,
        trigger_event='both',
        affected_model='dcim.cablepath',
        handler='circuits.signals.rebuild_cablepaths',
        description='Rebuild cable paths through peer circuit termination on save/delete',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Signal dispatch
# ──────────────────────────────────────────────────────────────────────

_handler_cache = {}


def _resolve_handler(handler_str):
    """Import and cache a handler function from a dotted path."""
    if handler_str not in _handler_cache:
        module_path, func_name = handler_str.rsplit('.', 1)
        module = importlib.import_module(module_path)
        _handler_cache[handler_str] = getattr(module, func_name)
    return _handler_cache[handler_str]


def _handle_graph_post_save(sender, instance, **kwargs):
    label = f'{sender._meta.app_label}.{sender._meta.model_name}'
    specs = graph_registry.get_for_trigger(label)
    for spec in specs:
        if spec.trigger_event in ('post_save', 'both') and spec.handler:
            handler = _resolve_handler(spec.handler)
            handler(sender=sender, instance=instance, **kwargs)


def _handle_graph_post_delete(sender, instance, **kwargs):
    label = f'{sender._meta.app_label}.{sender._meta.model_name}'
    specs = graph_registry.get_for_trigger(label)
    for spec in specs:
        if spec.trigger_event in ('post_delete', 'both') and spec.handler:
            handler = _resolve_handler(spec.handler)
            handler(sender=sender, instance=instance, **kwargs)


def connect_graph_signals():
    from django.db.models.signals import post_save, post_delete
    post_save.connect(_handle_graph_post_save, dispatch_uid='netbox.graphs.post_save')
    post_delete.connect(_handle_graph_post_delete, dispatch_uid='netbox.graphs.post_delete')
