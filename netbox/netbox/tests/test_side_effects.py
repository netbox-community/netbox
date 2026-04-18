"""
Tests for the side-effect registry.

Validates that:
1. The registry is populated with effects from all apps.
2. Query APIs return correct results for known scenarios.
3. needs_full_save() matches expectations from the audit.
4. invisible_to_changelog() identifies the most dangerous effects.
"""
from django.test import TestCase

from netbox.side_effects import Effect, EffectTiming, EffectType, SideEffectRegistry, _fs, effect_registry


class SideEffectRegistryFrameworkTest(TestCase):
    """Tests for the registry framework itself (not the NetBox-specific data)."""

    def setUp(self):
        self.reg = SideEffectRegistry()

    def test_register_and_retrieve(self):
        effect = Effect(
            effect_type=EffectType.DENORMALIZATION,
            source_model='test.source',
            target_model='test.target',
            description='Test effect',
        )
        self.reg.register(effect)
        self.assertEqual(len(self.reg.get_all()), 1)
        self.assertEqual(self.reg.get_for_source('test.source'), [effect])

    def test_get_for_target(self):
        e1 = Effect(effect_type=EffectType.DENORMALIZATION, source_model='a.x', target_model='b.y')
        e2 = Effect(effect_type=EffectType.CASCADE_UPDATE, source_model='c.z', target_model='b.y')
        e3 = Effect(effect_type=EffectType.DENORMALIZATION, source_model='a.x', target_model='d.w')
        self.reg.register_many(e1, e2, e3)
        self.assertEqual(set(self.reg.get_for_target('b.y')), {e1, e2})

    def test_get_triggered_by_field_filter(self):
        e_site = Effect(
            effect_type=EffectType.CASCADE_UPDATE,
            source_model='dcim.device',
            source_fields=_fs(['site', 'location', 'rack']),
        )
        e_name = Effect(
            effect_type=EffectType.FIELD_NORMALIZATION,
            source_model='dcim.device',
            source_fields=_fs(['name']),
        )
        e_any = Effect(
            effect_type=EffectType.DENORMALIZATION,
            source_model='dcim.device',
            source_fields=None,
        )
        self.reg.register_many(e_site, e_name, e_any)

        triggered = self.reg.get_triggered_by('dcim.device', {'site'})
        self.assertIn(e_site, triggered)
        self.assertNotIn(e_name, triggered)
        self.assertIn(e_any, triggered)

    def test_get_triggered_by_excludes_create_only(self):
        e_create = Effect(
            effect_type=EffectType.ENTITY_INSTANTIATION,
            source_model='dcim.device',
            only_on_create=True,
        )
        e_update = Effect(
            effect_type=EffectType.CASCADE_UPDATE,
            source_model='dcim.device',
        )
        self.reg.register_many(e_create, e_update)
        triggered = self.reg.get_triggered_by('dcim.device', {'site'})
        self.assertNotIn(e_create, triggered)
        self.assertIn(e_update, triggered)

    def test_needs_full_save(self):
        self.reg.register(Effect(
            effect_type=EffectType.CASCADE_UPDATE,
            source_model='dcim.device',
            source_fields=_fs(['site', 'rack']),
        ))
        self.reg.register(Effect(
            effect_type=EffectType.FIELD_NORMALIZATION,
            source_model='dcim.device',
            source_fields=_fs(['name']),
        ))
        self.assertTrue(self.reg.needs_full_save('dcim.device', {'site'}))
        self.assertFalse(self.reg.needs_full_save('dcim.device', {'name'}))

    def test_invisible_to_changelog(self):
        e_visible = Effect(
            effect_type=EffectType.CASCADE_UPDATE,
            source_model='a.b',
            uses_bulk_sql=True,
            produces_object_change=True,
        )
        e_invisible = Effect(
            effect_type=EffectType.DENORMALIZATION,
            source_model='a.b',
            uses_bulk_sql=True,
            produces_object_change=False,
        )
        e_orm = Effect(
            effect_type=EffectType.CASCADE_UPDATE,
            source_model='a.b',
            uses_bulk_sql=False,
            produces_object_change=False,
        )
        self.reg.register_many(e_visible, e_invisible, e_orm)
        invisible = self.reg.invisible_to_changelog()
        self.assertEqual(invisible, [e_invisible])

    def test_summary(self):
        self.reg.register(Effect(effect_type=EffectType.DENORMALIZATION, source_model='a.b'))
        self.reg.register(Effect(effect_type=EffectType.CASCADE_UPDATE, source_model='a.b', target_model='c.d'))
        s = self.reg.summary()
        self.assertEqual(s['total_effects'], 2)
        self.assertEqual(s['source_models'], 1)
        self.assertEqual(s['target_models'], 1)


class GlobalRegistryPopulationTest(TestCase):
    """Tests that the global effect_registry is populated by app startup."""

    def test_registry_is_populated(self):
        self.assertGreater(len(effect_registry.get_all()), 50,
                           "Expected at least 50 effects in the global registry")

    def test_dcim_effects_present(self):
        dcim_sources = [e for e in effect_registry.get_all()
                        if e.source_model.startswith('dcim.')]
        self.assertGreater(len(dcim_sources), 20)

    def test_ipam_effects_present(self):
        ipam_sources = [e for e in effect_registry.get_all()
                        if e.source_model.startswith('ipam.')]
        self.assertGreater(len(ipam_sources), 5)

    def test_all_effect_types_represented(self):
        types_present = {e.effect_type for e in effect_registry.get_all()}
        expected_types = {
            EffectType.DENORMALIZATION,
            EffectType.FIELD_NORMALIZATION,
            EffectType.CASCADE_UPDATE,
            EffectType.GRAPH_RECOMPUTATION,
            EffectType.ENTITY_INSTANTIATION,
            EffectType.COUNTER_CACHE,
            EffectType.CONDITIONAL_CLEANUP,
            EffectType.EVENT_DISPATCH,
        }
        missing = expected_types - types_present
        self.assertEqual(missing, set(), f"Missing effect types in registry: {missing}")


class NeedsFullSaveTest(TestCase):
    """
    Validates needs_full_save() against the known FIELDS_REQUIRING_FULL_SAVE
    from netbox-branching. The registry should identify the same models/fields.
    """

    def test_device_site_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.device', {'site'}))

    def test_device_location_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.device', {'location'}))

    def test_device_rack_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.device', {'rack'}))

    def test_device_name_does_not_need_full_save(self):
        self.assertFalse(effect_registry.needs_full_save('dcim.device', {'name'}))

    def test_racktype_any_field_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.racktype', {'name'}))

    def test_cable_any_field_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.cable', {'status'}))

    def test_cabletermination_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.cabletermination', {'cable'}))

    def test_circuittermination_circuit_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('circuits.circuittermination', {'circuit'}))

    def test_circuittermination_term_side_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('circuits.circuittermination', {'term_side'}))

    def test_interface_mode_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.interface', {'mode'}))

    def test_vminterface_mode_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('virtualization.vminterface', {'mode'}))

    def test_location_site_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.location', {'site'}))

    def test_rack_site_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.rack', {'site'}))

    def test_rack_location_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.rack', {'location'}))

    def test_prefix_prefix_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('ipam.prefix', {'prefix'}))

    def test_prefix_vrf_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('ipam.prefix', {'vrf'}))

    def test_prefix_description_does_not_need_full_save(self):
        self.assertFalse(effect_registry.needs_full_save('ipam.prefix', {'description'}))

    def test_wirelesslink_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('wireless.wirelesslink', {'interface_a'}))

    def test_site_region_needs_full_save(self):
        self.assertTrue(effect_registry.needs_full_save('dcim.site', {'region'}))

    def test_site_name_does_not_need_full_save(self):
        self.assertFalse(effect_registry.needs_full_save('dcim.site', {'name'}))

    def test_location_name_does_not_need_full_save(self):
        self.assertFalse(effect_registry.needs_full_save('dcim.location', {'name'}))

    def test_simple_model_does_not_need_full_save(self):
        self.assertFalse(effect_registry.needs_full_save('ipam.ipaddress', {'dns_name'}))
        self.assertFalse(effect_registry.needs_full_save('ipam.iprange', {'description'}))
        self.assertFalse(effect_registry.needs_full_save('dcim.interface', {'description'}))
        self.assertFalse(effect_registry.needs_full_save('dcim.rack', {'name'}))


class InvisibleToChangelogTest(TestCase):
    """Validates that the most dangerous side effects are identified."""

    def test_invisible_effects_exist(self):
        invisible = effect_registry.invisible_to_changelog()
        self.assertGreater(len(invisible), 10,
                           "Expected at least 10 effects invisible to changelog")

    def test_counter_caches_are_invisible(self):
        invisible = effect_registry.invisible_to_changelog()
        counter_effects = [e for e in invisible if e.effect_type == EffectType.COUNTER_CACHE]
        self.assertGreater(len(counter_effects), 5)

    def test_sync_cached_scope_fields_invisible(self):
        invisible = effect_registry.invisible_to_changelog()
        scope_effects = [e for e in invisible
                         if 'sync_cached_scope_fields' in e.handler]
        self.assertGreater(len(scope_effects), 0,
                           "sync_cached_scope_fields should be identified as invisible")

    def test_denormalized_registry_invisible(self):
        invisible = effect_registry.invisible_to_changelog()
        denorm_effects = [e for e in invisible
                          if 'denormalized' in e.handler]
        self.assertGreater(len(denorm_effects), 0,
                           "denormalized field updates should be identified as invisible")

    def test_prefix_hierarchy_invisible(self):
        invisible = effect_registry.invisible_to_changelog()
        prefix_effects = [e for e in invisible
                          if 'handle_prefix' in e.handler]
        self.assertGreater(len(prefix_effects), 0,
                           "Prefix hierarchy updates should be identified as invisible")


class EffectGraphQueryTest(TestCase):
    """Tests for understanding the full impact of specific model changes."""

    def test_device_site_change_cascades(self):
        """Changing Device.site should cascade to components and child devices."""
        effects = effect_registry.get_triggered_by('dcim.device', {'site'})
        target_models = {e.target_model for e in effects if e.target_model}
        self.assertIn('dcim.device', target_models, "Should cascade to child devices")

    def test_location_change_wide_impact(self):
        """Changing Location.site should have wide cascading impact."""
        effects = effect_registry.get_triggered_by('dcim.location', {'site'})
        target_models = {e.target_model for e in effects if e.target_model}
        self.assertTrue(len(target_models) >= 3,
                        f"Location.site change should affect 3+ models, got: {target_models}")

    def test_cable_change_triggers_graph(self):
        """Cable changes should trigger graph recomputation."""
        effects = effect_registry.get_triggered_by('dcim.cable', {'status'})
        graph_effects = [e for e in effects if e.effect_type == EffectType.GRAPH_RECOMPUTATION]
        self.assertGreater(len(graph_effects), 0, "Cable changes should trigger path recomputation")

    def test_prefix_change_triggers_hierarchy(self):
        """Prefix changes should trigger hierarchy recalculation."""
        effects = effect_registry.get_triggered_by('ipam.prefix', {'prefix'})
        denorm_effects = [e for e in effects if e.effect_type == EffectType.DENORMALIZATION]
        self.assertGreater(len(denorm_effects), 0, "Prefix changes should trigger hierarchy update")

    def test_summary_stats(self):
        """Verify summary provides useful stats."""
        s = effect_registry.summary()
        self.assertGreater(s['total_effects'], 50)
        self.assertGreater(s['source_models'], 10)
        self.assertGreater(s['invisible_to_changelog'], 5)
