"""
Side-effect registry for NetBox models.

Makes the implicit side-effect graph of save(), clean(), and signal handlers explicit and
inspectable. External tools (branching, Terraform providers, Ansible, Diode, NetBox Designs)
can query this registry to understand what happens when a model field changes, without
executing opaque Python code.

Phase 1: Declarative metadata alongside existing code (no behavior changes).
Phase 2+: Registry declarations will progressively replace the imperative side-effect code.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EffectType(Enum):
    DENORMALIZATION = 'denormalization'
    FIELD_NORMALIZATION = 'field_normalization'
    CASCADE_UPDATE = 'cascade_update'
    GRAPH_RECOMPUTATION = 'graph_recomputation'
    ENTITY_INSTANTIATION = 'entity_instantiation'
    COUNTER_CACHE = 'counter_cache'
    CONDITIONAL_CLEANUP = 'conditional_cleanup'
    EVENT_DISPATCH = 'event_dispatch'
    OTHER = 'other'


class EffectTiming(Enum):
    PRE_SAVE = 'pre_save'
    POST_SAVE = 'post_save'
    PRE_DELETE = 'pre_delete'
    POST_DELETE = 'post_delete'


@dataclass(frozen=True)
class Effect:
    """
    A declarative description of a single side effect, without the execution logic.

    Attributes:
        effect_type: Category of side effect.
        source_model: App-label.model_name of the model whose change triggers this effect.
        source_fields: Field names that trigger this effect. None means any field change triggers it.
        target_model: Model affected by this effect. None means the same model as source.
        target_fields: Fields modified on the target. None means "complex / multiple".
        timing: When the effect fires relative to the database write.
        description: Human-readable explanation of what happens.
        produces_object_change: Whether this effect creates ObjectChange audit records.
        uses_bulk_sql: Whether this uses QuerySet.update() / bulk_update() (invisible to signals).
        handler: Dotted path to the current implementation (signal handler or save method).
        only_on_create: Effect only fires when the source object is first created.
    """
    effect_type: EffectType
    source_model: str
    source_fields: Optional[frozenset] = None
    target_model: Optional[str] = None
    target_fields: Optional[frozenset] = None
    timing: EffectTiming = EffectTiming.POST_SAVE
    description: str = ''
    produces_object_change: bool = False
    uses_bulk_sql: bool = False
    handler: str = ''
    only_on_create: bool = False


def _fs(fields):
    """Convenience: convert an iterable of field names to a frozenset."""
    if fields is None:
        return None
    return frozenset(fields)


class SideEffectRegistry:
    """
    Central registry of all known side effects in the NetBox data model.

    Query methods let callers understand the impact of any model change without
    executing the change.
    """

    def __init__(self):
        self._effects: list[Effect] = []
        self._index_by_source: dict[str, list[Effect]] = {}

    def register(self, effect: Effect):
        self._effects.append(effect)
        self._index_by_source.setdefault(effect.source_model, []).append(effect)

    def register_many(self, *effects: Effect):
        for e in effects:
            self.register(e)

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get_all(self) -> list[Effect]:
        return list(self._effects)

    def get_for_source(self, model_label: str) -> list[Effect]:
        """All effects triggered by changes to the given model."""
        return list(self._index_by_source.get(model_label, []))

    def get_for_target(self, model_label: str) -> list[Effect]:
        """All effects that modify the given model."""
        return [e for e in self._effects if e.target_model == model_label]

    def get_triggered_by(self, model_label: str, changed_fields: set[str],
                         include_global: bool = False) -> list[Effect]:
        """
        Effects that would fire when the given fields change on the given model.
        Excludes create-only effects when changed_fields is provided (assumes update).

        Args:
            include_global: If True, also include wildcard '*' effects (event pipeline,
                search index, notifications). These fire on every save but are typically
                orthogonal to data correctness.
        """
        results = []
        sources = [model_label]
        if include_global:
            sources.append('*')
        for source in sources:
            for e in self._index_by_source.get(source, []):
                if e.only_on_create:
                    continue
                if e.source_fields is None or e.source_fields & changed_fields:
                    results.append(e)
        return results

    def needs_full_save(self, model_label: str, changed_fields: set[str]) -> bool:
        """
        Return True if changing these fields requires the full ORM save() path
        (i.e., there are cascade/graph/instantiation/cleanup effects that a raw
        SQL UPDATE would miss).

        Only considers effects specific to this model (not wildcard '*' sources
        like the global event pipeline, which are orthogonal to data correctness).

        Denormalization effects that target OTHER models (not self) also require
        full save because they rely on post_save signals firing.
        """
        requires_save_types = {
            EffectType.CASCADE_UPDATE,
            EffectType.GRAPH_RECOMPUTATION,
            EffectType.ENTITY_INSTANTIATION,
            EffectType.CONDITIONAL_CLEANUP,
        }
        save_timings = {EffectTiming.PRE_SAVE, EffectTiming.POST_SAVE}
        for e in self.get_triggered_by(model_label, changed_fields):
            if e.timing not in save_timings:
                continue
            if e.effect_type in requires_save_types:
                return True
            if (e.effect_type == EffectType.DENORMALIZATION
                    and e.target_model is not None
                    and e.timing == EffectTiming.POST_SAVE):
                return True
        return False

    def invisible_to_changelog(self) -> list[Effect]:
        """
        Effects that use bulk SQL and don't produce ObjectChange records.
        These are invisible to merge replay and are the most dangerous for branching.
        """
        return [
            e for e in self._effects
            if e.uses_bulk_sql and not e.produces_object_change
        ]

    def by_type(self, effect_type: EffectType) -> list[Effect]:
        return [e for e in self._effects if e.effect_type == effect_type]

    def source_models(self) -> set[str]:
        """All model labels that have registered side effects."""
        return set(self._index_by_source.keys())

    def target_models(self) -> set[str]:
        """All model labels that are affected by side effects."""
        return {e.target_model for e in self._effects if e.target_model is not None}

    def summary(self) -> dict:
        """Quick stats for inspection/debugging."""
        from collections import Counter
        type_counts = Counter(e.effect_type.value for e in self._effects)
        return {
            'total_effects': len(self._effects),
            'source_models': len(self.source_models()),
            'target_models': len(self.target_models()),
            'by_type': dict(type_counts),
            'invisible_to_changelog': len(self.invisible_to_changelog()),
        }


# Global singleton — populated by app registrations in AppConfig.ready()
effect_registry = SideEffectRegistry()


# ══════════════════════════════════════════════════════════════════════
# Mixin-level save() side effects (METADATA-ONLY — code stays imperative)
# ══════════════════════════════════════════════════════════════════════

effect_registry.register_many(
    Effect(
        effect_type=EffectType.FIELD_NORMALIZATION,
        source_model='*',
        description=(
            'PARTIAL: CustomFieldsMixin.save() populates default values for custom fields '
            'not already present in custom_field_data. Applies to all CF-enabled models.'
        ),
        timing=EffectTiming.PRE_SAVE,
        handler='netbox.models.features.CustomFieldsMixin.save',
    ),
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='*',
        description=(
            'PARTIAL: SyncedDataMixin.save() creates or deletes AutoSyncRecord based on '
            'auto_sync_enabled. Applies to all synced-data models.'
        ),
        timing=EffectTiming.POST_SAVE,
        handler='netbox.models.features.SyncedDataMixin.save',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='extras.scriptmodule',
        description=(
            'PARTIAL: ScriptModule.save() sets file_root and calls sync_classes() to '
            'discover/update script classes from the module file.'
        ),
        timing=EffectTiming.POST_SAVE,
        handler='extras.models.scripts.ScriptModule.save',
    ),
)


# ══════════════════════════════════════════════════════════════════════
# Infrastructure signal handlers (METADATA-ONLY)
# ══════════════════════════════════════════════════════════════════════

effect_registry.register_many(

    # -- core/signals.py --

    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        description='handle_changed_object: creates ObjectChange record and queues events on post_save/m2m_changed',
        timing=EffectTiming.POST_SAVE,
        produces_object_change=True,
        handler='core.signals.handle_changed_object',
    ),
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        description=(
            'handle_deleted_object: runs protection rules, creates ObjectChange record, '
            'touches reverse M2M/FK relations, and queues delete events on pre_delete'
        ),
        timing=EffectTiming.PRE_DELETE,
        produces_object_change=True,
        handler='core.signals.handle_deleted_object',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='*',
        description='update_object_types: creates/updates ObjectType records for each model on post_migrate',
        handler='core.signals.update_object_types',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='*',
        description='clear_signal_history: clears thread-local pre_delete signal set on request_finished',
        handler='core.signals.clear_signal_history',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='*',
        description='clear_events_queue: resets the events queue on clear_events signal',
        handler='core.signals.clear_events_queue',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='core.datasource',
        description='enqueue_sync_job: enqueues or removes periodic sync jobs when DataSource is saved',
        timing=EffectTiming.POST_SAVE,
        handler='core.signals.enqueue_sync_job',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='core.datasource',
        description='auto_sync: iterates AutoSyncRecords and syncs objects after DataSource sync completes',
        handler='core.signals.auto_sync',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='extras.configrevision',
        description='update_config: activates new config revision on post_save',
        timing=EffectTiming.POST_SAVE,
        handler='core.signals.update_config',
    ),

    # -- extras/signals.py --

    Effect(
        effect_type=EffectType.OTHER,
        source_model='*',
        description='run_save_validators: runs CUSTOM_VALIDATORS from config on post_clean for all models',
        handler='extras.signals.run_save_validators',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='extras.taggeditem',
        description='validate_assigned_tags: checks tag object-type restrictions on m2m_changed pre_add',
        handler='extras.signals.validate_assigned_tags',
    ),
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        description='process_job_start_event_rules: processes EventRules for JOB_STARTED on job_start signal',
        handler='extras.signals.process_job_start_event_rules',
    ),
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        description='process_job_end_event_rules: processes EventRules for JOB_COMPLETED on job_end signal',
        handler='extras.signals.process_job_end_event_rules',
    ),
    Effect(
        effect_type=EffectType.EVENT_DISPATCH,
        source_model='*',
        description=(
            'notify_object_changed: creates Notification objects for subscribed users '
            'on post_save (update) and pre_delete'
        ),
        timing=EffectTiming.POST_SAVE,
        handler='extras.signals.notify_object_changed',
    ),

    # -- extras/models/scripts.py --

    Effect(
        effect_type=EffectType.OTHER,
        source_model='extras.scriptmodule',
        description='script_module_post_save_handler: calls sync_classes() on ScriptModule post_save signal',
        timing=EffectTiming.POST_SAVE,
        handler='extras.models.scripts.script_module_post_save_handler',
    ),

    # -- users/signals.py --

    Effect(
        effect_type=EffectType.OTHER,
        source_model='users.user',
        description='log_user_login_failed: logs failed login attempts with client IP on user_login_failed signal',
        handler='users.signals.log_user_login_failed',
    ),
    Effect(
        effect_type=EffectType.OTHER,
        source_model='users.user',
        description=(
            'set_language_on_login: stores preferred language on request '
            'for middleware cookie on user_logged_in signal'
        ),
        handler='users.signals.set_language_on_login',
    ),
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='users.user',
        description='create_userconfig: creates UserConfig with default preferences when User is created',
        timing=EffectTiming.POST_SAVE,
        only_on_create=True,
        handler='users.signals.create_userconfig',
    ),

    # -- netbox/denormalized.py --

    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='*',
        description=(
            'update_denormalized_fields: bulk-updates cross-model FK denormalized '
            'copies on post_save (skips created/raw). Registered per-model in apps.py '
            'ready() via denormalized.register(). Currently: CableTermination._device/_rack/_location, '
            'CircuitTermination._site/_location, Prefix._site/_location.'
        ),
        timing=EffectTiming.POST_SAVE,
        uses_bulk_sql=True,
        handler='netbox.denormalized.update_denormalized_fields',
    ),

    # -- netbox/search/backends.py --

    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='*',
        target_model='extras.cachedvalue',
        description='search caching_handler: updates CachedValue entries on post_save for searchable models',
        timing=EffectTiming.POST_SAVE,
        uses_bulk_sql=True,
        handler='netbox.search.backends.SearchBackend.caching_handler',
    ),
    Effect(
        effect_type=EffectType.DENORMALIZATION,
        source_model='*',
        target_model='extras.cachedvalue',
        description='search removal_handler: deletes CachedValue entries on post_delete for searchable models',
        timing=EffectTiming.POST_DELETE,
        uses_bulk_sql=True,
        handler='netbox.search.backends.SearchBackend.removal_handler',
    ),
)
