from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import router
from django.db.models import Q
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from dcim.constants import MODULE_TOKEN
from dcim.utils import (
    get_module_bay_positions,
    get_module_bay_raw_positions,
    resolve_module_placeholder,
    resolve_position_chain,
)
from utilities.counters import update_counter
from utilities.exceptions import AbortRequest

from .device_components import (
    ConsolePort,
    ConsoleServerPort,
    FrontPort,
    Interface,
    ModuleBay,
    PortMapping,
    PowerOutlet,
    PowerPort,
    RearPort,
)

__all__ = (
    'ComponentMove',
    'ModuleMovePlan',
)

BATCH_SIZE = 1000

# Modular component models relocated during a move, mapped to the ModuleType template
# accessor used for conservative template-derived renaming. ModuleBay is handled
# separately (nested hierarchy, distinct uniqueness constraint).
COMPONENT_TEMPLATE_ATTRS = {
    ConsolePort: 'consoleporttemplates',
    ConsoleServerPort: 'consoleserverporttemplates',
    FrontPort: 'frontporttemplates',
    Interface: 'interfacetemplates',
    PowerOutlet: 'poweroutlettemplates',
    PowerPort: 'powerporttemplates',
    RearPort: 'rearporttemplates',
}

MODULEBAY_TEMPLATE_ATTR = 'modulebaytemplates'


@dataclass
class ComponentMove:
    """
    The planned final state of a single component affected by a module move. Unchanged
    values remain equal to the instance's current values.
    """
    instance: object
    target_name: str
    target_label: str
    target_position: str = None   # ModuleBay only
    target_parent_id: int = None  # ModuleBay only; set for the root module's direct child bays


class ModuleMovePlan:
    """
    Plans and applies the relocation of an installed module (including its nested module
    subtree) to a different module bay and/or device. Build via from_module(), then call
    lock(), validate(), and (after the root Module row has been saved) apply_after_root_save().
    """

    def __init__(self, old_module, new_module):
        self.old_module = old_module
        self.new_module = new_module
        self.module_model = type(old_module)
        self.device_model = self.module_model._meta.get_field('device').related_model
        self.old_device_id = old_module.device_id
        self.new_device_id = new_module.device_id
        self.new_device = new_module.device
        self.new_bay = new_module.module_bay
        self.cross_device = old_module.device_id != new_module.device_id

        self.modules_by_level = []   # [[Module]]; level 0 is [old_module]
        # Seeded with the root module's own pk (always known without a query) so that
        # lock()'s first (pre-discovery) and second (post-discovery) membership snapshots
        # compare equal when the root module truly has no descendants, bays, or
        # components, keeping the common case to a single discover+lock pass.
        self.module_pks = {old_module.pk}
        self.moved_bays = []         # all ModuleBays owned by moved modules
        self.components = {}         # {model: [instances]} for COMPONENT_TEMPLATE_ATTRS models
        self.component_moves = {model: [] for model in COMPONENT_TEMPLATE_ATTRS}
        self.bay_moves = []          # [ComponentMove] for moved ModuleBays
        self._target_resolution_failures = []  # display strings; see _record_target_failure()
        self._template_cache = {}    # {(module_type_id, template_attr): [templates]} per planning pass
        self._planned = False        # set once discovery + rename planning have run at least once
        self._now = None

    @classmethod
    def from_module(cls, *, old_module, new_module):
        """
        Build a plan for the given move. Discovery and rename planning are NOT run here;
        they run lazily (see _ensure_planned()) on the first call to validate(), or
        eagerly inside lock() for the locked save path. A caller that goes on to call
        lock() (Module._save_existing()) would otherwise pay for an unlocked discovery
        pass that lock() immediately re-does under row locks - pure waste.
        """
        return cls(old_module, new_module)

    def _ensure_planned(self):
        """
        Run discovery and rename planning if they have not already run for this
        instance. lock() always (re-)discovers and (re-)plans itself under row locks, so
        this is a no-op after lock() - it only does work for the unlocked clean() path,
        where validate() is called directly against a freshly constructed plan.
        """
        if not self._planned:
            self._discover()
            self._plan_renames()
            self._planned = True

    def _discover(self):
        """
        Collect the moved subtree by module ownership: the root module, all ModuleBays
        owned by moved modules (level by level), the modules installed in those bays,
        and all non-bay components owned by any moved module.

        Re-entrant: resets its accumulators first so a re-run (see lock()) reflects only
        the current database state, not whatever a prior pass appended.
        """
        self.modules_by_level = []
        self.moved_bays = []
        self.components = {}

        self.modules_by_level = [[self.old_module]]
        visited_pks = {self.old_module.pk}
        frontier = [self.old_module.pk]
        while frontier:
            level_bays = list(ModuleBay.objects.filter(module_id__in=frontier))
            self.moved_bays.extend(level_bays)
            child_modules = list(
                self.module_model.objects.select_related('module_type').filter(
                    module_bay_id__in=[bay.pk for bay in level_bays]
                )
            )
            # A revisited module pk means a cycle (creatable via .update(), bypassing clean()).
            for module in child_modules:
                if module.pk in visited_pks:
                    raise ValueError(_("Module bay hierarchy contains a cycle."))
                visited_pks.add(module.pk)
            frontier = [module.pk for module in child_modules]
            if child_modules:
                self.modules_by_level.append(child_modules)

        self.module_pks = {module.pk for level in self.modules_by_level for module in level}
        for model in COMPONENT_TEMPLATE_ATTRS:
            self.components[model] = list(model.objects.filter(module_id__in=self.module_pks))

    def _plan_renames(self):
        """
        Compute the planned final name/label/position for every moved component, top-down
        so that a child module's new position context reflects its containing bay's
        planned position. A component is renamed only when exactly one template of the
        owning module's current type resolves to its current name in the old context.

        Re-entrant: resets its accumulators first so a re-run reflects only the current
        self.components/self.moved_bays, not whatever a prior pass appended.
        """
        self.component_moves = {model: [] for model in COMPONENT_TEMPLATE_ATTRS}
        self.bay_moves = []
        self._target_resolution_failures = []
        self._template_cache = {}

        # A target bay inside the moved subtree is rejected by validate(); do not walk its chain
        if self.new_bay.pk in {bay.pk for bay in self.moved_bays}:
            return

        old_chains = {self.old_module.pk: get_module_bay_positions(self.old_module.module_bay)}
        new_raw_chains = {self.old_module.pk: get_module_bay_raw_positions(self.new_bay)}

        components_by_module = {model: {} for model in COMPONENT_TEMPLATE_ATTRS}
        for model, instances in self.components.items():
            for obj in instances:
                components_by_module[model].setdefault(obj.module_id, []).append(obj)
        bays_by_module = {}
        for bay in self.moved_bays:
            bays_by_module.setdefault(bay.module_id, []).append(bay)
        installed_module_by_bay = {
            module.module_bay_id: module
            for level in self.modules_by_level[1:]
            for module in level
        }

        for level in self.modules_by_level:
            for module in level:
                old_positions = old_chains[module.pk]
                new_positions = resolve_position_chain(new_raw_chains[module.pk])

                for model, template_attr in COMPONENT_TEMPLATE_ATTRS.items():
                    templates_by_old_name = self._index_templates(
                        self._cached_templates(module.module_type, template_attr), old_positions
                    )
                    for component in components_by_module[model].get(module.pk, []):
                        self.component_moves[model].append(self._plan_component(
                            component, templates_by_old_name, old_positions, new_positions
                        ))

                bay_templates_by_old_name = self._index_templates(
                    self._cached_templates(module.module_type, MODULEBAY_TEMPLATE_ATTR), old_positions
                )
                for bay in bays_by_module.get(module.pk, []):
                    move = self._plan_component(
                        bay, bay_templates_by_old_name, old_positions, new_positions, include_position=True
                    )
                    if bay.module_id == self.old_module.pk:
                        move.target_parent_id = self.new_bay.pk
                    self.bay_moves.append(move)

                    # Track planned chains raw and resolve on use: the fold inherits an
                    # ancestor's {module} token from the planned position below it,
                    # exactly as a fresh get_module_bay_positions() walk will once the
                    # planned positions are stored, so planner and walker cannot diverge.
                    if (child := installed_module_by_bay.get(bay.pk)) is not None:
                        old_chains[child.pk] = get_module_bay_positions(bay)
                        new_raw_chains[child.pk] = new_raw_chains[module.pk] + [move.target_position or '']

    def _cached_templates(self, module_type, template_attr):
        """
        Return the given template queryset for module_type as a list, fetched once per
        (module_type, template_attr) pair per planning pass regardless of how many moved
        modules share that module_type.
        """
        key = (module_type.pk, template_attr)
        if key not in self._template_cache:
            self._template_cache[key] = list(getattr(module_type, template_attr).all())
        return self._template_cache[key]

    def _index_templates(self, templates, old_positions):
        """
        Map each template's old-context resolved name to the templates producing it. A
        name is a usable rename hint only when exactly one template produces it.
        """
        index = {}
        for template in templates:
            try:
                resolved = self._resolve(template, template.name, old_positions, self.old_module.device)
            except ValueError:
                continue
            index.setdefault(resolved, []).append(template)
        return index

    def _plan_component(self, component, templates_by_old_name, old_positions, new_positions,
                        include_position=False):
        move = ComponentMove(instance=component, target_name=component.name, target_label=component.label)
        if include_position:
            move.target_position = component.position

        matches = templates_by_old_name.get(component.name, ())
        if len(matches) != 1:
            return move
        template = matches[0]

        try:
            move.target_name = self._resolve(template, template.name, new_positions, self.new_device)
        except ValueError:
            self._record_target_failure(component, 'name')
            return move

        try:
            old_label = self._resolve(template, template.label, old_positions, self.old_module.device)
        except ValueError:
            old_label = None
        if old_label is not None and component.label == old_label:
            try:
                move.target_label = self._resolve(template, template.label, new_positions, self.new_device)
            except ValueError:
                self._record_target_failure(component, 'label')

        if include_position:
            try:
                old_position = self._resolve(
                    template, template.position, old_positions, self.old_module.device
                )
            except ValueError:
                old_position = None
            if old_position is not None and component.position == old_position:
                try:
                    move.target_position = self._resolve(
                        template, template.position, new_positions, self.new_device
                    )
                except ValueError:
                    self._record_target_failure(component, 'position')

        return move

    @staticmethod
    def _resolve(template, value, positions, device):
        """
        Resolve {module} and {vc_position} tokens in a template value against an explicit
        position chain and device. Raises ValueError on a token-count mismatch.
        """
        if MODULE_TOKEN in value:
            value = resolve_module_placeholder(value, positions)
        return type(template)._resolve_vc_position(value, device)

    def lock(self):
        """
        Acquire row locks in deterministic order, then re-discover: FK inserts take KEY
        SHARE on their referenced rows, so membership is stable only once every owning
        row is locked. Loop until a re-discovery pass finds no new members, then refresh
        the target rows and recompute the planned changes from the locked state.
        """
        while True:
            self._lock_current_set()
            locked_pks = self._membership_pks()
            self._discover()
            if self._membership_pks() == locked_pks:
                break
        self._refresh_target_state()
        self._plan_renames()
        self._planned = True

    def _membership_pks(self):
        return (
            frozenset(self.module_pks),
            frozenset(bay.pk for bay in self.moved_bays),
            frozenset((model._meta.label, obj.pk) for model, objs in self.components.items() for obj in objs),
        )

    def _refresh_target_state(self):
        # A concurrently deleted target bay is reported by validate(), not raised here
        if (bay := ModuleBay.objects.filter(pk=self.new_bay.pk).first()) is not None:
            self.new_bay = bay
        self.new_device.refresh_from_db()

    def _lock_current_set(self):
        """
        Acquire row locks in a deterministic order: devices, module bays (source
        containing bay, target bay, moved bays), descendant modules, then moved
        components per model. The root Module row is locked by the caller.
        """
        device_pks = sorted({self.old_device_id, self.new_device_id})
        locked_devices = list(
            self.device_model.objects.select_for_update().filter(pk__in=device_pks).order_by('pk')
        )
        if len(locked_devices) != len(device_pks):
            raise AbortRequest(_("Device was deleted before the move could be saved."))
        bay_pks = sorted({
            self.old_module.module_bay_id, self.new_bay.pk, *(bay.pk for bay in self.moved_bays)
        })
        list(ModuleBay.objects.select_for_update().filter(pk__in=bay_pks).order_by('pk'))
        descendant_pks = sorted(self.module_pks - {self.old_module.pk})
        if descendant_pks:
            list(self.module_model.objects.select_for_update().filter(pk__in=descendant_pks).order_by('pk'))
        for model in sorted(self.components, key=lambda model: model._meta.label):
            pks = sorted(obj.pk for obj in self.components[model])
            if pks:
                list(model.objects.select_for_update().filter(pk__in=pks).order_by('pk'))

    # Interface relations carrying topology or device-scoped configuration state which
    # block a cross-device move
    INTERFACE_BLOCKERS = (
        (gettext_lazy('IP addresses assigned'), Q(ip_addresses__isnull=False)),
        (gettext_lazy('FHRP group assignments'), Q(fhrp_group_assignments__isnull=False)),
        (gettext_lazy('tunnel terminations'), Q(tunnel_terminations__isnull=False)),
        (gettext_lazy('L2VPN terminations'), Q(l2vpn_terminations__isnull=False)),
        (gettext_lazy('virtual circuit terminations'), Q(virtual_circuit_termination__isnull=False)),
        (gettext_lazy('wireless links'), Q(wireless_link__isnull=False)),
        (gettext_lazy('wireless LAN assignments'), Q(wireless_lans__isnull=False)),
        (gettext_lazy('an untagged VLAN'), Q(untagged_vlan__isnull=False)),
        (gettext_lazy('tagged VLANs'), Q(tagged_vlans__isnull=False)),
        (gettext_lazy('a Q-in-Q service VLAN'), Q(qinq_svlan__isnull=False)),
        (gettext_lazy('a VLAN translation policy'), Q(vlan_translation_policy__isnull=False)),
        (gettext_lazy('VDC assignments'), Q(vdcs__isnull=False)),
        (gettext_lazy('a VRF assignment'), Q(vrf__isnull=False)),
    )

    def validate(self):
        """
        Validate the move against current database state. Raises ValidationError with
        all failures collected. Called unlocked from Module.clean() for UX and again
        under row locks from Module.save(). The locked pass is authoritative for the
        state its row locks serialize (the moved rows and FK-backed relations to
        them). GenericForeignKey-backed relations (inventory items, IP addresses,
        FHRP, tunnel, and L2VPN terminations) carry no database-level reference to
        the moved rows, so a concurrent insert can still land alongside the move
        after this check has passed; enforcing those invariants atomically is a
        database-level follow-up.
        """
        self._ensure_planned()
        errors = []
        self._validate_target_bay(errors)
        if self.cross_device:
            errors.extend(self._check_cross_device_blockers())
        errors.extend(self._check_name_conflicts())
        errors.extend(self._check_length_violations())
        errors.extend(self._check_target_resolution_failures())
        if errors:
            raise ValidationError(errors)

    def _check_cross_device_blockers(self):
        """
        Reject a cross-device move when any moved component carries topology or
        device-scoped configuration state, or when a parent/bridge/LAG, power outlet,
        or port mapping relation would cross the moved subtree's boundary in either
        direction. Inventory items attached to a moved component also block (v1).
        """
        blockers = []
        moved_interface_pks = {obj.pk for obj in self.components[Interface]}

        # Cabled or connection-marked components
        for model, instances in self.components.items():
            pks = [obj.pk for obj in instances]
            if not pks:
                continue
            count = model.objects.filter(pk__in=pks).filter(
                Q(cable__isnull=False) | Q(mark_connected=True)
            ).count()
            if count:
                blockers.append(_("{count} cabled or connection-marked {type}").format(
                    count=count, type=model._meta.verbose_name_plural
                ))

        # Interface topology/configuration state
        for label, condition in self.INTERFACE_BLOCKERS:
            count = Interface.objects.filter(pk__in=moved_interface_pks).filter(
                condition
            ).distinct().count()
            if count:
                blockers.append(_("{count} interfaces with {label}").format(count=count, label=label))

        # Parent/bridge/LAG relations crossing the moved-set boundary (either direction)
        outward = Interface.objects.filter(pk__in=moved_interface_pks).filter(
            Q(parent__isnull=False) & ~Q(parent_id__in=moved_interface_pks) |
            Q(bridge__isnull=False) & ~Q(bridge_id__in=moved_interface_pks) |
            Q(lag__isnull=False) & ~Q(lag_id__in=moved_interface_pks)
        ).count()
        inward = Interface.objects.exclude(pk__in=moved_interface_pks).filter(
            Q(parent_id__in=moved_interface_pks) |
            Q(bridge_id__in=moved_interface_pks) |
            Q(lag_id__in=moved_interface_pks)
        ).count()
        if outward or inward:
            blockers.append(_(
                "{count} parent, bridge, or LAG interface relations crossing the moved module's boundary"
            ).format(count=outward + inward))

        # Power outlet to power port relations crossing the boundary
        moved_outlet_pks = {obj.pk for obj in self.components[PowerOutlet]}
        moved_power_port_pks = {obj.pk for obj in self.components[PowerPort]}
        split_power = PowerOutlet.objects.filter(
            pk__in=moved_outlet_pks, power_port__isnull=False
        ).exclude(power_port_id__in=moved_power_port_pks).count()
        split_power += PowerOutlet.objects.exclude(pk__in=moved_outlet_pks).filter(
            power_port_id__in=moved_power_port_pks
        ).count()
        if split_power:
            blockers.append(_(
                "{count} power outlet relations crossing the moved module's boundary"
            ).format(count=split_power))

        # Front/rear port mappings crossing the boundary
        moved_front_port_pks = {obj.pk for obj in self.components[FrontPort]}
        moved_rear_port_pks = {obj.pk for obj in self.components[RearPort]}
        split_mappings = PortMapping.objects.filter(
            front_port_id__in=moved_front_port_pks
        ).exclude(rear_port_id__in=moved_rear_port_pks).count()
        split_mappings += PortMapping.objects.filter(
            rear_port_id__in=moved_rear_port_pks
        ).exclude(front_port_id__in=moved_front_port_pks).count()
        if split_mappings:
            blockers.append(_(
                "{count} front/rear port mappings crossing the moved module's boundary"
            ).format(count=split_mappings))

        # Attached inventory items (blocked in v1)
        item_count = 0
        for model, instances in self.components.items():
            pks = [obj.pk for obj in instances]
            if pks:
                item_count += model.objects.filter(
                    pk__in=pks, inventory_items__isnull=False
                ).distinct().count()
        if bay_pks := [bay.pk for bay in self.moved_bays]:
            item_count += ModuleBay.objects.filter(
                pk__in=bay_pks, inventory_items__isnull=False
            ).distinct().count()
        if item_count:
            blockers.append(_("{count} components with attached inventory items").format(count=item_count))

        if not blockers:
            return []
        return [
            _(
                "This module cannot be moved to a different device because the moved components have "
                "active related objects: {blockers}."
            ).format(blockers='; '.join(str(blocker) for blocker in blockers))
        ]

    def _check_name_conflicts(self):
        errors = []
        for model, moves in self.component_moves.items():
            if not moves:
                continue
            seen = set()
            for move in moves:
                if move.target_name in seen:
                    errors.append(
                        _("Moving this module would create more than one {type} named {name}.").format(
                            type=model._meta.verbose_name, name=move.target_name
                        )
                    )
                seen.add(move.target_name)
            conflict_qs = model.objects.filter(
                device_id=self.new_device_id, name__in=seen
            ).exclude(pk__in=[move.instance.pk for move in moves])
            if count := conflict_qs.count():
                sample = ', '.join(conflict_qs.order_by('name').values_list('name', flat=True)[:5])
                errors.append(
                    _(
                        "Moving this module would conflict with {count} existing {type} on device "
                        "{device} (e.g. {sample})."
                    ).format(
                        count=count, type=model._meta.verbose_name_plural,
                        device=self.new_device, sample=sample
                    )
                )
            if not self.cross_device:
                current_names = {move.instance.name for move in moves}
                for move in moves:
                    if move.target_name != move.instance.name and move.target_name in current_names:
                        errors.append(
                            _(
                                "Moving this module would rename {old_name} to {new_name}, which is the "
                                "current name of another moved {type}. Rename the affected components "
                                "manually before moving."
                            ).format(
                                old_name=move.instance.name,
                                new_name=move.target_name,
                                type=model._meta.verbose_name,
                            )
                        )
        # ModuleBay names are unique per (device, module, name); moved bays keep their
        # module assignment, so conflicts are only possible within the moved set
        seen_bays = set()
        for move in self.bay_moves:
            key = (move.instance.module_id, move.target_name)
            if key in seen_bays:
                errors.append(
                    _(
                        "Moving this module would create more than one module bay named {name} "
                        "within the same module."
                    ).format(name=move.target_name)
                )
            seen_bays.add(key)
        if not self.cross_device:
            current_bay_keys = {(move.instance.module_id, move.instance.name) for move in self.bay_moves}
            for move in self.bay_moves:
                if move.target_name != move.instance.name and (
                    (move.instance.module_id, move.target_name) in current_bay_keys
                ):
                    errors.append(
                        _(
                            "Moving this module would rename module bay {old_name} to {new_name}, which is "
                            "the current name of another moved module bay in the same module."
                        ).format(old_name=move.instance.name, new_name=move.target_name)
                    )
        return errors

    def _check_length_violations(self):
        """
        Reject a move whose planned rename would exceed the destination field's
        max_length, rather than deferring to a mid-apply DataError from bulk_update().
        Limits are read from model meta so a future field-length change stays correct
        without editing this method.
        """
        offenders = []
        for model, moves in self.component_moves.items():
            name_limit = model._meta.get_field('name').max_length
            label_limit = model._meta.get_field('label').max_length
            for move in moves:
                offenders.extend(self._length_offenders(move, name=name_limit, label=label_limit))
        name_limit = ModuleBay._meta.get_field('name').max_length
        label_limit = ModuleBay._meta.get_field('label').max_length
        position_limit = ModuleBay._meta.get_field('position').max_length
        for move in self.bay_moves:
            offenders.extend(
                self._length_offenders(move, name=name_limit, label=label_limit, position=position_limit)
            )
        if not offenders:
            return []
        return [
            _("Moving this module would exceed the maximum field length for the following: {offenders}.").format(
                offenders='; '.join(offenders)
            )
        ]

    def _length_offenders(self, move, **limits):
        """
        Return one display string per (field, value) pair on move whose length exceeds
        the given limit. limits maps a field name ('name', 'label', and 'position' for
        module bays) to the destination model's max_length for that field.
        """
        values = {'name': move.target_name, 'label': move.target_label, 'position': move.target_position or ''}
        offenders = []
        for field, limit in limits.items():
            value = values[field]
            if len(value) > limit:
                offenders.append(
                    _("{component}: new {field} {value} ({length} characters) exceeds the "
                      "{limit}-character limit").format(
                        component=move.instance, field=field, value=self._truncate_for_display(value),
                        length=len(value), limit=limit,
                    )
                )
        return offenders

    @staticmethod
    def _truncate_for_display(value, limit=40):
        if len(value) <= limit:
            return value
        return f'{value[:limit]}...'

    def _record_target_failure(self, component, field):
        """
        Record a component whose source value matched a template that cannot be
        resolved for the destination; reported collectively by validate().
        """
        self._target_resolution_failures.append(
            _("{component}: the matched template's {field} cannot be resolved for the destination "
              "bay hierarchy").format(component=component, field=field)
        )

    def _check_target_resolution_failures(self):
        if not self._target_resolution_failures:
            return []
        return [
            _(
                "Moving this module would require template-derived values that cannot be resolved for "
                "the destination bay hierarchy: {failures}. Choose a destination at a compatible "
                "nesting depth or rename the affected components manually before moving."
            ).format(failures='; '.join(self._target_resolution_failures))
        ]

    def _validate_target_bay(self, errors):
        bay = ModuleBay.objects.filter(pk=self.new_bay.pk).first()
        if bay is None:
            errors.append(_("The target module bay no longer exists."))
            return
        if bay.device_id != self.new_device_id:
            errors.append(
                _("Module bay {module_bay} does not belong to device {device}.").format(
                    module_bay=bay, device=self.new_device
                )
            )
        if not bay.enabled:
            errors.append(_("Cannot install a module in a disabled module bay."))
        if occupant := self.module_model.objects.filter(
            module_bay_id=bay.pk
        ).exclude(pk=self.old_module.pk).first():
            errors.append(
                _("Module bay {module_bay} is already occupied by module {module}.").format(
                    module_bay=bay, module=occupant
                )
            )
        if bay.pk in {moved_bay.pk for moved_bay in self.moved_bays}:
            errors.append(_("A module bay cannot belong to a module installed within it."))

    def apply_after_root_save(self):
        """
        Apply the planned updates after the root Module row has been saved: descendant
        modules, then module bays (parent re-pointing; ltree triggers recompute
        path/sort_path), then components, port mappings, and device counters, with
        manual post_save emission for changelog/search side effects.
        """
        self._now = timezone.now()
        self._apply_descendant_modules()
        self._apply_bays()
        self._apply_components()
        self._apply_port_mappings()
        self._recompute_counters()

    def _apply_descendant_modules(self):
        if not self.cross_device:
            return
        descendants = [module for level in self.modules_by_level[1:] for module in level]
        if not descendants:
            return
        for module in descendants:
            module.snapshot()
            module.device_id = self.new_device_id
            module.last_updated = self._now
        self.module_model.objects.bulk_update(descendants, ['device', 'last_updated'], batch_size=BATCH_SIZE)
        self._send_post_saves(self.module_model, descendants, ['device', 'last_updated'])

    def _apply_bays(self):
        """
        Persist planned bay changes in four stages so that ltree hierarchy columns
        (parent) and naming columns (name/position/label) never share a bulk_update
        statement across overlapping subtrees; see utilities/ltree.py for the trigger
        behavior this must respect (BEFORE on parent_id/name; AFTER cascade on the same).
        A cross-device move's device/_site/_location/_rack fields are written in the same
        per-row statement as any rename below, so a bay's (device, name) pair changes as
        one atomic write and is never transiently mismatched against either device.
        """
        bay_changes = []  # [(bay, changed_fields)]
        for move in self.bay_moves:
            bay = move.instance
            changed = []
            if move.target_parent_id is not None and bay.parent_id != move.target_parent_id:
                changed.append('parent')
            if bay.name != move.target_name:
                changed.append('name')
            if bay.label != move.target_label:
                changed.append('label')
            if move.target_position is not None and bay.position != move.target_position:
                changed.append('position')
            if self.cross_device:
                changed.extend(['device', '_site', '_location', '_rack'])
            if not changed:
                continue
            bay.snapshot()
            if self.cross_device:
                bay.device_id = self.new_device_id
                bay._site = self.new_device.site
                bay._location = self.new_device.location
                bay._rack = self.new_device.rack
            if 'parent' in changed:
                bay.parent_id = move.target_parent_id
            bay.name = move.target_name
            bay.label = move.target_label
            if move.target_position is not None:
                bay.position = move.target_position
            bay.last_updated = self._now
            bay_changes.append((bay, changed))

        if not bay_changes:
            return

        # Stage 1: parent-only, for the root's direct child bays being reparented.
        reparented = [bay for bay, changed in bay_changes if 'parent' in changed]
        if reparented:
            ModuleBay.objects.bulk_update(reparented, ['parent'], batch_size=BATCH_SIZE)

        # Stage 2: renames, level-by-level top-down. Same-level bays are disjoint
        # subtrees, so per-level statements cannot overlap, and level N's AFTER-trigger
        # cascade settles descendant sort_paths before level N+1's statement runs.
        # Cross-device device/_site/_location/_rack fields ride along in the same statement.
        level_by_module_pk = {
            module.pk: level_index
            for level_index, level in enumerate(self.modules_by_level)
            for module in level
        }
        renames_by_level = {}
        for bay, changed in bay_changes:
            level_fields = [
                field for field in ('name', 'position', 'label', 'device', '_site', '_location', '_rack')
                if field in changed
            ]
            if not level_fields:
                continue
            level_index = level_by_module_pk[bay.module_id]
            renames_by_level.setdefault(level_index, []).append((bay, level_fields))
        for level_index in sorted(renames_by_level):
            level_bays = renames_by_level[level_index]
            fields = sorted({field for _bay, bay_fields in level_bays for field in bay_fields})
            ModuleBay.objects.bulk_update([bay for bay, _field in level_bays], fields, batch_size=BATCH_SIZE)

        # Stage 3: one scalar statement for every changed bay; never parent/name here.
        updated = [bay for bay, _ in bay_changes]
        ModuleBay.objects.bulk_update(updated, ['last_updated'], batch_size=BATCH_SIZE)

        # Stage 4: sync in-memory ltree columns, then emit post_save per bay with the
        # union of its own changed fields (fields differ per bay, so one call each).
        self._refresh_ltree_columns(updated)
        for bay, changed in bay_changes:
            self._send_post_saves(ModuleBay, [bay], sorted({*changed, 'last_updated'}))

    def _apply_components(self):
        for model, moves in self.component_moves.items():
            updated = []
            update_fields = set()
            for move in moves:
                component = move.instance
                changed = []
                if component.name != move.target_name:
                    changed.append('name')
                if component.label != move.target_label:
                    changed.append('label')
                if self.cross_device:
                    changed.extend(['device', '_site', '_location', '_rack'])
                if not changed:
                    continue
                component.snapshot()
                if self.cross_device:
                    component.device_id = self.new_device_id
                    component._site = self.new_device.site
                    component._location = self.new_device.location
                    component._rack = self.new_device.rack
                component.name = move.target_name
                component.label = move.target_label
                component.last_updated = self._now
                updated.append(component)
                update_fields.update(changed)
            if not updated:
                continue
            fields = set(update_fields)
            if model is Interface and 'name' in update_fields:
                name_field = Interface._meta.get_field('_name')
                for component in updated:
                    name_field.pre_save(component, False)
                fields.add('_name')
            fields.add('last_updated')
            fields = sorted(fields)
            model.objects.bulk_update(updated, fields, batch_size=BATCH_SIZE)
            self._send_post_saves(model, updated, fields)

    def _apply_port_mappings(self):
        # Private model, no changelog or last_updated field; mirrors PortMapping.save()'s device derivation.
        if not self.cross_device:
            return
        moved_front_port_pks = [obj.pk for obj in self.components[FrontPort]]
        moved_rear_port_pks = [obj.pk for obj in self.components[RearPort]]
        if moved_front_port_pks and moved_rear_port_pks:
            PortMapping.objects.filter(
                front_port_id__in=moved_front_port_pks,
                rear_port_id__in=moved_rear_port_pks,
            ).update(device_id=self.new_device_id)

    def _recompute_counters(self):
        # bulk updates bypass the signal-driven counters; apply exact deltas for both devices
        if not self.cross_device:
            return
        counts = {
            'console_port_count': len(self.components[ConsolePort]),
            'console_server_port_count': len(self.components[ConsoleServerPort]),
            'power_port_count': len(self.components[PowerPort]),
            'power_outlet_count': len(self.components[PowerOutlet]),
            'interface_count': len(self.components[Interface]),
            'front_port_count': len(self.components[FrontPort]),
            'rear_port_count': len(self.components[RearPort]),
            'module_bay_count': len(self.moved_bays),
        }
        for counter, count in counts.items():
            if count:
                update_counter(self.device_model, self.old_device_id, counter, -count)
                update_counter(self.device_model, self.new_device_id, counter, count)

    def _refresh_ltree_columns(self, bays):
        """
        bulk_update fires the DB triggers that rewrite path/sort_path, but the in-memory
        instances keep stale values which would leak into changelog snapshots.
        """
        refreshed = {
            row['pk']: row
            for row in ModuleBay.objects.filter(pk__in=[bay.pk for bay in bays]).values(
                'pk', 'path', 'sort_path'
            )
        }
        for bay in bays:
            bay.path = refreshed[bay.pk]['path']
            bay.sort_path = refreshed[bay.pk]['sort_path']

    @staticmethod
    def _send_post_saves(model, instances, update_fields):
        for instance in instances:
            # Clear tracked counter state so the incremental counter receiver no-ops;
            # counters are recomputed explicitly for cross-device moves.
            instance.tracker.clear()
            post_save.send(
                sender=model,
                instance=instance,
                created=False,
                raw=False,
                using=router.db_for_write(model),
                update_fields=update_fields,
            )
