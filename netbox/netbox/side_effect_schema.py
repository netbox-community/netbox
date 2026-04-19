"""
Unified side-effect schema export for NetBox.

Provides a single entry point that aggregates all declarative registries
into a complete, machine-readable description of every side effect in
the NetBox data model.

This is the key integration point for the datamodel-service: instead of
brittle AST parsing and regex matching, it can call get_full_side_effect_schema()
to get a structured dict describing all:

- Denormalization rules (self-denorm via DenormRegistry)
- Cross-model cascades (CascadeRegistry)
- Validation rules (ValidatorRegistry)
- Graph recomputation triggers (GraphRegistry)
- Component instantiation rules (InstantiationRegistry)
- Counter cache relationships (CounterRegistry)
- Side-effect metadata (EffectRegistry from Phase 1)
"""


def get_full_side_effect_schema() -> dict:
    """
    Return the complete side-effect schema for the entire NetBox data model.

    This is designed to be called once at startup or on demand by the
    datamodel-service API. The result is a pure dict suitable for
    JSON serialization.
    """
    from netbox.cascades import cascade_registry
    from netbox.counters import counter_registry
    from netbox.denorm import denorm_registry
    from netbox.graphs import graph_registry
    from netbox.instantiation import instantiation_registry
    from netbox.side_effects import effect_registry
    from netbox.validators import validator_registry

    return {
        'version': '1.0',
        'registries': {
            'denormalization': {
                'summary': denorm_registry.summary(),
                'specs': {
                    model: [
                        {
                            'field_name': spec.field_name,
                            'source_path': spec.source_path,
                            'has_compute': spec.compute is not None,
                            'depends_on': sorted(spec.depends_on) if spec.depends_on else [],
                        }
                        for spec in denorm_registry.get_specs(model)
                    ]
                    for model in sorted(denorm_registry.registered_models())
                },
            },
            'cascades': cascade_registry.export(),
            'validators': {
                'summary': validator_registry.summary(),
                'by_model': {
                    model: [
                        {
                            'name': v.name,
                            'fields': sorted(v.fields) if v.fields else [],
                            'category': v.category.value,
                            'queries_db': v.queries_db,
                            'description': v.description,
                        }
                        for v in validator_registry.get_validators(model)
                    ]
                    for model in sorted(validator_registry.registered_models())
                },
            },
            'graphs': graph_registry.export(),
            'instantiation': instantiation_registry.export(),
            'counters': counter_registry.export(),
            'effects': {
                'summary': effect_registry.summary(),
            },
        },
    }


def get_impact_of(model_label: str, changed_fields: set[str] = None) -> dict:
    """
    Return the full impact of changing a specific model.

    This answers the question: "If I change Device.site, what happens?"
    Used by the datamodel-service to build impact graphs.
    """
    from netbox.cascades import cascade_registry
    from netbox.denorm import denorm_registry
    from netbox.graphs import graph_registry
    from netbox.validators import validator_registry

    impact = {
        'model': model_label,
        'changed_fields': sorted(changed_fields) if changed_fields else None,
    }

    # Denormalization: what fields get recomputed on this model?
    denorm_specs = denorm_registry.get_specs(model_label)
    if changed_fields:
        denorm_specs = [
            s for s in denorm_specs
            if not s.depends_on or s.depends_on & changed_fields
        ]
    if denorm_specs:
        impact['denormalization'] = [
            {'field': s.field_name, 'depends_on': sorted(s.depends_on) if s.depends_on else []}
            for s in denorm_specs
        ]

    # Cascades: what other models get updated?
    cascade_impact = cascade_registry.impact_of(model_label, changed_fields)
    if cascade_impact:
        impact['cascades'] = cascade_impact

    # Graph recomputation: what graph rebuilds trigger?
    graph_specs = graph_registry.get_for_trigger(model_label)
    if graph_specs:
        impact['graph_recomputation'] = [s.export() for s in graph_specs]

    # Validators: what gets validated?
    validators = validator_registry.get_validators(model_label, fields=changed_fields)
    if validators:
        impact['validators'] = [
            {'name': v.name, 'category': v.category.value, 'description': v.description}
            for v in validators
        ]

    return impact
